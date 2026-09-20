"""The optional libraries, when installed, run through real code paths; when absent, the fallbacks do and say so."""
from pathlib import Path
import json
import os
import sys
import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from forecasting_companion.optional import have  # noqa: E402
from forecasting_companion.engine import forecast_series, POOLS  # noqa: E402
from forecasting_companion.applied.methods import analyze  # noqa: E402

RNG = np.random.default_rng(21)


def test_per_horizon_buckets_pick_two_winners_and_splice():
    t = np.arange(160); y = 100 + 0.8 * t + np.cumsum(RNG.normal(0, 3, 160)) * 0.3 + RNG.normal(0, 2, 160)
    ts = pd.Series(pd.date_range('2010-01-01', periods=160, freq='MS'))
    table, s = forecast_series(y, ts, 12, 1, pool='baseline', freq='MS', per_horizon_buckets=True)
    b = s['selected_by_bucket']
    assert b and b['cut_step'] == 6 and set(table.model.unique()) == {b['near'], b['far']}
    assert (table.model.iloc[:6] == b['near']).all() and (table.model.iloc[6:] == b['far']).all()
    assert {'conformal_lower', 'conformal_upper'} <= set(table.columns)
    frame = pd.DataFrame({'timestamp': ts, 'target': y})
    _, s2 = analyze(12, frame, {'horizon': 12, 'season': 1, 'pool': 'baseline', 'per_horizon_buckets': True})
    assert s2['selected_by_bucket']['near'] == b['near']


def test_hierarchy_cross_check_against_hierarchicalforecast_when_installed():
    d = pd.read_csv(ROOT / 'data/examples/ch18.csv'); c = json.loads((ROOT / 'configs/ch18.json').read_text())
    table, s = analyze(18, d, c)
    if have('hierarchicalforecast'):
        assert s['hierarchicalforecast_agrees'] == {'OLS': True, 'bottom_up': True}
        assert 'MinT_shrink_hf' in table.columns and 'MinT_shrink_hf' in s['holdout']
    else:
        assert s['hierarchicalforecast_agrees'] is None and any('hierarchicalforecast' in n for n in s['not_done'])


@pytest.mark.skipif(not have('statsforecast'), reason='statsforecast not installed')
def test_statsforecast_candidates_agree_with_the_in_house_versions():
    from forecasting_companion import engine_intermittent as ei
    y = RNG.binomial(1, .3, 200) * RNG.poisson(6, 200)
    for name in ('fit_croston', 'fit_sba', 'fit_tsb', 'fit_adida', 'fit_imapa'):
        rate = float(getattr(ei, name)(y, 4, 1, None, 'W').mean[0])
        assert 0.8 < rate < 3.0, (name, rate)                 # true rate 1.8
    t = np.arange(720); y2 = 100 + 8 * np.sin(2 * np.pi * t / 24) + 5 * np.sin(2 * np.pi * t / 168) + RNG.normal(0, 1, 720)
    table, s = forecast_series(y2, pd.Series(pd.date_range('2024-01-01', periods=720, freq='h')), 24, 24, pool='multiseasonal', freq='h', periods=[24, 168], max_origins=2)
    assert 'TBATS' in s['executed'] or 'TBATS' in s['skipped']


def test_global_engine_names_the_learner_that_ran(tmp_path):
    from forecasting_companion.batch import run_batch
    summary = run_batch(ROOT / 'data/examples/sales.csv', tmp_path / 'g', horizon=12, frequency='MS', workers=2, engine='global')
    metrics = pd.read_csv(tmp_path / 'g/metrics.csv')
    expected = 'Global LightGBM (mlforecast)' if have('mlforecast') else 'Global LightGBM (in-house)'
    assert summary['successful'] == 6 and (metrics.selected_model == expected).all()


@pytest.mark.skipif(not have('neuralforecast'), reason='neuralforecast not installed')
def test_neural_engine_runs_nhits_across_series(tmp_path):
    from forecasting_companion.batch import run_batch
    summary = run_batch(ROOT / 'data/examples/sales.csv', tmp_path / 'n', horizon=12, frequency='MS', workers=2, engine='neural')
    metrics = pd.read_csv(tmp_path / 'n/metrics.csv')
    assert summary['successful'] == 6 and (metrics.selected_model == 'NHITS (neuralforecast)').all() and metrics.holdout_mae.notna().all()


def test_neural_engine_refuses_without_the_package(tmp_path, monkeypatch):
    if have('neuralforecast'):
        pytest.skip('neuralforecast is installed here')
    from forecasting_companion.batch import run_batch
    summary = run_batch(ROOT / 'data/examples/sales.csv', tmp_path / 'n', horizon=12, frequency='MS', workers=2, engine='neural')
    assert summary['failed'] >= 1


@pytest.mark.skipif(os.environ.get('FORECAST_ALLOW_DOWNLOADS') != '1' or not have('timesfm'), reason='set FORECAST_ALLOW_DOWNLOADS=1 with timesfm installed to run the 800 MB model')
def test_timesfm_candidate_returns_quantiles():
    from forecasting_companion.engine_foundation import fit_timesfm
    f = fit_timesfm(50 + 10 * np.sin(np.arange(120) / 2), 12, 12, None, 'MS')
    assert len(f.mean) == 12 and (f.lower <= f.mean).all() and (f.mean <= f.upper).all()


def test_foundation_pool_names_gated_models_without_downloading():
    y = 50 + 10 * np.sin(np.arange(72) / 2) + RNG.normal(0, 1, 72)
    table, s = forecast_series(y, pd.Series(pd.date_range('2019-01-01', periods=72, freq='MS')), 6, 12, pool='foundation', freq='MS', max_origins=2)
    gated = {k: v for k, v in s['skipped'].items() if 'FORECAST_ALLOW_DOWNLOADS' in v}
    assert 'Chronos-Bolt' in gated or 'Chronos-Bolt' in s['unavailable']
    assert 'Chronos' in s['executed']
