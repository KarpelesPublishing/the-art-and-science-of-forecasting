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
             'Combination(top3)', 'Equal ensemble'],
    'baseline': ['Naive', 'Seasonal naive', 'Drift', 'Equal ensemble'],
}
NOMINAL = 0.8  # the interval level scored during validation


@dataclass
class Spec:
    """Specification choices frozen on the first training slice."""
    log: bool = False
    ets: Optional[dict] = None
    arima: Optional[tuple] = None
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


def fit_airline(y, h, s, spec, freq):
    if s <= 1 or len(y) < 3 * s:
        raise ValueError('needs three seasonal cycles')
    return _arima(y, h, s, freq, (0, 1, 1), (0, 1, 1, s))[1]


def choose_arima(y, s, freq) -> tuple:
    """AICc grid over p,q in 0..2 and P,Q in 0..1 with d, D from diagnostics."""
    d, D, _ = choose_differencing(y, s)
    seasonal_grid = [(P, D, Q, s) for P in (0, 1) for Q in (0, 1)] if s > 1 and len(y) >= 3 * s else [(0, 0, 0, 0)]
    best, best_score = None, np.inf
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
    return _arima(y, h, s, freq, order, seasonal)[1]


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


CANDIDATES: dict[str, Callable] = {
    'Naive': fit_naive, 'Seasonal naive': fit_seasonal_naive, 'Drift': fit_drift,
    'SES': fit_ses, 'Holt': fit_holt, 'Damped Holt': fit_damped, 'ETS(auto)': fit_ets_auto,
    'Theta': fit_theta, 'STL+ETS': fit_stl_ets, 'ARIMA(0,1,1)': fit_arima_011,
    'ARIMA(1,1,0)': fit_arima_110, 'Airline ARIMA': fit_airline, 'ARIMA(auto)': fit_arima_auto,
    'LightGBM': fit_lightgbm,
}
COMBINATIONS = {'Combination(top3)', 'Equal ensemble'}


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


def _combine(fits, names, ranking):
    if 'Equal ensemble' in names and fits:
        members = [f.mean for k, f in fits.items() if k not in COMBINATIONS]
        if members:
            fits['Equal ensemble'] = Fit(np.mean(members, axis=0))
    if 'Combination(top3)' in names and ranking:
        top = [k for k in ranking if k in fits and k not in COMBINATIONS][:3]
        if len(top) >= 2:
            fits['Combination(top3)'] = Fit(np.median([fits[k].mean for k in top], axis=0))
    return fits


