"""Chapter 22: what the counterfactual is, and how badly it can be wrong.

Difference-in-differences, a pre-period OLS counterfactual on the declared controls,
a synthetic control with nonnegative weights summing to one, placebo-in-space and
placebo-in-time distributions with p-values, and an event-study table with a
pre-trend check. Everything is conditional on the stated identification argument.
"""
import numpy as np
import pandas as pd
from scipy import stats
from scipy.optimize import minimize
from .core import require, numeric, time_frame, integer, finish


def synthetic_weights(donors_pre, treated_pre):
    """Nonnegative weights summing to one that best reproduce the treated pre-period."""
    k = donors_pre.shape[1]
    if k < 2:
        raise ValueError('synthetic control needs at least two donors')
    obj = lambda w: float(np.sum((donors_pre @ w - treated_pre) ** 2))
    res = minimize(obj, np.full(k, 1 / k), method='SLSQP', bounds=[(0, 1)] * k, constraints={'type': 'eq', 'fun': lambda w: w.sum() - 1})
    w = np.clip(res.x, 0, None); w = w / w.sum()
    return w


def _ols_counterfactual(controls, treated, pre):
    X = np.c_[np.ones(len(treated)), controls]
    beta = np.linalg.lstsq(X[pre], treated[pre], rcond=None)[0]
    return X @ beta


