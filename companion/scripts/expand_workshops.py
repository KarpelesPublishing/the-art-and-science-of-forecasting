"""Synchronize reviewed chapter workshops into editable percent-cell lesson sources.

Run before chapter execution. The generated block is reviewable in the source;
notebook creation itself continues to use author.py without hidden text injection.
"""
from pathlib import Path
import re
ROOT=Path(__file__).resolve().parents[1];PROJECT=ROOT.parent
MARKER='# %% [markdown]\n# <!-- APPLIED-WORKSHOP-START -->'
OBSERVED={3:'monthly-temperature',4:'monthly-temperature',6:'monthly-temperature',12:'monthly-temperature',15:'monthly-temperature',16:'monthly-temperature',5:'annual-nile',24:'annual-nile'}

def markdown(text):return '# %% [markdown]\n'+'\n'.join('# '+line if line else '#' for line in text.splitlines())+'\n'

def main():
    for lesson in sorted((ROOT/'lessons').glob('*.py')):
        n=int(lesson.name[:2]);ref=PROJECT/'forecasting-skills'/f'forecasting-ch{lesson.stem}'/'references/workshop.md'
        if not ref.exists():continue
        original=lesson.read_text().split(MARKER)[0].rstrip()+'\n'
        prose=re.sub(r'^# Chapter \d+ workshop:[^\n]*\n+','',ref.read_text())
        skill_text=(ref.parent.parent/'SKILL.md').read_text()
        contract=re.search(r'## Input contract[^\n]*\n(.*?)(?=\n## |\Z)',skill_text,re.S)
        if contract:prose='## Input contract and format example\n'+contract[1].strip('\n')+'\n\n'+prose
        # Notebook-relative links; the copied narrative must not retain skill-relative links.
        def link(m):
            target=m.group(2)
            if '://' in target or target.startswith('#'):return m.group(0)
            import os
            resolved=(ref.parent/target).resolve()
            return '['+m.group(1)+']('+os.path.relpath(resolved,ROOT/'notebooks')+')'
        prose=re.sub(r'\[([^]]+)\]\(([^)]+)\)',link,prose)
        text=original+MARKER+'\n# ## Guided application workshop\n# The sections below come from the chapter skill: the mechanism, the arithmetic, how to adapt the lesson to your data, exercises with worked solutions, and the exact contract of the applied tool.\n'+markdown(prose)
        text+=markdown('## Apply this chapter to your own data\n\nThe two paths below are the only things to change: point `INPUT_PATH` at a file with the\ncolumns in the input contract above and `CONFIG_PATH` at a copy of the shipped configuration\nwith your `source` and `units`. The call is the same tested function behind `run.py apply`.\nThe printed digest shows what ran, its status, the interpretation, the assumptions and the\n`not_done` list; the full summary is saved beside the table. A validation error is a reason to\ninspect the data, not to fill gaps with invented observations. Shared rules for provenance,\noutput folders and reading `status` are in the Complete Forecasting Skill\'s conventions reference.')
        ext='json' if n==10 else 'csv'
        text+=f'''# %%
from forecasting_companion.applied.methods import analyze as analyze_chapter
from forecasting_companion.applied.core import clean_json, summarize, preview
import pandas as pd
import json, os
project_path = next(p for p in [Path.cwd(), *Path.cwd().parents] if (p/'companion/src').exists())
INPUT_PATH = project_path / 'companion/data/examples/ch{n:02d}.{ext}'      # replace with your file
CONFIG_PATH = project_path / 'companion/configs/ch{n:02d}.json'            # replace with your configuration
workshop_config = json.loads(CONFIG_PATH.read_text())
workshop_input = {'json.loads(INPUT_PATH.read_text())' if n==10 else 'pd.read_csv(INPUT_PATH)'}
workshop_table, workshop_summary = analyze_chapter({n}, workshop_input, workshop_config)
print(summarize(workshop_summary, workshop_table))
print()
print(preview(workshop_table))
workshop_output = Path(os.environ.get('FORECAST_OUTPUT', project_path / 'companion')) / 'results'
workshop_output.mkdir(parents=True, exist_ok=True)
workshop_table.to_csv(workshop_output/'ch{n:02d}-workshop-results.csv', index=False)
_ = (workshop_output/'ch{n:02d}-workshop-summary.json').write_text(json.dumps(clean_json(workshop_summary), indent=2)+'\\n')
'''
        if n in OBSERVED:
            dataset=OBSERVED[n]
            text+=markdown('## The same workflow on observed data\n\nA second run on a bundled public-domain series documented in `data/registry.json` (a revised\nhistorical snapshot, not an archived real-time vintage). The earlier time cuts prevent fitting\non held-out outcomes; they do not undo revisions made before the snapshot was published.\nCompare this digest with the controlled case above: a method need not win to be useful, and\nthe winner on synthetic data has no claim on observed data.')
            text+=f'''# %%
observed_input = pd.read_csv(project_path/'companion/data/observed/{dataset}.csv')
observed_config = json.loads((project_path/'companion/configs/ch{n:02d}-observed.json').read_text())
observed_table, observed_summary = analyze_chapter({n}, observed_input, observed_config)
print('Observed-data source:', observed_config['source'])
print(summarize(observed_summary, observed_table))
print()
print(preview(observed_table))
observed_table.to_csv(workshop_output/'ch{n:02d}-observed-results.csv', index=False)
_ = (workshop_output/'ch{n:02d}-observed-summary.json').write_text(json.dumps(clean_json(observed_summary), indent=2)+'\\n')
'''
        lesson.write_text(text)
    print('Expanded available chapter workshops into editable lesson sources.')
if __name__=='__main__':main()
