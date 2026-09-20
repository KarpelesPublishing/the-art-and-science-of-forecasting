"""Bounded local batch forecasting with content-addressed per-series checkpoints.

Run ``python -m forecasting_companion.batch --help``.

Two engines. ``--engine baseline`` (default) compares naive, drift, seasonal-naive
and their equal ensemble at up to five origins: fast, transparent, and suitable
for thousands of series. ``--engine full`` (or ``smoothing`` / ``arima``) runs the
real engine in ``forecasting_companion.engine`` for every series: ETS with an
AICc-chosen form, Theta, STL+ETS, seasonal ARIMA with diagnostic-chosen
differencing, LightGBM where history allows, and combinations, each selected by
rolling-origin validation with a final untouched holdout and reported interval
coverage. Budget a few seconds per series for the full engine.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import os
from pathlib import Path
import tempfile
import time

import numpy as np
import pandas as pd

FORECAST_COLUMNS = ['series_id', 'origin', 'timestamp', 'horizon_step', 'model',
                    'point', 'quantile', 'value', 'status', 'band_method', 'residual_count']


def _write_json(path: Path, value: dict) -> None:
    """Publish complete checkpoints atomically; interrupted temp files are ignored."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode='w', dir=path.parent, suffix='.tmp',
                                     delete=False, encoding='utf-8') as handle:
        temporary = Path(handle.name)
        json.dump(value, handle, sort_keys=True, allow_nan=False)
    os.replace(temporary, path)


def _season(frequency: str) -> int:
    offset = pd.tseries.frequencies.to_offset(frequency)
    if offset.n != 1:
        return 1
    name = offset.name.upper()
    if name in {'MS', 'ME'}:
        return 12
    if name in {'D', 'B'}:
        return 7 if name == 'D' else 5
    if name == 'H':
        return 24
    if name.startswith('Q'):
        return 4
    return 1  # No guessed annual seasonality for other frequencies.


def _forecast(y: np.ndarray, horizon: int, model: str, season: int) -> np.ndarray:
    if model == 'naive':
        return np.repeat(y[-1], horizon)
    if model == 'drift':
        return y[-1] + np.arange(1, horizon+1)*(y[-1]-y[0])/(len(y)-1)
    if model == 'seasonal_naive':
        return np.resize(y[-season:], horizon)
    members = ['naive', 'drift'] + (['seasonal_naive'] if season > 1 and len(y) >= season else [])
    return np.mean([_forecast(y, horizon, name, season) for name in members], axis=0)


def _engine_one(series_id: str, frame: pd.DataFrame, y: np.ndarray, config: dict, start: float) -> dict:
    """Run the full engine for one series and map its output onto the batch schema."""
    from .engine import forecast_series
    horizon, season = config['horizon'], _season(config['frequency'])
    table, summary = forecast_series(y, frame.timestamp.reset_index(drop=True), horizon, season,
                                     pool=config['engine'], freq=config['frequency'])
    has_model_band = 'lower' in table
    output = []
    for step, row in enumerate(table.itertuples(index=False), 1):
        values = {.1: row.empirical_q10, .5: row.empirical_q50, .9: row.empirical_q90}
        for quantile, value in values.items():
            output.append(dict(series_id=series_id, origin=frame.timestamp.iloc[-1].isoformat(),
                timestamp=pd.Timestamp(row.timestamp).isoformat(), horizon_step=step, model=summary['selected'],
                point=float(row.forecast), quantile=quantile, value=float(value), status='ok',
                band_method='empirical_signed_residual_by_horizon', residual_count=len(summary['origins'])))
        if has_model_band:
            for quantile, value in ((.1, row.lower), (.9, row.upper)):
                output.append(dict(series_id=series_id, origin=frame.timestamp.iloc[-1].isoformat(),
                    timestamp=pd.Timestamp(row.timestamp).isoformat(), horizon_step=step, model=summary['selected'],
                    point=float(row.forecast), quantile=quantile, value=float(value), status='ok',
                    band_method='model_interval_80', residual_count=len(summary['origins'])))
    board = {r['model']: round(r['mae'], 6) for r in summary['leaderboard']}
    return {'series_id': series_id, 'status': 'ok', 'forecasts': output,
            'metrics': dict(series_id=series_id, status='ok', observations=len(y),
                origin=frame.timestamp.iloc[-1].isoformat(), selected_model=summary['selected'],
                validation_mae=board[summary['selected']], validation_origins=len(summary['origins']),
                validation_pairs=len(summary['origins'])*horizon, candidate_mae=json.dumps(board, sort_keys=True),
                transform=summary['transform'], holdout_mae=summary['test_mae'].get(summary['selected']),
                interval_coverage=next((r['interval_coverage'] for r in summary['leaderboard'] if r['model']==summary['selected']), None),
                skipped=json.dumps(summary['skipped'], sort_keys=True),
                error='', elapsed_seconds=time.perf_counter()-start)}


