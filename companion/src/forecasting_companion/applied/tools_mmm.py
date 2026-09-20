"""Chapter 20: marketing mix modelling with N channels.

Adstock and saturation per channel with the decay and saturation kind chosen on earlier
origins by predictive error (never on the holdout), a closed-form ridge fit, holdout
accuracy against seasonal naive, response curves and marginal ROAS at current spend,
refit stability across expanding windows, optional Gaussian priors on the channel
coefficients, and a budget reallocation scenario under a fixed total. Attribution here
is a fitted decomposition, not an identified causal effect; the summary says so.
"""
import numpy as np
import pandas as pd
from .core import require, numeric, integer, time_frame, finish
from ..practitioner import adstock

SATURATIONS = ('hill', 'log', 'negexp', 'none')


def saturate(x, kind, scale):
    """Diminishing-returns transform with the scale fixed on training data."""
    x = np.asarray(x, float)
    if kind == 'hill':
        return x / (scale + x)
    if kind == 'log':
        return np.log1p(x / max(scale, 1e-9))
    if kind == 'negexp':
        return 1 - np.exp(-x / max(scale, 1e-9))
    if kind == 'none':
        return x / max(scale, 1e-9)
    raise ValueError(f'saturation must be one of {SATURATIONS}')


def ridge(X, y, alpha, penalised):
    """Closed-form ridge with a penalty only on the columns flagged in `penalised`."""
    P = np.diag(penalised.astype(float))
    return np.linalg.solve(X.T @ X + alpha * P, X.T @ y)


