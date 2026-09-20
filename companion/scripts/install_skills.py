"""Expose the library to project-local Codex discovery without replacing files."""
from pathlib import Path
import os
ROOT=Path(__file__).resolve().parents[2]
dest=ROOT/'.agents/skills'; dest.mkdir(parents=True,exist_ok=True)
for source in sorted((ROOT/'forecasting-skills').iterdir()):
    if not (source/'SKILL.md').exists(): continue
    target=dest/source.name
    if target.is_symlink() and target.resolve()==source.resolve(): continue
    if target.exists() or target.is_symlink(): raise FileExistsError(f'Existing different skill: {target}')
    target.symlink_to(os.path.relpath(source,dest),target_is_directory=True)
print('Project skill links ready:',dest)
