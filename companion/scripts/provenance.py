"""Content hashes make an execution claim specific to code, data and environment."""
from pathlib import Path
import hashlib
import importlib.metadata

ROOT=Path(__file__).resolve().parents[1]

def digest(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def manuscript_for(lesson, root=None):
    """The book chapter behind a lesson, or None in a tree without the manuscript (the public companion)."""
    root=Path(root or ROOT); n=int(lesson.name[:2])
    return next((root.parent/'manuscript').glob(f'{n:02d}-*.md'),None)

def inputs(lesson, root=None):
    root=Path(root or ROOT); n=int(lesson.name[:2]); project=root.parent
    paths=[lesson]
    chapter=manuscript_for(lesson,root)
    if chapter is not None: paths.append(chapter)
    # Conservative dependency closure: shared modules and declared teaching inputs.
    # A change may invalidate extra chapters, but never silently leaves a stale run.
    paths += sorted((root/'src').rglob('*.py'))
    paths += sorted(p for p in (root/'data').rglob('*') if p.is_file() and p.suffix in {'.csv','.json','.md'} and 'benchmarks' not in p.parts)   # fetched benchmark data is not a teaching input
    paths += sorted((root/'configs').glob('*.json'))
    if n == 2: paths.append(root/'assets/returning-aircraft-schematic.png')
    versions={}
    for name in ['numpy','pandas','scipy','matplotlib','statsmodels','nbformat','nbclient','lightgbm','torch','prophet','chronos-forecasting','transformers']:
        try: versions[name]=importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError: versions[name]=None
    return {'files':{str(p.relative_to(project)):digest(p) for p in paths},'versions':versions}

def same_inputs(recorded, current):
    """Compare an execution record with the current tree, ignoring the manuscript entry when the
    tree has no manuscript: the public companion must accept executions made beside the book."""
    if not recorded: return False
    def strip(files, manuscript):
        return {k:v for k,v in files.items() if not k.startswith('companion/data/benchmarks/') and (manuscript or not k.startswith('manuscript/'))}
    has_manuscript=any(k.startswith('manuscript/') for k in current['files'])
    return strip(recorded.get('files',{}),has_manuscript)==strip(current['files'],True) and recorded.get('versions')==current.get('versions')
