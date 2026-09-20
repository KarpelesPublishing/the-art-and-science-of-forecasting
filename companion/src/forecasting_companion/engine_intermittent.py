"""Intermittent-demand candidates: Croston, SBA, TSB, ADIDA, IMAPA.

Demand that is zero most periods breaks the ordinary candidates and the ordinary error measures:
a forecast of zero has a fine MAE and is useless for stocking. These methods forecast the demand
rate (size over interval), and the engine scores them on RMSSE and cumulative horizon error, not
MAE. In-house implementations are used; when statsforecast is installed the same names run its
versions.
"""
import numpy as np
from .optional import have


def croston_family(y, alpha=0.1, variant='croston', beta=None):
    """One-step rate forecast after every observation; returns the path of forecasts made before each point
    and the forecast for the next period. variant: croston | sba | tsb."""
    y = np.asarray(y, float); n = len(y)
    nz = y[y > 0]
    size = float(nz[0]) if len(nz) else 0.0
    idx = np.flatnonzero(y > 0)
    interval = float(np.mean(np.diff(idx))) if len(idx) > 1 else float(n) if n else 1.0
    prob = float(np.mean(y > 0)) if n else 0.0
    beta = alpha if beta is None else beta
    gap = 1; path = np.empty(n)
    for t, v in enumerate(y):
        if variant == 'tsb':
            path[t] = prob * size
            prob = (1 - beta) * prob + beta * (v > 0)
            if v > 0:
                size = (1 - alpha) * size + alpha * v
        else:
            rate = size / max(interval, 1e-9)
            path[t] = rate * (1 - alpha / 2) if variant == 'sba' else rate
            if v > 0:
                size = (1 - alpha) * size + alpha * v
                interval = (1 - alpha) * interval + alpha * gap
                gap = 1
            else:
                gap += 1
    if variant == 'tsb':
        nxt = prob * size
    else:
        rate = size / max(interval, 1e-9); nxt = rate * (1 - alpha / 2) if variant == 'sba' else rate
    return path, float(nxt)


def _best_alpha(y, variant):
    """Pick alpha on in-sample one-step squared error over a small grid (training data only)."""
    best = None
    for a in (0.05, 0.1, 0.2, 0.3):
        path, _ = croston_family(y, a, variant)
        sse = float(np.mean((y[1:] - path[1:]) ** 2))
        if best is None or sse < best[0]:
            best = (sse, a)
    return best[1]


def _rate_forecast(y, h, variant):
    a = _best_alpha(y, variant)
    _, nxt = croston_family(y, a, variant)
    return np.repeat(max(nxt, 0.0), h)


def fit_croston(y, h, s, spec, freq):
    from .engine import Fit
    return Fit(_rate_forecast(y, h, 'croston'))


def fit_sba(y, h, s, spec, freq):
    from .engine import Fit
    return Fit(_rate_forecast(y, h, 'sba'))


def fit_tsb(y, h, s, spec, freq):
    from .engine import Fit
    return Fit(_rate_forecast(y, h, 'tsb'))


def _ses_level(z, alpha=None):
    """Simple exponential smoothing level with alpha chosen on in-sample squared error."""
    z = np.asarray(z, float)
    if alpha is None:
        best = None
        for a in (0.05, 0.1, 0.2, 0.3, 0.5):
            lvl = z[0]; sse = 0.0
            for v in z[1:]:
                sse += (v - lvl) ** 2; lvl = a * v + (1 - a) * lvl
            if best is None or sse < best[0]:
                best = (sse, a)
        alpha = best[1]
    lvl = z[0]
    for v in z[1:]:
        lvl = alpha * v + (1 - alpha) * lvl
    return float(lvl)


def fit_adida(y, h, s, spec, freq):
    """Aggregate to buckets of the mean demand interval, smooth, disaggregate equally."""
    from .engine import Fit
    y = np.asarray(y, float); idx = np.flatnonzero(y > 0)
    k = int(max(1, round(np.mean(np.diff(idx))))) if len(idx) > 1 else 1
    k = min(k, max(1, len(y) // 4))
    trimmed = y[len(y) % k:] if len(y) % k else y
    buckets = trimmed.reshape(-1, k).sum(axis=1)
    level = _ses_level(buckets) if len(buckets) > 1 else float(buckets[0])
    return Fit(np.repeat(max(level / k, 0.0), h))


def fit_imapa(y, h, s, spec, freq):
    """Mean of ADIDA-style rate forecasts over aggregation levels 1..k."""
    from .engine import Fit
    y = np.asarray(y, float); idx = np.flatnonzero(y > 0)
    kmax = int(max(1, round(np.mean(np.diff(idx))))) if len(idx) > 1 else 1
    kmax = min(kmax, max(1, len(y) // 4))
    rates = []
    for k in range(1, kmax + 1):
        trimmed = y[len(y) % k:] if len(y) % k else y
        buckets = trimmed.reshape(-1, k).sum(axis=1)
        level = _ses_level(buckets) if len(buckets) > 1 else float(buckets[0])
        rates.append(level / k)
    return Fit(np.repeat(max(float(np.mean(rates)), 0.0), h))


def fit_mean(y, h, s, spec, freq):
    from .engine import Fit
    return Fit(np.repeat(float(np.mean(y)), h))


def fit_zero(y, h, s, spec, freq):
    from .engine import Fit
    return Fit(np.zeros(h))


if have('statsforecast'):
    def _sf(model_cls, **kw):
        def fit(y, h, s, spec, freq):
            from .engine import Fit
            m = model_cls(**kw); m.fit(np.asarray(y, float))
            return Fit(np.asarray(m.predict(h)['mean'], float))
        return fit
    try:
        from statsforecast.models import CrostonClassic, CrostonSBA, TSB, ADIDA, IMAPA
        fit_croston = _sf(CrostonClassic); fit_sba = _sf(CrostonSBA); fit_tsb = _sf(TSB, alpha_d=0.2, alpha_p=0.2); fit_adida = _sf(ADIDA); fit_imapa = _sf(IMAPA)
    except Exception:
        pass