def _global(tasks, config: dict) -> list:
    """The global learner over every valid series; invalid series are reported like any other failure."""
    from .global_model import run_global
    start = time.perf_counter(); horizon, season = config['horizon'], _season(config['frequency'])
    series, results = {}, []
    for series_id, rows, _ in tasks:
        try:
            frame = pd.DataFrame(rows, columns=['timestamp', 'target'])
            frame['timestamp'] = pd.to_datetime(frame.timestamp, errors='coerce', utc=True, format='mixed')
            if frame.timestamp.isna().any() or frame.timestamp.duplicated().any():
                raise ValueError('invalid or duplicate timestamp')
            frame = frame.sort_values('timestamp'); y = pd.to_numeric(frame.target, errors='coerce').to_numpy(float)
            if not np.isfinite(y).all():
                raise ValueError('nonfinite or nonnumeric target')
            dates = pd.DatetimeIndex(frame.timestamp)
            if not dates.equals(pd.date_range(dates[0], dates[-1], freq=config['frequency'])):
                raise ValueError('frequency gaps or timestamps off the requested grid')
            series[series_id] = (frame.timestamp.reset_index(drop=True), y)
        except ValueError as exc:
            results.append({'series_id': series_id, 'status': 'failed', 'forecasts': [], 'metrics': dict(series_id=series_id, status='failed', error=f'ValueError: {exc}', elapsed_seconds=0.0)})
    fitted = run_global(series, horizon, season) if series else {}
    for series_id, (ts, y) in series.items():
        if series_id not in fitted:
            results.append({'series_id': series_id, 'status': 'failed', 'forecasts': [], 'metrics': dict(series_id=series_id, status='failed', error='ValueError: too short for the global model', elapsed_seconds=0.0)})
            continue
        table, summary = fitted[series_id]
        output = []
        for step, row in enumerate(table.itertuples(index=False), 1):
            for quantile, value in ((.1, row.empirical_q10), (.5, row.empirical_q50), (.9, row.empirical_q90)):
                output.append(dict(series_id=series_id, origin=ts.iloc[-1].isoformat(), timestamp=pd.Timestamp(row.timestamp).isoformat(), horizon_step=step, model='Global LightGBM',
                                   point=float(row.forecast), quantile=quantile, value=float(value), status='ok', band_method='empirical_signed_residual_by_horizon', residual_count=len(summary['origins'])))
        results.append({'series_id': series_id, 'status': 'ok', 'forecasts': output,
                        'metrics': dict(series_id=series_id, status='ok', observations=len(y), origin=ts.iloc[-1].isoformat(), selected_model='Global LightGBM',
                                        validation_mae=round(summary['validation_mae'], 6), validation_origins=len(summary['origins']), validation_pairs=len(summary['origins']) * horizon,
                                        candidate_mae=json.dumps({'Global LightGBM': round(summary['validation_mae'], 6), 'Seasonal naive': round(summary['baseline_validation_mae'], 6)}, sort_keys=True),
                                        transform='none', holdout_mae=summary['test_mae']['Global LightGBM'], interval_coverage=None,
                                        skipped=json.dumps({'note': 'lost to seasonal naive at validation' if summary['lost_to_baseline'] else ''}), error='',
                                        elapsed_seconds=(time.perf_counter() - start) / max(len(series), 1))})
    return results


