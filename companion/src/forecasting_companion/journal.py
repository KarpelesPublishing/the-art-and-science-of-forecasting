"""Keep score. A forecast that is never scored teaches nothing.

The journal is a JSON-lines file. `add(run_dir)` records a run's forecast rows with the brief
and the scoring date; `score(actuals)` matches actuals by timestamp and writes accuracy,
bias, band coverage and interval score into the entry; `calibration()` reads the whole
history back as the reader's own track record: how often the bands held, which way the
errors lean, and how the errors grew with the horizon.
"""
from pathlib import Path
from datetime import datetime, timezone
import json
import hashlib
import numpy as np
import pandas as pd

DEFAULT = Path('applied-runs/journal/forecasts.jsonl')


def _rows(table, column=None):
    cols = set(table.columns)
    point = column if column in cols else next((c for c in ('forecast', 'prediction', 'median', 'nowcast', 'MinT', 'OLS', 'bottom_up') if c in cols), None)
    if point is None or 'timestamp' not in cols:
        return None, None
    pairs = [('break_scenario_low', 'break_scenario_high')] if point == 'break_scenario' else [('band_lower', 'band_upper'), ('conformal_lower', 'conformal_upper'), ('lower', 'upper'), ('scenario_low', 'scenario_high'), ('empirical_q10', 'empirical_q90'), ('q10', 'q90'), ('MinT_q10', 'MinT_q90')]
    lo, hi = next(((a, b) for a, b in pairs if a in cols and b in cols), (None, None))
    level = float(table['interval_level'].iloc[0]) if 'interval_level' in cols else (0.8 if lo else None)
    rows = []
    for k, r in table.iterrows():
        rows.append(dict(timestamp=str(pd.to_datetime(r['timestamp']).date()), step=len(rows) + 1, point=float(r[point]), lower=float(r[lo]) if lo else None, upper=float(r[hi]) if hi else None, node=str(r['node']) if 'node' in cols else None))
    if 'node' in cols:
        for i, row in enumerate(rows):
            row['step'] = 1 + sum(1 for q in rows[:i] if q['node'] == row['node'])
    return rows, level


def add(run_dir, journal=DEFAULT, note='', column=None):
    run_dir = Path(run_dir); journal = Path(journal)
    summary = json.loads((run_dir / 'summary.json').read_text())
    record = json.loads((run_dir / 'run.json').read_text()) if (run_dir / 'run.json').exists() else {}
    brief = json.loads((run_dir / 'brief.json').read_text()) if (run_dir / 'brief.json').exists() else None
    table = pd.read_csv(run_dir / 'results.csv') if (run_dir / 'results.csv').exists() else pd.DataFrame()
    rows, level = _rows(table, column)
    if not rows:
        raise ValueError('this run has no dated forecast column (forecast, prediction, median or nowcast); only series forecasts are journaled')
    if column:
        note = (note + ' ' if note else '') + f'journaled column: {column}'
    entry = dict(id=hashlib.sha256((str(run_dir.resolve()) + record.get('created_at', '')).encode()).hexdigest()[:12],
                 created_at=datetime.now(timezone.utc).isoformat(), run_dir=str(run_dir.resolve()), chapter=summary.get('chapter'),
                 target=(brief or {}).get('target') or summary.get('source'), units=summary.get('units'), decision=(brief or {}).get('decision'),
                 method=summary.get('method'), selected=summary.get('selected'), status=summary.get('status'),
                 outcome_due=(brief or {}).get('outcome_date') or record.get('outcome_due'), interval_level=level, note=note,
                 forecasts=rows, actuals=None, scores=None)
    journal.parent.mkdir(parents=True, exist_ok=True)
    with journal.open('a') as f:
        f.write(json.dumps(entry) + '\n')
    return entry


def load(journal=DEFAULT):
    journal = Path(journal)
    if not journal.exists():
        return []
    return [json.loads(line) for line in journal.read_text().splitlines() if line.strip()]


def save(entries, journal=DEFAULT):
    Path(journal).write_text(''.join(json.dumps(e) + '\n' for e in entries))


