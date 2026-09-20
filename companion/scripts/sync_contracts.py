"""Keep every skill's output contract equal to what the tool actually returns.

For each chapter the shipped example is run through `analyze`, and the `results.csv` columns
and `summary.json` keys are written into the chapter skill (section "Applied report contract")
and its workshop reference (the adapter bullets and the "applied deliverable" sentence).
The five standard keys (method, interpretation, assumptions, not_done, status) are named as
such rather than listed.

Usage:
  python scripts/sync_contracts.py            rewrite all 27 skills
  python scripts/sync_contracts.py --check    exit 1 if any skill text disagrees with the tools
  python scripts/sync_contracts.py 4 18       only these chapters
"""
from pathlib import Path
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT.parent
sys.path.insert(0, str(ROOT / 'src'))
STANDARD = ('method', 'interpretation', 'assumptions', 'not_done', 'status')
STANDARD_SKILL = 'plus the standard `method`, `interpretation`, `assumptions`, `not_done` and `status`'
STANDARD_WORKSHOP = 'plus method, interpretation, assumptions, not_done and status'


def live_contract(chapter):
    import pandas as pd
    from forecasting_companion.applied.methods import analyze
    path = ROOT / 'data/examples' / f'ch{chapter:02d}.{"json" if chapter == 10 else "csv"}'
    data = json.loads(path.read_text()) if chapter == 10 else pd.read_csv(path)
    config = json.loads((ROOT / 'configs' / f'ch{chapter:02d}.json').read_text())
    table, summary = analyze(chapter, data, config)
    missing = [k for k in STANDARD if k not in summary]
    if missing:
        raise AssertionError(f'chapter {chapter} summary lacks {missing}')
    keys = [k for k in summary if k not in STANDARD]
    return ','.join(map(str, table.columns)), ','.join(keys)


def folder_for(chapter):
    return next((PROJECT / 'forecasting-skills').glob(f'forecasting-ch{chapter:02d}-*'))


def skill_text(text, columns, keys):
    """Rewrite the opening sentence of '## Applied report contract'; keep the chapter's own prose."""
    m = re.search(r'(^## Applied report contract\n\n)(.*?)(?=^## |\Z)', text, re.S | re.M)
    if not m:
        raise ValueError('Applied report contract section not found')
    body = m.group(2).strip()
    body = re.sub(r'^`results\.csv` columns: `[^`]*`\. `summary\.json` keys: `[^`]*` ' + re.escape(STANDARD_SKILL) + r'\.\s*', '', body)
    body = re.sub(r'^Forecast table: [^.]*\.\s*', '', body)
    lead = f'`results.csv` columns: `{columns}`. `summary.json` keys: `{keys}` {STANDARD_SKILL}.'
    new = lead + ('\n\n' + body if body else '') + '\n\n'
    return text[:m.start(2)] + new + text[m.end(2):]


def workshop_text(text, columns, keys):
    bullets = re.compile(r'- `results\.csv`: .*?\n- `summary\.json`: .*?\n', re.S)
    if not bullets.search(text):
        raise ValueError('workshop adapter bullets not found')
    text = bullets.sub(f'- `results.csv`: `{columns}`.\n- `summary.json`: `{keys}` {STANDARD_WORKSHOP}.\n', text, count=1)
    m = re.search(r'The applied deliverable must make these items inspectable: (.*?)(?=\n\n)', text, re.S)
    if not m:
        raise ValueError('workshop deliverable sentence not found')
    old = m.group(1)
    rest = re.sub(r'^`results\.csv` columns: `[^`]*`; `summary\.json` keys: `[^`]*` ' + re.escape(STANDARD_WORKSHOP) + r'\.\s*', '', old)
    rest = re.sub(r'^Forecast table: [^.]*\.\s*', '', rest)
    new = f'`results.csv` columns: `{columns}`; `summary.json` keys: `{keys}` {STANDARD_WORKSHOP}.' + (' ' + rest if rest else '')
    return text[:m.start(1)] + new + text[m.end(1):]


def sync(chapters, check=False):
    changed = []
    for chapter in chapters:
        columns, keys = live_contract(chapter)
        folder = folder_for(chapter)
        for path, fn in ((folder / 'SKILL.md', skill_text), (folder / 'references/workshop.md', workshop_text)):
            old = path.read_text(); new = fn(old, columns, keys)
            if new != old:
                changed.append(str(path.relative_to(PROJECT)))
                if not check:
                    path.write_text(new)
    return changed


if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if a != '--check']
    check = '--check' in sys.argv
    chapters = [int(a) for a in args] or list(range(1, 28))
    if len(chapters) > 1:
        # One process per chapter: torch (14, 15) and lightgbm (12, 13) each ship an OpenMP runtime and abort when both load.
        import subprocess
        changed = []
        for chapter in chapters:
            out = subprocess.run([sys.executable, __file__, str(chapter), *(['--check'] if check else [])], capture_output=True, text=True)
            if out.returncode not in (0, 1) or 'Traceback' in out.stderr:
                raise SystemExit(f'chapter {chapter} failed:\n{out.stderr[-2000:]}')
            changed += [line.strip() for line in out.stdout.splitlines() if line.startswith('  ') and line.strip()]
    else:
        changed = sync(chapters, check=check)
    if check:
        print('out of sync:' if changed else 'contracts in sync', *changed, sep='\n  ')
        sys.exit(1 if changed else 0)
    print(f'rewrote {len(changed)} files', *changed, sep='\n  ')