def _one(series_id: str, rows: list[list[str]], config: dict) -> dict:
    """Validate one series, select a model, and return JSON-serializable output."""
    start = time.perf_counter()
    try:
        if not series_id:
            raise ValueError('empty series_id')
        frame = pd.DataFrame(rows, columns=['timestamp', 'target'])
        frame['timestamp'] = pd.to_datetime(frame.timestamp, errors='coerce', utc=True, format='mixed')
        if frame.timestamp.isna().any():
            raise ValueError('invalid timestamp')
        if frame.timestamp.duplicated().any():
            raise ValueError('duplicate timestamp key')
        frame = frame.sort_values('timestamp')
        y = pd.to_numeric(frame.target, errors='coerce').to_numpy(dtype=float)
        if not np.isfinite(y).all():
            raise ValueError('nonfinite or nonnumeric target')
        if len(y) < 8:
            raise ValueError('fewer than 8 observations at the cutoff')
        dates = pd.DatetimeIndex(frame.timestamp)
        expected = pd.date_range(dates[0], dates[-1], freq=config['frequency'])
        if not dates.equals(expected):
            raise ValueError('frequency gaps or timestamps off the requested grid')
        if config.get('engine', 'baseline') != 'baseline':
            return _engine_one(series_id, frame, y, config, start)
        horizon, season = config['horizon'], _season(config['frequency'])
        seasonal_eligible = season > 1 and len(y) >= 2*season
        effective_season = season if seasonal_eligible else 1
        candidates = ['naive', 'drift'] + (['seasonal_naive'] if seasonal_eligible else []) + ['ensemble']
        warmup = max(4, effective_season)
        # At most five expanding-window origins. Later targets never enter a fit.
        origins = np.unique(np.linspace(warmup, len(y)-1, min(5, len(y)-warmup), dtype=int))
        errors = {name: {} for name in candidates}
        absolute = {name: [] for name in candidates}
        for origin in origins:
            steps = min(horizon, len(y)-origin)
            actual = y[origin:origin+steps]
            for name in candidates:
                residual = actual-_forecast(y[:origin], steps, name, effective_season)
                absolute[name].extend(np.abs(residual).tolist())
                for step, error in enumerate(residual, 1):
                    errors[name].setdefault(step, []).append(float(error))
        scores = {name: float(np.mean(values)) for name, values in absolute.items()}
        if not np.isfinite(list(scores.values())).all():
            raise ValueError('numerical overflow in validation; rescale the target')
        # Dict order provides a documented deterministic tie break: simplest first.
        selected = min(scores, key=scores.get)
        point = _forecast(y, horizon, selected, effective_season)
        if not np.isfinite(point).all():
            raise ValueError('numerical overflow in forecast; rescale the target')
        future = pd.date_range(dates[-1], periods=horizon+1, freq=config['frequency'])[1:]
        output = []
        for step, (timestamp, prediction) in enumerate(zip(future, point), 1):
            available_step = min(step, max(errors[selected]))
            residuals = np.asarray(errors[selected][available_step])
            extrapolated = available_step != step
            # Explicit fallback when history cannot validate a requested horizon.
            # Square-root scaling is a heuristic, not a calibrated probability law.
            residuals = residuals*np.sqrt(step/available_step)
            offsets = np.quantile(residuals, [.1, .5, .9])
            if not np.isfinite(prediction+offsets).all():
                raise ValueError('numerical overflow in residual bands; rescale the target')
            for quantile, offset in zip([.1, .5, .9], offsets):
                output.append(dict(series_id=series_id, origin=dates[-1].isoformat(),
                    timestamp=timestamp.isoformat(), horizon_step=step, model=selected,
                    point=float(prediction), quantile=quantile, value=float(prediction+offset), status='ok',
                    band_method='empirical_signed_residual_sqrt_extrapolation' if extrapolated else 'empirical_signed_residual_by_horizon',
                    residual_count=len(residuals)))
        return {'series_id': series_id, 'status': 'ok', 'forecasts': output,
                'metrics': dict(series_id=series_id, status='ok', observations=len(y),
                    origin=dates[-1].isoformat(), selected_model=selected,
                    validation_mae=scores[selected], validation_origins=len(origins),
                    validation_pairs=len(absolute[selected]), candidate_mae=json.dumps(scores, sort_keys=True),
                    error='', elapsed_seconds=time.perf_counter()-start)}
    except Exception as error:
        return {'series_id': series_id, 'status': 'failed', 'forecasts': [],
                'metrics': dict(series_id=series_id, status='failed', error=f'{type(error).__name__}: {error}',
                                elapsed_seconds=time.perf_counter()-start)}


