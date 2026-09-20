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
            req = urllib.request.Request(src[kind], headers={'User-Agent': 'Mozilla/5.0 (forecasting-companion benchmark)'})
            with urllib.request.urlopen(req, timeout=120) as resp, open(target, 'wb') as out:
                out.write(resp.read())
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


def load_m3(paths, subset, seed):
    """M3 monthly sheet from a hand-placed M3C.xls (N series with N-obs values then 18 test points)."""
    frame = pd.read_excel(paths['file'], sheet_name='M3Month')
    rng = np.random.default_rng(seed); rows = list(frame.index)
    if subset and subset < len(rows):
        rows = sorted(rng.choice(rows, subset, replace=False))
    for i in rows:
        r = frame.loc[i]; n = int(r['N']); values = pd.to_numeric(r.iloc[6:6 + n], errors='coerce').dropna().to_numpy(float)
        yield str(r['Series']), values[:-18], values[-18:]


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
        col = pd.to_numeric(train[c], errors='coerce'); n_in = int(col.iloc[0])           # rows 0..2 are length, start year, start month
        y = col.iloc[3:3 + n_in].dropna().to_numpy(float)
        tcol = pd.to_numeric(test[c], errors='coerce'); n_out = int(tcol.iloc[0])
        yt = tcol.iloc[3:3 + n_out].dropna().to_numpy(float)
        if len(y) > 36 and len(yt) >= 12:
            yield c, y, yt[:24]


def smape(a, f):
    return float(200 * np.mean(np.abs(f - a) / np.maximum(np.abs(a) + np.abs(f), 1e-9)))


def mase(a, f, train, m):
    scale = np.mean(np.abs(train[m:] - train[:-m])) if len(train) > m else np.mean(np.abs(np.diff(train)))
    return float(np.mean(np.abs(f - a)) / scale) if scale > 0 else None


def run(name, subset=50, pool=None, budget=None, seed=2026, max_origins=5):
    from forecasting_companion.engine import forecast_series
    src = SOURCES[name]
    paths = {'file': DATA / src['file']} if src.get('file') else fetch(name)
    h, s = src['horizon'], src['season']; freq = src['freq']
    pool = pool or ('multiseasonal' if src['route'] == 'multiseasonal' else 'full')
    series = load_tourism(paths, subset, seed) if name == 'tourism' else load_m3(paths, subset, seed) if name == 'm3' else load_m4(name, paths, subset, seed)
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
            # the band a reader receives: the engine's band_lower/upper (model, conformal or their midpoint by the holdout rule)
            row['coverage_delivered'] = float(np.mean((yt >= table.band_lower) & (yt <= table.band_upper))) if 'band_lower' in table else row['coverage_conformal']
            row['band_delivered'] = summary.get('band_method') or 'conformal'
        except Exception as exc:
            row.update(error=f'{type(exc).__name__}: {str(exc)[:80]}')
        row['seconds'] = time.perf_counter() - t0
        rows.append(row)
        if budget and sum(r['seconds'] for r in rows) > budget:
            break
    frame = pd.DataFrame(rows)
    ok = frame[frame.get('error', pd.Series(dtype=object)).isna()] if 'error' in frame else frame
    result = dict(dataset=name, pool=pool, series=len(frame), scored=len(ok), horizon=h, season=s, origins=max_origins,
                  smape_engine=float(ok.smape_engine.mean()) if len(ok) else None, smape_snaive=float(ok.smape_snaive.mean()) if len(ok) else None,
                  mase_engine=float(ok.mase_engine.mean()) if len(ok) else None, mase_snaive=float(ok.mase_snaive.mean()) if len(ok) else None,
                  coverage_model=float(ok.coverage_model.dropna().mean()) if len(ok) and ok.coverage_model.notna().any() else None,
                  coverage_conformal=float(ok.coverage_conformal.dropna().mean()) if len(ok) and ok.coverage_conformal.notna().any() else None,
                  coverage_empirical=float(ok.coverage_empirical.mean()) if len(ok) else None,
                  coverage_delivered=float(ok.coverage_delivered.dropna().mean()) if len(ok) and ok.coverage_delivered.notna().any() else None,
                  band_delivered=ok.band_delivered.value_counts().to_dict() if len(ok) else {},
                  seconds_per_series=float(frame.seconds.mean()), forced_baseline_share=float(ok.forced_baseline.mean()) if len(ok) else None,
                  selected=ok.selected.value_counts().to_dict() if len(ok) else {}, errors=int(len(frame) - len(ok)), reference=REFERENCES.get(name, ''))
    REPORTS.mkdir(parents=True, exist_ok=True)
    frame.to_csv(REPORTS / f'{name}-series.csv', index=False)
    results_path = REPORTS / 'results.json'
    all_results = json.loads(results_path.read_text()) if results_path.exists() else {}
    all_results[f'{name}:{pool}'] = result; results_path.write_text(json.dumps(all_results, indent=2) + '\n')
    (REPORTS / f'{name}-{pool}.md').write_text(report_md(result, frame))
    write_readme(all_results)
    return result, frame


