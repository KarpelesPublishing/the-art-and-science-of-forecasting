"""Write the public companion repository tree (no book text) to a target directory.

Included: companion notebooks, lessons, source, scripts, data, configs, figures, results,
assets, tests, START-HERE and README; the 29 skill folders; the root skill-library README;
the packaged reconcile-tdbu skill; companion/public-README.md as the repo README and
companion/public-LICENSE (MIT) as LICENSE. Excluded: the manuscript, the revision pipeline
(patches, author sections, built editions), reports that quote the book, and the
production scripts that carry book prose.
Usage: python export_public.py <target-dir>
"""
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]; PROJECT = ROOT.parent
SKIP_PARTS = {'.venv', '__pycache__', '.pytest_cache', 'legacy-run-journals', 'checkpoints', 'batch-benchmark', 'layout-pages', 'chart-sheets', 'applied-runs', '.ipynb_checkpoints', '.DS_Store', 'benchmarks'}   # benchmark data is fetched, never bundled
SKIP_COMPANION = {'revision', 'reports/quality-loop', 'reports/triage-report.md', 'reports/applied-corrections.json', 'reports/index-review.json', 'reports/black-and-white-review.md',
                  'reports/chart-and-navigation-review.md', 'reports/current-quality-audit.md', 'reports/practitioner-revision.md', 'reports/validation.md', 'reports/package.json',
                  'reports/method-audit.md', 'reports/visual-audit.md', 'reports/upgrade/summary.md', 'reports/upgrade/skill-evaluation.md', 'reports/upgrade/content-inventory.json', 'reports/upgrade/portability.json', 'reports/original-pdf-audit.json', 'reports/current-quality-audit-evidence.json', 'reports/layout-inspection.json', 'reports/skill-review.md', 'reports/prophet-page.png', 'reports/build.json', 'reports/validation.json',
                  'scripts/author_revision.py', 'scripts/build_revision.py', 'scripts/revision_index.py', 'scripts/index_common.py', 'scripts/epub_index.py', 'scripts/strip_em_dashes.py', 'scripts/audit_pdf.py', 'scripts/package.py', 'scripts/validate.py',
                  'public-README.md', 'public-LICENSE', 'scripts/review_grayscale.py', 'scripts/review_layout.py', 'tests/test_strip_em_dashes.py', 'tests/test_author_revision.py', 'tests/test_book_review.py', 'tests/test_epub_equations.py', 'tests/test_no_em_dashes.py', 'tests/test_package.py', 'tests/test_revision_index.py'}


def wanted(rel):
    if SKIP_PARTS & set(rel.parts) or rel.suffix in {'.pyc', '.zip'}:
        return False
    if rel.parts[0] == 'companion':
        inner = rel.relative_to('companion').as_posix()
        if inner.startswith('harness/runs/') and rel.name not in ('score.json', 'SUMMARY.md'):
            return False                                  # the harness evidence (scores and summaries), not every working file
        return not any(inner == s or inner.startswith(s + '/') for s in SKIP_COMPANION)
    return True


def main(target):
    target = Path(target).resolve()
    if target.exists():
        shutil.rmtree(target)
    sources = [PROJECT / 'companion', PROJECT / 'forecasting-skills']
    skip_top = {'forecasting-skills/CHAPTERS-TO-ADD.md'}
    n = 0
    for folder in sources:
        for p in folder.rglob('*'):
            if not p.is_file():
                continue
            rel = p.relative_to(PROJECT)
            if rel.as_posix() in skip_top or not wanted(rel) or any((parent / 'run.json').is_file() for parent in p.parents if PROJECT in parent.parents):
                continue
            dest = target / rel; dest.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(p, dest); n += 1
    package_skill(PROJECT / 'forecasting-skills/reconcile-tdbu', target / 'reconcile-tdbu.skill')
    shutil.copy2(target / 'reconcile-tdbu.skill', PROJECT / 'reconcile-tdbu.skill')
    shutil.copy2(PROJECT / 'README.md', target / 'SKILL-LIBRARY.md')
    public_readme(target / 'companion/README.md')
    strip_manuscript_records(target / 'companion')
    shutil.copy2(ROOT / 'public-README.md', target / 'README.md')
    shutil.copy2(ROOT / 'public-LICENSE', target / 'LICENSE')
    (target / '.gitignore').write_text('.venv/\n__pycache__/\n.pytest_cache/\n.ipynb_checkpoints/\ncompanion/applied-runs/\ncompanion/data/benchmarks/\n.agents/\n.claude/\n*.pyc\n.DS_Store\n')
    print(f'exported {n + 4} files to {target}')


def package_skill(folder, archive):
    """Zip the desk-model skill folder as a single .skill file (stored, deterministic order)."""
    import zipfile
    with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_STORED) as z:
        for p in sorted(folder.rglob('*')):
            if p.is_file() and '__pycache__' not in p.parts:
                z.write(p, str(p.relative_to(folder.parent)))


def strip_manuscript_records(companion):
    """The execution records hash the book chapter beside each lesson; the public tree has no book,
    so those entries go, and catalog.py accepts the records as current (see provenance.same_inputs)."""
    import json
    for path in [companion / 'manifest.json', *sorted((companion / 'results').glob('ch*-execution.json'))]:
        if not path.exists():
            continue
        data = json.loads(path.read_text())
        records = data['chapters'] if 'chapters' in data else [data]
        for record in records:
            record.pop('source', None); record.pop('source_sha256', None)
            execution = record.get('execution', record)
            files = execution.get('inputs', {}).get('files')
            if files:
                execution['inputs']['files'] = {k: v for k, v in files.items() if not k.startswith('manuscript/')}
        path.write_text(json.dumps(data, indent=2) + '\n')


def public_readme(path):
    """The technical guide without the author's book-production section."""
    s = path.read_text()
    a = s.index('## Read the revised book'); b = s.index('## Data and method scope')
    s = s[:a] + '## The book\n\n*The Art and Science of Forecasting* by Jason Karpeles. Book website, with articles, additional material and the audiobook (activated by contacting the author through the site): <https://karpeles.com/publishing/the-art-and-science-of-forecasting>. This repository is the free companion; it does not contain the book text.\n\n' + s[b:]
    s = s.replace('This package connects the revised book\'s figures to 27 executed Jupyter notebooks,', 'This package connects the book\'s figures to 27 executed Jupyter notebooks,')
    for line in ('companion/.venv/bin/python companion/scripts/build_revision.py\n', 'companion/.venv/bin/python companion/scripts/validate.py\n'):
        s = s.replace(line, '')
    a = s.index('The book build also needs Pandoc'); b = s.index('Editable notebook sources are')
    s = s[:a] + s[b:]
    s = s.replace('## Reproduce the chapters and book', '## Reproduce the chapters')
    path.write_text(s)


if __name__ == '__main__':
    main(sys.argv[1])