def run_batch(input_path: str | Path, output: str | Path, horizon: int = 12,
              frequency: str = 'MS', workers: int = 4, resume: bool = False,
              as_of: str | None = None, engine: str = 'baseline') -> dict:
    """Run all series; input/config errors raise, individual series failures do not."""
    if engine not in ('baseline', 'full', 'smoothing', 'arima', 'intermittent', 'multiseasonal', 'foundation', 'global'):
        raise ValueError("engine must be 'baseline', 'full', 'smoothing', 'arima', 'intermittent', 'multiseasonal', 'foundation' or 'global'")
    if isinstance(horizon, bool) or not isinstance(horizon, int) or not 1 <= horizon <= 10000:
        raise ValueError('horizon must be an integer from 1 to 10000')
    if isinstance(workers, bool) or not isinstance(workers, int) or not 1 <= workers <= 64:
        raise ValueError('workers must be an integer from 1 to 64')
    offset = pd.tseries.frequencies.to_offset(frequency)
    if offset.n <= 0:
        raise ValueError('frequency must advance time')
    cutoff = pd.to_datetime(as_of, utc=True) if as_of is not None else None
    if cutoff is not None and pd.isna(cutoff):
        raise ValueError('invalid as-of cutoff')
    start = time.perf_counter()
    source = pd.read_csv(input_path, dtype=str, keep_default_na=False)
    required = {'series_id', 'timestamp', 'target'}
    if not required.issubset(source.columns):
        raise ValueError(f'input must contain columns {sorted(required)}')
    output = Path(output)
    checkpoint_dir = output/'checkpoints'
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    code_hash = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    engine_hash = hashlib.sha256((Path(__file__).parent/'engine.py').read_bytes()).hexdigest() if engine != 'baseline' else None
    config = dict(horizon=horizon, frequency=offset.freqstr, engine=engine,
                  as_of=cutoff.isoformat() if cutoff is not None else None,
                  numpy=np.__version__, pandas=pd.__version__, code_hash=code_hash, engine_hash=engine_hash)
    tasks = []
    for series_id, group in source.groupby('series_id', sort=True, dropna=False):
        if cutoff is not None:
            timestamps = pd.to_datetime(group.timestamp, errors='coerce', utc=True, format='mixed')
            # Invalid dates remain, so they cannot disappear silently at the cutoff.
            group = group[timestamps.isna() | (timestamps <= cutoff)]
        rows = sorted(group[['timestamp', 'target']].values.tolist())
        key = hashlib.sha256(json.dumps([series_id, rows, config], sort_keys=True).encode()).hexdigest()
        tasks.append((str(series_id), rows, key))

    def worker(task):
        series_id, rows, key = task
        checkpoint = checkpoint_dir/f'{key}.json'
        if resume and checkpoint.exists():
            try:
                cached = json.loads(checkpoint.read_text())
                result_hash = hashlib.sha256(json.dumps(cached['result'], sort_keys=True,
                                                        allow_nan=False).encode()).hexdigest()
                if (cached['key'] == key and cached['result']['series_id'] == series_id
                        and cached['result_hash'] == result_hash):
                    return cached['result'], True
            except (OSError, ValueError, KeyError, TypeError):
                pass  # A damaged checkpoint is recomputed, not trusted.
        result = _one(series_id, rows, config)
        result_hash = hashlib.sha256(json.dumps(result, sort_keys=True, allow_nan=False).encode()).hexdigest()
        _write_json(checkpoint, {'key': key, 'config': config, 'result': result,
                                'result_hash': result_hash})
        return result, False

    # Executor limits active workers; batches also bound the queued task count.
    results, reused = [], 0
    if engine == 'global':
        results = _global(tasks, config)                      # one model for every series: no per-series checkpoints
    else:
      with ThreadPoolExecutor(max_workers=workers) as pool:
          for start_at in range(0, len(tasks), workers*2):
            for result, cached in pool.map(worker, tasks[start_at:start_at+workers*2]):
                results.append(result)
                reused += int(cached)
    forecasts = [row for result in results for row in result['forecasts']]
    pd.DataFrame(forecasts, columns=FORECAST_COLUMNS).to_csv(output/'forecast.csv', index=False)
    metrics = pd.DataFrame([result['metrics'] for result in results])
    if metrics.empty:
        metrics = pd.DataFrame(columns=['series_id', 'status', 'error'])
    metrics.to_csv(output/'metrics.csv', index=False)
    failures = [result['metrics'] for result in results if result['status'] != 'ok']
    _write_json(output/'failures.json', {'failures': failures})
    summary = dict(series=len(results), successful=len(results)-len(failures), failed=len(failures),
                   resumed=reused, computed=len(results)-reused,
                   elapsed_seconds=time.perf_counter()-start, config=config,
                   workers=workers, input=str(Path(input_path).resolve()))
    _write_json(output/'run.json', summary)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--horizon', type=int, default=12)
    parser.add_argument('--frequency', default='MS')
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--resume', action='store_true')
    parser.add_argument('--as-of')
    parser.add_argument('--engine', default='baseline', choices=['baseline', 'full', 'smoothing', 'arima', 'intermittent', 'multiseasonal', 'foundation', 'global'],
                        help='baseline: transparent baselines for thousands of series; full: the real engine per series; global: one LightGBM across all series')
    args = parser.parse_args()
    print(json.dumps(run_batch(args.input, args.output, args.horizon, args.frequency,
                               args.workers, args.resume, args.as_of, args.engine), indent=2))


if __name__ == '__main__':
    main()
