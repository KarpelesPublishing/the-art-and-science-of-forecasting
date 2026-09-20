"""Convert reviewable percent-cell Python lessons into Jupyter notebooks.

The .py sources are the editable source of truth; generated notebooks retain
all visible teaching code, explanatory Markdown, stable cell IDs and outputs.
"""
from pathlib import Path
import re
import sys
import nbformat

ROOT = Path(__file__).resolve().parents[1]

def build(source):
    text = source.read_text()
    cells = []
    for i, part in enumerate(re.split(r'^# %%', text, flags=re.M)):
        if not part.strip():
            continue
        markdown = part.startswith(' [markdown]')
        body = part.split('\n', 1)[1] if markdown or part.startswith('\n') else part
        if markdown:
            body = '\n'.join(re.sub(r'^# ?', '', line) for line in body.splitlines())
        cell = (nbformat.v4.new_markdown_cell if markdown else nbformat.v4.new_code_cell)(body.strip())
        cell['id'] = f'{source.stem}-cell-{i:02d}'
        cells.append(cell)
    nb = nbformat.v4.new_notebook(cells=cells, metadata={
        'kernelspec': {'name':'python3','display_name':'Python 3','language':'python'},
        'language_info': {'name':'python','version':'3.12'}})
    dest = ROOT/'notebooks'/f'{source.stem}.ipynb'
    dest.parent.mkdir(exist_ok=True)
    nbformat.write(nb, dest)
    return dest

if __name__ == '__main__':
    for path in sorted((ROOT/'lessons').glob('*.py')):
        if len(sys.argv) == 1 or path.name[:2] in sys.argv[1:]:
            print(build(path).relative_to(ROOT))
