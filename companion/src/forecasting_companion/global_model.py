"""One model across many series: cross-series learning for the batch runner.

Two learners share one schedule. `run_global` trains a single direct LightGBM (one booster per
horizon step, or mlforecast's MLForecast when that package is installed) on every series at once,
each series scaled by its own training mean so large and small series share one loss.
`run_neural` trains neuralforecast's NHITS on every series (a small CPU configuration with a
bounded step budget). Validation follows the engine's origin rule per series against seasonal
naive; the future forecast uses a model refitted on all history. The metrics name which learner
ran. Bands are per-series empirical residual quantiles by horizon step from the validation origins.
"""
import logging
import os
import numpy as np
import pandas as pd
from .optional import have, hint
from .applied.core import expanding_origins


def _features(y, t, s, lags, roll):
    return [y[t - l] for l in lags] + [float(np.mean(y[t - roll:t]))] + [t % s if s > 1 else 0]


def _prepare(series, horizon, season, max_origins):
    h, s = int(horizon), int(season)
    min_train = max(2 * s + h if s > 1 else h + 8, 24)
    prepared = {}
    for sid, (ts, y) in series.items():
        y = np.asarray(y, float)
        if len(y) < min_train + 3 * h:
            continue
        prepared[sid] = dict(ts=pd.Series(ts).reset_index(drop=True), y=y, origins=expanding_origins(len(y), h, min_train, max_origins))
    if not prepared:
        raise ValueError(f'no series has the {min_train + 3 * h} observations the global model needs')
    return prepared


def _finish(prepared, h, s, val, residuals, predict_future, predict_holdout, label):
    out = {}
    for sid, p in prepared.items():
        y = p['y']; ts = p['ts']; cut = len(y) - h
        hold_pred = predict_holdout(sid); actual = y[cut:]
        base = np.resize(y[cut - s:cut], h) if s > 1 else np.repeat(y[cut - 1], h)
        future = predict_future(sid)
        freq = pd.infer_freq(pd.DatetimeIndex(ts)) or 'MS'
        dates = pd.date_range(pd.Timestamp(ts.iloc[-1]), periods=h + 1, freq=freq)[1:]
        table = pd.DataFrame({'timestamp': dates, 'forecast': future, 'model': label})
        for q in (0.1, 0.5, 0.9):
            table[f'empirical_q{int(q * 100):02d}'] = [future[step - 1] + float(np.quantile(residuals[sid][step], q)) for step in range(1, h + 1)]
        mae_model = float(np.mean([v['model_mae'] for v in val[sid]])); mae_base = float(np.mean([v['seasonal_naive_mae'] for v in val[sid]]))
        out[sid] = (table, dict(selected=label, method=f'{label} across {len(prepared)} series, per-series scaling',
                               validation=val[sid], validation_mae=mae_model, baseline_validation_mae=mae_base,
                               test_mae={label: float(np.abs(actual - hold_pred).mean()), 'Seasonal naive': float(np.abs(actual - base).mean())},
                               origins=[v['origin'] for v in val[sid]], series_in_model=len(prepared), lost_to_baseline=bool(mae_model > mae_base)))
    return out


def _frame(prepared, cut_fn, freq):
    rows = []
    for sid, p in prepared.items():
        cut = cut_fn(sid, p)
        rows.append(pd.DataFrame({'unique_id': sid, 'ds': pd.DatetimeIndex(p['ts'].iloc[:cut]).tz_localize(None), 'y': p['y'][:cut]}))
    return pd.concat(rows, ignore_index=True)


