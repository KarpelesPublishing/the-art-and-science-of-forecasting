"""The public companion (no manuscript beside it) must run the documented commands."""
from pathlib import Path
import json
import shutil
import subprocess
import sys

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import provenance          # noqa: E402
import catalog             # noqa: E402
import export_public       # noqa: E402


def _tree_without_manuscript(tmp_path):
    root = tmp_path / 'project' / 'companion'
    for folder in ('lessons', 'configs'):
        shutil.copytree(ROOT / folder, root / folder)
    shutil.copytree(ROOT / 'src', root / 'src', ignore=shutil.ignore_patterns('__pycache__'))
    (root / 'data').mkdir(); shutil.copy2(ROOT / 'data/registry.json', root / 'data/registry.json')
    (root / 'assets').mkdir(); shutil.copy2(ROOT / 'assets/returning-aircraft-schematic.png', root / 'assets/returning-aircraft-schematic.png')
    return root


def test_provenance_tolerates_a_missing_manuscript(tmp_path):
    root = _tree_without_manuscript(tmp_path)
    lesson = root / 'lessons/04-smoothing.py'
    assert provenance.manuscript_for(lesson, root) is None
    current = provenance.inputs(lesson, root)
    assert not any(k.startswith('manuscript/') for k in current['files'])
    recorded = {'files': {'manuscript/04-the-smoother.md': 'abc', **current['files']}, 'versions': current['versions']}
    assert provenance.same_inputs(recorded, current), 'a record made beside the book must stay current without it'
    assert not provenance.same_inputs({'files': {**current['files'], 'companion/src/x.py': '0'}, 'versions': current['versions']}, current)


def test_catalog_titles_without_the_book():
    lesson = ROOT / 'lessons/04-smoothing.py'
    assert catalog.lesson_title(lesson, 4).startswith('Chapter 4')


def test_export_strips_manuscript_records(tmp_path):
    companion = tmp_path / 'companion'; (companion / 'results').mkdir(parents=True)
    shutil.copy2(ROOT / 'manifest.json', companion / 'manifest.json')
    shutil.copy2(ROOT / 'results/ch04-execution.json', companion / 'results/ch04-execution.json')
    export_public.strip_manuscript_records(companion)
    for path in (companion / 'manifest.json', companion / 'results/ch04-execution.json'):
        text = path.read_text()
        assert 'manuscript/' not in text and 'source_sha256' not in text


def test_run_help_lists_every_command():
    out = subprocess.run([sys.executable, str(ROOT / 'scripts/run.py'), '--help'], capture_output=True, text=True)
    assert out.returncode == 0
    for word in ('chapters', 'apply', 'forecast'):
        assert word in out.stdout
    out = subprocess.run([sys.executable, str(ROOT / 'scripts/run.py'), 'forecast', '--help'], capture_output=True, text=True)
    assert '--engine' in out.stdout


def test_batch_example_runs_as_documented(tmp_path):
    out = subprocess.run([sys.executable, str(ROOT / 'scripts/run.py'), 'forecast', '--input', str(ROOT / 'data/examples/sales.csv'),
                          '--output', str(tmp_path / 'sales'), '--horizon', '12', '--frequency', 'MS', '--workers', '2'], capture_output=True, text=True)
    assert out.returncode == 0, out.stderr[-500:]
    metrics = pd.read_csv(tmp_path / 'sales/metrics.csv')
    assert len(metrics) == 6 and (metrics.status == 'ok').all()


def test_notebook_is_written_only_after_execution(tmp_path, monkeypatch):
    import author
    lesson = ROOT / 'lessons/09-expert-scoring.py'
    nb = author.build(lesson, write=False)
    assert nb.cells and not (tmp_path / 'notebooks').exists()


def test_workflow_commands_exist_and_walkthrough_file_ships():
    out = subprocess.run([sys.executable, str(ROOT / 'scripts/run.py'), '--help'], capture_output=True, text=True)
    for word in ('brief', 'profile', 'report', 'journal'):
        assert word in out.stdout
    assert (ROOT / 'data/examples/first-forecast.csv').exists()
    assert (ROOT.parent / 'forecasting-skills/forecast-workflow/SKILL.md').exists()
    assert (ROOT / 'harness/score.py').exists() and (ROOT / 'harness/tasks/A-hierarchy/task.md').exists()