def mmm(d, c):
    f, _ = time_frame(d, c, columns=('sales',), minimum=60)
    available = [col for col in f.columns if col not in ('timestamp', 'sales')]
    channels = c.get('channels')
    legacy = channels is None and {'spend_a', 'spend_b'} <= set(available)
    if channels is None:
        channels = ['spend_a', 'spend_b'] if legacy else [col for col in available if col.startswith('spend')]
    if not channels or any(col not in available for col in channels):
        raise ValueError(f'channels must name spend columns present in the data; available: {available}')
    controls = c.get('controls', [])
    if any(col not in available or col in channels for col in controls):
        raise ValueError('controls must name numeric columns that are not channels')
    numeric(f, channels, True)
    if controls:
        numeric(f, controls)
    h = integer(c, 'horizon', 12); season = integer(c, 'season', 12)
    n_origins = integer(c, 'origins', 3, 1); windows = integer(c, 'windows', 3, 1)
    alpha = float(c.get('alpha', 1.0))
    if alpha < 0:
        raise ValueError('alpha must be nonnegative')
    grid = c.get('decay_grid', [0.0, 0.3, 0.5, 0.7, 0.9])
    if not all(0 <= g < 1 for g in grid):
        raise ValueError('decay_grid values must lie in [0, 1)')
    sat_cfg = c.get('saturation', 'auto')
    if sat_cfg not in SATURATIONS + ('auto',):
        raise ValueError(f'saturation must be auto or one of {SATURATIONS}')
    y = f.sales.to_numpy(float); n = len(y); t = np.arange(n)
    if h >= n // 3:
        raise ValueError('Reserve enough training observations before the holdout')
    spend = {ch: f[ch].to_numpy(float) for ch in channels}
    initial = {ch: float(c.get('initial_' + ch.split('_')[-1], 0)) if legacy else 0.0 for ch in channels}
    fixed_decay = {ch: float(c['decay_' + ch.split('_')[-1]]) for ch in channels if legacy and ('decay_' + ch.split('_')[-1]) in c}
    fixed_half = {ch: float(c['half_' + ch.split('_')[-1]]) for ch in channels if legacy and ('half_' + ch.split('_')[-1]) in c}

    def design(stop, decays, kind, scales=None):
        cols = [np.ones(n), t / season, np.sin(2 * np.pi * t / season), np.cos(2 * np.pi * t / season)]
        pen = [False] * 4
        scales = scales or {}
        for ch in channels:
            stock = adstock(spend[ch], decays[ch], initial[ch])
            scale = scales.get(ch)
            if scale is None:
                train_stock = stock[:stop]
                scale = fixed_half.get(ch, float(np.median(train_stock[train_stock > 0])) if np.any(train_stock > 0) else 1.0)
                scales[ch] = scale
            cols.append(saturate(stock, kind, scale)); pen.append(True)
        for col in controls:
            v = f[col].to_numpy(float); mu, sd = v[:stop].mean(), v[:stop].std() or 1.0
            cols.append((v - mu) / sd); pen.append(True)
        return np.column_stack(cols), np.array(pen), scales

    def block_mae(stop, decays, kind):
        X, pen, _ = design(stop - h, decays, kind)
        beta = ridge(X[:stop - h], y[:stop - h], alpha, pen)
        return float(np.abs(X[stop - h:stop] @ beta - y[stop - h:stop]).mean())

    end = n - h
    origins = [end - j * h for j in range(n_origins, 0, -1)]
    if origins[0] - h < 24:
        raise ValueError('Not enough history before the selection origins for the requested horizon and origins')
    # coordinate-wise selection on earlier origins only
    decays = {ch: fixed_decay.get(ch, 0.5) for ch in channels}
    kind0 = 'hill' if sat_cfg == 'auto' else sat_cfg
    selection = {}
    for ch in channels:
        if ch in fixed_decay:
            continue
        scores = {g: float(np.mean([block_mae(o, {**decays, ch: g}, kind0) for o in origins])) for g in grid}
        decays[ch] = min(scores, key=scores.get); selection[ch] = {str(k): v for k, v in scores.items()}
    kind = kind0
    if sat_cfg == 'auto':
        kscores = {k: float(np.mean([block_mae(o, decays, k) for o in origins])) for k in SATURATIONS}
        kind = min(kscores, key=kscores.get); selection['saturation'] = kscores
    # final fit on training, holdout scored once
    X, pen, scales = design(end, decays, kind)
    beta = ridge(X[:end], y[:end], alpha, pen)
    pred = X[end:] @ beta
    baseline = np.resize(y[:end][-season:], h) if end >= season else np.repeat(y[end - 1], h)
    test_mae = float(np.abs(y[end:] - pred).mean()); baseline_mae = float(np.abs(y[end:] - baseline).mean())
    names = ['intercept', 'trend', 'sin', 'cos'] + channels + controls
    coefficients = dict(zip(names, map(float, beta)))
    # response curves and marginal ROAS at current spend
    curves, marginal = {}, {}
    for i, ch in enumerate(channels):
        coef = beta[4 + i]; current = float(spend[ch][-season:].mean()); steady = lambda s: s / (1 - decays[ch])
        gridspend = np.linspace(0, max(spend[ch].max() * 1.5, 1e-9), 25)
        curves[ch] = dict(spend=gridspend.tolist(), response=(coef * saturate(steady(gridspend), kind, scales[ch])).tolist())
        eps = max(current * 0.01, 1e-6)
        marginal[ch] = float(coef * (saturate(steady(current + eps), kind, scales[ch]) - saturate(steady(current - eps), kind, scales[ch])) / (2 * eps))
    # refit stability
    refits = []
    for stop in np.linspace(max(24, end // 2), end, windows, dtype=int):
        Xw, penw, _ = design(int(stop), decays, kind); bw = ridge(Xw[:stop], y[:stop], alpha, penw)
        refits.append(dict(training_rows=int(stop), **{ch: float(bw[4 + i]) for i, ch in enumerate(channels)}))
    # optional Gaussian priors on channel coefficients
    posterior = None
    if 'prior_mean' in c:
        pm = np.asarray(c['prior_mean'], float); ps = np.asarray(c.get('prior_sd', np.ones(len(channels))), float)
        noise = float(c.get('noise_sd', np.std(y[:end] - X[:end] @ beta)))
        if pm.shape != (len(channels),) or ps.shape != (len(channels),):
            raise ValueError('prior_mean and prior_sd need one value per channel')
        background = X[:end][:, [0, 1, 2, 3] + list(range(4 + len(channels), X.shape[1]))] @ beta[[0, 1, 2, 3] + list(range(4 + len(channels), X.shape[1]))]
        Xc = X[:end][:, 4:4 + len(channels)]; resid = y[:end] - background
        # exact Gaussian posterior with a diagonal prior (practitioner.gaussian_update takes one scalar prior sd)
        prec = np.diag(1 / ps ** 2) + Xc.T @ Xc / noise ** 2
        cov = np.linalg.inv(prec); mean = cov @ (np.diag(1 / ps ** 2) @ pm + Xc.T @ resid / noise ** 2)
        posterior = dict(mean={ch: float(mean[i]) for i, ch in enumerate(channels)}, sd={ch: float(np.sqrt(cov[i, i])) for i, ch in enumerate(channels)}, noise_sd=noise)
    # reallocation under a fixed total (conditional scenario)
    total = float(c.get('reallocation_total', sum(spend[ch][-season:].mean() for ch in channels)))
    alloc = {ch: float(spend[ch][-season:].mean()) for ch in channels}
    scale_to = total / max(sum(alloc.values()), 1e-9); alloc = {ch: v * scale_to for ch, v in alloc.items()}
    def response(a):
        return sum(beta[4 + i] * saturate(a[ch] / (1 - decays[ch]), kind, scales[ch]) for i, ch in enumerate(channels))
    start_resp = response(alloc); step = total * 0.01
    for _ in range(200):
        best = None
        for src in channels:
            if alloc[src] < step:
                continue
            for dst in channels:
                if dst == src:
                    continue
                trial = dict(alloc); trial[src] -= step; trial[dst] += step
                gain = response(trial) - response(alloc)
                if best is None or gain > best[0]:
                    best = (gain, trial)
        if best is None or best[0] <= 1e-9:
            break
        alloc = best[1]
    reallocation = dict(total=total, current={ch: float(spend[ch][-season:].mean()) for ch in channels}, proposed=alloc,
                        predicted_response_change=float(response(alloc) - start_resp), note='Conditional scenario from the fitted response curves; not a measured causal return')
    table = pd.DataFrame({'timestamp': f.timestamp.iloc[end:].to_numpy(), 'actual': y[end:], 'prediction': pred, 'baseline': baseline})
    not_done = ['Causal identification: coefficients are a fitted decomposition; confounding by unobserved demand drivers remains',
                'No geo or holdout experiment was used to calibrate the response curves']
    if posterior is None:
        not_done.append('No priors supplied (prior_mean, prior_sd); ridge only')
    interpretation = (f'{len(channels)}-channel MMM ({kind} saturation, decays {decays}) holdout MAE {test_mae:.4g} vs seasonal naive {baseline_mae:.4g}. '
                      f'Marginal response at current spend: ' + ', '.join(f'{ch} {marginal[ch]:.3g}' for ch in channels) + '. '
                      f'Refits across {windows} windows show how stable the channel coefficients are; instability is a warning about attribution, not about prediction.')
    return finish(table, method='Adstock and saturation MMM with ridge fit and rolling-origin selection', interpretation=interpretation,
                  assumptions=['Spend schedules known for the holdout', 'Geometric carryover with the selected decays', f'{kind} saturation scaled on training data', 'Trend and one seasonal harmonic as background'],
                  not_done=not_done, status='passed', channels=channels, controls=controls, selected=dict(decays=decays, saturation=kind, scores=selection), alpha=alpha,
                  coefficients=coefficients, condition_number=float(np.linalg.cond(X[:end])), test_mae=test_mae, baseline_mae=baseline_mae,
                  response_curves=curves, marginal_roas=marginal, refits=refits, posterior=posterior, reallocation=reallocation, origins=[str(f.timestamp.iloc[o - 1]) for o in origins])
