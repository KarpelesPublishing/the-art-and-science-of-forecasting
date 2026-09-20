"""Cycle 1 tools: hierarchy (18), conformal intervals (17), covariate panel (13), Prophet calendar (16)."""
from pathlib import Path
import sys
import warnings

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
warnings.filterwarnings('ignore')
from forecasting_companion.applied.methods import analyze  # noqa: E402
from forecasting_companion.applied.tools_hierarchy import build_S, reconcile  # noqa: E402
from forecasting_companion.applied.tools_probabilistic import conformal_radius  # noqa: E402


def monthly(n, start='2010-01-01'):
    return pd.Series(pd.date_range(start, periods=n, freq='MS'))


# ---------------------------------------------------------------- 18
def test_build_S_orders_aggregates_first_and_leaves_last():
    S, nodes, leaves = build_S([['A', 'Total'], ['B', 'Total'], ['A1', 'A'], ['A2', 'A']])
    assert nodes == ['Total', 'A', 'A1', 'A2', 'B'] and leaves == ['A1', 'A2', 'B']
    assert np.allclose(S[-3:], np.eye(3))
    assert list(S[0]) == [1, 1, 1] and list(S[1]) == [1, 1, 0]
    with pytest.raises(ValueError, match='two parents'):
        build_S([['A', 'T'], ['A', 'U']])


def test_reconcile_helper_ols_and_mint():
    S = np.array([[1, 1], [1, 0], [0, 1]], float)
    rec, _ = reconcile(S, [210, 90, 105])
    assert np.allclose(rec, [205, 95, 110])
    mint, _ = reconcile(S, [210, 90, 105], W=np.eye(3))
    assert np.allclose(mint, rec)


def test_hierarchy_tool_is_coherent_and_scores_holdout():
    rng = np.random.default_rng(18); n = 144; t = np.arange(n)
    a = 100 + 0.3 * t + 15 * np.sin(2 * np.pi * t / 12) + rng.normal(0, 3, n)
    b = 60 + 0.1 * t + 8 * np.cos(2 * np.pi * t / 12) + rng.normal(0, 2, n)
    ts = monthly(n)
    frame = pd.concat([pd.DataFrame({'node': k, 'timestamp': ts.dt.strftime('%Y-%m-%d'), 'target': v}) for k, v in (('Total', a + b), ('A', a), ('B', b))])
    table, s = analyze(18, frame, {'horizon': 12, 'season': 12, 'edges': [['A', 'Total'], ['B', 'Total']], 'pool': 'baseline', 'origins': 3})
    assert s['status'] == 'passed' and s['nodes'] == ['Total', 'A', 'B'] and 'MinT' in table
    piv = table.pivot(index='timestamp', columns='node', values='MinT')
    assert np.allclose(piv['Total'], piv['A'] + piv['B'], atol=1e-8)
    bu = table.pivot(index='timestamp', columns='node', values='bottom_up'); base = table.pivot(index='timestamp', columns='node', values='base')
    assert np.allclose(bu['A'], base['A']) and np.allclose(bu['B'], base['B'])
    assert set(s['holdout']) >= {'base', 'bottom_up', 'OLS', 'MinT'} and s['leaderboard'][0] in s['holdout']
    with pytest.raises(ValueError, match='Complete'):
        analyze(18, frame[frame.node != 'B'], {'horizon': 12, 'season': 12, 'edges': [['A', 'Total'], ['B', 'Total']]})
    with pytest.raises(ValueError, match='coherent'):
        bad = frame.copy(); bad.loc[bad.node == 'Total', 'target'] += 50
        analyze(18, bad, {'horizon': 12, 'season': 12, 'edges': [['A', 'Total'], ['B', 'Total']]})


def test_legacy_hierarchy_path_still_works():
    f = pd.DataFrame({'node': ['Total', 'A', 'B'], 'forecast': [210, 90, 105]})
    table, s = analyze(18, f, {'nodes': ['Total', 'A', 'B'], 'S': [[1, 1], [1, 0], [0, 1]]})
    assert np.allclose(table.OLS, [205, 95, 110])


# ---------------------------------------------------------------- 17
def test_conformal_radius_rank():
    r = np.arange(1, 81, dtype=float)
    radius, rank = conformal_radius(r, 0.1)
    assert rank == 73 and radius == 73.0


def test_conformal_tool_on_ar1_matches_hand_rank():
    rng = np.random.default_rng(17); n = 300; y = np.zeros(n)
    for t in range(1, n):
        y[t] = 0.7 * y[t - 1] + rng.normal()
    y += 50
    frame = pd.DataFrame({'timestamp': monthly(n).dt.strftime('%Y-%m-%d'), 'target': y})
    table, s = analyze(17, frame, {'horizon': 1, 'season': 1, 'alpha': 0.1, 'pool': 'baseline', 'transform': 'none', 'calibration_size': 80, 'test_size': 40, 'origins': 2})
    assert s['selected'] in ('Naive', 'Drift')
    # recompute the calibration residuals of the selected atomic model by hand and check the rank rule
    T2 = n - 40; T1 = T2 - 80
    resid = []
    for t in range(T1, T2):
        pred = y[t - 1] if s['selected'] == 'Naive' else y[t - 1] + (y[t - 1] - y[0]) / (t - 1)
        resid.append(abs(y[t] - pred))
    assert s['calibration_rows'][1] == 80
    assert s['radius'][1] == pytest.approx(float(np.sort(resid)[72]))
    assert 0.8 <= s['coverage']['split'] <= 0.98
    assert len(table) == 40 and (table.split_lower <= table.split_upper).all()
    assert 'adaptive' in s['coverage'] and s['interval_score']['split'] > 0


