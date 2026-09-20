"""Candidates that use drivers known in advance: prices, promotions, holidays, weather forecasts.

The contract: the history frame carries the driver columns beside `target`; `future_regressors`
is a frame with `timestamp` plus the same columns for exactly the next `horizon` periods. At each
rolling origin the validation window's driver values come from the history (they were known then
by contract). `validate_regressors` enforces all of this before any model sees the data.
"""
import warnings
import numpy as np
import pandas as pd
from .optional import have


def validate_regressors(history, future, columns, horizon):
    """Return (X_history, X_future) as float arrays, or raise with the reason."""
    missing = [c for c in columns if c not in history.columns]
    if missing:
        raise ValueError(f'regressor columns missing from the history: {missing}')
    if future is None:
        raise ValueError('future_regressors are required for the next horizon periods when regressors are used')
    future = pd.DataFrame(future)
    if 'timestamp' not in future.columns:
        raise ValueError('future_regressors need a timestamp column')
    missing = [c for c in columns if c not in future.columns]
    if missing:
        raise ValueError(f'future_regressors lack columns {missing}')
    if len(future) != horizon:
        raise ValueError(f'future_regressors must have exactly {horizon} rows (one per horizon step); got {len(future)}')
    Xh = history[columns].apply(pd.to_numeric, errors='raise').to_numpy(float)
    Xf = future[columns].apply(pd.to_numeric, errors='raise').to_numpy(float)
    if not np.isfinite(Xh).all() or not np.isfinite(Xf).all():
        raise ValueError('regressors must be finite and complete')
    return Xh, Xf


def _calendar(timestamps, country=None):
    ts = pd.DatetimeIndex(pd.to_datetime(timestamps)); cols = {}
    if ts.freqstr and ts.freqstr.upper().startswith(('D', 'B', 'H')) or (len(ts) > 1 and (ts[1] - ts[0]).days <= 1):
        cols['dow_sin'] = np.sin(2 * np.pi * ts.dayofweek / 7); cols['dow_cos'] = np.cos(2 * np.pi * ts.dayofweek / 7)
    cols['month_sin'] = np.sin(2 * np.pi * ts.month / 12); cols['month_cos'] = np.cos(2 * np.pi * ts.month / 12)
    if country:
        try:
            import holidays
            cal = holidays.country_holidays(country, years=sorted(set(ts.year)))
            cols['holiday'] = np.array([d.date() in cal for d in ts], float)
        except Exception:
            pass
    return np.column_stack(list(cols.values())) if cols else np.zeros((len(ts), 0))


def _design(spec, n, h):
    """History and future regressor matrices for a training slice of length n; the future is the next h rows of the history when
    the slice is a validation origin, or the declared future_regressors when the slice is the full history."""
    X, Xf = spec.regressors['X'], spec.regressors['future']
    if n + h <= len(X):
        return X[:n], X[n:n + h]
    if n == len(X):
        return X, Xf
    raise ValueError('regressor design does not cover this slice')


def fit_arimax(y, h, s, spec, freq):
    """Regression with ARIMA errors on the declared regressors."""
    from statsmodels.tsa.arima.model import ARIMA
    from .engine import Fit, NOMINAL, choose_differencing
    y = np.asarray(y, float); n = len(y)
    Xh, Xf = _design(spec, n, h)
    d, D, _ = choose_differencing(y, s)
    order = (1, min(d, 1), 1); seasonal = (0, D, 1, s) if s > 1 and D else (0, 0, 0, 0)
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        res = ARIMA(y, exog=Xh, order=order, seasonal_order=seasonal).fit(method_kwargs={'maxiter': 100})
        fc = res.get_forecast(h, exog=Xf); ci = np.asarray(fc.conf_int(alpha=1 - NOMINAL))
    return Fit(np.asarray(fc.predicted_mean, float), ci[:, 0], ci[:, 1])


def fit_lightgbm_x(y, h, s, spec, freq):
    """Direct LightGBM on lags, seasonal position and the regressors at the target date."""
    if not have('lightgbm'):
        raise ValueError('lightgbm not installed')
    import lightgbm as lgb
    from .engine import Fit
    y = np.asarray(y, float); n = len(y)
    Xh, Xf = _design(spec, n, h)
    lags = sorted({1, 2, 3, s, 2 * s} if s > 1 else {1, 2, 3, 6, 12}); lags = [l for l in lags if l < n // 2]
    if not lags or n < max(lags) + 2 * h + 12:
        raise ValueError('too short for a lag learner')
    rows, targets = [], []
    for t in range(max(lags), n - h + 1):
        base = [y[t - l] for l in lags] + [t % s if s > 1 else 0]
        for step in range(1, h + 1):
            if t + step - 1 < n:
                rows.append(base + [step] + list(Xh[t + step - 1])); targets.append(y[t + step - 1])
    params = dict(objective='regression', verbosity=-1, num_threads=1, seed=12, num_leaves=15, learning_rate=0.05, min_data_in_leaf=5)
    booster = lgb.train(params, lgb.Dataset(np.asarray(rows, float), label=np.asarray(targets, float)), num_boost_round=200)
    base = [y[n - l] for l in lags] + [n % s if s > 1 else 0]
    query = np.asarray([base + [step] + list(Xf[step - 1]) for step in range(1, h + 1)], float)
    return Fit(booster.predict(query))


def fit_prophet_x(y, h, s, spec, freq):
    """Prophet with the regressors added as extra regressors and the country's holidays when declared."""
    if not have('prophet'):
        raise ValueError('prophet not installed')
    from .common import quiet_libraries
    quiet_libraries()
    from prophet import Prophet
    from .engine import Fit, NOMINAL
    y = np.asarray(y, float); n = len(y)
    Xh, Xf = _design(spec, n, h)
    names = spec.regressors['columns']
    ds = pd.date_range('2000-01-01', periods=n + h, freq=freq or 'D')
    m = Prophet(uncertainty_samples=100, interval_width=NOMINAL, weekly_seasonality=(s == 7), yearly_seasonality=(s in (12, 52, 365)), daily_seasonality=False)
    for c in names:
        m.add_regressor(c)
    hist = pd.DataFrame({'ds': ds[:n], 'y': y}); fut = pd.DataFrame({'ds': ds[n:]})
    for j, c in enumerate(names):
        hist[c] = Xh[:, j]; fut[c] = Xf[:, j]
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        np.random.seed(16); m.fit(hist, seed=16)
        np.random.seed(16); pred = m.predict(fut)
    return Fit(pred.yhat.to_numpy(), pred.yhat_lower.to_numpy(), pred.yhat_upper.to_numpy())