def causal_effects(d, c):
    controls = c.get('controls', ['control'])
    if not isinstance(controls, list) or not controls:
        raise ValueError('controls must be a non-empty list of column names')
    f, _ = time_frame(d, c, columns=('treated', *controls), minimum=30)
    if not c.get('intervention'):
        raise ValueError('Declare the intervention timestamp before estimation')
    split = pd.to_datetime(c['intervention'], utc=True); pre = (f.timestamp < split).to_numpy()
    if pre.sum() < 15 or (~pre).sum() < 5:
        raise ValueError('Need 15 pre and 5 post observations')
    seed = integer(c, 'seed', 22, 0); rng = np.random.default_rng(seed)
    placebos = integer(c, 'placebos', 200, 10); window = integer(c, 'event_window', 6, 1)
    y = f.treated.to_numpy(float); C = f[controls].to_numpy(float)
    post = ~pre
    did = float((y[post].mean() - y[pre].mean()) - (C[post].mean(axis=0).mean() - C[pre].mean(axis=0).mean()))
    ols_cf = _ols_counterfactual(C, y, pre); ols_effect = y - ols_cf
    pre_rmse = float(np.sqrt(np.mean(ols_effect[pre] ** 2)))
    table = pd.DataFrame({'timestamp': f.timestamp.to_numpy(), 'observed': y, 'ols_counterfactual': ols_cf, 'ols_effect': ols_effect, 'post': post})
    first_post = int(np.argmax(post)); table['relative_period'] = np.arange(len(y)) - first_post
    not_done = []
    sc = None
    if len(controls) >= 2:
        w = synthetic_weights(C[pre], y[pre]); sc_cf = C @ w; sc_effect = y - sc_cf
        table['sc_counterfactual'] = sc_cf; table['sc_effect'] = sc_effect
        sc = dict(weights={col: float(w[i]) for i, col in enumerate(controls)}, pre_rmse=float(np.sqrt(np.mean(sc_effect[pre] ** 2))), post_mean_effect=float(sc_effect[post].mean()))
        # placebo in space: treat each donor in turn, remaining donors as its pool
        ratios = []; actual_ratio = abs(sc['post_mean_effect']) / max(sc['pre_rmse'], 1e-9)
        for j in range(len(controls)):
            others = np.delete(C, j, axis=1)
            if others.shape[1] < 2:
                continue
            wj = synthetic_weights(others[pre], C[pre, j]); ej = C[:, j] - others @ wj
            ratios.append(abs(ej[post].mean()) / max(np.sqrt(np.mean(ej[pre] ** 2)), 1e-9))
        if ratios:
            sc['placebo_space'] = dict(ratios=[float(r) for r in ratios], actual_ratio=float(actual_ratio), p_value=float((1 + sum(r >= actual_ratio for r in ratios)) / (1 + len(ratios))),
                                       note='Ratio of post effect to pre RMSE; p is the rank of the treated unit among donors treated in turn')
        else:
            not_done.append('Placebo-in-space needs at least three controls')
    else:
        not_done.append('Synthetic control skipped: needs at least two control columns')
    # placebo in time: pseudo interventions inside the pre period
    pre_idx = np.where(pre)[0]; candidates = [i for i in pre_idx if i >= 10 and pre.sum() - i >= 5]
    if candidates:
        picks = rng.choice(candidates, size=min(placebos, len(candidates)), replace=len(candidates) < placebos)
        placebo_effects = []
        for i in picks:
            pseudo_pre = np.zeros(len(y), bool); pseudo_pre[:i] = True
            cf = _ols_counterfactual(C[pre], y[pre], pseudo_pre[pre])
            placebo_effects.append(float((y[pre] - cf)[~pseudo_pre[pre]].mean()))
        actual = float(ols_effect[post].mean())
        placebo_time = dict(effects_summary=dict(mean=float(np.mean(placebo_effects)), sd=float(np.std(placebo_effects)), q05=float(np.quantile(placebo_effects, .05)), q95=float(np.quantile(placebo_effects, .95))),
                            p_value=float(np.mean(np.abs(placebo_effects) >= abs(actual))), draws=len(placebo_effects))
    else:
        placebo_time = None; not_done.append('Placebo-in-time skipped: pre period too short')
    # event study
    rel = table.relative_period.to_numpy(); es = []
    for r in range(-window, int(post.sum())):
        mask = rel == r
        if mask.any():
            es.append(dict(relative_period=int(r), ols_effect=float(ols_effect[mask].mean()), **({'sc_effect': float(table.sc_effect[mask].mean())} if sc else {})))
    pre_window = (rel < 0) & (rel >= -window)
    slope = stats.linregress(rel[pre_window], ols_effect[pre_window]) if pre_window.sum() >= 3 else None
    pretrend = dict(slope=float(slope.slope), p_value=float(slope.pvalue), flag=bool(slope.pvalue < 0.1)) if slope else None
    identification = c.get('identification', 'Not established from these data alone')
    interpretation = (f'DiD {did:.4g}; OLS counterfactual post-mean effect {float(ols_effect[post].mean()):.4g} (pre RMSE {pre_rmse:.4g})'
                      + (f'; synthetic control effect {sc["post_mean_effect"]:.4g} with weights {sc["weights"]}' if sc else '')
                      + (f'; placebo-in-space p {sc["placebo_space"]["p_value"]:.2f}' if sc and 'placebo_space' in sc else '')
                      + (f'; placebo-in-time p {placebo_time["p_value"]:.2f}' if placebo_time else '')
                      + (f'. Pre-trend slope p {pretrend["p_value"]:.2f}' + (' (flag)' if pretrend['flag'] else '') if pretrend else '')
                      + f'. Identification: {identification}. These are conditional counterfactual calculations, not automatic causal identification.')
    return finish(table, method='DiD, OLS counterfactual, synthetic control, placebo and event-study checks', interpretation=interpretation,
                  assumptions=['Controls unaffected by the intervention', 'Pre-period relationship would have continued untreated', 'No concurrent treated-only shocks', 'Intervention date declared before estimation'],
                  not_done=not_done, status='passed', did=did, post_mean_effect=float(ols_effect[post].mean()), pre_rmse=pre_rmse,
                  sc_weights=sc['weights'] if sc else None, sc_post_mean_effect=sc['post_mean_effect'] if sc else None, sc_pre_rmse=sc['pre_rmse'] if sc else None,
                  placebo_space=sc.get('placebo_space') if sc else None, placebo_time=placebo_time, event_study=es, pretrend=pretrend, identification=identification, controls=controls)
