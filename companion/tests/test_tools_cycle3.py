"""Cycle 3 tools: breaks (24), epidemics (23), state space (5), foundation (15), diffusion (19), markets (1)."""
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
from forecasting_companion.applied.tools_breaks import binary_segmentation  # noqa: E402
from forecasting_companion.applied.tools_epidemics import estimate_delay_law  # noqa: E402
from forecasting_companion.applied.tools_diffusion import parfitt_collins  # noqa: E402
from forecasting_companion.applied.tools_markets import benford  # noqa: E402


def monthly(n, start='2010-01-01'):
    return pd.date_range(start, periods=n, freq='MS').strftime('%Y-%m-%d')


def test_break_tool_dates_the_shift_and_adapts():
    rng = np.random.default_rng(24); n = 200
    y = np.where(np.arange(n) < 100, 50, 65) + rng.normal(0, 3, n)
    table, s = analyze(24, pd.DataFrame({'timestamp': monthly(n), 'target': y}), {'horizon': 12, 'season': 1, 'calibration_size': 40})
    assert s['status'] == 'passed' and {'method', 'assumptions', 'not_done'} <= set(s)
    assert any(abs(k - 100) <= 3 for k in s['changepoint_positions'])
    assert s['detection']['delay_periods'] is not None and 0 <= s['detection']['delay_periods'] < 10
    assert s['detection']['false_alarms_before'] == 0
    assert s['mae']['rolling'] < s['mae']['frozen'] and s['mae']['adaptive'] < s['mae']['frozen']
    assert not table.select_dtypes('number').isna().any().any()
    assert binary_segmentation(np.r_[np.zeros(50), np.ones(50) * 5], 8, 5) == [50]
    assert binary_segmentation(np.zeros(100) + rng.normal(0, 1, 100), 8, 5) == []
    # downward shift alarms too
    _, down = analyze(24, pd.DataFrame({'timestamp': monthly(n), 'target': -y}), {'horizon': 12, 'season': 1, 'calibration_size': 40})
    assert down['detection']['delay_periods'] is not None and down['detection']['delay_periods'] < 10


def epidemic_frame(delay, days=60, mean=100, seed=23):
    rng = np.random.default_rng(seed); rows = []; start = pd.Timestamp('2020-01-01')
    for i in range(days):
        counts = rng.multinomial(rng.poisson(mean), delay)
        for lag, count in enumerate(counts):
            rows.append(dict(event_date=start + pd.Timedelta(days=i), report_date=start + pd.Timedelta(days=i + lag), count=count))
    return pd.DataFrame(rows)


def test_nowcast_estimates_the_delay_law_and_bounds_incomplete_cohorts():
    delay = np.array([.2, .3, .25, .15, .1])
    d = epidemic_frame(delay)
    table, s = analyze(23, d, {'horizon': 7, 'season': 1, 'as_of': '2020-02-20', 'mature_age': 5, 'population': 1_000_000})
    assert s['status'] in ('passed', 'provisional')
    law = np.array(s['delay_law']['probabilities'][:5])
    assert np.abs(law - delay).max() < .05
    mature = table[table.age >= 5]
    assert np.allclose(mature.nowcast, mature.reported) and np.allclose(mature.completeness, 1)
    assert (table.lower <= table.nowcast + 1e-9).all() and (table.nowcast <= table.upper + 1e-9).all()
    young = table[table.age < 5]
    assert (young.nowcast >= young.reported).all() and (young.upper >= young.lower).all()
    assert (young[young.completeness < .99].upper > young[young.completeness < .99].lower).all()
    assert s['seir'] is not None and 'rmse' in str(s['seir'])
    assert not table.select_dtypes('number').isna().any().any()
    # supplied law still honoured
    _, given = analyze(23, d, {'horizon': 7, 'season': 1, 'as_of': '2020-02-20', 'delay_prob': delay.tolist()})
    assert given['delay_law']['source'] == 'supplied'
    assert 'population' in ' '.join(given['not_done']).lower()


def test_estimate_delay_law_direct():
    d = epidemic_frame(np.array([.5, .3, .2]), days=40)
    d['lag'] = (d.report_date - d.event_date).dt.days; d['age'] = (pd.Timestamp('2020-02-20') - d.event_date).dt.days
    probs, cohorts = estimate_delay_law(d, 3, 3)
    assert cohorts >= 10 and abs(probs[0] - .5) < .06 and abs(sum(probs) - 1) < 1e-9


def test_state_space_handles_missing_values():
    rng = np.random.default_rng(5); n = 200
    truth = np.cumsum(rng.normal(0, 1, n)); y = truth + rng.normal(0, 3, n)
    frame = pd.DataFrame({'timestamp': monthly(n), 'target': y}); frame.loc[rng.choice(n, 10, replace=False), 'target'] = np.nan
    frame['timestamp'] = frame.timestamp
    table, s = analyze(5, frame, {'horizon': 12, 'season': 12, 'model': 'local level', 'origins': 3})
    assert s['missing_count'] == 10 and len(s['missing_timestamps']) == 10
    assert 4 <= s['params']['sigma2.irregular'] <= 14
    filt = table[table.kind == 'filtered'].estimate.to_numpy(); smooth = table[table.kind == 'smoothed'].estimate.to_numpy()
    assert np.sqrt(np.mean((smooth - truth) ** 2)) < np.sqrt(np.mean((filt - truth) ** 2))
    assert (table.kind == 'forecast').sum() == 12 and not table.select_dtypes('number').isna().any().any()
    assert (table.lower <= table.estimate).all() and (table.estimate <= table.upper).all()
    _, manual = analyze(5, frame.assign(target=frame.target.interpolate()), {'horizon': 12, 'season': 12, 'model': 'local_level_manual'})
    assert manual['interpretation']
    with pytest.raises(ValueError, match='model must be'):
        analyze(5, frame, {'horizon': 12, 'season': 12, 'model': 'wobbly'})


