"""A real forecasting engine for a single regular time series.

What it does, in the order the book teaches it:

1. Decide the working scale on training data only: a Box-Cox lambda near zero
   with positive data selects a log transform (multiplicative seasonality).
2. Fit a pool of candidate models anew at several expanding origins strictly
   before a final holdout: naive baselines, the exponential-smoothing family
   with an AICc-selected ETS specification, Theta, STL plus ETS, an AICc-selected
   seasonal ARIMA whose differencing orders come from KPSS and seasonal-strength
   checks, a direct LightGBM learner when the history is long enough, and
   combinations of the strongest candidates.
3. Score every candidate at every origin on MAE, RMSE and training-scaled MASE,
   and score the nominal 80% intervals of the models that produce them.
4. Select on earlier-origin MAE, evaluate the selection once on the untouched
   final holdout, then refit on all history and forecast the future with
   quantiles.

Uncertainty comes from two places and both are reported: the selected model's
own intervals, with their measured coverage at the earlier origins, and
empirical signed residual quantiles by horizon step from those origins. When a
model has no intervals, the empirical bands are the only ones offered and are
labelled as such.

Nothing here looks past an origin when fitting, transforming or choosing a
specification for that origin. Specifications (ETS form, ARIMA orders, the
transform) are chosen on the first training slice and then held fixed while
parameters are re-estimated at every later origin, so later actuals cannot
influence the choice.
"""
from __future__ import annotations

import warnings
from dataclasses import dataclass, field
from itertools import product
from typing import Callable, Optional

import numpy as np
import pandas as pd

POOLS = {
    # Chapter 4: the exponential-smoothing family and its neighbours.
    'smoothing': ['Naive', 'Seasonal naive', 'Drift', 'SES', 'Holt', 'Damped Holt',
                  'ETS(auto)', 'Theta', 'STL+ETS'],
    # Chapter 6: Box-Jenkins.
    'arima': ['Naive', 'Seasonal naive', 'Drift', 'ARIMA(0,1,1)', 'ARIMA(1,1,0)',
              'Airline ARIMA', 'ARIMA(auto)'],
    # Chapter 12 and the master skill: everything, then combine.
    'full': ['Naive', 'Seasonal naive', 'Drift', 'SES', 'Holt', 'Damped Holt', 'ETS(auto)',
             'Theta', 'STL+ETS', 'ARIMA(auto)', 'Airline ARIMA', 'LightGBM',
             'Combination(top3)', 'Equal ensemble', 'Weighted ensemble'],
    'baseline': ['Naive', 'Seasonal naive', 'Drift', 'Equal ensemble'],
    # Chapter 21 and the profile's intermittent route: rate methods scored on RMSSE, never MAE on zeros.
    'intermittent': ['Zero', 'Mean', 'Naive', 'Croston', 'SBA', 'TSB', 'ADIDA', 'IMAPA', 'Equal ensemble'],
    # Daily or hourly data with two cycles: decompose per period, or model the cycles as Fourier terms.
    'multiseasonal': ['Naive', 'Seasonal naive', 'Drift', 'MSTL+ETS', 'MSTL+ARIMA', 'Fourier ARIMA', 'Prophet', 'TBATS',
                      'Combination(top3)', 'Equal ensemble'],
    # Drivers known in advance: regression with ARIMA errors, boosting with covariates, Prophet with regressors.
    'regressors': ['Naive', 'Seasonal naive', 'Drift', 'ETS(auto)', 'ARIMA(auto)', 'ARIMAX', 'LightGBM+X', 'Prophet+X',
                   'Combination(top3)'],
    # Pretrained models beside the baselines, at identical origins.
    'foundation': ['Naive', 'Seasonal naive', 'Drift', 'Chronos', 'Chronos-Bolt', 'TimesFM'],
}
NOMINAL = 0.8  # the interval level scored during validation
CRITERIA = ('mae', 'mase', 'rmsse', 'pinball')
BASELINE_FOR = {'intermittent': 'Mean'}          # the model every selection must beat; Seasonal naive (Naive when s = 1) elsewhere


@dataclass
class Spec:
    """Specification choices frozen on the first training slice."""
    log: bool = False
    ets: Optional[dict] = None
    arima: Optional[tuple] = None
    periods: list = field(default_factory=list)          # seasonal periods for the multiseasonal candidates
    regressors: Optional[dict] = None                     # {'X': history matrix, 'future': next-h matrix, 'columns': names}
    country: Optional[str] = None
    notes: dict = field(default_factory=dict)


@dataclass
class Fit:
    """One fitted candidate: point path plus optional interval paths."""
    mean: np.ndarray
    lower: Optional[np.ndarray] = None
    upper: Optional[np.ndarray] = None


# --------------------------------------------------------------------------
# transforms and diagnostics (training data only)
# --------------------------------------------------------------------------
def choose_log(y: np.ndarray) -> tuple[bool, dict]:
    """Log-transform when data are positive and the Box-Cox lambda is near zero.

    The threshold is a convention (lambda below 0.35 with a clearly positive series);
    it matches the book's airline example, where lambda is about 0.1.
    """
    if np.any(y <= 0) or len(y) < 12:
        return False, {'boxcox_lambda': None, 'reason': 'nonpositive values or too short'}
    from scipy.stats import boxcox
    try:
        _, lam = boxcox(y)
    except Exception:
        return False, {'boxcox_lambda': None, 'reason': 'boxcox failed'}
    return bool(lam < 0.35), {'boxcox_lambda': float(lam)}


