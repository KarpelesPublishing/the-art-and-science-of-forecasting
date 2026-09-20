"""Chapter 5: state-space models with missing data.

statsmodels UnobservedComponents with a chosen level model, optional seasonal and
cycle components, NaN targets allowed, filtered versus smoothed states labelled,
forecasts with 80 percent intervals, and a rolling check against the last observed
value. The hand-rolled local-level filter remains available as model 'local_level_manual'.
"""
import warnings
import numpy as np
import pandas as pd
from .core import time_frame, integer, expanding_origins, finish

LEVELS = ('local level', 'local linear trend', 'smooth trend')


def unobserved_components(d, c):
    model = c.get('model', 'local level')
    if model == 'local_level_manual':
        from .series import kalman
        return kalman(d, c)
    if model not in LEVELS:
        raise ValueError(f"model must be one of {LEVELS} or 'local_level_manual'")
    from statsmodels.tsa.statespace.structural import UnobservedComponents
    f, freq = time_frame(d, c, minimum=30, allow_missing=True)
    y = f.target.to_numpy(float); n = len(y); h = integer(c, 'horizon', 12); season = integer(c, 'season', 12)
    seasonal = bool(c.get('seasonal', False)); cycle = bool(c.get('cycle', False)); stochastic_cycle = bool(c.get('stochastic_cycle', True))
    if seasonal and season < 2:
        raise ValueError('seasonal requires season >= 2')
    missing = np.isnan(y)
    kwargs = dict(level=model, seasonal=season if seasonal else None, cycle=cycle, stochastic_cycle=stochastic_cycle if cycle else False)
    def fit(values):
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            return UnobservedComponents(values, **kwargs).fit(disp=False, maxiter=200)
    res = fit(y)
    filtered = res.filtered_state[0]; fvar = res.filtered_state_cov[0, 0]
    smoothed = res.smoothed_state[0]; svar = res.smoothed_state_cov[0, 0]
    fc = res.get_forecast(h); frame = fc.summary_frame(alpha=0.2)
    dates = pd.date_range(f.timestamp.iloc[-1], periods=h + 1, freq=freq)[1:]
    rows = []
    for kind, est, var in (('filtered', filtered, fvar), ('smoothed', smoothed, svar)):
        se = np.sqrt(np.maximum(var, 0))
        for t in range(n):
            rows.append(dict(timestamp=f.timestamp.iloc[t], kind=kind, estimate=float(est[t]), lower=float(est[t] - 1.2816 * se[t]), upper=float(est[t] + 1.2816 * se[t])))
    for t in range(h):
        rows.append(dict(timestamp=dates[t], kind='forecast', estimate=float(frame['mean'].iloc[t]), lower=float(frame['mean_ci_lower'].iloc[t]), upper=float(frame['mean_ci_upper'].iloc[t])))
    table = pd.DataFrame(rows)
    # rolling check against last observed value
    n_origins = integer(c, 'origins', 3, 2)
    validation = []
    try:
        origins = expanding_origins(n, h, max(30, 2 * season if seasonal else 30), n_origins)
    except ValueError:
        origins = []
    for o in origins:
        r = fit(y[:o]); pred = r.get_forecast(h).predicted_mean; actual = y[o:o + h]; ok = ~np.isnan(actual)
        last = y[:o][~np.isnan(y[:o])][-1]
        validation.append(dict(origin=str(f.timestamp.iloc[o - 1]), model_mae=float(np.abs(pred[ok] - actual[ok]).mean()) if ok.any() else None, naive_mae=float(np.abs(last - actual[ok]).mean()) if ok.any() else None))
    # innovations diagnostic on the second half
    from statsmodels.stats.diagnostic import acorr_ljungbox
    innov = res.standardized_forecasts_error[0]; half = innov[n // 2:]; half = half[~np.isnan(half)]
    lb = float(acorr_ljungbox(half, lags=[min(5, max(1, len(half) // 4))], return_df=True).lb_pvalue.iloc[0]) if len(half) > 8 else None
    params = {k: float(v) for k, v in zip(res.param_names, np.asarray(res.params))}
    model_mae = [v['model_mae'] for v in validation if v['model_mae'] is not None]; naive_mae = [v['naive_mae'] for v in validation if v['naive_mae'] is not None]
    interpretation = (f'{model}' + (f' + seasonal({season})' if seasonal else '') + (' + cycle' if cycle else '') + f' fitted with {int(missing.sum())} missing observations handled by the filter. '
                      + (f'Rolling check over {len(validation)} origins: model MAE {np.mean(model_mae):.4g} vs last-value {np.mean(naive_mae):.4g}. ' if model_mae else 'Rolling check skipped for lack of history. ')
                      + (f'Ljung-Box p on second-half innovations {lb:.2f}. ' if lb is not None else '')
                      + 'Smoothed states use later observations and are retrospective; filtered states and forecasts use only the past.')
    return finish(table, method='UnobservedComponents state-space model', interpretation=interpretation,
                  assumptions=['Gaussian state and measurement noise', f'{model} dynamics' + (', deterministic-period seasonality' if seasonal else ''), 'Missing values are missing at random'],
                  not_done=['No regression effects or exogenous inputs', 'Nonlinear or non-Gaussian filtering not attempted'], status='passed',
                  model=model, seasonal=seasonal, cycle=cycle, params=params, llf=float(res.llf), missing_count=int(missing.sum()), missing_timestamps=[str(t) for t in f.timestamp[missing]],
                  ljung_box_p=lb, validation=validation, test_mae=float(np.mean(model_mae)) if model_mae else None, horizon=h)
