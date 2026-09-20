from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import catalog


def test_catalog_preserves_reviewed_skill(tmp_path):
    write=getattr(catalog,'initialize_skill',None)
    assert callable(write), 'Catalog regeneration must preserve hand-reviewed skills'
    skill=tmp_path/'SKILL.md'
    skill.write_text('Author-reviewed instructions')
    write(skill,'Generated scaffold')
    assert skill.read_text()=='Author-reviewed instructions'
    fresh=tmp_path/'new.md'
    write(fresh,'Generated scaffold')
    assert fresh.read_text()=='Generated scaffold'