def seasonal_strength(y: np.ndarray, season: int) -> float:
    """Hyndman's F_s = max(0, 1 - Var(remainder)/Var(seasonal+remainder)) from a robust STL."""
    if season <= 1 or len(y) < 3 * season:
        return 0.0
    from statsmodels.tsa.seasonal import STL
    fit = STL(y, period=season, robust=True).fit()
    denom = np.var(fit.seasonal + fit.resid)
    return float(max(0.0, 1 - np.var(fit.resid) / denom)) if denom > 0 else 0.0


def choose_differencing(y: np.ndarray, season: int) -> tuple[int, int, dict]:
    """d from repeated KPSS tests (at most 2); D=1 when seasonality is strong."""
    from statsmodels.tsa.stattools import kpss
    strength = seasonal_strength(y, season)
    D = 1 if season > 1 and strength >= 0.64 and len(y) >= 3 * season else 0
    z = np.diff(y, season) if D else y.copy()
    d = 0
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        while d < 2 and len(z) > 10:
            try:
                p = kpss(z, regression='c', nlags='auto')[1]
            except Exception:
                break
            if p >= 0.05:
                break
            z = np.diff(z)
            d += 1
    return d, D, {'seasonal_strength': strength, 'kpss_d': d, 'seasonal_D': D}


def aicc(fit_aic: float, k: int, n: int) -> float:
    return fit_aic + (2 * k * k + 2 * k) / max(n - k - 1, 1)


# --------------------------------------------------------------------------
# candidate models: each takes the training series (working scale) and returns a Fit
# --------------------------------------------------------------------------
def _index(n: int, freq: str) -> pd.PeriodIndex:
    try:
        return pd.period_range('2000-01-01', periods=n, freq=freq)
    except Exception:
        return pd.period_range('2000-01-01', periods=n, freq='D')


def _series(y: np.ndarray, freq: str) -> pd.Series:
    return pd.Series(y, index=_index(len(y), freq), dtype=float)


def fit_naive(y, h, s, spec, freq):
    return Fit(np.repeat(y[-1], h))


def fit_seasonal_naive(y, h, s, spec, freq):
    if s <= 1 or len(y) < 2 * s:
        raise ValueError('needs two seasonal cycles')
    return Fit(np.resize(y[-s:], h))


def fit_drift(y, h, s, spec, freq):
    return Fit(y[-1] + np.arange(1, h + 1) * (y[-1] - y[0]) / (len(y) - 1))


def _ets(y, h, s, freq, error, trend, damped, seasonal):
    from statsmodels.tsa.exponential_smoothing.ets import ETSModel
    kwargs = dict(error=error, trend=trend, damped_trend=damped, seasonal=seasonal)
    if seasonal:
        kwargs['seasonal_periods'] = s
    model = ETSModel(_series(y, freq), **kwargs)
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        res = model.fit(disp=False, maxiter=200)
    # Multiplicative-error ETS intervals are simulated; fix the seed so results are reproducible.
    frame = res.get_prediction(start=len(y), end=len(y) + h - 1, simulate_repetitions=2000,
                               random_state=np.random.RandomState(20260918)).summary_frame(alpha=1 - NOMINAL)
    return res, Fit(frame['mean'].to_numpy(), frame['pi_lower'].to_numpy(), frame['pi_upper'].to_numpy())


def fit_ses(y, h, s, spec, freq):
    return _ets(y, h, s, freq, 'add', None, False, None)[1]


def fit_holt(y, h, s, spec, freq):
    if len(y) < 10:
        raise ValueError('too short for a trend')
    return _ets(y, h, s, freq, 'add', 'add', False, None)[1]


def fit_damped(y, h, s, spec, freq):
    if len(y) < 10:
        raise ValueError('too short for a trend')
    return _ets(y, h, s, freq, 'add', 'add', True, None)[1]


def choose_ets(y, s, freq) -> dict:
    """AICc over admissible ETS forms on the first training slice."""
    positive = bool(np.all(y > 0))
    seasonal_options = [None] + (['add', 'mul'] if s > 1 and len(y) >= 2 * s else [])
    best, best_score = None, np.inf
    for error, trend, damped, seasonal in product(['add', 'mul'], [None, 'add'], [False, True], seasonal_options):
        if trend is None and damped:
            continue
        if (error == 'mul' or seasonal == 'mul') and not positive:
            continue
        try:
            res, _ = _ets(y, 1, s, freq, error, trend, damped, seasonal)
        except Exception:
            continue
        score = aicc(res.aic, len(res.params), len(y))
        if np.isfinite(score) and score < best_score:
            best, best_score = dict(error=error, trend=trend, damped=damped, seasonal=seasonal), score
    if best is None:
        raise ValueError('no ETS form fitted')
    return best


def fit_ets_auto(y, h, s, spec, freq):
    if spec.ets is None:
        raise ValueError('ETS specification unavailable')
    e = spec.ets
    return _ets(y, h, s, freq, e['error'], e['trend'], e['damped'], e['seasonal'])[1]


def fit_theta(y, h, s, spec, freq):
    from statsmodels.tsa.forecasting.theta import ThetaModel
    if len(y) < max(10, 2 * s):
        raise ValueError('too short for Theta')
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        res = ThetaModel(_series(y, freq), period=s if s > 1 else None, deseasonalize=s > 1).fit()
        mean = res.forecast(h).to_numpy()
        pi = res.prediction_intervals(h, alpha=1 - NOMINAL)
    return Fit(mean, pi['lower'].to_numpy(), pi['upper'].to_numpy())


