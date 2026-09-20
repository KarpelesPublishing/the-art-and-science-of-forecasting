"""The port follows the original sheet structure exactly; rounded constants keep results within a percent or two."""
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from forecasting_companion import reconcile_sim as rs  # noqa: E402


def test_structural_values_unchanged_by_rounding():
    """Cells that use no rounded constant must still match the original sheet exactly."""
    d = rs.run()
    r = d.resolved
    assert r.adjusted_frequency == pytest.approx(7.33333, abs=1e-5)  # Dashboard!F3
    assert r.model_frequency == pytest.approx(4.66667, abs=1e-5)     # Dashboard!S24
    assert r.first_repeat_rate == pytest.approx(0.50426, abs=1e-5)   # T25
    assert r.units_at_trial == pytest.approx(1.215)                  # T26
    assert (r.soc_low, r.soc_high) == pytest.approx((25.32049, 41.19526), abs=1e-4)
    assert r.share_of_choice == 0.25                                 # E27 override
    assert d.bottom_up.solved_market_size_mm == pytest.approx(417.35027, abs=1e-4)  # T&R!H30
    assert d.implied_frequency == pytest.approx(11.92116, abs=1e-4)                  # E3
    assert d.implied_market_size == pytest.approx(655.83613, abs=1e-4)               # E9


def test_regression_with_rounded_constants():
    d = rs.run()
    r = d.resolved
    assert r.trial == pytest.approx(0.233)
    assert r.trial_index == pytest.approx(35.94, abs=0.01)
    assert r.awareness_media == pytest.approx(0.1888, abs=5e-4)
    assert r.awareness == pytest.approx(0.2478, abs=5e-4)
    assert r.repeats_per_repeater == pytest.approx(1.542, abs=1e-3)
    assert r.triers_first_year == pytest.approx(0.926, abs=1e-3)
    assert d.bottom_up.total_units_mm == pytest.approx(3.5454, abs=1e-3)
    assert d.top_down.total_units_mm == pytest.approx(3.5255, abs=1e-3)
    assert d.top_down.solved_penetration == pytest.approx(0.527, abs=1e-3)
    assert d.gap == pytest.approx(0.0056, abs=2e-4)


def test_close_to_original_sheet():
    """Rounded constants move the answer by about one percent, not more."""
    d = rs.run()
    sheet = dict(trial=0.236, awareness=0.24719, bottom_up=3.58712, top_down=3.56692,
                 dollars=14.31263, penetration=0.52702)
    assert abs(d.resolved.trial / sheet["trial"] - 1) < 0.02
    assert abs(d.resolved.awareness / sheet["awareness"] - 1) < 0.01
    assert abs(d.bottom_up.total_units_mm / sheet["bottom_up"] - 1) < 0.02
    assert abs(d.top_down.total_units_mm / sheet["top_down"] - 1) < 0.02
    assert abs(d.dollars_mm[0] / sheet["dollars"] - 1) < 0.02
    assert abs(d.top_down.solved_penetration - sheet["penetration"]) < 0.001


def test_units_and_shares_are_distinct():
    d = rs.run()
    units, dollars = d.units_mm[0], d.dollars_mm[0]
    assert dollars == pytest.approx(units * 3.99)
    # The stored G12 is dollars over unit volume; the clean volume share is much smaller.
    assert d.mixed_unit_share[0] == pytest.approx(dollars / 415)
    assert d.volume_share[0] == pytest.approx(units / 415)
    assert d.mixed_unit_share[0] / d.volume_share[0] == pytest.approx(3.99)


def test_loop_converges_in_two_passes_to_observed_frequency():
    hist = rs.iterate()
    assert len(hist) <= 4
    last_inputs, last = hist[-1]
    assert last.gap < 1e-6
    # implied claimed frequency lands at 12; adjusted (12-1)/3+1 equals the observed 4.6667 in S23
    assert last_inputs.category_purchases_per_year == pytest.approx(12.0, abs=1e-3)
    assert last.resolved.adjusted_frequency == pytest.approx(rs.Options().external_frequency, abs=1e-3)
    assert last.implied_market_size == pytest.approx(415.0, abs=0.5)
    assert last.units_mm[0] == pytest.approx(3.45, abs=0.01)
    assert last.dollars_mm[0] == pytest.approx(13.77, abs=0.01)


def test_overrides_and_toggles():
    # Overriding both build-speed outputs makes the peak irrelevant (Dashboard!A37 footnote)
    ov = rs.Overrides(repeats_per_repeater=1.5, triers_try_first_year=0.9)
    a = rs.run(opt=rs.Options(build_speed="Very Fast"), ov=ov)
    b = rs.run(opt=rs.Options(build_speed="Very Slow"), ov=ov)
    assert a.units_mm == pytest.approx(b.units_mm)
    # Supplying measured awareness and trial replaces the models
    opt = rs.Options(calculate_awareness=False, awareness_if_supplied=0.40,
                     calculate_trial=False, trial_if_supplied=0.30)
    d = rs.run(opt=opt)
    assert d.resolved.awareness == 0.40 and d.resolved.trial == 0.30
    with pytest.raises(ValueError):
        rs.run(opt=rs.Options(calculate_trial=False))


def test_penetration_cap_reported():
    # A tiny population forces the top-down solve past 100 percent
    d = rs.run(hard=rs.HardInputs(population_mm=5.0))
    assert d.top_down.penetration_capped and d.top_down.solved_penetration == 1.0


def test_evoked_set_dominates_detector():
    c = rs.TrialDetector().contributions()
    negatives = {k: v for k, v in c.items() if v < 0}
    assert abs(negatives["brands_in_evoked_set"]) >= 15
    # one more brand in the evoked set costs three index points
    d = rs.TrialDetector(brands_in_evoked_set=6)
    assert rs.TrialDetector().index() - d.index() == pytest.approx(3.0, abs=1e-9)