def test_supplied_intervals_path_unchanged():
    f = pd.DataFrame({'timestamp': monthly(30).dt.strftime('%Y-%m-%d'), 'actual': np.linspace(1, 30, 30), 'lower': np.linspace(0, 29, 30), 'median': np.linspace(1, 30, 30), 'upper': np.linspace(2, 31, 30)})
    _, s = analyze(17, f, {'alpha': 0.2})
    assert s['coverage'] == 1.0


# ---------------------------------------------------------------- 13
def panel_with_promo(n_series=6, days=200, seed=13):
    rng = np.random.default_rng(seed); rows = []
    dates = pd.date_range('2023-01-01', periods=days, freq='D')
    for k in range(n_series):
        promo = rng.binomial(1, 0.2, days).astype(float)
        base = 20 + 3 * k + 4 * np.sin(2 * np.pi * np.arange(days) / 7)
        y = base + 10 * promo + rng.normal(0, 1, days)
        rows.append(pd.DataFrame({'series_id': f's{k}', 'timestamp': dates.strftime('%Y-%m-%d'), 'target': y, 'promo': promo, 'price': 5 + rng.normal(0, .1, days)}))
    return pd.concat(rows, ignore_index=True)


def test_retail_ml_covariates_help_and_holdout_is_isolated():
    frame = panel_with_promo()
    cfg = {'horizon': 7, 'season': 7, 'covariates': ['promo', 'price'], 'known_in_advance': ['promo', 'price'], 'origins': 2}
    table, s = analyze(13, frame, cfg)
    assert s['strategy'] == 'direct' and s['test_mae'] < s['baseline_mae']
    assert s['ablation']['covariates']['delta_vs_full'] > 0
    assert set(table.columns) == {'series_id', 'timestamp', 'horizon', 'actual', 'seasonal_naive', 'prediction'}
    corrupted = frame.copy(); last = corrupted.timestamp >= sorted(corrupted.timestamp.unique())[-7]
    corrupted.loc[last, 'target'] += 1e6
    _, s2 = analyze(13, corrupted, cfg)
    assert s2['validation'] == s['validation']
    _, s3 = analyze(13, frame, dict(cfg, strategy='recursive', ablation=False))
    assert s3['strategy'] == 'recursive' and 'Ablation skipped by config' in s3['not_done']
    with pytest.raises(ValueError, match='subset'):
        analyze(13, frame, dict(cfg, known_in_advance=['weather']))


# ---------------------------------------------------------------- 16
def test_prophet_calendar_events_and_future_regressors():
    rng = np.random.default_rng(16); n = 400
    dates = pd.date_range('2022-01-01', periods=n, freq='D')
    t = np.arange(n); y = 100 + 0.05 * t + 5 * np.sin(2 * np.pi * t / 7) + rng.normal(0, 2, n)
    event_days = list(range(9, n, 10))
    for d in event_days:
        y[d] += 22
    events = [{'name': 'promo', 'date': str(dates[d].date())} for d in event_days] + [{'name': 'promo', 'date': str((dates[-1] + pd.Timedelta(days=30)).date())}]
    frame = pd.DataFrame({'timestamp': dates.strftime('%Y-%m-%d'), 'target': y})
    table, s = analyze(16, frame, {'horizon': 14, 'season': 7, 'events': events, 'weekly': True, 'yearly': False, 'priors': [0.05, 0.5], 'origins': 2})
    assert s['ablation']['without_events'] > s['ablation']['full']
    assert s['table_scope'] == 'future' and len(table) == 14 and s['mode'] in ('additive', 'multiplicative')
    # regressor path: without future rows the table falls back to the holdout and says so
    frame['temp'] = 20 + 5 * np.sin(2 * np.pi * t / 30)
    frame['target'] = y + 2 * frame.temp
    _, s2 = analyze(16, frame, {'horizon': 14, 'season': 7, 'regressors': ['temp'], 'weekly': True, 'yearly': False, 'priors': [0.05], 'origins': 1})
    assert s2['table_scope'] == 'holdout' and any('Future forecast skipped' in x for x in s2['not_done'])
    future = pd.DataFrame({'timestamp': pd.date_range(dates[-1] + pd.Timedelta(days=1), periods=14, freq='D').strftime('%Y-%m-%d'), 'target': [''] * 14, 'temp': 22.0})
    table3, s3 = analyze(16, pd.concat([frame, future], ignore_index=True), {'horizon': 14, 'season': 7, 'regressors': ['temp'], 'weekly': True, 'yearly': False, 'priors': [0.05], 'origins': 1})
    assert s3['table_scope'] == 'future' and len(table3) == 14