def run_global(series, horizon, season, max_origins=3, seed=12):
    """series: dict id -> (timestamps, y). Returns dict id -> (future table, summary). Uses mlforecast when installed."""
    if not have('lightgbm'):
        raise ValueError('lightgbm not installed')
    h, s = int(horizon), int(season)
    prepared = _prepare(series, h, s, max_origins)
    k = min(len(p['origins']) for p in prepared.values())
    residuals = {sid: {step: [] for step in range(1, h + 1)} for sid in prepared}; val = {sid: [] for sid in prepared}
    freq = pd.infer_freq(pd.DatetimeIndex(next(iter(prepared.values()))['ts'])) or 'MS'
    if have('mlforecast'):
        from mlforecast import MLForecast
        from mlforecast.target_transforms import LocalStandardScaler
        from mlforecast.lag_transforms import RollingMean
        import lightgbm as lgb
        lags = sorted({1, 2, 3, s, 2 * s} if s > 1 else {1, 2, 3, 6, 12})
        def fit(cut_fn):
            m = MLForecast(models={'lgb': lgb.LGBMRegressor(n_estimators=150, learning_rate=0.05, num_leaves=31, min_child_samples=20, verbosity=-1, num_threads=1, random_state=seed)},
                           freq=freq, lags=lags, lag_transforms={1: [RollingMean(window_size=max(s, 3))]}, date_features=['month'] if s in (12, 4) else ['dayofweek'] if s == 7 else [],
                           target_transforms=[LocalStandardScaler()])
            m.fit(_frame(prepared, cut_fn, freq), max_horizon=h)
            pred = m.predict(h)
            return {sid: g.sort_values('ds').lgb.to_numpy() for sid, g in pred.groupby('unique_id')}
        label = 'Global LightGBM (mlforecast)'
    else:
        import lightgbm as lgb
        lags = sorted({1, 2, 3, s, 2 * s} if s > 1 else {1, 2, 3, 6, 12}); roll = max(s, 3); lookback = max(lags + [roll])
        params = dict(objective='regression', verbosity=-1, num_threads=1, seed=seed, num_leaves=31, learning_rate=0.05, min_data_in_leaf=20)
        def fit(cut_fn):
            X = {step: [] for step in range(1, h + 1)}; Y = {step: [] for step in range(1, h + 1)}
            for sid, p in prepared.items():
                y = p['y']; cut = cut_fn(sid, p); scale = max(float(np.mean(np.abs(y[:cut]))), 1e-6)
                for t in range(lookback, cut):
                    f = _features(y / scale, t, s, lags, roll)
                    for step in range(1, h + 1):
                        if t + step - 1 < cut:
                            X[step].append(f + [step]); Y[step].append(y[t + step - 1] / scale)
            models = {step: lgb.train(params, lgb.Dataset(np.asarray(X[step], float), label=np.asarray(Y[step], float)), num_boost_round=150) for step in range(1, h + 1) if X[step]}
            out = {}
            for sid, p in prepared.items():
                y = p['y']; cut = cut_fn(sid, p); scale = max(float(np.mean(np.abs(y[:cut]))), 1e-6); f = _features(y[:cut] / scale, cut, s, lags, roll)
                out[sid] = np.array([models[step].predict(np.asarray([f + [step]], float))[0] * scale for step in range(1, h + 1)])
            return out
        label = 'Global LightGBM (in-house)'
    for j in range(k):
        cut_of = {sid: p['origins'][len(p['origins']) - k + j] for sid, p in prepared.items()}
        preds = fit(lambda sid, p: cut_of[sid])
        for sid, p in prepared.items():
            cut = cut_of[sid]; y = p['y']; actual = y[cut:cut + h]; pred = preds[sid]
            base = np.resize(y[cut - s:cut], h) if s > 1 and cut >= s else np.repeat(y[cut - 1], h)
            val[sid].append(dict(origin=str(p['ts'].iloc[cut - 1]), model_mae=float(np.abs(actual - pred).mean()), seasonal_naive_mae=float(np.abs(actual - base).mean())))
            for step in range(1, h + 1):
                residuals[sid][step].append(float(actual[step - 1] - pred[step - 1]))
    holdout = fit(lambda sid, p: len(p['y']) - h); final = fit(lambda sid, p: len(p['y']))
    return _finish(prepared, h, s, val, residuals, lambda sid: final[sid], lambda sid: holdout[sid], label)


def run_neural(series, horizon, season, max_origins=2, seed=1, max_steps=100):
    """NHITS from neuralforecast on every series, CPU, bounded steps; same schedule and scoring as run_global."""
    if not have('neuralforecast'):
        raise ValueError('neuralforecast not installed: ' + hint('neuralforecast'))
    os.environ.setdefault('PYTORCH_ENABLE_MPS_FALLBACK', '1')
    for name in ('pytorch_lightning', 'lightning', 'lightning.pytorch', 'neuralforecast'):
        logging.getLogger(name).setLevel(logging.ERROR)
    from neuralforecast import NeuralForecast
    from neuralforecast.models import NHITS
    h, s = int(horizon), int(season)
    prepared = _prepare(series, h, s, max_origins)
    k = min(len(p['origins']) for p in prepared.values())
    residuals = {sid: {step: [] for step in range(1, h + 1)} for sid in prepared}; val = {sid: [] for sid in prepared}
    freq = pd.infer_freq(pd.DatetimeIndex(next(iter(prepared.values()))['ts'])) or 'MS'
    input_size = max(2 * s, 2 * h, 12)
    def fit(cut_fn):
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            nf = NeuralForecast(models=[NHITS(h=h, input_size=input_size, max_steps=max_steps, scaler_type='standard', random_seed=seed, enable_progress_bar=False, logger=False, enable_checkpointing=False, accelerator='cpu', devices=1)], freq=freq)
            nf.fit(_frame(prepared, cut_fn, freq)); pred = nf.predict()
        return {sid: g.sort_values('ds').NHITS.to_numpy() for sid, g in pred.groupby('unique_id')}
    for j in range(k):
        cut_of = {sid: p['origins'][len(p['origins']) - k + j] for sid, p in prepared.items()}
        preds = fit(lambda sid, p: cut_of[sid])
        for sid, p in prepared.items():
            cut = cut_of[sid]; y = p['y']; actual = y[cut:cut + h]; pred = preds[sid]
            base = np.resize(y[cut - s:cut], h) if s > 1 and cut >= s else np.repeat(y[cut - 1], h)
            val[sid].append(dict(origin=str(p['ts'].iloc[cut - 1]), model_mae=float(np.abs(actual - pred).mean()), seasonal_naive_mae=float(np.abs(actual - base).mean())))
            for step in range(1, h + 1):
                residuals[sid][step].append(float(actual[step - 1] - pred[step - 1]))
    holdout = fit(lambda sid, p: len(p['y']) - h); final = fit(lambda sid, p: len(p['y']))
    return _finish(prepared, h, s, val, residuals, lambda sid: final[sid], lambda sid: holdout[sid], 'NHITS (neuralforecast)')
