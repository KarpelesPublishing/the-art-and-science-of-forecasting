"""Prove each engine route on public data of the kind it claims to handle.

Datasets (see benchmark_sources.json) are fetched on demand into data/benchmarks/ and verified by
SHA-256; nothing is bundled. Each series is forecast by the engine (light pool by route) and by the
baselines, the test period is scored, and the report says MASE, sMAPE, band coverage and runtime.
The floor the tests hold the engine to is modest and honest: never worse than seasonal naive on
MASE, coverage within ten points of nominal. Published references are context, not a claim.

Usage:
  python scripts/benchmark.py m4-hourly --subset 40
  python scripts/benchmark.py m4-monthly --subset 100 --pool full --budget-seconds 20
  python scripts/benchmark.py --list
"""
from pathlib import Path
import argparse
import hashlib
import json
import sys
import time
import urllib.request
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
SOURCES = json.loads((ROOT / 'scripts/benchmark_sources.json').read_text())
DATA = ROOT / 'data/benchmarks'
REPORTS = ROOT / 'reports/benchmarks'
REFERENCES = {'m4-monthly': 'M4 Theta sMAPE 13.00 (monthly), Comb benchmark 13.43; winner (Smyl) 12.13', 'm4-hourly': 'M4 Theta sMAPE 18.14 (hourly); winner (Smyl) 9.33',
              'm4-quarterly': 'M4 Theta sMAPE 10.31 (quarterly)', 'm4-weekly': 'M4 Theta sMAPE 9.09 (weekly)', 'm4-daily': 'M4 Theta sMAPE 3.05 (daily)', 'tourism': 'Tourism competition: seasonal naive and damped ETS were hard to beat on monthly series'}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def fetch(name):
    src = SOURCES[name]; DATA.mkdir(parents=True, exist_ok=True); paths = {}
    for kind in ('train', 'test', 'zip'):
        if kind not in src:
            continue
        target = DATA / f'{name}-{kind}{Path(src[kind]).suffix}'
        if not target.exists():
            print(f'downloading {src[kind]} -> {target.name}')
            urllib.request.urlretrieve(src[kind], target)
        digest = sha(target); recorded = src['sha256'].get(kind)
        if recorded and recorded != digest:
            raise ValueError(f'{target.name}: sha256 {digest} does not match the recorded {recorded}; delete the file to refetch')
        if not recorded:
            src['sha256'][kind] = digest; SOURCES[name] = src
            (ROOT / 'scripts/benchmark_sources.json').write_text(json.dumps(SOURCES, indent=2) + '\n')
            print(f'recorded sha256 for {target.name}')
        paths[kind] = target
    return paths


def load_m4(name, paths, subset, seed):
    train = pd.read_csv(paths['train']); test = pd.read_csv(paths['test'])
    ids = list(train.V1)
    rng = np.random.default_rng(seed)
    if subset and subset < len(ids):
        ids = sorted(rng.choice(ids, subset, replace=False))
    tr = train.set_index('V1'); te = test.set_index('V1')
    for sid in ids:
        y = tr.loc[sid].dropna().to_numpy(float); yt = te.loc[sid].dropna().to_numpy(float)
        yield sid, y, yt


def load_tourism(paths, subset, seed):
    import zipfile
    with zipfile.ZipFile(paths['zip']) as z:
        names = [n for n in z.namelist() if n.lower().endswith('.csv')]
        mtr = next((n for n in names if 'monthly' in n.lower() and 'in' in n.lower()), None); mte = next((n for n in names if 'monthly' in n.lower() and 'oos' in n.lower()), None)
        if not mtr or not mte:
            raise ValueError(f'tourism zip layout not recognised: {names[:6]}')
        train = pd.read_csv(z.open(mtr)); test = pd.read_csv(z.open(mte))
    cols = list(train.columns); rng = np.random.default_rng(seed)
    if subset and subset < len(cols):
        cols = sorted(rng.choice(cols, subset, replace=False))
    for c in cols:
        y = pd.to_numeric(train[c], errors='coerce').dropna().to_numpy(float)[2:]   # first rows carry metadata in this release
        yt = pd.to_numeric(test[c], errors='coerce').dropna().to_numpy(float)[2:]
        if len(y) > 24 and len(yt) >= 12:
            yield c, y, yt[:24]


def smape(a, f):
    return float(200 * np.mean(np.abs(f - a) / np.maximum(np.abs(a) + np.abs(f), 1e-9)))


def mase(a, f, train, m):
    scale = np.mean(np.abs(train[m:] - train[:-m])) if len(train) > m else np.mean(np.abs(np.diff(train)))
    return float(np.mean(np.abs(f - a)) / scale) if scale > 0 else None


