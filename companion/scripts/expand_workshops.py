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
        prose=ref.read_text()
        skill_text=(ref.parent.parent/'SKILL.md').read_text()
        contract=re.search(r'## Input contract\n(.*?)(?=\n## |\Z)',skill_text,re.S)
        if contract:prose='## Input contract and format example\n'+contract[1]+'\n'+prose
        # Notebook-relative links; the copied narrative must not retain skill-relative links.
        def link(m):
            target=m.group(2)
            if '://' in target or target.startswith('#'):return m.group(0)
            import os
            resolved=(ref.parent/target).resolve()
            return '['+m.group(1)+']('+os.path.relpath(resolved,ROOT/'notebooks')+')'
        prose=re.sub(r'\[([^]]+)\]\(([^)]+)\)',link,prose)
        text=original+MARKER+'\n# ## Guided application workshop\n# The sections below connect the controlled figures to a complete applied input/output workflow.\n'+markdown(prose)
        text+=markdown('## Configure and run the applied case\n\nThe input file and JSON below are the only entry-point changes needed to try another\ncase with the same schema. Keep the original examples for comparison. Supply source\nand units in the configuration; resolve missing periods rather than silently filling\nunknown observations with zeros. These calculations call the same tested functions\nas the `run.py apply` command. A failed validation is a reason to inspect the data,\nnot to replace it with invented observations.\n\nThe default input here is a **seeded synthetic schema example**, separate from any\nobserved-data application below. Read the summary before interpreting its results.')
        ext='json' if n==10 else 'csv'
        text+=f'''# %%
from forecasting_companion.applied.methods import analyze as analyze_chapter
from forecasting_companion.applied.core import clean_json
import pandas as pd
import json, os
INPUT_PATH = project_path = next(p for p in [Path.cwd(), *Path.cwd().parents] if (p/'companion/src').exists()) / 'companion/data/examples/ch{n:02d}.{ext}'
CONFIG_PATH = project_path.parents[2] / 'configs/ch{n:02d}.json'
# Input paths are explicit and may be replaced with reader-supplied files.
workshop_config = json.loads(CONFIG_PATH.read_text())
workshop_input = {'json.loads(INPUT_PATH.read_text())' if n==10 else 'pd.read_csv(INPUT_PATH)'}
workshop_table, workshop_summary = analyze_chapter({n}, workshop_input, workshop_config)
print(json.dumps(clean_json(workshop_summary), indent=2))
print(workshop_table.head(12).to_string(index=False))
workshop_output = Path(os.environ.get('FORECAST_OUTPUT', CONFIG_PATH.parents[1])) / 'results'
workshop_output.mkdir(parents=True, exist_ok=True)
workshop_table.to_csv(workshop_output/'ch{n:02d}-workshop-results.csv', index=False)
(workshop_output/'ch{n:02d}-workshop-summary.json').write_text(json.dumps(clean_json(workshop_summary), indent=2)+'\\n')
'''
        if n in OBSERVED:
            dataset=OBSERVED[n]
            text+=markdown('## Apply the same workflow to observed data\n\nThis second case uses a bundled public-domain historical dataset documented in\n`data/registry.json`. It is a revised snapshot, not an archived real-time vintage.\nThe earlier time cuts prevent fitting on held-out outcomes; they do not undo\nrevisions that may have occurred before the snapshot was published. Compare the\nactual output below with the controlled case. A method need not win to be useful.\nThe source, transformation and units are in the configuration and registry.')
            text+=f'''# %%
observed_input = pd.read_csv(CONFIG_PATH.parents[1]/'data/observed/{dataset}.csv')
observed_config = json.loads((CONFIG_PATH.parent/'ch{n:02d}-observed.json').read_text())
observed_table, observed_summary = analyze_chapter({n}, observed_input, observed_config)
print('Observed-data source:', observed_config['source'])
print(json.dumps(clean_json(observed_summary), indent=2))
print(observed_table.head(12).to_string(index=False))
observed_table.to_csv(workshop_output/'ch{n:02d}-observed-results.csv', index=False)
(workshop_output/'ch{n:02d}-observed-summary.json').write_text(json.dumps(clean_json(observed_summary), indent=2)+'\\n')
'''
        else:
            text+=markdown('## Real-data boundary\n\nThe bundled case is controlled, not a reconstruction of historical records. No\nverified, appropriately licensed domain dataset is supplied for this particular\nworkflow. Use the input contract to supply your own observations and evidence.\nDo not substitute an unrelated public dataset simply to call the example real.\nThe wider companion includes observed time-series applications in chapters\n3–6, 12, 15–16 and 24; their data do not establish this chapter’s domain assumptions.')
        text+=markdown('## Read the result as a decision record\n\nStart with the summary’s **interpretation**, then examine its numerical evidence.\nDistinguish what was fitted, what was supplied, and what remains unidentified.\nThe results table is the calculation; it is not permission to act. Explain which\nassumption would most change the answer and what new evidence would test it.\nFor a live forecast, set an outcome date and keep the original result for scoring.\n\nThe exercises and worked solutions above test interpretation, calculation, and\nadaptation. Re-run a changed assumption and compare the actual output; do not\nreuse numbers from the book when your input or horizon changes.')
        lesson.write_text(text)
    print('Expanded available chapter workshops into editable lesson sources.')
if __name__=='__main__':main()
