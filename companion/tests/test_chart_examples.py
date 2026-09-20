import os
from pathlib import Path
import runpy
import sys
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))

def test_fermi_chart_matches_piano_tuner_example(tmp_path, monkeypatch):
    monkeypatch.setenv('FORECAST_OUTPUT', str(tmp_path))
    result = runpy.run_path(str(ROOT/'lessons/10-superforecasting.py'))
    assert 'tuner_base' in result, 'Chart still uses unrelated equal-bar product example'
    assert np.isclose(result['tuner_base'], 110)
    scenarios = result['tuner_scenarios']
    np.testing.assert_allclose(scenarios['Piano ownership (5–15%)'], [55,165])
    np.testing.assert_allclose(scenarios['Hours per tuner (1,200–1,800)'], [110*1500/1800,110*1500/1200])
