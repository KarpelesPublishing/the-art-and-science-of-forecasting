"""Cycle 2 tools: MMM (20), causal (22), supply chain (21)."""
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
from forecasting_companion.applied.tools_mmm import ridge, saturate  # noqa: E402
from forecasting_companion.applied.tools_causal import synthetic_weights  # noqa: E402
from forecasting_companion.applied.tools_supply import echelons  # noqa: E402
from forecasting_companion.practitioner import adstock  # noqa: E402


def monthly(n):
    return pd.Series(pd.date_range('2010-01-01', periods=n, freq='MS'))


# ---------------------------------------------------------------- 20
def mmm_frame(n=144, seed=20):
    rng = np.random.default_rng(seed); t = np.arange(n)
    tv = rng.uniform(0,100, n); digital = rng.uniform(0, 80, n); radio = rng.uniform(0, 40, n); temp = rng.normal(0, 1, n)
    stv, sd, sr = adstock(tv, .5), adstock(digital, .5), adstock(radio, .5)
    sales = 100 + .1 * t + 8 * np.sin(2 * np.pi * t / 12) + 35 * stv / (80 + stv) + 20 * sd / (80 + sd) + 10 * sr / (40 + sr) + 3 * temp + rng.normal(0, 2, n)
    return pd.DataFrame({'timestamp': monthly(n).dt.strftime('%Y-%m-%d'), 'sales': sales, 'tv': tv, 'digital': digital, 'radio': radio, 'temp': temp})


def test_ridge_closed_form_matches_lstsq_at_zero_alpha():
    rng = np.random.default_rng(1); X = np.c_[np.ones(50), rng.normal(size=(50, 3))]; y = X @ [1, 2, -1, .5] + rng.normal(0, .1, 50)
    assert np.allclose(ridge(X, y, 0.0, np.array([False, True, True, True])), np.linalg.lstsq(X, y, rcond=None)[0])
    assert saturate(np.array([0., 80.]), 'hill', 80.).tolist() == [0.0, 0.5]


def test_mmm_selects_reasonable_decays_and_reports_curves():
    frame = mmm_frame()
    cfg = {'horizon': 12, 'season': 12, 'channels': ['tv', 'digital', 'radio'], 'controls': ['temp'], 'decay_grid': [0.0, 0.3, 0.5, 0.7, 0.9], 'saturation': 'auto', 'origins': 3, 'windows': 3}
    table, s = analyze(20, frame, cfg)
    assert s['status'] == 'passed' and set(s['channels']) == {'tv', 'digital', 'radio'}
    assert all(s['selected']['decays'][ch] in (0.3, 0.5, 0.7) for ch in s['channels'])
    assert all(s['marginal_roas'][ch] > 0 for ch in s['channels'])
    assert s['test_mae'] < s['baseline_mae'] and len(table) == 12
    assert len(s['refits']) == 3 and set(s['response_curves']) == set(s['channels'])
    assert s['reallocation']['predicted_response_change'] >= -1e-9
    _, s2 = analyze(20, frame, dict(cfg, prior_mean=[30, 20, 10], prior_sd=[10, 10, 10]))
    assert s2['posterior'] and set(s2['posterior']['mean']) == set(s['channels'])


def test_mmm_legacy_two_channel_example_still_runs():
    frame = pd.read_csv(ROOT / 'data/examples/ch20.csv')
    _, s = analyze(20, frame, {'horizon': 12, 'season': 12, 'decay_a': .5, 'decay_b': .5})
    assert s['channels'] == ['spend_a', 'spend_b'] and s['selected']['decays'] == {'spend_a': .5, 'spend_b': .5}


# ---------------------------------------------------------------- 22
def test_synthetic_control_recovers_weights_and_effect():
    rng = np.random.default_rng(22); n = 150; t = np.arange(n)
    c1 = 100 + .1 * t + rng.normal(0, 1, n); c2 = 80 + .05 * t + rng.normal(0, 1, n); c3 = 50 + rng.normal(0, 3, n)
    treated = .5 * c1 + .5 * c2 + 8 * (t >= 100) + rng.normal(0, .5, n)
    frame = pd.DataFrame({'timestamp': monthly(n).dt.strftime('%Y-%m-%d'), 'control': c1, 'c2': c2, 'c3': c3, 'treated': treated})
    table, s = analyze(22, frame, {'intervention': str(monthly(n)[100].date()), 'controls': ['control', 'c2', 'c3'], 'placebos': 50})
    w = s['sc_weights']
    assert abs(sum(w.values()) - 1) < 1e-6 and w['c3'] < .1
    assert abs(s['sc_post_mean_effect'] - 8) < 1
    assert s['placebo_space']['p_value'] == pytest.approx(1 / 4)      # treated beats all three donors
    assert s['placebo_time']['p_value'] < .1 and s['pretrend'] is not None
    assert 'sc_effect' in table and len(s['event_study']) > 0
    w2 = synthetic_weights(np.c_[c1[:100], c2[:100]], (.3 * c1 + .7 * c2)[:100])
    assert np.allclose(w2, [.3, .7], atol=.05)


def test_causal_single_control_skips_synthetic_control():
    frame = pd.read_csv(ROOT / 'data/examples/ch22.csv')
    _, s = analyze(22, frame, {'intervention': '2018-05-01'})
    assert s['sc_weights'] is None and any('Synthetic control skipped' in x for x in s['not_done'])


# ---------------------------------------------------------------- 21
def test_inventory_policy_constant_demand_never_backorders():
    n = 120; frame = pd.DataFrame({'timestamp': monthly(n).dt.strftime('%Y-%m-%d'), 'target': 5.0})
    table, s = analyze(21, frame, {'horizon': 12, 'season': 12, 'lead_time': 2, 'service_level': .9})
    assert s['fill_rate'] == 1.0 and table.backlog.max() == 0.0 and s['achieved_cycle_service'] == 1.0


def test_inventory_policy_poisson_demand_meets_service_and_bullwhip_shared_is_calmer():
    rng = np.random.default_rng(21); n = 200
    frame = pd.DataFrame({'timestamp': monthly(n).dt.strftime('%Y-%m-%d'), 'target': rng.poisson(5, n).astype(float)})
    _, s = analyze(21, frame, {'horizon': 12, 'season': 12, 'lead_time': 2, 'service_level': .95, 'echelons': 3})
    assert s['achieved_cycle_service'] >= .85 and 0 < s['fill_rate'] <= 1
    demand = 100 + rng.normal(0, 5, 400); demand[200:] += 20
    _, local = echelons(demand, 3, 3, shared=False); _, shared = echelons(demand, 3, 3, shared=True)
    assert local[-1] >= local[0] and shared[-1] <= local[-1]
    with pytest.raises(ValueError, match='finite'):
        analyze(21, frame, {'overage_cost': float('inf')})
