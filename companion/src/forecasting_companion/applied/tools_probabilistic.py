"""Chapter 17: prediction intervals you can check.

Given a plain series, select a model with the engine on history before a calibration
block, build split-conformal intervals from the calibration residuals (finite-sample
rank), then run the adaptive conformal update of Gibbs and Candes through a later
test block. Report coverage, width, interval score and pinball loss for both, and
compare with the model's own nominal band when one exists.
"""
import math
import numpy as np
import pandas as pd
from .core import integer, time_frame, finish


def conformal_radius(abs_residuals, alpha):
    """Finite-sample split-conformal radius: rank ceil((m+1)(1-alpha)) of the sorted absolute residuals."""
    r = np.sort(np.asarray(abs_residuals, float))
    m = len(r)
    rank = int(math.ceil((m + 1) * (1 - alpha)))
    if rank > m:
        raise ValueError(f'{m} calibration residuals cannot support level {1 - alpha:.2f}; need at least {math.ceil(1 / alpha)}')
    return float(r[rank - 1]), rank


def pinball(actual, forecast, tau):
    diff = np.asarray(actual, float) - np.asarray(forecast, float)
    return float(np.mean(np.where(diff >= 0, tau * diff, (tau - 1) * diff)))


def interval_score(actual, lower, upper, alpha):
    actual, lower, upper = (np.asarray(v, float) for v in (actual, lower, upper))
    return (upper - lower) + 2 / alpha * np.maximum(lower - actual, 0) + 2 / alpha * np.maximum(actual - upper, 0)


