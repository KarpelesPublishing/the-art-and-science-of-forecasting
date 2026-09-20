"""The profile must read the data the way a forecaster would; the brief must refuse to let a number float free."""
from pathlib import Path
import json
import sys
import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from forecasting_companion.profile import profile_series, describe, classify_intermittency  # noqa: E402
from forecasting_companion.brief import Brief  # noqa: E402
from forecasting_companion.applied.methods import analyze  # noqa: E402
from forecasting_companion.applied.core import run  # noqa: E402

RNG = np.random.default_rng(11)


def monthly(n, **kw):
    t = np.arange(n)
    return pd.DataFrame({'timestamp': pd.date_range('2015-01-01', periods=n, freq='MS'), 'target': 40 + .1 * t + 8 * np.sin(2 * np.pi * t / 12) + RNG.normal(0, 2, n)})


def test_monthly_seasonal_series_is_read_correctly():
    p = profile_series(monthly(144), {'horizon': 12})
    assert p['frequency']['frequency'] == 'MS' and p['season'] == 12 and p['seasonality']['periods'] == [12]
    assert p['intermittency']['quadrant'] == 'smooth' and p['route'] == 'engine'
    assert p['trend']['direction'] == 'up' and p['outliers']['count'] == 0 and not p['break']['found']
    assert p['minimum_for_engine'] == 72 and 'Route: engine' in describe(p)


def test_planted_outlier_shift_and_gap_are_reported_not_edited():
    f = monthly(144); f.loc[70, 'target'] += 25
    assert profile_series(f, {'horizon': 12})['outliers']['positions'] == [70]
    g = monthly(144); g.loc[100:, 'target'] += 20
    b = profile_series(g, {'horizon': 12})['break']
    assert b['found'] and abs(b['position'] - 100) <= 2
    h = monthly(144).drop(index=[50, 51])
    p = profile_series(h, {'horizon': 12})
    assert p['gaps']['count'] == 2 and p['gaps']['action'] == 'interpolate' and p['route'] == 'engine'
    many = monthly(144).drop(index=list(range(40, 80)))
    assert profile_series(many, {'horizon': 12})['route'] == 'unusable'


def test_intermittent_demand_routes_to_croston_family():
    y = RNG.binomial(1, .3, 120) * RNG.poisson(6, 120)
    p = profile_series(pd.DataFrame({'timestamp': pd.date_range('2020-01-01', periods=120, freq='MS'), 'target': y}), {'horizon': 6})
    assert p['intermittency']['quadrant'] in ('intermittent', 'lumpy') and p['route'] == 'intermittent'
    assert p['outliers']['method'] == 'skipped'
    assert classify_intermittency(np.ones(50))['quadrant'] == 'smooth'


def test_daily_data_finds_weekly_and_yearly_cycles_without_echoes():
    t = np.arange(730)
    two = pd.DataFrame({'timestamp': pd.date_range('2023-01-01', periods=730, freq='D'), 'target': 100 + 8 * np.sin(2 * np.pi * t / 7) + 20 * np.sin(2 * np.pi * t / 365.25) + RNG.normal(0, 2, 730)})
    p = profile_series(two, {'horizon': 14})
    assert p['seasonality']['periods'] == [7, 365] and p['route'] == 'multiseasonal' and not p['break']['found']
    one = pd.DataFrame({'timestamp': pd.date_range('2023-01-01', periods=730, freq='D'), 'target': 100 + 8 * np.sin(2 * np.pi * t / 7) + RNG.normal(0, 2, 730)})
    assert profile_series(one, {'horizon': 14})['seasonality']['periods'] == [7]
    h = np.arange(24 * 30)
    hourly = pd.DataFrame({'timestamp': pd.date_range('2024-01-01', periods=len(h), freq='h'), 'target': 50 + 10 * np.sin(2 * np.pi * h / 24) + 5 * np.sin(2 * np.pi * h / 168) + RNG.normal(0, 1, len(h))})
    assert profile_series(hourly, {'horizon': 24})['seasonality']['periods'] == [24, 168]


def test_short_history_is_named_not_forced():
    p = profile_series(monthly(30), {'horizon': 12})
    assert p['route'] == 'too_short' and any('floor' in w for w in p['warnings'])
    p = profile_series(monthly(50), {'horizon': 6})
    assert p['route'] in ('short', 'engine')


def test_season_auto_flows_from_profile_into_the_engine():
    table, s = analyze(4, monthly(144), {'horizon': 12, 'season': 'auto'})
    assert s['status'] == 'passed' and s['season'] == 12 and s['profile']['route'] == 'engine'
    _, s = analyze(4, monthly(144), {'horizon': 12})          # no season declared: the profile supplies it
    assert s['season'] == 12 and s['profile']['seasonality']['periods'] == [12]


def test_brief_interview_validation_and_overrides(tmp_path):
    b = Brief()
    assert len(b.interview()) == 11 and b.validate()
    b = Brief(target='units of sku 1', units='units', decision='order quantity', horizon=6, frequency='monthly', as_of='2025-12-01', outcome_date='2026-07-01')
    assert [k for k, _ in b.interview()] == ['cost_of_over', 'cost_of_under', 'known_in_advance', 'audience']
    assert b.validate() == [] and b.config_overrides() == {'horizon': 6, 'frequency': 'MS', 'as_of': '2025-12-01', 'units': 'units', 'outcome_due': '2026-07-01'}
    path = b.save(tmp_path / 'brief.json'); assert Brief.load(path).horizon == 6
    bad = Brief(target='x', units='u', decision='d', horizon=3, frequency='weekly', as_of='soon', outcome_date='2026-01-01')
    assert any('ISO date' in p for p in bad.validate())


def test_run_records_the_brief_and_the_profile(tmp_path):
    monthly(144).to_csv(tmp_path / 'y.csv', index=False)
    (tmp_path / 'c.json').write_text(json.dumps({'source': 'test', 'units': 'units', 'horizon': 12, 'season': 12}))
    Brief(target='units', units='units', decision='order', horizon=6, frequency='monthly', as_of='2026-12-01', outcome_date='2027-07-01').save(tmp_path / 'brief.json')
    s = run(4, tmp_path / 'y.csv', tmp_path / 'c.json', tmp_path / 'out', brief_path=tmp_path / 'brief.json')
    assert s['horizon'] == 6 and s['brief']['decision'] == 'order'
    assert (tmp_path / 'out/brief.json').exists() and (tmp_path / 'out/profile.json').exists()
    assert json.loads((tmp_path / 'out/run.json').read_text())['config']['outcome_due'] == '2027-07-01'
    Brief(target='units').save(tmp_path / 'bad.json')
    with pytest.raises(ValueError, match='Brief is not usable'):
        run(4, tmp_path / 'y.csv', tmp_path / 'c.json', tmp_path / 'out2', brief_path=tmp_path / 'bad.json')
