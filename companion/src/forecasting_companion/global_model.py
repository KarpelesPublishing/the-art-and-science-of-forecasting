"""One model across many series: cross-series learning for the batch runner.

A single direct LightGBM learner (one booster per horizon step) is trained on every series at once,
with each series scaled by its own training mean so that large and small series share one loss.
Validation follows the engine's origin rule per series against seasonal naive; the future forecast
uses a model refitted on all history. When mlforecast is installed it is used instead and named in
the metrics; the in-house learner is the fallback. Bands are per-series empirical residual quantiles
by horizon step from the validation origins.
"""
import numpy as np
import pandas as pd
from .optional import have
from .applied.core import expanding_origins


def _features(y, t, s, lags, roll):
    row = [y[t - l] for l in lags] + [float(np.mean(y[t - roll:t]))] + [t % s if s > 1 else 0]
    return row


def run_global(series, horizon, season, max_origins=3, seed=12):
    """series: dict id -> (timestamps: pd.Series, y: np.ndarray). Returns dict id -> (future table, summary)."""
    if not have('lightgbm'):
        raise ValueError('lightgbm not installed')
    import lightgbm as lgb
    h, s = int(horizon), int(season)
    lags = sorted({1, 2, 3, s, 2 * s} if s > 1 else {1, 2, 3, 6, 12}); roll = max(s, 3)
    lookback = max(lags + [roll])
    min_train = max(2 * s + h if s > 1 else h + 8, 24)
    params = dict(objective='regression', verbosity=-1, num_threads=1, seed=seed, num_leaves=31, learning_rate=0.05, min_data_in_leaf=20)
    prepared = {}
    for sid, (ts, y) in series.items():
        y = np.asarray(y, float)
        if len(y) < min_train + 3 * h:
            continue
        prepared[sid] = dict(ts=pd.Series(ts).reset_index(drop=True), y=y, origins=expanding_origins(len(y), h, min_train, max_origins))
    if not prepared:
        raise ValueError(f'no series has the {min_train + 3 * h} observations the global model needs')
    def rows_before(cut_fn):
        X = {step: [] for step in range(1, h + 1)}; Y = {step: [] for step in range(1, h + 1)}
        for sid, p in prepared.items():
            y = p['y']; cut = cut_fn(sid, p); scale = max(float(np.mean(np.abs(y[:cut]))), 1e-6)
            for t in range(lookback, cut):
                f = _features(y / scale, t, s, lags, roll)
                for step in range(1, h + 1):
                    if t + step - 1 < cut:
                        X[step].append(f + [step]); Y[step].append(y[t + step - 1] / scale)
        return X, Y
    def fit(X, Y):
        return {step: lgb.train(params, lgb.Dataset(np.asarray(X[step], float), label=np.asarray(Y[step], float)), num_boost_round=150) for step in range(1, h + 1) if X[step]}
    def predict(models, y, cut):
        scale = max(float(np.mean(np.abs(y[:cut]))), 1e-6); f = _features(y[:cut] / scale, cut, s, lags, roll)
        return np.array([models[step].predict(np.asarray([f + [step]], float))[0] * scale for step in range(1, h + 1)])
    # validation: one model per origin index (all series share the origin index j = 1..k counted from the end)
    k = min(len(p['origins']) for p in prepared.values())
    residuals = {sid: {step: [] for step in range(1, h + 1)} for sid in prepared}
    val = {sid: [] for sid in prepared}
    for j in range(k):
        cut_of = {sid: p['origins'][len(p['origins']) - k + j] for sid, p in prepared.items()}
        models = fit(*rows_before(lambda sid, p: cut_of[sid]))
        for sid, p in prepared.items():
            cut = cut_of[sid]; y = p['y']; actual = y[cut:cut + h]; pred = predict(models, y, cut)
            base = np.resize(y[cut - s:cut], h) if s > 1 and cut >= s else np.repeat(y[cut - 1], h)
            val[sid].append(dict(origin=str(p['ts'].iloc[cut - 1]), model_mae=float(np.abs(actual - pred).mean()), seasonal_naive_mae=float(np.abs(actual - base).mean())))
            for step in range(1, h + 1):
                residuals[sid][step].append(float(actual[step - 1] - pred[step - 1]))
    # holdout, scored once, then refit on everything for the future
    holdout_models = fit(*rows_before(lambda sid, p: len(p['y']) - h))
    final_models = fit(*rows_before(lambda sid, p: len(p['y'])))
    out = {}
    for sid, p in prepared.items():
        y = p['y']; ts = p['ts']; cut = len(y) - h
        hold_pred = predict(holdout_models, y, cut); actual = y[cut:]
        base = np.resize(y[cut - s:cut], h) if s > 1 else np.repeat(y[cut - 1], h)
        future = predict(final_models, y, len(y))
        freq = pd.infer_freq(pd.DatetimeIndex(ts)) or 'MS'
        dates = pd.date_range(pd.Timestamp(ts.iloc[-1]), periods=h + 1, freq=freq)[1:]
        table = pd.DataFrame({'timestamp': dates, 'forecast': future, 'model': 'Global LightGBM'})
        for q in (0.1, 0.5, 0.9):
            table[f'empirical_q{int(q * 100):02d}'] = [future[step - 1] + float(np.quantile(residuals[sid][step], q)) for step in range(1, h + 1)]
        mae_model = float(np.mean([v['model_mae'] for v in val[sid]])); mae_base = float(np.mean([v['seasonal_naive_mae'] for v in val[sid]]))
        out[sid] = (table, dict(selected='Global LightGBM', method='Global direct LightGBM across series, per-series scaling',
                               validation=val[sid], validation_mae=mae_model, baseline_validation_mae=mae_base,
                               test_mae={'Global LightGBM': float(np.abs(actual - hold_pred).mean()), 'Seasonal naive': float(np.abs(actual - base).mean())},
                               origins=[v['origin'] for v in val[sid]], series_in_model=len(prepared), lost_to_baseline=bool(mae_model > mae_base)))
    return out
