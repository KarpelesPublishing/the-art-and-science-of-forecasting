"""The engine's coverage: intermittent, multiseasonal, regressors, gaps, robustness and conformal bands."""
from pathlib import Path
import sys
import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from forecasting_companion.engine import forecast_series, POOLS, CANDIDATES, score_origins, conformal_band  # noqa: E402
from forecasting_companion.engine_intermittent import croston_family  # noqa: E402
from forecasting_companion.engine_regressors import validate_regressors  # noqa: E402
from forecasting_companion.applied.methods import analyze  # noqa: E402
from forecasting_companion.optional import have, describe_extras  # noqa: E402

RNG = np.random.default_rng(3)


def test_every_pool_names_registered_candidates():
    for pool, names in POOLS.items():
        for n in names:
            assert n in CANDIDATES or n in ('Combination(top3)', 'Equal ensemble', 'Weighted ensemble'), (pool, n)
    assert isinstance(describe_extras(), dict) and have('numpy')


def test_intermittent_pool_scores_on_rmsse_and_recovers_the_rate():
    y = RNG.binomial(1, .3, 156) * RNG.poisson(6, 156); ts = pd.Series(pd.date_range('2023-01-02', periods=156, freq='W-MON'))
    table, s = forecast_series(y, ts, 13, 52, pool='intermittent', freq='W-MON')
    assert s['criterion'] == 'rmsse' and s['baseline'] == 'Mean' and (table.forecast >= 0).all()
    assert abs(table.forecast.iloc[0] - 1.8) < 0.6           # true demand rate 0.3 * 6
    assert all(r['rmsse'] is not None for r in s['leaderboard'])
    path, nxt = croston_family(np.array([0, 0, 4, 0, 0, 0, 6, 0]), 0.1, 'tsb')
    assert 0 < nxt < 6


def test_multiseasonal_pool_finds_both_cycles():
    t = np.arange(1095); y = 100 + 8 * np.sin(2 * np.pi * t / 7) + 20 * np.sin(2 * np.pi * t / 365.25) + RNG.normal(0, 2, 1095)
    ts = pd.Series(pd.date_range('2022-01-01', periods=1095, freq='D'))
    table, s = forecast_series(y, ts, 28, 7, pool='multiseasonal', freq='D', periods=[7, 365])
    board = {r['model']: r['mae'] for r in s['leaderboard']}
    assert s['selected'] in ('Fourier ARIMA', 'MSTL+ETS', 'MSTL+ARIMA', 'Prophet', 'Combination(top3)')
    assert board[s['selected']] < 0.5 * board['Seasonal naive']
    assert 'TBATS' in s['unavailable'] or have('statsforecast')


def test_regressors_pool_uses_known_future_drivers_without_leaking_selection():
    n = 200; promo = RNG.binomial(1, .2, n + 14)
    y = 50 + 5 * np.sin(2 * np.pi * np.arange(n) / 7) + 20 * promo[:n] + RNG.normal(0, 2, n)
    ts = pd.Series(pd.date_range('2025-01-01', periods=n, freq='D'))
    reg = {'X': promo[:n, None].astype(float), 'future': promo[n:, None].astype(float), 'columns': ['promo']}
    table, s = forecast_series(y, ts, 14, 7, pool='regressors', freq='D', regressors=reg)
    board = {r['model']: r['mae'] for r in s['leaderboard']}
    assert s['selected'] in ('ARIMAX', 'LightGBM+X', 'Prophet+X', 'Combination(top3)') and board[s['selected']] < board['Seasonal naive']
    other = dict(reg, future=1 - reg['future'])                     # different future drivers: the forecast moves, the leaderboard does not
    table2, s2 = forecast_series(y, ts, 14, 7, pool='regressors', freq='D', regressors=other)
    assert [(r['model'], r['mae']) for r in s2['leaderboard']] == [(r['model'], r['mae']) for r in s['leaderboard']] and not np.allclose(table.forecast, table2.forecast)
    hist = pd.DataFrame({'promo': promo[:n]})
    with pytest.raises(ValueError, match='exactly 14 rows'):
        validate_regressors(hist, pd.DataFrame({'timestamp': ts[:5], 'promo': promo[:5]}), ['promo'], 14)


def test_gaps_are_filled_for_fitting_but_never_scored():
    t = np.arange(144); frame = pd.DataFrame({'timestamp': pd.date_range('2012-01-01', periods=144, freq='MS'), 'target': 40 + .1 * t + 8 * np.sin(2 * np.pi * t / 12) + RNG.normal(0, 2, 144)})
    gappy = frame.drop(index=[50, 51, 130])                        # two gaps in training, one inside the holdout
    _, s = analyze(12, gappy, {'horizon': 12})
    assert s['gaps_filled'] == 3 and s['status'] == 'passed'
    assert all(len(r) for r in s['validation'])
    assert s['profile']['gaps']['action'] == 'interpolate'


def test_selection_rules_and_conformal_bands():
    scores = pd.DataFrame([dict(origin=1, model='A', mae=1.0, rmsse=2.0), dict(origin=2, model='A', mae=3.0, rmsse=1.0), dict(origin=1, model='B', mae=2.0, rmsse=1.0), dict(origin=2, model='B', mae=2.0, rmsse=1.0)])
    assert list(score_origins(scores, 'mae').index) == ['A', 'B'] or list(score_origins(scores, 'mae').index) == ['B', 'A']
    assert list(score_origins(scores, 'rmsse').index)[0] == 'B'
    band = conformal_band({1: [1, -2, 3, -4, 5], 2: [0.5, 0.5]}, 0.8)
    assert 0 < band[2] <= band[1] <= 5.0                          # pooled across steps, scaled by each step's (smoothed) error
    wide = conformal_band({s: list(RNG.normal(0, s, 20)) for s in range(1, 7)}, 0.8)
    assert wide[6] > wide[1] * 2                                  # later steps get wider bands
    t = np.arange(120); y = 40 + 8 * np.sin(2 * np.pi * t / 12) + RNG.normal(0, 2, 120)
    table, s = forecast_series(y, pd.Series(pd.date_range('2014-01-01', periods=120, freq='MS')), 12, 12, pool='smoothing', freq='MS')
    assert {'conformal_lower', 'conformal_upper'} <= set(table.columns) and (table.conformal_upper >= table.forecast).all()
    assert s['robustness'][s['selected']]['lost_to_baseline_at'] <= len(s['origins']) / 2 and s['conformal']


def test_batch_global_engine_runs_and_reports_the_baseline(tmp_path):
    from forecasting_companion.batch import run_batch
    summary = run_batch(ROOT / 'data/examples/sales.csv', tmp_path / 'out', horizon=12, frequency='MS', workers=2, engine='global')
    assert summary['successful'] == 6
    metrics = pd.read_csv(tmp_path / 'out/metrics.csv')
    assert (metrics.selected_model == 'Global LightGBM').all() and metrics.holdout_mae.notna().all()
    assert all('Seasonal naive' in c for c in metrics.candidate_mae)