def fit_stl_ets(y, h, s, spec, freq):
    if s <= 1 or len(y) < 3 * s:
        raise ValueError('needs three seasonal cycles')
    from statsmodels.tsa.forecasting.stl import STLForecast
    from statsmodels.tsa.exponential_smoothing.ets import ETSModel
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        res = STLForecast(_series(y, freq), ETSModel, model_kwargs=dict(error='add', trend='add', damped_trend=True),
                          period=s, robust=True).fit(fit_kwargs=dict(disp=False))
        frame = res.get_prediction(start=len(y), end=len(y) + h - 1).summary_frame(alpha=1 - NOMINAL)
    lower = frame['pi_lower'] if 'pi_lower' in frame else frame.iloc[:, -2]
    upper = frame['pi_upper'] if 'pi_upper' in frame else frame.iloc[:, -1]
    return Fit(frame['mean'].to_numpy(), lower.to_numpy(), upper.to_numpy())


def _arima(y, h, s, freq, order, seasonal_order):
    from statsmodels.tsa.arima.model import ARIMA
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        model = ARIMA(_series(y, freq), order=order, seasonal_order=seasonal_order if s > 1 else (0, 0, 0, 0))
        res = model.fit(method_kwargs={'maxiter': 200})
        if not res.mle_retvals.get('converged', True):
            raise ValueError(f'ARIMA{order}{seasonal_order} did not converge')
        fc = res.get_forecast(h)
        ci = fc.conf_int(alpha=1 - NOMINAL)
    return res, Fit(fc.predicted_mean.to_numpy(), ci.iloc[:, 0].to_numpy(), ci.iloc[:, 1].to_numpy())


def fit_arima_011(y, h, s, spec, freq):
    return _arima(y, h, s, freq, (0, 1, 1), (0, 0, 0, 0))[1]


def fit_arima_110(y, h, s, spec, freq):
    return _arima(y, h, s, freq, (1, 1, 0), (0, 0, 0, 0))[1]


def _recent(y, s):
    """For long seasons, fit on the most recent ten seasons: enough for the seasonal pattern, fast enough to run at every origin."""
    return y[-10 * s:] if s > 24 and len(y) > 10 * s else y


def fit_airline(y, h, s, spec, freq):
    if s <= 1 or len(y) < 3 * s:
        raise ValueError('needs three seasonal cycles')
    if s > 24:
        # long seasons: the seasonal MA(1) term is slow to estimate; difference seasonally first, fit
        # ARIMA(0,1,1) on the differences and re-integrate. Same structure, a fraction of the time.
        y = _recent(np.asarray(y, float), s); z = y[s:] - y[:-s]
        _, f = _arima(z, h, 1, freq, (0, 1, 1), (0, 0, 0, 0))
        base = np.array([y[len(y) - s + j] if j < s else np.nan for j in range(h)])
        path = np.empty(h); lo = np.empty(h); hi = np.empty(h)
        for j in range(h):
            prev = y[len(y) - s + j] if j < s else path[j - s]
            path[j] = prev + f.mean[j]; lo[j] = prev + (f.lower[j] if f.lower is not None else f.mean[j]); hi[j] = prev + (f.upper[j] if f.upper is not None else f.mean[j])
        return Fit(path, lo if f.lower is not None else None, hi if f.upper is not None else None)
    return _arima(y, h, s, freq, (0, 1, 1), (0, 1, 1, s))[1]


def choose_arima(y, s, freq) -> tuple:
    """AICc grid over p,q in 0..2 and P,Q in 0..1 with d, D from diagnostics."""
    d, D, _ = choose_differencing(y, s)
    if s > 24:
        # long seasons (weekly 52, daily 365): seasonal AR and MA terms are slow to estimate and rarely
        # earn their keep; keep seasonal differencing when diagnosed and search only the nonseasonal orders
        seasonal_grid = [(0, D, 0, s)] if D else [(0, 0, 0, 0)]
    else:
        seasonal_grid = [(P, D, Q, s) for P in (0, 1) for Q in (0, 1)] if s > 1 and len(y) >= 3 * s else [(0, 0, 0, 0)]
    best, best_score = None, np.inf
    y = y[-max(10 * s, 200):] if s > 24 and len(y) > max(10 * s, 200) else y      # the order search needs recent structure, not the whole archive
    for p, q in product(range(3), range(3)):
        for so in seasonal_grid:
            if p == q == 0 and so[0] == so[2] == 0 and d == 0 and so[1] == 0:
                continue
            try:
                res, _ = _arima(y, 1, s, freq, (p, d, q), so)
            except Exception:
                continue
            score = aicc(res.aic, len(res.params), len(y))
            if np.isfinite(score) and score < best_score:
                best, best_score = ((p, d, q), so), score
    if best is None:
        raise ValueError('no ARIMA fitted')
    return best


def fit_arima_auto(y, h, s, spec, freq):
    if spec.arima is None:
        raise ValueError('ARIMA specification unavailable')
    order, seasonal = spec.arima
    return _arima(_recent(y, s), h, s, freq, order, seasonal)[1]