def score_entry(entry, actuals):
    """actuals: DataFrame with timestamp and actual. Scores only the periods that have an actual."""
    a = actuals.copy(); a['timestamp'] = pd.to_datetime(a['timestamp']).dt.strftime('%Y-%m-%d'); lookup = dict(zip(a['timestamp'], pd.to_numeric(a['actual'])))
    if 'node' in a.columns:
        lookup = {(str(n), t): v for n, t, v in zip(a['node'], a['timestamp'], pd.to_numeric(a['actual']))}
        matched = [dict(r, actual=float(lookup[(r['node'], r['timestamp'])])) for r in entry['forecasts'] if (r.get('node'), r['timestamp']) in lookup]
    else:
        matched = [dict(r, actual=float(lookup[r['timestamp']])) for r in entry['forecasts'] if r.get('node') is None and r['timestamp'] in lookup and np.isfinite(lookup[r['timestamp']])]
    if not matched:
        return None
    err = np.array([m['actual'] - m['point'] for m in matched]); act = np.array([m['actual'] for m in matched])
    scores = dict(scored_periods=len(matched), mae=float(np.mean(np.abs(err))), bias=float(np.mean(err)), mape=float(np.mean(np.abs(err) / np.abs(act))) if np.all(act != 0) else None,
                  total_forecast=float(sum(m['point'] for m in matched)), total_actual=float(act.sum()))
    if all(m['lower'] is not None for m in matched):
        lo = np.array([m['lower'] for m in matched]); hi = np.array([m['upper'] for m in matched]); level = entry.get('interval_level') or 0.8; alpha = 1 - level
        inside = (act >= lo) & (act <= hi)
        scores.update(band_coverage=float(inside.mean()), nominal_level=level, mean_width=float(np.mean(hi - lo)),
                      interval_score=float(np.mean((hi - lo) + 2 / alpha * np.maximum(lo - act, 0) + 2 / alpha * np.maximum(act - hi, 0))))
    scores['by_step'] = [dict(step=m['step'], error=m['actual'] - m['point'], inside=(m['lower'] is not None and m['lower'] <= m['actual'] <= m['upper'])) for m in matched]
    return matched, scores


def score(actuals_path, journal=DEFAULT, entry_id=None):
    actuals = pd.read_csv(actuals_path)
    if not {'timestamp', 'actual'} <= set(actuals.columns):
        raise ValueError('actuals need timestamp and actual columns')
    entries = load(journal); scored = []
    for e in entries:
        if entry_id and e['id'] != entry_id:
            continue
        result = score_entry(e, actuals)
        if result is None:
            continue
        matched, scores = result
        e['actuals'] = [dict(timestamp=m['timestamp'], actual=m['actual']) for m in matched]; e['scores'] = scores; e['scored_at'] = datetime.now(timezone.utc).isoformat()
        scored.append(e)
    save(entries, journal)
    return scored


def calibration(journal=DEFAULT):
    """The reader's track record across every scored forecast."""
    entries = [e for e in load(journal) if e.get('scores')]
    if not entries:
        return dict(scored=0, note='no scored forecasts yet; add actuals with `run.py journal score`'), 'No scored forecasts yet.'
    steps = {}; inside = []; bias = []; ratio = []
    for e in entries:
        s = e['scores']
        if s.get('band_coverage') is not None:
            inside.append(s['band_coverage'])
        bias.append(np.sign(s['bias']))
        if s.get('total_actual'):
            ratio.append(s['total_forecast'] / s['total_actual'])
        for b in s['by_step']:
            steps.setdefault(b['step'], []).append(abs(b['error']))
    nominal = [e.get('interval_level') or 0.8 for e in entries if e['scores'].get('band_coverage') is not None]
    out = dict(scored=len(entries), band_coverage=float(np.mean(inside)) if inside else None, nominal_level=float(np.mean(nominal)) if nominal else None,
               share_forecast_too_high=float(np.mean(np.array(bias) < 0)) if bias else None, median_forecast_to_actual_ratio=float(np.median(ratio)) if ratio else None,
               mae_by_step={int(k): float(np.mean(v)) for k, v in sorted(steps.items())})
    lines = [f'{out["scored"]} scored forecasts.']
    if len(entries) < 5:
        lines.append(f'Too few to judge calibration; {5 - len(entries)} more scored forecasts are needed before a coverage or bias verdict means anything.')
        out['verdict'] = 'insufficient'
        if out['mae_by_step']:
            lines.append('Mean absolute error by horizon step so far: ' + ', '.join(f'{k}: {v:.4g}' for k, v in out['mae_by_step'].items()) + '.')
        return out, '\n'.join(lines)
    if out['band_coverage'] is not None:
        verdict = 'about right' if abs(out['band_coverage'] - out['nominal_level']) <= 0.1 else ('too narrow: the bands miss more than they should' if out['band_coverage'] < out['nominal_level'] else 'too wide: the bands could be tighter')
        lines.append(f'Bands held {out["band_coverage"]:.0%} of the time against a nominal {out["nominal_level"]:.0%}: {verdict}.')
    if out['share_forecast_too_high'] is not None:
        lean = 'too high' if out['share_forecast_too_high'] > 0.6 else 'too low' if out['share_forecast_too_high'] < 0.4 else 'neither way'
        lines.append(f'Forecasts ran too high in {out["share_forecast_too_high"]:.0%} of cases: the lean is {lean}.' + (f' Median forecast/actual ratio {out["median_forecast_to_actual_ratio"]:.3f}.' if out['median_forecast_to_actual_ratio'] else ''))
    if out['mae_by_step']:
        lines.append('Mean absolute error by horizon step: ' + ', '.join(f'{k}: {v:.4g}' for k, v in out['mae_by_step'].items()) + '.')
    return out, '\n'.join(lines)
