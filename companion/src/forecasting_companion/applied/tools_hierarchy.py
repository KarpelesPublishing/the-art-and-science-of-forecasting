"""Chapter 18: hierarchical forecasting from node histories.

Builds the summing matrix from a child,parent edge list, forecasts every node with
the engine, estimates the base-forecast error covariance from the engine's own
validation origins, and reconciles by bottom-up, OLS and MinT. Every reconciled
forecast is checked for coherence; every method is scored on the untouched final
holdout so the reader sees whether reconciliation helped this hierarchy.
"""
import numpy as np
import pandas as pd
from .core import require, numeric, integer, time_frame, finish
from ..optional import have, hint


def build_S(edges):
    """child,parent edges -> (S, nodes, leaves). Aggregates first (by depth, then name), leaves last and sorted,
    so the bottom rows of S are the identity."""
    parents = {}
    for child, parent in edges:
        child, parent = str(child), str(parent)
        if child == parent:
            raise ValueError(f'Node {child} cannot be its own parent')
        if child in parents:
            raise ValueError(f'Node {child} has two parents; a tree hierarchy is required')
        parents[child] = parent
    all_nodes = set(parents) | set(parents.values())
    leaves = sorted(n for n in all_nodes if n not in parents.values())
    def depth(node):
        d = 0
        while node in parents:
            node = parents[node]; d += 1
            if d > len(all_nodes):
                raise ValueError('Cycle in hierarchy edges')
        return d
    aggregates = sorted((n for n in all_nodes if n not in leaves), key=lambda n: (depth(n), n))
    nodes = aggregates + leaves
    def descendants(node):
        out = set()
        stack = [node]
        while stack:
            cur = stack.pop()
            for child, parent in parents.items():
                if parent == cur:
                    out.add(child); stack.append(child)
        return out
    S = np.zeros((len(nodes), len(leaves)))
    for i, node in enumerate(nodes):
        if node in leaves:
            S[i, leaves.index(node)] = 1.0
        else:
            for leaf in descendants(node) & set(leaves):
                S[i, leaves.index(leaf)] = 1.0
    return S, nodes, leaves


def reconcile(S, base, W=None):
    """Linear reconciliation. W=None gives OLS (G=(S'S)^-1 S'); otherwise MinT with G = solve(S'W^-1 S, S'W^-1)."""
    S = np.asarray(S, float); base = np.asarray(base, float)
    if W is None:
        G = np.linalg.solve(S.T @ S, S.T)
    else:
        W = np.asarray(W, float)
        inv = np.linalg.inv(W)
        G = np.linalg.solve(S.T @ inv @ S, S.T @ inv)
    return S @ (G @ base), G


def shrink_covariance(E, lam):
    W = np.cov(E, rowvar=False)
    W = (1 - lam) * W + lam * np.diag(np.diag(W))
    return W


