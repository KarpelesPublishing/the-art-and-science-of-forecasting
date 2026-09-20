"""Reports are rendered from run artifacts; the journal scores forecasts when actuals arrive."""
from pathlib import Path
import json
import sys
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from forecasting_companion.applied.core import run  # noqa: E402
from forecasting_companion.brief import Brief  # noqa: E402
from forecasting_companion.report import render, check_claims  # noqa: E402
from forecasting_companion import journal as J  # noqa: E402


def _run(tmp_path, name='out', horizon=6):
    t = np.arange(144)
    pd.DataFrame({'timestamp': pd.date_range('2015-01-01', periods=144, freq='MS'), 'target': 40 + .1 * t + 8 * np.sin(2 * np.pi * t / 12) + np.random.default_rng(5).normal(0, 2, 144)}).to_csv(tmp_path / 'y.csv', index=False)
    (tmp_path / 'c.json').write_text(json.dumps({'source': 'test', 'units': 'units', 'horizon': 12, 'season': 12}))
    Brief(target='units of sku 1', units='units', decision='order quantity', horizon=horizon, frequency='monthly', as_of='2026-12-01', outcome_date='2027-07-01').save(tmp_path / 'brief.json')
    run(4, tmp_path / 'y.csv', tmp_path / 'c.json', tmp_path / name, brief_path=tmp_path / 'brief.json')
    return tmp_path / name


def test_report_numbers_all_trace_to_claims(tmp_path):
    out = _run(tmp_path)
    text, claims = render(out)
    assert (out / 'report.md').exists() and (out / 'claims.json').exists()
    assert 'order quantity' in text and '## Not done' in text and '## Provenance' in text
    assert check_claims(text, claims) == []
    assert all({'label', 'value', 'source', 'key'} <= set(c) for c in claims) and any(c['source'] == 'results.csv' for c in claims)
    assert check_claims('The total is 9999 units and I would order 400.', claims) == ['9999', '400.']
    total = next(c['value'] for c in claims if c['label'] == 'forecast total')
    assert check_claims(f'The six months add up to about {total:.0f} units.', claims) == []


def test_report_without_brief_says_so(tmp_path):
    t = np.arange(144)
    pd.DataFrame({'timestamp': pd.date_range('2015-01-01', periods=144, freq='MS'), 'target': 40 + .1 * t + 8 * np.sin(2 * np.pi * t / 12)}).to_csv(tmp_path / 'y.csv', index=False)
    (tmp_path / 'c.json').write_text(json.dumps({'source': 'test', 'units': 'units', 'horizon': 12, 'season': 12}))
    run(4, tmp_path / 'y.csv', tmp_path / 'c.json', tmp_path / 'nb')
    text, _ = render(tmp_path / 'nb')
    assert 'No brief was attached' in text


def test_journal_add_score_and_calibration(tmp_path):
    out = _run(tmp_path); journal = tmp_path / 'j.jsonl'
    entry = J.add(out, journal)
    assert len(entry['forecasts']) == 6 and entry['outcome_due'] == '2027-07-01' and entry['decision'] == 'order quantity'
    assert J.load(journal)[0]['scores'] is None
    first = entry['forecasts'][0]
    actuals = pd.DataFrame({'timestamp': [r['timestamp'] for r in entry['forecasts'][:4]], 'actual': [r['point'] + 1 for r in entry['forecasts'][:4]]})
    actuals.to_csv(tmp_path / 'a.csv', index=False)
    scored = J.score(tmp_path / 'a.csv', journal)
    assert len(scored) == 1 and scored[0]['scores']['scored_periods'] == 4
    assert abs(scored[0]['scores']['mae'] - 1) < 1e-9 and abs(scored[0]['scores']['bias'] - 1) < 1e-9
    assert scored[0]['scores']['band_coverage'] == 1.0 and first['lower'] is not None
    out_stats, text = J.calibration(journal)
    assert out_stats['scored'] == 1 and out_stats['verdict'] == 'insufficient' and 'Too few' in text
    for k in range(4):                                   # five scored entries unlock a verdict
        J.add(out, journal, note=str(k))
    J.score(tmp_path / 'a.csv', journal)
    out_stats, text = J.calibration(journal)
    assert out_stats['scored'] == 5 and out_stats['band_coverage'] == 1.0 and 'too wide' in text and out_stats['mae_by_step'][1] > 0
