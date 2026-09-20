"""Rewrite the executable sections of a chapter skill and its workshop reference from one spec.

Usage: python scripts/skill_text.py <chapter> <spec.json>
The spec carries: schema, controls, input_example (csv text), input_note, interface (paragraph),
results_columns, summary_keys, report_note. The sections rewritten are:
  SKILL.md   '## Input contract and additional evidence', '## Executable interface', '## Applied report contract'
  workshop.md 'The current applied adapter adds ...' block (results/summary bullets + mirrored paragraph)
              and the 'The applied deliverable must make these items inspectable:' sentence.
Run scripts/expand_workshops.py afterwards to push the workshop text into the lesson notebooks.
"""
from pathlib import Path
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
CAPABLE = 'The tool runs only when asked; the assistant decides, with the reader, whether the method fits before running it.'


def replace_section(text, heading, body):
    pattern = re.compile(r'(^' + re.escape(heading) + r'\n)(.*?)(?=^## |\Z)', re.S | re.M)
    if not pattern.search(text):
        raise ValueError(f'section {heading!r} not found')
    return pattern.sub(lambda m: m.group(1) + '\n' + body.strip('\n') + '\n\n', text, count=1)


def main(chapter, spec_path):
    spec = json.loads(Path(spec_path).read_text())
    folder = next((ROOT / 'forecasting-skills').glob(f'forecasting-ch{chapter:02d}-*'))
    skill = folder / 'SKILL.md'; workshop = folder / 'references' / 'workshop.md'
    controls = ', '.join(spec['controls'])
    interface = (f"Exact CLI columns: `{spec['schema']}`. All configs require `source` and `units`; `outcome_due` is recorded for future scoring. "
                 f"Supported method controls: `{controls}`. Unknown config keys are rejected.\n\n{spec['interface'].strip()}\n\n{CAPABLE}")
    contract = (f"`results.csv` columns: `{spec['results_columns']}`. `summary.json` keys: `{spec['summary_keys']}` plus the standard "
                f"`method`, `interpretation`, `assumptions`, `not_done` and `status`. {spec['report_note'].strip()} "
                "Include units, horizon, evidence cutoff, sources, assumptions and limitations. For a live forecast record creation time and outcome/scoring date.")
    contract_first = f"`results.csv` columns: `{spec['results_columns']}`; `summary.json` keys: `{spec['summary_keys']}` plus method, interpretation, assumptions, not_done and status. {spec['report_note'].strip()}"
    inp = f"{spec['input_note'].strip()}\n\nMinimal **format illustration**, not sufficient training data:\n\n```csv\n{spec['input_example'].strip()}\n```"
    s = skill.read_text()
    s = replace_section(s, '## Input contract and additional evidence', inp)
    s = replace_section(s, '## Executable interface', interface)
    s = replace_section(s, '## Applied report contract', contract)
    skill.write_text(s)
    w = workshop.read_text()
    block = re.compile(r'The current applied adapter adds a separately inspectable numerical result:\n\n- `results\.csv`: .*?\n- `summary\.json`: .*?\n\n.*?\n\n', re.S)
    if not block.search(w):
        raise ValueError('workshop adapter block not found')
    w = block.sub(f"The current applied adapter adds a separately inspectable numerical result:\n\n- `results.csv`: `{spec['results_columns']}`.\n- `summary.json`: `{spec['summary_keys']}` plus method, interpretation, assumptions, not_done and status.\n\n{spec['interface'].strip()} {CAPABLE}\n\n", w, count=1)
    w = re.sub(r'The applied deliverable must make these items inspectable: .*?(?=\n\n## )', 'The applied deliverable must make these items inspectable: ' + contract_first, w, count=1, flags=re.S)
    workshop.write_text(w)
    print('rewrote', skill.relative_to(ROOT), 'and', workshop.relative_to(ROOT))


if __name__ == '__main__':
    main(int(sys.argv[1]), sys.argv[2])
