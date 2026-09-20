"""Candidates for series with more than one seasonal cycle (daily data with weekly and yearly
patterns, hourly data with daily and weekly), plus Prophet as a candidate.

MSTL splits the series into one component per period; the remainder (trend plus noise) goes to a
damped ETS or an ARIMA, and each seasonal component is extended by repeating its last cycle.
Fourier ARIMA fits sine and cosine terms for every period as regressors with ARIMA errors. TBATS
runs through statsforecast when that is installed.
"""
import warnings
import numpy as np
import pandas as pd
from .optional import have


def _periods(spec, s):
    p = list(getattr(spec, 'periods', None) or [])
    return [int(q) for q in p if q > 1] or ([int(s)] if s > 1 else [])


def _mstl(y, periods):
    from statsmodels.tsa.seasonal import MSTL
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        fit = MSTL(np.asarray(y, float), periods=periods, stl_kwargs={'robust': True}).fit()
    seasonal = np.asarray(fit.seasonal)
    if seasonal.ndim == 1:
        seasonal = seasonal[:, None]
    return np.asarray(fit.trend) + np.asarray(fit.resid), seasonal


def _extend_seasonal(seasonal, periods, h):
    out = np.zeros(h)
    for j, p in enumerate(periods):
        last = seasonal[-p:, j]
        out += np.resize(last, h)
    return out


def fit_mstl_ets(y, h, s, spec, freq):
    from .engine import Fit, _ets
    periods = _periods(spec, s)
    if not periods or len(y) < 2 * max(periods):
        raise ValueError('MSTL needs two full cycles of the longest period')
    deseason, seasonal = _mstl(y, periods)
    f = _ets(deseason, h, 1, freq, 'add', 'add', True, None)
    add = _extend_seasonal(seasonal, periods, h)
    return Fit(f.mean + add, None if f.lower is None else f.lower + add, None if f.upper is None else f.upper + add)


def fit_mstl_arima(y, h, s, spec, freq):
    from .engine import Fit, _arima, choose_differencing
    periods = _periods(spec, s)
    if not periods or len(y) < 2 * max(periods):
        raise ValueError('MSTL needs two full cycles of the longest period')
    deseason, seasonal = _mstl(y, periods)
    d, _, _ = choose_differencing(deseason, 1)
    f = _arima(deseason, h, 1, freq, (1, d, 1), (0, 0, 0, 0))[1]
    add = _extend_seasonal(seasonal, periods, h)
    return Fit(f.mean + add, None if f.lower is None else f.lower + add, None if f.upper is None else f.upper + add)


def _fourier(n, periods, K, start=0):
    t = np.arange(start, start + n)
    cols = []
    for p in periods:
        for k in range(1, K + 1):
            cols.append(np.sin(2 * np.pi * k * t / p)); cols.append(np.cos(2 * np.pi * k * t / p))
    return np.column_stack(cols) if cols else np.zeros((n, 0))


def fit_fourier_arima(y, h, s, spec, freq):
    """ARIMA(p,d,q) errors with Fourier terms for every period; K chosen by AICc on the training slice."""
    from statsmodels.tsa.arima.model import ARIMA
    from .engine import Fit, aicc, NOMINAL
    periods = _periods(spec, s)
    if not periods or len(y) < max(periods) + 20:
        raise ValueError('Fourier ARIMA needs one full cycle plus 20 observations')
    y = np.asarray(y, float); n = len(y)
    kmax = max(1, min(3, min(periods) // 2))
    best = None
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        for K in range(1, kmax + 1):
            X = _fourier(n, periods, K)
            try:
                res = ARIMA(y, exog=X, order=(1, 1, 1)).fit(method_kwargs={'maxiter': 100})
            except Exception:
                continue
            score = aicc(res.aic, res.df_model + 1, n)
            if best is None or score < best[0]:
                best = (score, K, res)
    if best is None:
        raise ValueError('Fourier ARIMA failed to fit')
    _, K, res = best
    Xf = _fourier(h, periods, K, start=n)
    fc = res.get_forecast(h, exog=Xf); ci = fc.conf_int(alpha=1 - NOMINAL)
    ci = np.asarray(ci)
    return Fit(np.asarray(fc.predicted_mean, float), ci[:, 0], ci[:, 1])


def fit_prophet(y, h, s, spec, freq):
    """Prophet with the series' own seasonalities; nominal 80% band from its uncertainty samples."""
    if not have('prophet'):
        raise ValueError('prophet not installed')
    from .common import quiet_libraries
    quiet_libraries()
    from prophet import Prophet
    from .engine import Fit, NOMINAL
    y = np.asarray(y, float); n = len(y)
    periods = _periods(spec, s)
    if n < 2 * max(periods or [12]):
        raise ValueError('Prophet needs two cycles')
    ds = pd.date_range('2000-01-01', periods=n + h, freq=freq or 'D')
    m = Prophet(weekly_seasonality=False, yearly_seasonality=False, daily_seasonality=False, uncertainty_samples=100, interval_width=NOMINAL)
    for p in periods:
        days = p * (pd.tseries.frequencies.to_offset(freq or 'D').nanos / 8.64e13)
        m.add_seasonality(name=f'p{p}', period=days, fourier_order=min(5, max(2, p // 2)))
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        np.random.seed(16); m.fit(pd.DataFrame({'ds': ds[:n], 'y': y}), seed=16)
        np.random.seed(16); pred = m.predict(pd.DataFrame({'ds': ds[n:]}))
    return Fit(pred.yhat.to_numpy(), pred.yhat_lower.to_numpy(), pred.yhat_upper.to_numpy())


def fit_tbats(y, h, s, spec, freq):
    if not have('statsforecast'):
        raise ValueError('statsforecast not installed')
    from statsforecast.models import AutoTBATS
    from .engine import Fit
    periods = _periods(spec, s) or [1]
    m = AutoTBATS(season_length=periods); m.fit(np.asarray(y, float))
    return Fit(np.asarray(m.predict(h)['mean'], float))
