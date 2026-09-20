"""Score one assistant run of the harness: accuracy, calibration, coherence and, above all, process.

Usage: python harness/score.py runs/<label>          (a folder with one subfolder per task)
Writes runs/<label>/score.json and prints a table. The process checks are what "repeatable" means:
a brief with a decision and a scoring date, a data profile, a stated baseline, a not-done list,
a journal entry, and no number in the report that the run's claims do not support.
"""
from pathlib import Path
import json
import re
import sys
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'src'))
TASKS = HERE / 'tasks'
TRUTH = HERE / 'truth'


def _read_forecast(path, date_col='timestamp'):
    f = pd.read_csv(path)
    f[date_col] = pd.to_datetime(f[date_col], utc=True, errors='coerce').dt.tz_localize(None).dt.normalize()
    return f


def _band_checks(m):
    out = {}
    if {'lower', 'upper'} <= set(m.columns) and m.lower.notna().all():
        out['band_coverage'] = float(((m.target >= m.lower) & (m.target <= m.upper)).mean())
        out['band_mean_width'] = float((m.upper - m.lower).mean())
    return out


def _seasonal_naive_mae(history, truth, season):
    hist = history.sort_values('timestamp').target.to_numpy(); tr = truth.sort_values('timestamp').target.to_numpy()
    base = np.resize(hist[-season:], len(tr)) if len(hist) >= season else np.repeat(hist[-1], len(tr))
    return float(np.mean(np.abs(base - tr)))


def score_series(task, run, season, date_col='timestamp'):
    truth = _read_forecast(TRUTH / f'{task}.csv'); hist = _read_forecast(TASKS / task / 'data.csv')
    fc = run / 'forecast.csv'
    if not fc.exists():
        return dict(delivered=False)
    f = _read_forecast(fc)
    m = f.merge(truth, on=date_col, suffixes=('', '_true')) if 'node' not in truth.columns else f.merge(truth, on=['node', date_col], suffixes=('', '_true'))
    if 'forecast' not in m.columns or len(m) == 0:
        return dict(delivered=True, matched=0)
    out = dict(delivered=True, matched=int(len(m)), mae=float((m.forecast - m.target).abs().mean()), bias=float((m.forecast - m.target).mean()))
    if 'node' in truth.columns:
        out['baseline_mae'] = float(np.mean([_seasonal_naive_mae(hist[hist.node == n], truth[truth.node == n], season) for n in truth.node.unique()]))
        piv = f.pivot_table(index=date_col, columns='node', values='forecast')
        leaves = [c for c in piv.columns if c != 'Total']
        out['coherence_max_gap'] = float((piv['Total'] - piv[leaves].sum(axis=1)).abs().max()) if 'Total' in piv else None
    else:
        out['baseline_mae'] = _seasonal_naive_mae(hist, truth, season)
    out['mae_vs_baseline'] = out['mae'] / out['baseline_mae'] if out['baseline_mae'] else None
    out['total_error_pct'] = float((m.forecast.sum() - m.target.sum()) / m.target.sum()) if m.target.sum() else None
    out.update(_band_checks(m))
    return out


def score_events(run):
    truth = pd.read_csv(TRUTH / 'E-event-probability.csv'); base = json.load(open(TASKS / 'E-event-probability/base_rate.json'))['base_rate']
    p = run / 'probabilities.csv'
    if not p.exists():
        return dict(delivered=False)
    f = pd.read_csv(p).merge(truth, on='event_id')
    if len(f) == 0:
        return dict(delivered=True, matched=0)
    brier = float(np.mean((f.probability - f.outcome) ** 2)); base_brier = float(np.mean((base - f.outcome) ** 2))
    return dict(delivered=True, matched=int(len(f)), brier=brier, baseline_brier=base_brier, skill_vs_base_rate=1 - brier / base_brier if base_brier else None,
                extreme_share=float(np.mean((f.probability < 0.05) | (f.probability > 0.95))))


def score_intermittent(run):
    out = score_series('C-intermittent', run, season=52)
    rep = run / 'report.md'
    if rep.exists():
        m = re.search(r'order[- ]up[- ]to(?: level)?[ :=*]*\**\s*(?:S\s*=\s*)?(\d{1,3})\b(?![-/])', rep.read_text(), flags=re.I)
        if m:
            S = int(m.group(1)); d = _read_forecast(TRUTH / 'C-intermittent.csv').target.to_numpy()
            windows = [d[i:i + 3].sum() for i in range(len(d) - 2)]     # two-week lead plus one-week review
            out.update(order_up_to=S, three_week_windows_covered=float(np.mean([w <= S for w in windows])))
    return out