def reconcile_hierarchy(d, c):
    from ..engine import forecast_series, POOLS
    edges = c.get('edges')
    if not edges:
        raise ValueError('Supply edges as a list of [child, parent] pairs')
    S, nodes, leaves = build_S(edges)
    require(d, ['node', 'timestamp', 'target']); numeric(d, ['target'])
    histories = {}
    for name, g in d.groupby('node'):
        f, freq = time_frame(g, c, minimum=2)
        histories[str(name)] = (f, freq)
    if set(histories) != set(nodes):
        raise ValueError(f'Complete node histories required: edges name {sorted(nodes)}, histories cover {sorted(histories)}')
    ref = histories[nodes[0]][0].timestamp.reset_index(drop=True)
    for name, (f, _) in histories.items():
        if not f.timestamp.reset_index(drop=True).equals(ref):
            raise ValueError(f'Node {name} timestamps differ from {nodes[0]}; all nodes need identical calendars')
    freq = histories[nodes[0]][1]
    Y = np.column_stack([histories[n][0].target.to_numpy(float) for n in nodes])
    m = len(leaves); n_nodes = len(nodes)
    tol = float(c.get('history_tolerance', 0.01))
    resid = np.abs(S @ Y[:, -m:].T - Y.T).max()
    scale = max(np.abs(Y).max(), 1e-12)
    if resid / scale > tol:
        raise ValueError(f'Historical values are not coherent: max |S*leaves - node| = {resid:.4g} exceeds tolerance {tol} of max |value|')
    h = integer(c, 'horizon', 12)
    if c.get('season') == 'auto' or 'season' not in c:
        from ..profile import profile_series
        first = d[d.node == d.node.iloc[0]] if 'node' in d.columns else d
        season = int(profile_series(first.drop(columns=['node'], errors='ignore'), {k: v for k, v in c.items() if k != 'season'})['season'])
    else:
        season = integer(c, 'season', 12)
    pool = c.get('pool', 'smoothing')
    if pool not in POOLS:
        raise ValueError(f'pool must be one of {sorted(POOLS)}')
    transform = c.get('transform', 'auto'); origins = integer(c, 'origins', 5, 2)
    lam = float(c.get('shrinkage', 0.2))
    if not 0 <= lam <= 1:
        raise ValueError('shrinkage must lie in [0, 1]')
    T = len(ref)
    selected, holdout_base, future_base, errors, intervals = {}, {}, {}, {}, {}
    holdout_ok = True; short_reason = None
    for j, name in enumerate(nodes):
        y = Y[:, j]
        # run B: full history; its forecast is the production base forecast
        table_b, sum_b = forecast_series(y, ref, h, season, pool=pool, freq=freq, transform=transform, max_origins=origins)
        future_base[name] = table_b.forecast.to_numpy()
        if 'lower' in table_b:
            intervals[name] = (table_b.lower.to_numpy(), table_b.upper.to_numpy())
        # run A: everything before a tool-level holdout; its forecast is the holdout base forecast.
        # When the history cannot hold the engine's origins twice over, the holdout leaderboard is
        # skipped and the error covariance comes from run B's own rolling origins instead.
        try:
            table_a, sum_a = forecast_series(y[:-h], ref.iloc[:-h], h, season, pool=pool, freq=freq, transform=transform, max_origins=origins) if holdout_ok else (None, None)
        except ValueError as exc:
            holdout_ok = False; short_reason = str(exc); table_a = sum_a = None
        source = sum_a if holdout_ok else sum_b
        preds = pd.DataFrame(source['validation_predictions'])
        preds = preds[preds.model == source['selected']].sort_values(['origin', 'horizon'])
        errors[name] = (preds.actual - preds.forecast).to_numpy()
        if holdout_ok:
            holdout_base[name] = table_a.forecast.to_numpy()
        selected[name] = dict(holdout_model=sum_a['selected'] if holdout_ok else None, production_model=sum_b['selected'])
    # every node shares one timeline, so a too-short history fails on the first node and all errors come from run B
    lengths = {len(e) for e in errors.values()}
    not_done = []
    if not holdout_ok:
        not_done.append(f'Holdout leaderboard skipped: the history is too short to run the engine on a pre-holdout slice ({short_reason}); the error covariance comes from the engine\'s own rolling origins on the full history')
    W = None
    if len(lengths) == 1 and next(iter(lengths)) >= n_nodes + 2:
        E = np.column_stack([errors[n] for n in nodes])
        W = shrink_covariance(E, lam)
        if np.linalg.eigvalsh(W).min() <= 0:
            W = None; not_done.append('MinT skipped: shrunk error covariance is not positive definite')
    else:
        not_done.append(f'MinT skipped: need at least {n_nodes + 2} matched validation errors per node, have {sorted(lengths)}')
    error_rows = int(next(iter(lengths))) if len(lengths) == 1 else None
    E = E if (len(lengths) == 1 and next(iter(lengths)) >= n_nodes + 2) else None
    if not have('hierarchicalforecast'):
        not_done.append('hierarchicalforecast cross-check (MinTrace shrink, ERM) not tried: ' + hint('hierarchicalforecast'))
    hf_tags = {'aggregates': np.arange(n_nodes - m), 'bottom': np.arange(n_nodes - m, n_nodes)}
    hf_checked = {}

    def all_methods(base_matrix):
        # base_matrix: h x n_nodes
        out = {'base': base_matrix.copy()}
        out['bottom_up'] = (S @ base_matrix[:, -m:].T).T
        ols = np.vstack([reconcile(S, row, None)[0] for row in base_matrix])
        out['OLS'] = ols
        if W is not None:
            out['MinT'] = np.vstack([reconcile(S, row, W)[0] for row in base_matrix])
        if have('hierarchicalforecast'):
            # the optional extra: its OLS and bottom-up must agree with the in-house algebra (checked), its
            # shrinkage MinTrace estimates lambda itself and is reported as a separate row
            try:
                from hierarchicalforecast.methods import MinTrace, BottomUp
                hf_ols = MinTrace(method='ols').fit_predict(S=S, y_hat=base_matrix.T, tags=hf_tags)['mean'].T
                hf_bu = BottomUp().fit_predict(S=S, y_hat=base_matrix.T, tags=hf_tags)['mean'].T
                hf_checked['OLS'] = bool(np.allclose(hf_ols, out['OLS'], atol=1e-6)); hf_checked['bottom_up'] = bool(np.allclose(hf_bu, out['bottom_up'], atol=1e-6))
                if E is not None:
                    y_hat_in = np.zeros_like(E.T); y_in = E.T          # residuals are what the covariance needs; the level cancels
                    out['MinT_shrink_hf'] = MinTrace(method='mint_shrink').fit_predict(S=S, y_hat=base_matrix.T, tags=hf_tags, y_insample=y_in, y_hat_insample=y_hat_in)['mean'].T
            except Exception as exc:
                not_done.append(f'hierarchicalforecast cross-check failed: {str(exc)[:80]}')
        for k, v in out.items():
            if k != 'base' and not np.allclose(v, (S @ v[:, -m:].T).T, atol=1e-8):
                raise AssertionError(f'{k} lost coherence')
        return out

    holdout = {}
    if holdout_ok:
        hold = all_methods(np.column_stack([holdout_base[n] for n in nodes]))
        actual = Y[-h:, :]
        for k, v in hold.items():
            per_node = {n: float(np.abs(actual[:, j] - v[:, j]).mean()) for j, n in enumerate(nodes)}
            holdout[k] = dict(mae_by_node=per_node, mean_mae=float(np.mean(list(per_node.values()))),
                              nodes_improved_vs_base=int(sum(per_node[n] < np.abs(actual[:, j] - hold['base'][:, j]).mean() - 1e-12 for j, n in enumerate(nodes))) if k != 'base' else 0)
    leaderboard = sorted(holdout, key=lambda k: holdout[k]['mean_mae']) if holdout else ['MinT' if W is not None else 'OLS', 'bottom_up']
    fut = all_methods(np.column_stack([future_base[n] for n in nodes]))
    future_dates = pd.date_range(ref.iloc[-1], periods=h + 1, freq=freq)[1:]
    rows = []
    for j, name in enumerate(nodes):
        for step in range(h):
            row = dict(node=name, timestamp=future_dates[step], base=fut['base'][step, j], bottom_up=fut['bottom_up'][step, j], OLS=fut['OLS'][step, j])
            if 'MinT' in fut:
                row['MinT'] = fut['MinT'][step, j]
            if 'MinT_shrink_hf' in fut:
                row['MinT_shrink_hf'] = fut['MinT_shrink_hf'][step, j]
            rows.append(row)
    table = pd.DataFrame(rows)
    coherent = bool(c.get('coherent_quantiles', False))
    if coherent:
        if W is None or len(intervals) < n_nodes:
            not_done.append('Coherent quantiles skipped: every node needs a selected model with intervals and a usable error covariance')
        else:
            rng = np.random.default_rng(integer(c, 'seed', 18, 0))
            sd_w = np.sqrt(np.diag(W)); corr = W / np.outer(sd_w, sd_w)
            q = {0.1: [], 0.5: [], 0.9: []}
            for step in range(h):
                sd = np.array([(intervals[n][1][step] - intervals[n][0][step]) / 2.5631 for n in nodes])
                draws = rng.multivariate_normal(fut['base'][step], corr * np.outer(sd, sd), size=500)
                rec = np.vstack([reconcile(S, row, W)[0] for row in draws])
                for level in q:
                    q[level].append(np.quantile(rec, level, axis=0))
            for level, key in ((0.1, 'MinT_q10'), (0.5, 'MinT_q50'), (0.9, 'MinT_q90')):
                arr = np.vstack(q[level])
                table[key] = [arr[step, j] for j in range(n_nodes) for step in range(h)]
    else:
        not_done.append('Coherent quantiles not requested (set coherent_quantiles: true)')
    best = leaderboard[0]
    lead = ((f'On the final {h}-step holdout, {best} had the lowest mean MAE across {n_nodes} nodes '
             f'({holdout[best]["mean_mae"]:.4g} vs base {holdout["base"]["mean_mae"]:.4g}). ') if holdout else
            (f'No tool-level holdout was possible on {T} observations; {best} is reported first because it uses the most information, not because it was scored here. '))
    interpretation = (lead
                      + ('MinT used a shrunk covariance from ' + str(error_rows) + ' validation errors per node. ' if W is not None else '')
                      + 'Coherence holds exactly for every reconciled column; accuracy gains must be judged on the holdout, not assumed.')
    return finish(table, method='Hierarchical reconciliation (bottom-up, OLS' + (', MinT' if W is not None else '') + ') over engine base forecasts',
                  interpretation=interpretation,
                  assumptions=['Tree hierarchy with one parent per node', 'Base forecasts unbiased for MinT to dominate', f'Error covariance shrunk toward its diagonal with lambda {lam}', 'Historical values coherent within tolerance'],
                  not_done=not_done, status='passed' if holdout_ok else 'provisional',
                  nodes=nodes, leaves=leaves, S=S.tolist(), selected=selected, shrinkage=lam, error_rows=error_rows,
                  holdout=holdout, leaderboard=leaderboard, coherence_max_abs_residual=float(resid), pool=pool, horizon=h, hierarchicalforecast_agrees=hf_checked or None)
