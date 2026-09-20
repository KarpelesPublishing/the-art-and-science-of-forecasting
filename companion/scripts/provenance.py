"""Content hashes make an execution claim specific to code, data and environment."""
from pathlib import Path
import hashlib
import importlib.metadata

ROOT=Path(__file__).resolve().parents[1]

def digest(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def inputs(lesson):
    n=int(lesson.name[:2]); project=ROOT.parent
    paths=[lesson,next((project/'manuscript').glob(f'{n:02d}-*.md'))]
    # Conservative dependency closure: shared modules and declared teaching inputs.
    # A change may invalidate extra chapters, but never silently leaves a stale run.
    paths += sorted((ROOT/'src').rglob('*.py'))
    paths += sorted(p for p in (ROOT/'data').rglob('*') if p.is_file() and p.suffix in {'.csv','.json','.md'})
    paths += sorted((ROOT/'configs').glob('*.json'))
    if n == 2: paths.append(ROOT/'assets/returning-aircraft-schematic.png')
    versions={}
    for name in ['numpy','pandas','scipy','matplotlib','statsmodels','nbformat','nbclient','lightgbm','torch','prophet','chronos-forecasting','transformers']:
        try: versions[name]=importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError: versions[name]=None
    return {'files':{str(p.relative_to(project)):digest(p) for p in paths},'versions':versions}