def process_checks(run, task):
    """The repeatable-process checks. Each is a plain yes/no with the evidence looked for."""
    text = ''
    for p in run.rglob('*.md'):
        text += p.read_text() + '\n'
    briefs = list(run.rglob('brief.json')); profiles = list(run.rglob('profile.json')); summaries = list(run.rglob('summary.json'))
    claims = list(run.rglob('claims.json')); journals = list(run.rglob('*.jsonl')) + list(run.rglob('journal*'))
    checks = {
        'brief_with_decision_and_scoring_date': any({'decision', 'outcome_date'} <= set(json.load(open(b))) and json.load(open(b))['decision'] and json.load(open(b))['outcome_date'] for b in briefs),
        'data_profiled_before_modelling': bool(profiles) or task in ('B-launch', 'E-event-probability'),
        'baseline_stated': bool(re.search(r'seasonal[- ]naive|base rate|baseline|naive', text, re.I)),
        'not_done_reported': bool(re.search(r'not done|not_done|did not|was not|were not|does not', text, re.I)) and (bool(summaries) or task in ('B-launch', 'E-event-probability')),
        'uncertainty_labelled': bool(re.search(r'coverage|scenario|interval|range', text, re.I)) or (task == 'E-event-probability' and bool(re.search(r'probabilit', text, re.I))),
        'scoring_date_stated': bool(re.search(r'scor(e|ing) (date|on)|outcome (date|due)|will be known', text, re.I)),
        'journal_entry_made': bool(journals),
        'report_numbers_sourced': bool(claims),
    }
    if claims:
        from forecasting_companion.report import check_claims
        allc = [c for p in claims for c in json.load(open(p))]
        if task == 'E-event-probability' and (run / 'probabilities.csv').exists():
            # a judgment task: the delivered probabilities and the base rate are the evidence the interpretation may cite
            probs = pd.read_csv(run / 'probabilities.csv')
            allc += [dict(label=f'p {r.event_id}', value=float(r.probability), source='probabilities.csv', key=str(r.event_id)) for r in probs.itertuples()]
            base = json.load(open(TASKS / 'E-event-probability/base_rate.json'))
            allc += [dict(label='base rate', value=float(base['base_rate']), source='base_rate.json', key='base_rate'), dict(label='cases', value=float(base['cases']), source='base_rate.json', key='cases'), dict(label='threshold', value=0.4, source='task.md', key='threshold')]
        interp = [p for p in run.rglob('interpretation*.md')]
        if interp:
            bad = check_claims(interp[0].read_text(), allc)
            checks['interpretation_numbers_supported'] = not bad
    checks['status_honest'] = True
    if task == 'F-short-history':
        checks['status_honest'] = bool(re.search(r'provisional|cannot (be )?validated|not enough|too short|insufficient', text, re.I))
    if task == 'G-level-shift':
        checks['status_honest'] = bool(re.search(r'shift|break|change|closed|new level|regime', text, re.I))
    return checks


def score_run(run_root):
    run_root = Path(run_root); results = {}
    for task in sorted(p.name for p in TASKS.iterdir() if p.is_dir()):
        run = run_root / task
        if not run.exists():
            results[task] = dict(delivered=False, attempted=False, process={}); continue
        if task == 'A-hierarchy':
            r = score_series(task, run, season=12)
        elif task == 'C-intermittent':
            r = score_intermittent(run)
        elif task == 'D-daily-multiseasonal':
            r = score_series(task, run, season=7)
        elif task == 'E-event-probability':
            r = score_events(run)
        elif task in ('F-short-history', 'G-level-shift'):
            r = score_series(task, run, season=12)
        else:
            r = dict(delivered=(run / 'report.md').exists())
        r['process'] = process_checks(run, task)
        r['process_score'] = float(np.mean(list(r['process'].values()))) if r['process'] else 0.0
        results[task] = r
    (run_root / 'score.json').write_text(json.dumps(results, indent=2, default=float) + '\n')
    return results


def table(results):
    lines = ['| Task | Delivered | MAE / baseline | Band coverage | Other | Process |', '|---|---|---|---|---|---|']
    for task, r in results.items():
        other = []
        if r.get('coherence_max_gap') is not None: other.append(f'coherence gap {r["coherence_max_gap"]:.3g}')
        if r.get('skill_vs_base_rate') is not None: other.append(f'Brier skill {r["skill_vs_base_rate"]:+.0%}')
        if r.get('three_week_windows_covered') is not None: other.append(f'S={r["order_up_to"]} covers {r["three_week_windows_covered"]:.0%}')
        if r.get('total_error_pct') is not None: other.append(f'total {r["total_error_pct"]:+.0%}')
        failed = [k for k, v in r.get('process', {}).items() if not v]
        lines.append(f'| {task} | {"yes" if r.get("delivered") else "no"} | {("%.2f" % r["mae_vs_baseline"]) if r.get("mae_vs_baseline") is not None else ""} | {("%.0f%%" % (100 * r["band_coverage"])) if r.get("band_coverage") is not None else ""} | {"; ".join(other)} | {r.get("process_score", 0):.0%}' + (f' (missing: {", ".join(failed)})' if failed else '') + ' |')
    return '\n'.join(lines)


if __name__ == '__main__':
    res = score_run(sys.argv[1]); print(table(res))
