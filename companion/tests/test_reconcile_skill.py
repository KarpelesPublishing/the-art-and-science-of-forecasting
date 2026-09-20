"""The reconcile-tdbu skill and the companion port must agree: one model, two entry points."""
from pathlib import Path
import importlib.util
import json
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT.parent / "forecasting-skills" / "reconcile-tdbu"
sys.path.insert(0, str(ROOT / "src"))
from forecasting_companion import reconcile_sim as rs  # noqa: E402

spec = importlib.util.spec_from_file_location("reconcile_model", SKILL / "scripts" / "reconcile_model.py")
rm = importlib.util.module_from_spec(spec)
sys.modules["reconcile_model"] = rm  # dataclasses with postponed annotations need the module registered
spec.loader.exec_module(rm)


def test_skill_files_present_and_clean():
    for rel in ["SKILL.md", "references/interview-guide.md", "references/model-map.md", "scripts/reconcile_model.py"]:
        assert (SKILL / rel).exists(), rel
    text = "\n".join((SKILL / rel).read_text() for rel in ["SKILL.md", "references/model-map.md", "scripts/reconcile_model.py"])
    for banned in ["Ipsos", "Reconcile_Latest", "Dashboard!", "Options!", ".xlsx"]:
        assert banned not in text, banned
    assert "illustrative starting value" in text


def test_skill_matches_companion_port_on_reference_case():
    a = rs.run()
    b = rm.run(rm.Inputs())
    assert b.bottom_up.tr_build == pytest.approx(a.bottom_up.total_units_mm, rel=1e-9)
    assert b.top_down.share_build == pytest.approx(a.top_down.total_units_mm, rel=1e-9)
    assert b.top_down.penetration == pytest.approx(a.top_down.solved_penetration, rel=1e-9)
    assert b.gap == pytest.approx(a.gap, rel=1e-9)
    assert b.implied_purchases_year == pytest.approx(a.implied_frequency, rel=1e-9)
    assert b.implied_market_size == pytest.approx(a.implied_market_size, rel=1e-9)
    assert b.derived["trial_probability"] == pytest.approx(a.resolved.trial)
    assert b.derived["awareness"] == pytest.approx(a.resolved.awareness, rel=1e-9)
    assert b.forecast_value_mm == pytest.approx(a.dollars_mm[0], rel=1e-9)
    # share is units over unit volume in both, not dollars over volume
    assert b.volume_share < 0.02 and a.volume_share[0] < 0.02


def test_skill_matches_port_off_reference():
    a = rs.run(hard=rs.HardInputs(distribution=0.55, category_penetration=0.45),
               opt=rs.Options(build_speed="Somewhat Slow", detector=rs.TrialDetector(brands_in_evoked_set=6)),
               ov=rs.Overrides(share_of_choice=0.20))
    b = rm.run(rm.Inputs(distribution=0.55, penetration=0.45, build_speed="somewhat slow",
                         trial_inputs=rm.TrialInputs(brands_evoked_set=6), overrides=rm.Overrides(share_of_choice=0.20)))
    assert b.bottom_up.tr_build == pytest.approx(a.bottom_up.total_units_mm, rel=1e-9)
    assert b.top_down.share_build == pytest.approx(a.top_down.total_units_mm, rel=1e-9)


def test_skill_reconciles_like_the_port():
    sol = rm.reconcile(rm.Inputs())
    hist = rs.iterate()
    assert sol.converged
    assert sol.final.forecast_units_mm == pytest.approx(hist[-1][1].units_mm[0], rel=1e-6)
    assert sol.final_inputs.category_purchases_year == pytest.approx(12.0, abs=1e-3)


def test_skill_cli_selftest_and_validation(tmp_path):
    out = subprocess.run([sys.executable, str(SKILL / "scripts" / "reconcile_model.py"), "--selftest"], capture_output=True, text=True)
    assert out.returncode == 0 and "Reference case reproduced" in out.stdout
    bad = tmp_path / "bad.json"; bad.write_text(json.dumps({"penetration": 53}))
    out = subprocess.run([sys.executable, str(SKILL / "scripts" / "reconcile_model.py"), "--inputs", str(bad)], capture_output=True, text=True)
    assert out.returncode != 0 and "fraction" in (out.stdout + out.stderr)