def forecast_series(y: np.ndarray, timestamps: pd.Series, horizon: int, season: int, *,
                    pool: str = 'full', freq: str = 'MS', transform: str = 'auto',
                    max_origins: int = 5, quantiles=(0.1, 0.5, 0.9)) -> tuple[pd.DataFrame, dict]:
    """Forecast one regular series. Returns the future table and a full evidence summary."""
    y = np.asarray(y, float)
    n, h, s = len(y), int(horizon), int(season)
    if pool not in POOLS:
        raise ValueError(f'pool must be one of {sorted(POOLS)}')
    names = POOLS[pool]
    if transform not in ('auto', 'none', 'log'):
        raise ValueError("transform must be 'auto', 'none' or 'log'")
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
    spec = Spec(log=log, notes={'transform': tnote})
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
        work = np.log(train) if log else train
        scale = np.mean(np.abs(train[s:] - train[:-s])) if s > 1 and len(train) > s else np.mean(np.abs(np.diff(train)))
        fits, skipped = _fit_all(names, work, h, s, spec, freq, log)
        skipped_all.update(skipped)
        if rows:
            # rank on the origins already scored; the current actuals are not used
            seen = pd.DataFrame(rows)
            ranking = list(seen.groupby('model').mae.mean().sort_values().index)
        elif any(c in names for c in COMBINATIONS) and origin - h >= min_train:
            # first origin: rank on an inner holdout inside the training slice only
            inner_fits, _ = _fit_all([m for m in names if m not in COMBINATIONS], work[:-h], h, s, spec, freq, log)
            inner_actual = train[-h:]
            ranking = sorted(inner_fits, key=lambda m: float(np.abs(inner_actual - inner_fits[m].mean).mean()))
        else:
            ranking = []
        fits = _combine(fits, names, ranking)
        for name, f in fits.items():
            err = actual - f.mean
            rows.append(dict(origin=int(origin), model=name, mae=float(np.abs(err).mean()),
                             rmse=float(np.sqrt(np.mean(err ** 2))),
                             mase=float(np.abs(err).mean() / scale) if scale > 0 else None))
            for j in range(h):
                residuals.setdefault(name, {}).setdefault(j + 1, []).append(float(err[j]))
                predictions.append(dict(origin=str(timestamps.iloc[origin - 1]), horizon=j + 1,
                                        timestamp=str(timestamps.iloc[origin + j]), model=name,
                                        actual=float(actual[j]), forecast=float(f.mean[j]),
                                        absolute_error=float(abs(err[j]))))
            if f.lower is not None:
                covered.setdefault(name, []).extend(((actual >= f.lower) & (actual <= f.upper)).tolist())
    scores = pd.DataFrame(rows)
    if scores.empty:
        raise ValueError('no candidate produced a forecast')
    complete = scores.groupby('model').origin.nunique()
    eligible = complete[complete == len(origins)].index          # only models that ran at every origin
    ranked = scores[scores.model.isin(eligible)].groupby('model').mae.mean().sort_values()
    if ranked.empty:
        raise ValueError('no candidate succeeded at every origin')
    chosen = str(ranked.index[0])
    leaderboard = scores[scores.model.isin(eligible)].groupby('model').agg(
        mae=('mae', 'mean'), rmse=('rmse', 'mean'), mase=('mase', 'mean')).sort_values('mae').reset_index()
    leaderboard['interval_coverage'] = [float(np.mean(covered[m])) if m in covered else None for m in leaderboard.model]

    # final untouched holdout, scored once for every eligible model
    train, actual = y[:final_start], y[final_start:]
    work = np.log(train) if log else train
    test_fits, _ = _fit_all(list(eligible), work, h, s, spec, freq, log)
    test_fits = _combine(test_fits, names, list(ranked.index))
    test_mae = {k: float(np.abs(actual - f.mean).mean()) for k, f in test_fits.items()}
    test_coverage = {k: float(np.mean((actual >= f.lower) & (actual <= f.upper))) for k, f in test_fits.items() if f.lower is not None}

    # refit on everything and forecast
    work_all = np.log(y) if log else y
    final_fits, final_skipped = _fit_all(list(eligible), work_all, h, s, spec, freq, log)
    final_fits = _combine(final_fits, names, list(ranked.index))
    if chosen not in final_fits:
        raise ValueError(f'{chosen} failed on the full history: {final_skipped.get(chosen)}')
    f = final_fits[chosen]
    step_index = pd.date_range(pd.Timestamp(timestamps.iloc[-1]), periods=h + 1, freq=freq)[1:]
    table = pd.DataFrame({'timestamp': step_index, 'forecast': f.mean, 'model': chosen})
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
    summary = dict(
        method='Rolling-origin model comparison with final holdout',
        pool=pool, selected=chosen, transform='log' if log else 'none', specification=dict(
            ets=spec.ets, arima=[list(spec.arima[0]), list(spec.arima[1])] if spec.arima else None, notes=spec.notes),
        origins=[str(timestamps.iloc[o - 1]) for o in origins], horizon=h, season=s,
        leaderboard=[{k: (None if isinstance(v, float) and not np.isfinite(v) else v) for k, v in r.items()} for r in leaderboard.to_dict('records')],
        validation=[{k: (None if isinstance(v, float) and not np.isfinite(v) else v) for k, v in r.items()} for r in scores.to_dict('records')],
        validation_predictions=predictions, test_mae=test_mae, test_interval_coverage=test_coverage,
        skipped={**skipped_all, **final_skipped}, executed=sorted(final_fits),
        evaluation=(f'{len(origins)} expanding origins spaced {h} steps apart select the model on mean MAE; the final {h} '
                    'observations are scored once and never used for selection; the selection is refitted on all history.'),
        intervals=interval_note,
        interpretation=(f'{chosen} had the lowest mean validation MAE ({ranked.iloc[0]:.3g}); the runner-up was '
                        f'{ranked.index[1] if len(ranked) > 1 else "none"} ({ranked.iloc[1]:.3g}). Final-holdout MAE for the selection: '
                        f'{test_mae.get(chosen, float("nan")):.3g}. Compare against Seasonal naive before trusting the gain.'),
    )
    return table, summary
