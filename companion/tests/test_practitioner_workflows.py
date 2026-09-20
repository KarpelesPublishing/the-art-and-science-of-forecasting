import importlib
import importlib.util
from pathlib import Path
import sys

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))


def workflow():
    assert importlib.util.find_spec('forecasting_companion.practitioner') is not None, 'Missing executable practitioner workflows'
    return importlib.import_module('forecasting_companion.practitioner')


def test_gamma_horizon_and_speed():
    m = workflow()
    standard = m.launch_trials(1000, peak=4, horizon=24, denominator='horizon')
    assert sum(standard[:12]) == pytest.approx(800)
    assert sum(standard) == pytest.approx(1000)
    assert sum(m.launch_trials(1000, peak=3, horizon=24, denominator='horizon')[:12]) > 800
    assert sum(m.launch_trials(1000, peak=5, horizon=24, denominator='horizon')[:12]) < 800
    eventual = m.launch_trials(1000, peak=4, horizon=24, denominator='eventual')
    assert sum(eventual[:12]) == pytest.approx(800)
    assert sum(eventual) < 1000


def test_awareness_distribution_are_the_only_delays():
    m = workflow()
    assert m.trials_from_reach(100, [0,.5,1], [0,.4,1]).tolist() == pytest.approx([20,80])
    with pytest.raises(ValueError): m.trials_from_reach(100,[0,.5,.4],[0,.5,1])
    with pytest.raises(ValueError): m.launch_trials(100,denominator='unknown')
    with pytest.raises(ValueError): m.launch_trials(-1,denominator='horizon')
    with pytest.raises(ValueError): m.launch_trials(100,horizon=12,denominator='horizon')


def test_repeat_cohorts_do_not_become_trial_counts():
    m = workflow()
    assert m.cohort_units([10,20,0], [1,.5,.25]).tolist() == pytest.approx([10,25,12.5])
    with pytest.raises(ValueError): m.cohort_units([10,-1],[1])


def test_shared_calibration_and_fixed_prediction():
    m = workflow()
    exposure = np.array([100.,200.,300.])
    factor = m.calibrate_scale(exposure, exposure*1.4)
    assert factor == pytest.approx(1.4)
    assert 400*factor == pytest.approx(560)
    with pytest.raises(ValueError): m.calibrate_scale([0,0],[1,2])


def test_research_age_is_explicit_not_silent_demand_decay():
    m = workflow()
    assert m.evidence_weight('2024-01-01','2026-01-01',half_life_months=12) == pytest.approx(.25, abs=.002)
    with pytest.raises(ValueError): m.evidence_weight('2027-01-01','2026-01-01',12)


def test_journal_scores_one_pre_cutoff_forecast_per_resolved_event():
    m = workflow()
    events = [dict(event_id='a', cutoff='2026-02-01T00:00:00+00:00', resolved_at='2026-03-01T00:00:00+00:00', outcome=1, baseline=.5),
              dict(event_id='b', cutoff='2026-02-01T00:00:00+00:00', resolved_at=None, outcome=None, baseline=.5)]
    revisions = [dict(event_id='a',timestamp='2026-01-01T00:00:00+00:00',probability=.6),
                 dict(event_id='a',timestamp='2026-01-15T00:00:00+00:00',probability=.8),
                 dict(event_id='a',timestamp='2026-03-02T00:00:00+00:00',probability=1),
                 dict(event_id='b',timestamp='2026-01-01T00:00:00+00:00',probability=.2)]
    scored = m.score_journal(events,revisions,as_of='2026-04-01T00:00:00+00:00')
    assert len(scored) == 1
    assert scored[0]['brier'] == pytest.approx(.04)
    assert scored[0]['baseline_brier'] == .25
    assert m.score_journal(events,revisions,as_of='2026-02-15T00:00:00+00:00') == []
    with pytest.raises(ValueError): m.score_journal(events,revisions+[revisions[0]],as_of='2026-04-01T00:00:00+00:00')


def test_conditional_gaussian_posterior_and_initial_stock():
    m = workflow()
    mean,cov = m.gaussian_update(np.eye(2),np.array([2.,4.]),np.zeros(2),1.,1.)
    assert mean == pytest.approx([1.,2.])
    assert np.diag(cov) == pytest.approx([.5,.5])
    assert m.adstock([0,0],.5,initial=8) == pytest.approx([4,2])


def test_launch_notebook_eventual_option(tmp_path, monkeypatch):
    source=Path(__file__).resolve().parents[1]/'lessons/27-directed-forecasting.py'
    monkeypatch.setenv('FORECAST_OUTPUT',str(tmp_path))
    code=source.read_text().replace("DENOMINATOR='horizon'", "DENOMINATOR='eventual'")
    exec(compile(code,str(source),'exec'),{'__name__':'__main__'})