def run(name, subset=50, pool=None, budget=None, seed=2026, max_origins=3):
    from forecasting_companion.engine import forecast_series
    src = SOURCES[name]; paths = fetch(name)
    h, s = src['horizon'], src['season']; freq = src['freq']
    pool = pool or ('multiseasonal' if src['route'] == 'multiseasonal' else 'full')
    series = load_tourism(paths, subset, seed) if name == 'tourism' else load_m4(name, paths, subset, seed)
    rows = []
    for sid, y, yt in series:
        yt = yt[:h]
        if len(yt) < h:
            continue
        ts = pd.Series(pd.date_range('2000-01-01', periods=len(y), freq=freq))
        snaive = np.resize(y[-s:], h) if len(y) >= s else np.repeat(y[-1], h)
        row = dict(series=sid, n=len(y), smape_snaive=smape(yt, snaive), mase_snaive=mase(yt, snaive, y, s))
        t0 = time.perf_counter()
        try:
            table, summary = forecast_series(y, ts, h, s, pool=pool, freq=freq, max_origins=max_origins, periods=src.get('periods'))
            f = table.forecast.to_numpy()
            row.update(selected=summary['selected'], smape_engine=smape(yt, f), mase_engine=mase(yt, f, y, s), forced_baseline=summary['forced_baseline'],
                       coverage_model=float(np.mean((yt >= table.lower) & (yt <= table.upper))) if 'lower' in table else None,
                       coverage_conformal=float(np.mean((yt >= table.conformal_lower) & (yt <= table.conformal_upper))) if 'conformal_lower' in table else None,
                       coverage_empirical=float(np.mean((yt >= table.empirical_q10) & (yt <= table.empirical_q90))))
        except Exception as exc:
            row.update(error=f'{type(exc).__name__}: {str(exc)[:80]}')
        row['seconds'] = time.perf_counter() - t0
        rows.append(row)
        if budget and sum(r['seconds'] for r in rows) > budget:
            break
    frame = pd.DataFrame(rows)
    ok = frame[frame.get('error', pd.Series(dtype=object)).isna()] if 'error' in frame else frame
    result = dict(dataset=name, pool=pool, series=len(frame), scored=len(ok), horizon=h, season=s,
                  smape_engine=float(ok.smape_engine.mean()) if len(ok) else None, smape_snaive=float(ok.smape_snaive.mean()) if len(ok) else None,
                  mase_engine=float(ok.mase_engine.mean()) if len(ok) else None, mase_snaive=float(ok.mase_snaive.mean()) if len(ok) else None,
                  coverage_model=float(ok.coverage_model.dropna().mean()) if len(ok) and ok.coverage_model.notna().any() else None,
                  coverage_conformal=float(ok.coverage_conformal.dropna().mean()) if len(ok) and ok.coverage_conformal.notna().any() else None,
                  coverage_empirical=float(ok.coverage_empirical.mean()) if len(ok) else None,
                  seconds_per_series=float(frame.seconds.mean()), forced_baseline_share=float(ok.forced_baseline.mean()) if len(ok) else None,
                  selected=ok.selected.value_counts().to_dict() if len(ok) else {}, errors=int(len(frame) - len(ok)), reference=REFERENCES.get(name, ''))
    REPORTS.mkdir(parents=True, exist_ok=True)
    frame.to_csv(REPORTS / f'{name}-series.csv', index=False)
    results_path = REPORTS / 'results.json'
    all_results = json.loads(results_path.read_text()) if results_path.exists() else {}
    all_results[f'{name}:{pool}'] = result; results_path.write_text(json.dumps(all_results, indent=2) + '\n')
    (REPORTS / f'{name}-{pool}.md').write_text(report_md(result, frame))
    return result, frame


def report_md(r, frame):
    lines = [f'# Benchmark: {r["dataset"]} with pool `{r["pool"]}`', '',
             f'{r["scored"]} of {r["series"]} series scored ({r["errors"]} errors), horizon {r["horizon"]}, season {r["season"]}, {r["seconds_per_series"]:.1f} s per series.', '',
             '| Measure | Engine | Seasonal naive |', '|---|---|---|',
             f'| sMAPE | {r["smape_engine"]:.2f} | {r["smape_snaive"]:.2f} |' if r['smape_engine'] is not None else '| sMAPE | n/a | n/a |',
             f'| MASE | {r["mase_engine"]:.3f} | {r["mase_snaive"]:.3f} |' if r['mase_engine'] is not None else '| MASE | n/a | n/a |', '',
             f'Band coverage at nominal 80%: model band {r["coverage_model"]:.0%}, conformal {r["coverage_conformal"]:.0%}, empirical quantiles {r["coverage_empirical"]:.0%}.' if r['coverage_conformal'] is not None else 'No bands to score.', '',
             f'Selected models: {r["selected"]}. Baseline forced by the robustness rule on {r["forced_baseline_share"]:.0%} of series.' if r['forced_baseline_share'] is not None else '',
             '', f'Published reference (context, not a like-for-like comparison; subsets and horizons differ): {r["reference"]}', '',
             'Every series row is in the companion CSV beside this file.']
    return '\n'.join(lines) + '\n'


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('dataset', nargs='?'); ap.add_argument('--subset', type=int, default=50); ap.add_argument('--pool'); ap.add_argument('--budget-seconds', type=float); ap.add_argument('--list', action='store_true'); ap.add_argument('--seed', type=int, default=2026)
    a = ap.parse_args()
    if a.list or not a.dataset:
        for k, v in SOURCES.items():
            if isinstance(v, dict):
                print(f'{k:14s} route {v["route"]:14s} horizon {v["horizon"]:3d} season {v["season"]}')
        sys.exit(0)
    r, _ = run(a.dataset, a.subset, a.pool, a.budget_seconds, a.seed)
    print(json.dumps({k: v for k, v in r.items() if k != 'selected'}, indent=2)); print('selected:', r['selected'])