def fit_lightgbm(y, h, s, spec, freq):
    """Direct multi-step gradient boosting on lags and seasonal position; empirical bands only."""
    try:
        import lightgbm as lgb
    except ImportError as exc:
        raise ValueError('lightgbm not installed') from exc
    lags = sorted({1, 2, 3, s, 2 * s} if s > 1 else {1, 2, 3, 6, 12})
    lags = [l for l in lags if l < len(y) // 2]
    if not lags or len(y) < max(lags) + 2 * h + 12:
        raise ValueError('too short for a lag learner')
    rows, targets = [], []
    for t in range(max(lags), len(y) - h + 1):
        feats = [y[t - l] for l in lags] + [t % s if s > 1 else 0]
        for step in range(1, h + 1):
            if t + step - 1 < len(y):
                rows.append(feats + [step])
                targets.append(y[t + step - 1])
    X = np.asarray(rows, float)
    params = dict(objective='regression', verbosity=-1, num_threads=1, seed=12, num_leaves=15,
                  learning_rate=0.05, min_data_in_leaf=5)
    booster = lgb.train(params, lgb.Dataset(X, label=np.asarray(targets, float)), num_boost_round=200)
    t = len(y)
    feats = [y[t - l] for l in lags] + [t % s if s > 1 else 0]
    query = np.asarray([feats + [step] for step in range(1, h + 1)], float)
    return Fit(booster.predict(query))


CANDIDATES: dict[str, Callable] = {}
REQUIRES: dict[str, str] = {}


def register(name, fn, requires=None):
    """Add a candidate. `requires` names an optional package; when it is absent the candidate is
    reported under `unavailable` with the install hint instead of silently missing."""
    CANDIDATES[name] = fn
    if requires:
        REQUIRES[name] = requires


for _name, _fn in (('Naive', fit_naive), ('Seasonal naive', fit_seasonal_naive), ('Drift', fit_drift), ('SES', fit_ses), ('Holt', fit_holt),
                   ('Damped Holt', fit_damped), ('ETS(auto)', fit_ets_auto), ('Theta', fit_theta), ('STL+ETS', fit_stl_ets),
                   ('ARIMA(0,1,1)', fit_arima_011), ('ARIMA(1,1,0)', fit_arima_110), ('Airline ARIMA', fit_airline), ('ARIMA(auto)', fit_arima_auto)):
    register(_name, _fn)
register('LightGBM', fit_lightgbm, requires='lightgbm')
from .engine_intermittent import fit_zero, fit_mean, fit_croston, fit_sba, fit_tsb, fit_adida, fit_imapa  # noqa: E402
for _name, _fn in (('Zero', fit_zero), ('Mean', fit_mean), ('Croston', fit_croston), ('SBA', fit_sba), ('TSB', fit_tsb), ('ADIDA', fit_adida), ('IMAPA', fit_imapa)):
    register(_name, _fn)
from .engine_multiseasonal import fit_mstl_ets, fit_mstl_arima, fit_fourier_arima, fit_prophet, fit_tbats  # noqa: E402
register('MSTL+ETS', fit_mstl_ets); register('MSTL+ARIMA', fit_mstl_arima); register('Fourier ARIMA', fit_fourier_arima)
register('Prophet', fit_prophet, requires='prophet'); register('TBATS', fit_tbats, requires='statsforecast')
from .engine_regressors import fit_arimax, fit_lightgbm_x, fit_prophet_x  # noqa: E402
register('ARIMAX', fit_arimax); register('LightGBM+X', fit_lightgbm_x, requires='lightgbm'); register('Prophet+X', fit_prophet_x, requires='prophet')
from .engine_foundation import fit_chronos, fit_chronos_bolt, fit_timesfm  # noqa: E402
register('Chronos', fit_chronos, requires='chronos'); register('Chronos-Bolt', fit_chronos_bolt, requires='chronos'); register('TimesFM', fit_timesfm, requires='timesfm')
COMBINATIONS = {'Combination(top3)', 'Equal ensemble', 'Weighted ensemble'}


# --------------------------------------------------------------------------
# the engine
# --------------------------------------------------------------------------
def _back(values, log):
    return np.exp(values) if (log and values is not None) else values


def _fit_all(names, y_work, h, s, spec, freq, log):
    fits, skipped = {}, {}
    for name in names:
        if name in COMBINATIONS:
            continue
        try:
            f = CANDIDATES[name](y_work, h, s, spec, freq)
            mean = _back(f.mean, log)
            if len(mean) != h or not np.isfinite(mean).all():
                raise ValueError('invalid forecast path')
            lower, upper = _back(f.lower, log), _back(f.upper, log)
            if lower is not None and (not np.isfinite(lower).all() or not np.isfinite(upper).all()):
                lower = upper = None
            fits[name] = Fit(mean, lower, upper)
        except Exception as exc:  # a failed candidate is recorded, not fatal
            skipped[name] = f'{type(exc).__name__}: {exc}'[:160]
    return fits, skipped


def _combine(fits, names, ranking, errors=None):
    if 'Equal ensemble' in names and fits:
        members = [f.mean for k, f in fits.items() if k not in COMBINATIONS]
        if members:
            fits['Equal ensemble'] = Fit(np.mean(members, axis=0))
    if 'Combination(top3)' in names and ranking:
        top = [k for k in ranking if k in fits and k not in COMBINATIONS][:3]
        if len(top) >= 2:
            fits['Combination(top3)'] = Fit(np.median([fits[k].mean for k in top], axis=0))
    if 'Weighted ensemble' in names and ranking and errors:
        top = [k for k in ranking if k in fits and k not in COMBINATIONS and errors.get(k)][:5]
        if len(top) >= 2:
            w = np.array([1.0 / max(errors[k], 1e-9) for k in top]); w = w / w.sum()
            fits['Weighted ensemble'] = Fit(np.sum([w[i] * fits[k].mean for i, k in enumerate(top)], axis=0))
    return fits


def score_origins(scores, criterion):
    """Mean of the criterion per model over the scored origins, best first."""
    col = criterion if criterion in scores.columns else 'mae'
    return scores.groupby('model')[col].mean().dropna().sort_values()


def conformal_band(residuals, level=NOMINAL, extra=None, finite_sample=True, info=False):
    """Split-conformal radius per horizon step.

    Residuals are pooled across every step (k origins times h steps rather than k alone) after scaling
    each step's residuals by its mean absolute error, so the quantile rests on tens of residuals; the
    step's scale is then restored. `extra` adds residuals the selection never saw (the final holdout of
    the selected model), which is what defeats the winner's curse: the chosen model's origin residuals
    are optimistically small because it was chosen for them. With m pooled residuals and finite_sample
    the level is raised by one standard error of the Beta coverage distribution,
    level_m = min(0.95, level + sqrt(level (1 - level) / m)), and the radius is the
    ceil((m+1) level_m)-th smallest scaled |r|. With info=True returns (radius, details)."""
    merged = {s: list(residuals[s]) for s in residuals}
    for s, extra_res in (extra or {}).items():
        merged.setdefault(s, []); merged[s] = list(merged[s]) + list(extra_res)
    residuals = merged
    steps = sorted(residuals)
    scale = {}
    for step in steps:
        r = np.abs(np.asarray(residuals[step], float))
        scale[step] = float(r.mean()) if len(r) and r.mean() > 0 else None
    overall = float(np.mean([v for v in scale.values() if v])) if any(scale.values()) else 1.0
    for step in steps:
        if scale[step] is None:
            scale[step] = overall
    # smooth the per-step scale so a single lucky step does not shrink its own band
    smooth = {}
    for i, step in enumerate(steps):
        window = [scale[s] for s in steps[max(0, i - 1):i + 2]]
        smooth[step] = float(np.mean(window))
    pooled = np.sort(np.concatenate([np.abs(np.asarray(residuals[s], float)) / smooth[s] for s in steps if len(residuals[s])])) if steps else np.array([])
    m = len(pooled)
    if m == 0:
        radius = {s: float('nan') for s in steps}
        return (radius, dict(m=0, level_effective=level)) if info else radius
    level_m = min(0.95, level + np.sqrt(level * (1 - level) / m)) if finite_sample else level
    k = int(np.ceil((m + 1) * level_m)) - 1
    q = float(pooled[min(max(k, 0), m - 1)])
    radius = {s: q * smooth[s] for s in steps}
    return (radius, dict(m=int(m), level_effective=float(level_m), largest_error_used=bool(k >= m - 1))) if info else radius


def forecast_series(y: np.ndarray, timestamps: pd.Series, horizon: int, season: int, *,
                    pool: str = 'full', freq: str = 'MS', transform: str = 'auto',
                    max_origins: int = 5, quantiles=(0.1, 0.5, 0.9), criterion: str | None = None,
                    periods=None, regressors=None, country=None, observed=None, conformal: bool = True,
                    per_horizon_buckets: bool = False) -> tuple[pd.DataFrame, dict]:
    """Forecast one regular series. Returns the future table and a full evidence summary.

    criterion: mae (default), mase, rmsse (default for the intermittent pool) or pinball (on the model's
    own 10/50/90 quantiles). periods: seasonal periods for the multiseasonal pool. regressors:
    {'X': history matrix, 'future': next-h matrix, 'columns': names} for the regressors pool.
    observed: boolean mask; False marks filled gaps, which are used for fitting but never scored.
    conformal: add split-conformal bands from the selected model's origin residuals.
    per_horizon_buckets: select one model for the near steps (1..ceil(h/2)) and another for the far
    steps; the future table splices them and names the model per row."""
    from .optional import have, hint
    y = np.asarray(y, float)
    n, h, s = len(y), int(horizon), int(season)
    if pool not in POOLS:
        raise ValueError(f'pool must be one of {sorted(POOLS)}')
    criterion = criterion or ('rmsse' if pool == 'intermittent' else 'mae')
    if criterion not in CRITERIA:
        raise ValueError(f'criterion must be one of {CRITERIA}')
    unavailable = {m: hint(REQUIRES[m]) for m in POOLS[pool] if m in REQUIRES and not have(REQUIRES[m])}
    names = [m for m in POOLS[pool] if m not in unavailable]
    if transform not in ('auto', 'none', 'log'):
        raise ValueError("transform must be 'auto', 'none' or 'log'")
    observed = np.ones(n, bool) if observed is None else np.asarray(observed, bool)
    if len(observed) != n:
        raise ValueError('observed mask must match y')
    if np.isnan(y).any():
        raise ValueError('fill gaps before calling the engine and pass observed=False for the filled points')
    baseline_name = BASELINE_FOR.get(pool, 'Seasonal naive' if s > 1 else 'Naive')
    min_train = max(2 * s + h if s > 1 else h + 8, 24)
    final_start = n - h                      # the untouched final holdout
    room = final_start - min_train
    # k origins at final_start - k*h, ..., final_start - h; the earliest must still leave min_train
    # observations for the first training slice, or the seasonal candidates are skipped there and
    # a baseline wins by default (found on a six-year monthly series, 2026-09-20)
    k = int(min(max_origins, room // h)) if room >= 0 else 0
    if k < 2:
        raise ValueError(f'at least {min_train + 3 * h} observations are needed for two selection origins plus a final holdout')
    origins = [final_start - j * h for j in range(k, 0, -1)]  # earliest first, all before the holdout
    first = y[:origins[0]]

    # specification decisions on the first training slice only
    if transform == 'log':
        log, tnote = bool(np.all(first > 0)), {'forced': True}
        if not log:
            raise ValueError('log transform requires positive values')
    elif transform == 'none':
        log, tnote = False, {'forced': False}
    else:
        log, tnote = choose_log(first)
    spec = Spec(log=log, notes={'transform': tnote}, periods=[int(p) for p in (periods or []) if int(p) > 1] or ([s] if s > 1 else []), country=country)
    if regressors is not None:
        spec.regressors = regressors
        if len(regressors['X']) != n or len(regressors['future']) != h:
            raise ValueError('regressors X must align with y and future must have h rows')
    work_first = np.log(first) if log else first
    if 'ETS(auto)' in names:
        try:
            spec.ets = choose_ets(work_first, s, freq)
        except Exception as exc:
            spec.notes['ets'] = str(exc)
    if 'ARIMA(auto)' in names:
        try:
            spec.arima = choose_arima(work_first, s, freq)
            spec.notes['differencing'] = choose_differencing(work_first, s)[2]
        except Exception as exc:
            spec.notes['arima'] = str(exc)

    # rolling origins
    rows, predictions, skipped_all = [], [], {}
    residuals: dict[str, dict[int, list]] = {}
    covered: dict[str, list] = {}
    for origin in origins:
        train, actual = y[:origin], y[origin:origin + h]
        seen_mask = observed[origin:origin + h]
        work = np.log(train) if log else train
        scale = np.mean(np.abs(train[s:] - train[:-s])) if s > 1 and len(train) > s else np.mean(np.abs(np.diff(train)))
        rms_scale = float(np.sqrt(np.mean(np.diff(train) ** 2))) if len(train) > 1 else 0.0
        fits, skipped = _fit_all(names, work, h, s, spec, freq, log)
        skipped_all.update(skipped)
        if rows:
            # rank on the origins already scored; the current actuals are not used
            seen = pd.DataFrame(rows)
            ranked_seen = score_origins(seen, criterion)
            ranking = list(ranked_seen.index); prior_errors = ranked_seen.to_dict()
        elif any(c in names for c in COMBINATIONS) and origin - h >= min_train:
            # first origin: rank on an inner holdout inside the training slice only
            inner_fits, _ = _fit_all([m for m in names if m not in COMBINATIONS], work[:-h], h, s, spec, freq, log)
            inner_actual = train[-h:]
            prior_errors = {m: float(np.abs(inner_actual - inner_fits[m].mean).mean()) for m in inner_fits}
            ranking = sorted(prior_errors, key=prior_errors.get)
        else:
            ranking = []; prior_errors = {}
        fits = _combine(fits, names, ranking, prior_errors)
        for name, f in fits.items():
            err = (actual - f.mean)[seen_mask]
            if len(err) == 0:
                continue
            pin = None
            if f.lower is not None:
                lo, hi = f.lower[seen_mask], f.upper[seen_mask]; a = actual[seen_mask]; q = (1 - NOMINAL) / 2
                pin = float(np.mean(np.maximum(q * (a - lo), (q - 1) * (a - lo))) + np.mean(np.maximum((1 - q) * (a - hi), -q * (a - hi))) + 0.5 * np.mean(np.abs(err)))
            near = seen_mask.copy(); near[int(np.ceil(h / 2)):] = False; far = seen_mask & ~near
            rows.append(dict(origin=int(origin), model=name, mae=float(np.abs(err).mean()),
                             mae_near=float(np.abs(actual - f.mean)[near].mean()) if near.any() else None, mae_far=float(np.abs(actual - f.mean)[far].mean()) if far.any() else None,
                             rmse=float(np.sqrt(np.mean(err ** 2))),
                             mase=float(np.abs(err).mean() / scale) if scale > 0 else None,
                             rmsse=float(np.sqrt(np.mean(err ** 2)) / rms_scale) if rms_scale > 0 else None,
                             cumulative_error=float(abs(err.sum())), pinball=pin))
            full_err = actual - f.mean
            for j in range(h):
                if not seen_mask[j]:
                    continue                                    # a filled gap: fitted on, never scored
                residuals.setdefault(name, {}).setdefault(j + 1, []).append(float(full_err[j]))
                predictions.append(dict(origin=str(timestamps.iloc[origin - 1]), horizon=j + 1,
                                        timestamp=str(timestamps.iloc[origin + j]), model=name,
                                        actual=float(actual[j]), forecast=float(f.mean[j]),
                                        absolute_error=float(abs(full_err[j]))))
            if f.lower is not None:
                covered.setdefault(name, []).extend(((actual >= f.lower) & (actual <= f.upper))[seen_mask].tolist())
    scores = pd.DataFrame(rows)
    if scores.empty:
        raise ValueError('no candidate produced a forecast')
    complete = scores.groupby('model').origin.nunique()
    eligible = list(complete[complete == len(origins)].index)          # only models that ran at every origin
    ranked_all = score_origins(scores[scores.model.isin(eligible)], criterion)
    if ranked_all.empty:
        raise ValueError('no candidate succeeded at every origin')
    # robustness rule: a model that lost to the baseline at more than half the origins is not selectable
    robustness = {}
    if baseline_name in eligible:
        col = criterion if criterion in scores.columns else 'mae'
        base_by_origin = scores[scores.model == baseline_name].set_index('origin')[col]
        for m in eligible:
            own = scores[scores.model == m].set_index('origin')[col]
            losses = int((own.reindex(base_by_origin.index) > base_by_origin).sum())
            robustness[m] = dict(lost_to_baseline_at=losses, of=len(base_by_origin))
    selectable = [m for m in ranked_all.index if robustness.get(m, {}).get('lost_to_baseline_at', 0) <= len(origins) / 2]
    ranked = ranked_all.loc[selectable] if selectable else ranked_all.loc[[baseline_name]] if baseline_name in ranked_all.index else ranked_all
    chosen = str(ranked.index[0])
    forced_baseline = chosen == baseline_name and str(ranked_all.index[0]) != baseline_name
    leaderboard = scores[scores.model.isin(eligible)].groupby('model').agg(
        mae=('mae', 'mean'), rmse=('rmse', 'mean'), mase=('mase', 'mean'), rmsse=('rmsse', 'mean'), cumulative_error=('cumulative_error', 'mean'), pinball=('pinball', 'mean'), mae_near=('mae_near', 'mean'), mae_far=('mae_far', 'mean')).reset_index()
    leaderboard = leaderboard.set_index('model').loc[list(ranked_all.index)].reset_index()
    leaderboard['interval_coverage'] = [float(np.mean(covered[m])) if m in covered else None for m in leaderboard.model]
    leaderboard['lost_to_baseline_at'] = [robustness.get(m, {}).get('lost_to_baseline_at') for m in leaderboard.model]

    # final untouched holdout, scored once for every eligible model
    train, actual = y[:final_start], y[final_start:]
    work = np.log(train) if log else train
    test_mask = observed[final_start:]
    test_fits, _ = _fit_all(list(eligible), work, h, s, spec, freq, log)
    test_fits = _combine(test_fits, names, list(ranked_all.index), ranked_all.to_dict())
    test_mae = {k: float(np.abs(actual - f.mean)[test_mask].mean()) for k, f in test_fits.items() if test_mask.any()}
    test_coverage = {k: float(np.mean(((actual >= f.lower) & (actual <= f.upper))[test_mask])) for k, f in test_fits.items() if f.lower is not None and test_mask.any()}
    conformal_test_coverage = None; holdout_res = {}
    if conformal and chosen in residuals and chosen in test_fits and test_mask.any():
        radius_test = conformal_band(residuals[chosen], NOMINAL); ft = test_fits[chosen].mean
        inside = [(actual[j] >= ft[j] - radius_test[j + 1]) and (actual[j] <= ft[j] + radius_test[j + 1]) for j in range(h) if test_mask[j] and (j + 1) in radius_test]
        conformal_test_coverage = float(np.mean(inside)) if inside else None      # the origin-only band, measured once on the holdout
        holdout_res = {j + 1: [float(actual[j] - ft[j])] for j in range(h) if test_mask[j]}   # never used for selection: fair evidence for the band

    # refit on everything and forecast
    work_all = np.log(y) if log else y
    final_fits, final_skipped = _fit_all(list(eligible), work_all, h, s, spec, freq, log)
    final_fits = _combine(final_fits, names, list(ranked_all.index), ranked_all.to_dict())
    if chosen not in final_fits:
        raise ValueError(f'{chosen} failed on the full history: {final_skipped.get(chosen)}')
    f = final_fits[chosen]
    step_index = pd.date_range(pd.Timestamp(timestamps.iloc[-1]), periods=h + 1, freq=freq)[1:]
    table = pd.DataFrame({'timestamp': step_index, 'forecast': f.mean, 'model': chosen})
    buckets = None
    if per_horizon_buckets and h >= 2:
        cut_step = int(np.ceil(h / 2)); sel = scores[scores.model.isin(selectable if selectable else eligible)]
        near_rank = sel.groupby('model').mae_near.mean().dropna().sort_values(); far_rank = sel.groupby('model').mae_far.mean().dropna().sort_values()
        near_model = str(near_rank.index[0]) if len(near_rank) else chosen; far_model = str(far_rank.index[0]) if len(far_rank) else chosen
        if near_model in final_fits and far_model in final_fits:
            spliced = np.r_[final_fits[near_model].mean[:cut_step], final_fits[far_model].mean[cut_step:]]
            f = Fit(spliced,
                    np.r_[final_fits[near_model].lower[:cut_step], final_fits[far_model].lower[cut_step:]] if final_fits[near_model].lower is not None and final_fits[far_model].lower is not None else None,
                    np.r_[final_fits[near_model].upper[:cut_step], final_fits[far_model].upper[cut_step:]] if final_fits[near_model].upper is not None and final_fits[far_model].upper is not None else None)
            table['forecast'] = f.mean; table['model'] = [near_model] * cut_step + [far_model] * (h - cut_step)
            buckets = dict(near=near_model, far=far_model, cut_step=cut_step, near_mae=float(near_rank.iloc[0]), far_mae=float(far_rank.iloc[0]))
            residuals[chosen] = {j: (residuals.get(near_model, {}) if j <= cut_step else residuals.get(far_model, {})).get(j, residuals[chosen].get(j, [])) for j in range(1, h + 1)}
    band = {}
    for j in range(1, h + 1):
        res = np.asarray(residuals[chosen][j])
        band[j] = {q: float(np.quantile(res, q)) for q in quantiles}
    empirical = {f'empirical_q{int(q * 100):02d}': np.array([f.mean[j - 1] + band[j][q] for j in range(1, h + 1)]) for q in quantiles}
    for key, values in empirical.items():
        table[key] = values
    if f.lower is not None:
        table['lower'], table['upper'] = f.lower, f.upper
        table['interval_level'] = NOMINAL
        interval_note = (f'lower/upper are the {chosen} model\'s nominal {int(NOMINAL * 100)}% intervals; their coverage at the '
                         f'{len(origins)} selection origins was {leaderboard.set_index("model").interval_coverage.get(chosen):.0%}. '
                         f'empirical_q* columns add signed residual quantiles by horizon step from those origins '
                         f'({len(origins)} residuals per step).')
    else:
        interval_note = (f'{chosen} produces no model intervals; empirical_q* columns are signed residual quantiles by '
                         f'horizon step from the {len(origins)} selection origins ({len(origins)} residuals per step) and are descriptive.')
    conformal_note = None; conformal_info = None
    if conformal and chosen in residuals:
        radius, conformal_info = conformal_band(residuals[chosen], NOMINAL, extra=holdout_res, info=True)
        table['conformal_lower'] = [f.mean[j - 1] - radius[j] for j in range(1, h + 1)]
        table['conformal_upper'] = [f.mean[j - 1] + radius[j] for j in range(1, h + 1)]
        conformal_note = (f'conformal_lower/upper are split-conformal bands at nominal {int(NOMINAL * 100)}% from {chosen}\'s absolute residuals at the {len(origins)} selection '
                          f'origins plus its {sum(len(v) for v in holdout_res.values())} final-holdout residuals (the holdout was never used for selection), {conformal_info["m"]} residuals pooled and scaled per step, '
                          f'rank level raised to {conformal_info["level_effective"]:.3f} for the finite sample'
                          + (f'; the origin-only band covered {conformal_test_coverage:.0%} of the holdout' if conformal_test_coverage is not None else '')
                          + '. If future absolute errors are exchangeable with these residuals the band covers at least 80% on average across steps; the guarantee is marginal, not per step, and a level shift or a change in error size voids it.')
    # the band to deliver: the report, the journal and the benchmark all read band_lower/upper and band_method
    band_method = None
    mc = test_coverage.get(chosen); cc = conformal_test_coverage
    if 'conformal_lower' in table and 'lower' in table and mc is not None and cc is not None:
        if (mc - NOMINAL) * (cc - NOMINAL) < 0:
            band_method = 'blend'                            # one band too narrow and the other too wide on the holdout: the midpoint
            table['band_lower'] = (table['lower'] + table['conformal_lower']) / 2; table['band_upper'] = (table['upper'] + table['conformal_upper']) / 2
        elif abs(mc - NOMINAL) < abs(cc - NOMINAL):
            band_method = 'model'; table['band_lower'] = table['lower']; table['band_upper'] = table['upper']
        else:
            band_method = 'conformal'; table['band_lower'] = table['conformal_lower']; table['band_upper'] = table['conformal_upper']
    elif 'conformal_lower' in table:
        band_method = 'conformal'; table['band_lower'] = table['conformal_lower']; table['band_upper'] = table['conformal_upper']
    elif 'lower' in table:
        band_method = 'model'; table['band_lower'] = table['lower']; table['band_upper'] = table['upper']
    if pool == 'intermittent':
        table['forecast'] = np.maximum(table['forecast'], 0)
        for col in ('band_lower', 'conformal_lower', 'lower', 'empirical_q10'):
            if col in table:
                table[col] = np.maximum(table[col], 0)
    summary = dict(
        method='Rolling-origin model comparison with final holdout',
        pool=pool, selected=chosen, criterion=criterion, baseline=baseline_name, forced_baseline=forced_baseline, robustness=robustness,
        unavailable=unavailable, conformal=conformal_note, conformal_test_coverage=conformal_test_coverage, selected_by_bucket=buckets, band_method=band_method,
        band_note=({'blend': 'band_lower/upper is the midpoint of the model band and the conformal band: on the holdout one was too narrow and the other too wide', 'model': 'band_lower/upper is the model\'s own band, whose holdout coverage was nearer nominal than the conformal band\'s', 'conformal': 'band_lower/upper is the split-conformal band'}.get(band_method)), conformal_m=conformal_info['m'] if conformal_info else None, conformal_level_effective=conformal_info['level_effective'] if conformal_info else None,
        transform='log' if log else 'none', specification=dict(
            ets=spec.ets, arima=[list(spec.arima[0]), list(spec.arima[1])] if spec.arima else None, periods=spec.periods,
            regressors=spec.regressors['columns'] if spec.regressors else None, notes=spec.notes),
        origins=[str(timestamps.iloc[o - 1]) for o in origins], horizon=h, season=s,
        leaderboard=[{k: (None if isinstance(v, float) and not np.isfinite(v) else v) for k, v in r.items()} for r in leaderboard.to_dict('records')],
        validation=[{k: (None if isinstance(v, float) and not np.isfinite(v) else v) for k, v in r.items()} for r in scores.to_dict('records')],
        validation_predictions=predictions, test_mae=test_mae, test_interval_coverage=test_coverage,
        skipped={**skipped_all, **final_skipped}, executed=sorted(final_fits),
        evaluation=(f'{len(origins)} expanding origins spaced {h} steps apart select the model on mean {criterion.upper()}; the final {h} '
                    'observations are scored once and never used for selection; the selection is refitted on all history. '
                    f'A model that loses to {baseline_name} at more than half the origins cannot be selected.'),
        intervals=interval_note,
        interpretation=_interpretation(chosen, ranked, ranked_all, criterion, test_mae, baseline_name, forced_baseline, robustness, unavailable),
    )
    return table, summary


def _interpretation(chosen, ranked, ranked_all, criterion, test_mae, baseline_name, forced_baseline, robustness, unavailable):
    label = criterion.upper()
    text = f'{chosen} had the lowest mean validation {label} ({ranked.iloc[0]:.3g}); the runner-up was {ranked.index[1] if len(ranked) > 1 else "none"}' + (f' ({ranked.iloc[1]:.3g}).' if len(ranked) > 1 else '.')
    if forced_baseline:
        text = (f'Every candidate lost to {baseline_name} at more than half the selection origins, so {baseline_name} is selected; '
                f'the best-scoring candidate on average, {ranked_all.index[0]}, was not robust ({robustness[ranked_all.index[0]]["lost_to_baseline_at"]} losses of {robustness[ranked_all.index[0]]["of"]}).')
    if chosen in test_mae:
        text += f' Final-holdout MAE for the selection: {test_mae[chosen]:.3g}' + (f' against {test_mae[baseline_name]:.3g} for {baseline_name}.' if baseline_name in test_mae else '.')
    if baseline_name in ranked_all.index and chosen != baseline_name and not forced_baseline:
        text += f' Validation {label} of {baseline_name}: {ranked_all[baseline_name]:.3g}.'
    if unavailable:
        text += ' Not tried (package missing): ' + ', '.join(unavailable) + '.'
    return text
