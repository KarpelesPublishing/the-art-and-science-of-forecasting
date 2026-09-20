"""Expose the skill library to project-local assistant discovery without copying files.

Creates relative symlinks to every folder in forecasting-skills/ that holds a SKILL.md:
  .agents/skills/<name>   read by Codex
  .claude/skills/<name>   read by Claude Code
Other assistants that read SKILL.md files can be pointed at forecasting-skills/ directly
or given a link in their own skills directory the same way. Existing links to the same
folder are left alone; a different existing entry stops the script rather than being replaced.
"""
from pathlib import Path
import os
import sys
ROOT=Path(__file__).resolve().parents[2]
TARGETS={'codex':ROOT/'.agents/skills','claude':ROOT/'.claude/skills'}

def install(dest):
    dest.mkdir(parents=True,exist_ok=True); made=0
    for source in sorted((ROOT/'forecasting-skills').iterdir()):
        if not (source/'SKILL.md').exists(): continue
        target=dest/source.name
        if target.is_symlink() and target.resolve()==source.resolve(): continue
        if target.exists() or target.is_symlink(): raise FileExistsError(f'Existing different skill: {target}')
        target.symlink_to(os.path.relpath(source,dest),target_is_directory=True); made+=1
    return made

if __name__=='__main__':
    chosen=[a for a in sys.argv[1:] if a in TARGETS] or list(TARGETS)
    for name in chosen:
        made=install(TARGETS[name]); print(f'{name}: {TARGETS[name].relative_to(ROOT)} ready ({made} new links)')