@pytest.mark.slow
def test_foundation_origins_match_the_engine_and_bad_checkpoint_raises():
    rng = np.random.default_rng(15); n = 120; t = np.arange(n)
    y = 50 + 10 * np.sin(2 * np.pi * t / 12) + .1 * t + rng.normal(0, 1, n)
    frame = pd.DataFrame({'timestamp': monthly(n), 'target': y})
    table, s = analyze(15, frame, {'horizon': 12, 'season': 12, 'origins': 3, 'samples': 32})
    assert s['checkpoint'] == 'tiny' and s['revision'] and s['download_warning'] is None
    assert len(s['origins']) == 4 and s['per_origin'][-1]['holdout']
    assert set(s['engine_baselines']) >= {'Seasonal naive', 'Naive'}
    assert list(table.columns) == ['timestamp', 'forecast', 'q10', 'q50', 'q90'] and len(table) == 12
    assert (table.q10 <= table.q50).all() and (table.q50 <= table.q90).all()
    with pytest.raises(ValueError, match='checkpoint'):
        analyze(15, frame, {'horizon': 12, 'season': 12, 'checkpoint': 'huge'})


def test_diffusion_sales_timing_and_kernel():
    time = np.arange(1, 13); e = np.exp(-(.025 + .35) * time); adopt = 100000 * (1 - e) / (1 + .35 / .025 * e)
    d = pd.DataFrame({'time': time, 'adopters': adopt}); base = {'horizon': 12, 'season': 12, 'ceilings': [100000]}
    table, s = analyze(19, d, base)
    fit = s['fits'][0]
    assert abs(fit['p'] - .025) / .025 < .1 and abs(fit['q'] - .35) / .35 < .1
    assert np.allclose(table.bass_units, table.bass_trials) and np.allclose(table.gamma_units, table.gamma_trials)   # zero kernel
    assert abs(table.bass_trials.sum() - table.gamma_trials.sum()) < 1e-6
    assert s['timing_comparison'][0]['bass_peak_period'] != s['timing_comparison'][0]['gamma_peak_period']
    _, rep = analyze(19, d, {**base, 'repeat_kernel': [.3, .2, .1], 'fix_q': .4, 'parfitt_collins': {'T': .2, 'R': .4, 'B': 1.1}})
    assert rep['fits'][0]['q_fixed'] == .4 and rep['parfitt_collins']['share'] == pytest.approx(.088)
    assert rep['timing_comparison'][0]['bass_units_total'] > s['timing_comparison'][0]['bass_units_total']
    assert parfitt_collins(.5, .5)['share'] == .25
    with pytest.raises(ValueError, match='sales_horizon'):
        analyze(19, d, {**base, 'sales_horizon': 12})


def test_rule_backtest_is_honest_on_a_random_walk():
    rng = np.random.default_rng(1); n = 400
    close = 100 + np.cumsum(rng.normal(0, 1, n)); open_ = np.r_[100, close[:-1]]
    d = pd.DataFrame({'timestamp': pd.date_range('2015-01-01', periods=n, freq='D').strftime('%Y-%m-%d'), 'open': open_, 'close': close,
                      'high': np.maximum(open_, close) + 1, 'low': np.minimum(open_, close) - 1})
    table, s = analyze(1, d, {'horizon': 1, 'season': 1})
    assert abs(s['hit_rate']['momentum'] - .5) < .1 and abs(s['hit_rate']['mean_reversion'] - .5) < .1
    assert s['mae']['persistence'] <= min(s['mae']['momentum'], s['mae']['mean_reversion']) * 1.05
    assert {'momentum_hit', 'mean_reversion_hit', 'actual_direction'} <= set(table.columns)
    assert benford(rng.integers(100, 1000, 2000))['p_value'] < .001
    assert benford(rng.lognormal(0, 3, 2000))['p_value'] > .01
    with pytest.raises(ValueError, match='rules'):
        analyze(1, d, {'horizon': 1, 'season': 1, 'rules': ['oracle']})


def test_crowds_extremization_is_scored_and_guarded():
    rng = np.random.default_rng(11); rows = []
    for q in range(40):
        truth = rng.uniform(); outcome = int(rng.uniform() < truth)
        for e in range(5):
            rows.append(dict(question=q, expert=e, estimate=float(np.clip(.5 + .5 * (truth - .5) + rng.normal(0, .05), 0, 1)), actual=outcome))
    table, s = analyze(11, pd.DataFrame(rows), {'horizon': 1, 'season': 1, 'extremize_a': 2.5})
    assert 'extremized' in table and set(s['brier']) == {'mean', 'median', 'trimmed', 'extremized'}
    assert ((table.extremized - .5).abs() >= (table['mean'] - .5).abs() - 1e-12).all()
    with pytest.raises(ValueError, match='probability'):
        analyze(11, pd.DataFrame(rows).assign(estimate=lambda f: f.estimate * 100), {'horizon': 1, 'season': 1, 'extremize_a': 2.5})