def conformal_intervals(d, c):
    from ..engine import forecast_series, POOLS, COMBINATIONS, CANDIDATES, Spec
    from .methods import intervals as supplied_intervals
    if {'lower', 'median', 'upper'} <= set(d.columns):
        return supplied_intervals(d, c)
    alpha = float(c.get('alpha', 0.2)); gamma = float(c.get('gamma', 0.05))
    if not 0 < alpha < 1 or not 0 <= gamma < 1:
        raise ValueError('alpha in (0,1) and gamma in [0,1) required')
    h = integer(c, 'horizon', 12); season = integer(c, 'season', 12)
    pool = c.get('pool', 'smoothing')
    if pool not in POOLS:
        raise ValueError(f'pool must be one of {sorted(POOLS)}')
    transform = c.get('transform', 'auto'); origins = integer(c, 'origins', 5, 2)
    cal = integer(c, 'calibration_size', 36, 2); test = integer(c, 'test_size', 24, 1)
    f, freq = time_frame(d, c, minimum=2)
    y = f.target.to_numpy(float); n = len(y)
    T2 = n - test; T1 = T2 - cal
    min_train = max(24, 2 * season)
    if T1 < min_train:
        raise ValueError(f'Need at least {min_train + cal + test} observations for training, a {cal}-point calibration block and a {test}-point test block')
    if cal < math.ceil(1 / alpha) + h:
        raise ValueError(f'calibration_size must be at least {math.ceil(1 / alpha) + h} for alpha {alpha} and horizon {h}')
    table_sel, sel = forecast_series(y[:T2], f.timestamp.iloc[:T2], h, season, pool=pool, freq=freq, transform=transform, max_origins=origins)
    name = sel['selected']; note = None
    if name in COMBINATIONS:
        atomic = [r['model'] for r in sel['leaderboard'] if r['model'] not in COMBINATIONS]
        name = atomic[0]; note = f'{sel["selected"]} cannot be refit standalone; using the best atomic model {name}'
    spec_info = sel['specification']
    spec = Spec(log=sel['transform'] == 'log', ets=spec_info.get('ets'),
                arima=tuple(map(tuple, spec_info['arima'])) if spec_info.get('arima') else None)
    log = spec.log
    work = np.log(y) if log else y
    if log and np.any(y <= 0):
        raise ValueError('log transform selected but series has nonpositive values')

    def predict(t):
        fit = CANDIDATES[name](work[:t], h, season, spec, freq)
        mean = np.exp(fit.mean) if log else fit.mean
        lo = np.exp(fit.lower) if (log and fit.lower is not None) else fit.lower
        hi = np.exp(fit.upper) if (log and fit.upper is not None) else fit.upper
        return mean, lo, hi

    # calibration residuals by horizon step, targets strictly before T2
    cal_res = {j: [] for j in range(1, h + 1)}
    for t in range(T1, T2):
        mean, _, _ = predict(t)
        for j in range(1, h + 1):
            if t + j - 1 < T2:
                cal_res[j].append(y[t + j - 1] - mean[j - 1])
    radius = {}
    for j in range(1, h + 1):
        if len(cal_res[j]) >= math.ceil(1 / alpha):
            radius[j], _ = conformal_radius(np.abs(cal_res[j]), alpha)
    steps = sorted(radius)
    if not steps:
        raise ValueError('Calibration block too short for any horizon step')
    # test block: split intervals with fixed radius; adaptive alpha_t per step
    alpha_t = {j: alpha for j in steps}
    seen = {j: list(np.abs(cal_res[j])) for j in steps}
    rows = []
    for t in range(T2, n):
        mean, lo, hi = predict(t)
        for j in steps:
            if t + j - 1 >= n:
                continue
            actual = y[t + j - 1]
            r_split = radius[j]
            ranked = np.sort(seen[j]); m = len(ranked)
            rank = min(m, max(1, int(math.ceil((m + 1) * (1 - alpha_t[j])))))
            r_adapt = float(ranked[rank - 1])
            miss = float(not (mean[j - 1] - r_adapt <= actual <= mean[j - 1] + r_adapt))
            rows.append(dict(timestamp=f.timestamp.iloc[t + j - 1], origin=f.timestamp.iloc[t - 1], horizon=j, actual=actual, forecast=mean[j - 1],
                             split_lower=mean[j - 1] - r_split, split_upper=mean[j - 1] + r_split,
                             adaptive_lower=mean[j - 1] - r_adapt, adaptive_upper=mean[j - 1] + r_adapt, alpha_t=alpha_t[j],
                             covered_split=bool(mean[j - 1] - r_split <= actual <= mean[j - 1] + r_split), covered_adaptive=not miss,
                             model_lower=(lo[j - 1] if lo is not None else None), model_upper=(hi[j - 1] if hi is not None else None)))
            alpha_t[j] = float(np.clip(alpha_t[j] + gamma * (alpha - miss), 0.01, 0.99))
            seen[j].append(abs(actual - mean[j - 1]))
    table = pd.DataFrame(rows)
    if table.empty:
        raise ValueError('Test block produced no scoreable targets')
    has_model = table.model_lower.notna().all()
    if not has_model:
        table = table.drop(columns=['model_lower', 'model_upper'])
    table['interval_score_split'] = interval_score(table.actual, table.split_lower, table.split_upper, alpha)
    table['interval_score_adaptive'] = interval_score(table.actual, table.adaptive_lower, table.adaptive_upper, alpha)
    def block(kind):
        lo, hi = table[f'{kind}_lower'], table[f'{kind}_upper']
        return dict(coverage=float(table[f'covered_{kind}'].mean()), mean_width=float((hi - lo).mean()),
                    interval_score=float(table[f'interval_score_{kind}'].mean()),
                    pinball=dict(lower=pinball(table.actual, lo, alpha / 2), upper=pinball(table.actual, hi, 1 - alpha / 2)),
                    by_horizon={int(j): float(g[f'covered_{kind}'].mean()) for j, g in table.groupby('horizon')})
    scores = dict(split=block('split'), adaptive=block('adaptive'))
    model_note = None
    if has_model:
        cov = float(((table.actual >= table.model_lower) & (table.actual <= table.model_upper)).mean())
        scores['model_nominal_80'] = dict(coverage=cov, mean_width=float((table.model_upper - table.model_lower).mean()))
        model_note = f"the model's own nominal 80% band covered {cov:.0%} on the same test block" + ('' if abs(alpha - 0.2) < 1e-9 else f' (not directly comparable to alpha {alpha})')
    not_done = ['Conditional (per-time) coverage is not guaranteed; the split guarantee is marginal under exchangeability, the adaptive guarantee is long-run']
    if note: not_done.append(note)
    interpretation = (f'{name} intervals: split-conformal coverage {scores["split"]["coverage"]:.0%} (target {1 - alpha:.0%}, mean width {scores["split"]["mean_width"]:.3g}); '
                      f'adaptive coverage {scores["adaptive"]["coverage"]:.0%} (mean width {scores["adaptive"]["mean_width"]:.3g}). '
                      + (model_note + '. ' if model_note else '') + 'Lower interval score is better; judge width and coverage together.')
    return finish(table, method='Split and adaptive conformal intervals around an engine-selected model', interpretation=interpretation,
                  assumptions=['Calibration residuals exchangeable with test residuals for the split guarantee', f'Adaptive update with gamma {gamma} targets long-run coverage {1 - alpha:.2f}', 'Specification frozen before the calibration block'],
                  not_done=not_done, status='passed', selected=name, alpha=alpha, gamma=gamma,
                  calibration_rows={int(j): len(cal_res[j]) for j in steps}, test_rows=int(len(table)), radius={int(j): radius[j] for j in steps},
                  coverage={k: v['coverage'] for k, v in scores.items()}, mean_width={k: v['mean_width'] for k, v in scores.items()},
                  interval_score={k: v.get('interval_score') for k, v in scores.items() if 'interval_score' in v},
                  pinball={k: v['pinball'] for k, v in scores.items() if 'pinball' in v}, by_horizon={k: v['by_horizon'] for k, v in scores.items() if 'by_horizon' in v},
                  guarantee='split: marginal coverage >= 1-alpha under exchangeability; adaptive: long-run empirical coverage -> 1-alpha under the update',
                  calibration_block=[str(f.timestamp.iloc[T1]), str(f.timestamp.iloc[T2 - 1])], test_block=[str(f.timestamp.iloc[T2]), str(f.timestamp.iloc[-1])])
