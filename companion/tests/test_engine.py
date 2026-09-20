"""The engine must do what the book teaches, on the book's own example, without peeking."""
from pathlib import Path
import sys
import warnings

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
warnings.filterwarnings('ignore')
from forecasting_companion.engine import forecast_series, POOLS, choose_log, choose_differencing  # noqa: E402
from forecasting_companion.applied.methods import analyze  # noqa: E402
from forecasting_companion.batch import run_batch  # noqa: E402

AIR = [112,118,132,129,121,135,148,148,136,119,104,118,115,126,141,135,125,149,170,170,158,133,114,140,145,150,178,163,172,178,199,199,184,162,146,166,171,180,193,181,183,218,230,242,209,191,172,194,196,196,236,235,229,243,264,272,237,211,180,201,204,188,235,227,234,264,302,293,259,229,203,229,242,233,267,269,270,315,364,347,312,274,237,278,284,277,317,313,318,374,413,405,355,306,271,306,315,301,356,348,355,422,465,467,404,347,305,336,340,318,362,348,363,435,491,505,404,359,310,337,360,342,406,396,420,472,548,559,463,407,362,405,417,391,419,461,472,535,622,606,508,461,390,432]


def airline():
    ts = pd.Series(pd.to_datetime([f'{1949 + i // 12}-{i % 12 + 1:02d}-01' for i in range(144)], utc=True))
    return np.asarray(AIR, float), ts


def test_airline_selects_a_seasonal_model_with_log_transform_and_beats_seasonal_naive():
    y, ts = airline()
    table, s = forecast_series(y, ts, 12, 12, pool='full', freq='MS')
    assert s['transform'] == 'log'                                  # Box-Cox lambda about 0.13
    assert s['selected'] in {'Airline ARIMA', 'ARIMA(auto)', 'ETS(auto)', 'STL+ETS', 'Theta', 'Combination(top3)'}
    board = {r['model']: r for r in s['leaderboard']}
    assert board[s['selected']]['mae'] < 0.6 * board['Seasonal naive']['mae']
    assert s['test_mae'][s['selected']] < 0.5 * s['test_mae']['Seasonal naive']
    assert len(table) == 12 and np.isfinite(table.forecast).all()
    assert (table.empirical_q10 <= table.empirical_q50).all() and (table.empirical_q50 <= table.empirical_q90).all()
    assert 'lower' in table and (table.lower < table.forecast).all() and (table.upper > table.forecast).all()
    assert 0.6 <= board[s['selected']]['interval_coverage'] <= 1.0


def test_chapter_pools_are_distinct_and_the_arima_pool_can_fit_the_airline_model():
    y, ts = airline()
    _, arima = forecast_series(y, ts, 12, 12, pool='arima', freq='MS')
    assert 'Airline ARIMA' in arima['executed'] and arima['specification']['arima'] is not None
    _, smoothing = forecast_series(y, ts, 12, 12, pool='smoothing', freq='MS')
    assert smoothing['specification']['ets']['seasonal'] in ('add', 'mul')
    assert set(POOLS['smoothing']) != set(POOLS['arima'])


def test_specification_and_selection_use_only_history_before_the_holdout():
    y, ts = airline()
    _, before = forecast_series(y, ts, 12, 12, pool='full', freq='MS')
    y2 = y.copy(); y2[-12:] += 10000                                  # corrupt only the final holdout
    _, after = forecast_series(y2, ts, 12, 12, pool='full', freq='MS')
    assert before['selected'] == after['selected']
    assert before['specification'] == after['specification']
    assert before['leaderboard'] == after['leaderboard']
    assert after['test_mae'][after['selected']] > 5000                # the holdout score, and only it, changed


def test_diagnostics_on_training_data():
    y, _ = airline()
    log, note = choose_log(y[:72]); assert log and note['boxcox_lambda'] < 0.35
    d, D, note = choose_differencing(np.log(y[:96]), 12); assert D == 1 and d in (0, 1)
    log2, _ = choose_log(np.r_[y[:30], -1.0]); assert not log2       # nonpositive data never gets a log


def test_adapters_route_to_the_engine_and_keep_their_contract():
    y, ts = airline()
    frame = pd.DataFrame({'timestamp': ts.dt.strftime('%Y-%m-%d'), 'target': y})
    for chapter, expected_pool in ((4, 'smoothing'), (6, 'arima'), (12, 'full')):
        table, s = analyze(chapter, frame, {'horizon': 12, 'season': 12})
        assert s['pool'] == expected_pool and s['status'] == 'passed'
        assert {'selected', 'validation', 'test_mae', 'intervals', 'interpretation'} <= set(s)
        assert len(table) == 12
    _, forced = analyze(4, frame, {'horizon': 12, 'season': 12, 'transform': 'none', 'pool': 'baseline'})
    assert forced['transform'] == 'none' and forced['selected'] in POOLS['baseline']
    with pytest.raises(ValueError, match='Unsupported config'):
        analyze(4, frame, {'horizon': 12, 'season': 12, 'engine': 'full'})


def test_short_history_stays_provisional():
    y, ts = airline()
    frame = pd.DataFrame({'timestamp': ts.dt.strftime('%Y-%m-%d'), 'target': y}).iloc[:30]
    table, s = analyze(4, frame, {'horizon': 6, 'season': 12})
    assert s['status'] == 'provisional' and not s['validation'] and len(table) == 6


def test_batch_full_engine_records_models_and_bands(tmp_path):
    y, ts = airline()
    rows = []
    for k, scale in enumerate([1.0, 2.0, 0.5]):
        for t, v in zip(ts, y):
            rows.append(dict(series_id=f's{k}', timestamp=t.strftime('%Y-%m-%d'), target=v * scale))
    source = tmp_path / 'panel.csv'; pd.DataFrame(rows).to_csv(source, index=False)
    summary = run_batch(source, tmp_path / 'out', horizon=12, frequency='MS', workers=2, engine='smoothing')
    assert summary['successful'] == 3 and summary['config']['engine'] == 'smoothing'
    metrics = pd.read_csv(tmp_path / 'out' / 'metrics.csv')
    assert set(metrics.selected_model) <= set(POOLS['smoothing'])
    assert (metrics['transform'] == 'log').all() and metrics.holdout_mae.notna().all()
    forecast = pd.read_csv(tmp_path / 'out' / 'forecast.csv')
    assert {'empirical_signed_residual_by_horizon', 'model_interval_80'} <= set(forecast.band_method)
    assert run_batch(source, tmp_path / 'out', horizon=12, frequency='MS', workers=2, engine='smoothing', resume=True)['resumed'] == 3
    with pytest.raises(ValueError, match='engine'):
        run_batch(source, tmp_path / 'out2', engine='magic')