def write_readme(all_results):
    """One table over every benchmarked route, regenerated after each run."""
    lines = ['# Benchmarks', '',
             'Public datasets fetched by `scripts/benchmark.py` with SHA-256 verification (nothing is bundled). Each route runs the engine at its default of five selection origins on a fixed-seed subset and is scored on the untouched test period. The floor the tests hold the engine to: MASE no worse than seasonal naive, and the delivered 80 percent band (`band_lower/upper`: the model band, the conformal band, or their midpoint when the holdout showed one too narrow and the other too wide) between 70 and 95 percent coverage; the model and conformal bands are reported beside it. Published references are context only; subsets, horizons and pre-processing differ.', '',
             '| Route | Series | Horizon | Engine MASE | Seasonal naive MASE | Engine sMAPE | Seasonal naive sMAPE | Model band 80% | Conformal band 80% | Delivered band 80% | s per series | Reference |', '|---|---|---|---|---|---|---|---|---|---|---|---|']
    for key, r in sorted(all_results.items()):
        fmt = lambda v, f='{:.3f}': (f.format(v) if v is not None else 'n/a')
        lines.append(f"| {key} | {r['scored']} | {r['horizon']} | {fmt(r['mase_engine'])} | {fmt(r['mase_snaive'])} | {fmt(r['smape_engine'], '{:.2f}')} | {fmt(r['smape_snaive'], '{:.2f}')} | {fmt(r['coverage_model'], '{:.0%}')} | {fmt(r['coverage_conformal'], '{:.0%}')} | {fmt(r.get('coverage_delivered'), '{:.0%}')} | {r['seconds_per_series']:.1f} | {r['reference']} |")
    lines += ['', 'Per-series rows are in the `*-series.csv` files beside this file; `results.json` is what `tests/test_benchmark_floor.py` reads.', '',
              'M3 is listed in `benchmark_sources.json` but not fetched: forecasters.org returns 403 to scripted downloads. Place `M3C.xls` in `data/benchmarks/` by hand and `python scripts/benchmark.py m3` uses its monthly sheet.']
    (REPORTS / 'README.md').write_text('\n'.join(lines) + '\n')


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
    ap.add_argument('dataset', nargs='?'); ap.add_argument('--subset', type=int, default=50); ap.add_argument('--pool'); ap.add_argument('--budget-seconds', type=float); ap.add_argument('--list', action='store_true'); ap.add_argument('--seed', type=int, default=2026); ap.add_argument('--origins', type=int, default=5, help='selection origins per series (the engine default is 5)')
    a = ap.parse_args()
    if a.list or not a.dataset:
        for k, v in SOURCES.items():
            if isinstance(v, dict):
                print(f'{k:14s} route {v["route"]:14s} horizon {v["horizon"]:3d} season {v["season"]}' + (f'   ({v["unavailable"]})' if v.get('unavailable') else ''))
        sys.exit(0)
    if SOURCES[a.dataset].get('unavailable') and not (DATA / SOURCES[a.dataset]['file']).exists():
        sys.exit(f'{a.dataset}: {SOURCES[a.dataset]["unavailable"]}')
    r, _ = run(a.dataset, a.subset, a.pool, a.budget_seconds, a.seed, a.origins)
    print(json.dumps({k: v for k, v in r.items() if k != 'selected'}, indent=2)); print('selected:', r['selected'])
