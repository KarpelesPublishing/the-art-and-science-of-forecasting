"""Aggregate scored runs into reports/harness/latest.md: uplift per persona and spread.

Run folders are named <persona>-<skill|plain>-<repeat>, for example novice-skill-1. The report
answers the plan's question: with the skill, do all personas pass the process checks, and is the
spread between personas and between repeats smaller than without it?
"""
from pathlib import Path
import json
import sys
import numpy as np

HERE = Path(__file__).resolve().parent


def main(runs_dir=HERE / 'runs'):
    runs = {}
    for p in sorted(Path(runs_dir).glob('*/score.json')):
        parts = p.parent.name.split('-')
        if len(parts) < 3:
            continue
        persona, arm = parts[0], parts[1]
        scored = {k: v for k, v in json.load(open(p)).items() if v.get('attempted', True)}   # a partial run counts only the tasks it attempted
        runs.setdefault((persona, arm), []).append(scored)
    if not runs:
        print('no scored runs'); return
    lines = ['# Harness: uplift and repeatability', '', f'{sum(len(v) for v in runs.values())} scored runs.', '',
             '| Persona | Arm | Runs | Process (mean) | Process (min) | MAE/baseline (mean over series tasks) | Band coverage (mean) | Delivered |', '|---|---|---|---|---|---|---|---|']
    stats = {}
    for (persona, arm), scored in sorted(runs.items()):
        proc = [np.mean([r['process_score'] for r in s.values() if 'process_score' in r]) for s in scored]
        mae = [np.mean([r['mae_vs_baseline'] for r in s.values() if r.get('mae_vs_baseline') is not None]) for s in scored]
        cov = [np.mean([r['band_coverage'] for r in s.values() if r.get('band_coverage') is not None]) for s in scored]
        cov = [c for c in cov if not np.isnan(c)]
        delivered = [np.mean([bool(r.get('delivered')) for r in s.values()]) for s in scored]
        stats[(persona, arm)] = dict(process=np.mean(proc), process_min=np.min(proc), mae=np.mean(mae) if mae else None, cov=np.mean(cov) if cov else None)
        lines.append(f'| {persona} | {arm} | {len(scored)} | {np.mean(proc):.0%} | {np.min(proc):.0%} | {("%.2f" % np.mean(mae)) if mae else ""} | {("%.0f%%" % (100 * np.mean(cov))) if cov else ""} | {np.mean(delivered):.0%} |')
    lines += ['', '## Spread', '']
    for arm in ('skill', 'plain'):
        rows = [v for (p, a), v in stats.items() if a == arm]
        if len(rows) >= 2:
            lines.append(f'- {arm}: process scores range {min(r["process"] for r in rows):.0%} to {max(r["process"] for r in rows):.0%} across personas; MAE/baseline range ' + (f'{min(r["mae"] for r in rows if r["mae"] is not None):.2f} to {max(r["mae"] for r in rows if r["mae"] is not None):.2f}' if any(r['mae'] is not None for r in rows) else 'n/a') + '.')
    lines += ['', 'Success means: with the skill every persona passes every process check, and the spread between personas is smaller than without the skill.']
    out = HERE.parent / 'reports/harness'; out.mkdir(parents=True, exist_ok=True)
    (out / 'latest.md').write_text('\n'.join(lines) + '\n'); print('\n'.join(lines))


if __name__ == '__main__':
    main(*(sys.argv[1:2] or []))
