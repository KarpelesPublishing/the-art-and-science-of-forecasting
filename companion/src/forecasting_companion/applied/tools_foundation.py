"""Chapter 15: a pretrained foundation model, checked like any other model.

Chronos-T5 at a chosen checkpoint (tiny cached and pinned; larger sizes download on
request), run in a separate worker process so it can share a session with LightGBM,
sampled quantile forecasts at several origins plus the final holdout, latency
per call, and a comparison with the engine's baseline pool on identical origins.
"""
import os
from pathlib import Path
import numpy as np
import pandas as pd
from .core import time_frame, integer, expanding_origins, finish

CHECKPOINTS = {
    'tiny': dict(model='amazon/chronos-t5-tiny', revision='29d808298f1a62493e7b9a5e08529d0d930fa189', download=None),
    'mini': dict(model='amazon/chronos-t5-mini', revision=None, download='about 80 MB'),
    'small': dict(model='amazon/chronos-t5-small', revision=None, download='about 185 MB'),
    'base': dict(model='amazon/chronos-t5-base', revision=None, download='about 800 MB'),
}


def chronos_predict(contexts, *, model, revision, horizon, samples, quantiles, seed):
    """Run the worker process once for all contexts; returns per-context quantile dicts and latencies."""
    import subprocess, sys, json
    job = dict(model=model, revision=revision, horizon=horizon, samples=samples, quantiles=quantiles, seed=seed, contexts=[list(map(float, c)) for c in contexts])
    proc = subprocess.run([sys.executable, '-m', 'forecasting_companion.applied._chronos_worker'], input=json.dumps(job), capture_output=True, text=True,
                          env={**os.environ, 'PYTHONPATH': os.pathsep.join([str(Path(__file__).resolve().parents[2])] + [p for p in [os.environ.get('PYTHONPATH')] if p]), 'TOKENIZERS_PARALLELISM': 'false'})
    if proc.returncode != 0:
        raise RuntimeError('Chronos worker failed: ' + proc.stderr.strip().splitlines()[-1] if proc.stderr.strip() else 'Chronos worker failed')
    out = json.loads(proc.stdout)
    return [({float(k): np.asarray(v) for k, v in r['quantiles'].items()}, r['latency_s']) for r in out]


def foundation_forecast(d, c):
    from ..engine import forecast_series
    checkpoint = c.get('checkpoint', 'tiny')
    if checkpoint not in CHECKPOINTS:
        raise ValueError(f'checkpoint must be one of {sorted(CHECKPOINTS)}')
    quantiles = c.get('quantiles', [0.1, 0.5, 0.9])
    if not isinstance(quantiles, list) or not quantiles or any(not 0 < q < 1 for q in quantiles) or 0.5 not in quantiles:
        raise ValueError('quantiles must be a list in (0,1) that includes 0.5')
    h = integer(c, 'horizon', 12); s = integer(c, 'season', 12); n_origins = integer(c, 'origins', 3, 1); samples = integer(c, 'samples', 64, 8)
    f, freq = time_frame(d, c, minimum=max(3 * s, h + 30)); y = f.target.to_numpy(float); n = len(y)
    spec = CHECKPOINTS[checkpoint]
    origins = expanding_origins(n, h, max(3 * s, 30), n_origins) + [n - h]
    lo_q, hi_q = min(quantiles), max(quantiles)
    results = chronos_predict([y[:o] for o in origins] + [y], model=spec['model'], revision=spec['revision'], horizon=h, samples=samples, quantiles=quantiles, seed=integer(c, 'seed', 15, 0))
    per_origin = []; latencies = []
    for o, (qs, lat) in zip(origins, results[:-1]):
        actual = y[o:o + h]; latencies.append(lat)
        per_origin.append(dict(origin=str(f.timestamp.iloc[o - 1]), holdout=o == n - h, median_mae=float(np.abs(qs[0.5] - actual).mean()),
                               coverage=float(np.mean((actual >= qs[lo_q]) & (actual <= qs[hi_q]))), latency_s=lat))
    _, base = forecast_series(y, f.timestamp, h, s, pool='baseline', freq=freq, max_origins=n_origins)
    engine_origins = base['origins']
    assert engine_origins == [str(f.timestamp.iloc[o - 1]) for o in origins[:-1]], 'origin mismatch with the engine'
    engine_scores = {r['model']: r['mae'] for r in base['leaderboard']}
    qs_future, lat = results[-1]; latencies.append(lat); dates = pd.date_range(f.timestamp.iloc[-1], periods=h + 1, freq=freq)[1:]
    table = pd.DataFrame({'timestamp': dates, 'forecast': qs_future[0.5], **{f'q{int(q * 100):02d}': qs_future[q] for q in quantiles}})
    sel = [r for r in per_origin if not r['holdout']]
    interpretation = (f'Chronos {checkpoint}: mean median-MAE over {len(sel)} selection origins {np.mean([r["median_mae"] for r in sel]):.4g} vs engine baselines ' + ', '.join(f'{k} {v:.4g}' for k, v in engine_scores.items())
                      + f'; final holdout MAE {per_origin[-1]["median_mae"]:.4g}, coverage of the {lo_q}-{hi_q} band {per_origin[-1]["coverage"]:.0%}. Mean latency {np.mean(latencies):.2f} s per call on CPU. '
                      + 'Pretraining overlap with this series is not certified; one holdout cannot establish calibration.')
    return finish(table, method=f'Chronos-T5 {checkpoint} zero-shot forecast', interpretation=interpretation,
                  assumptions=['Series treated as univariate without covariates', 'Sampled quantiles from the pretrained model at the given seed'],
                  not_done=['No fine-tuning', 'No covariates', 'Pretraining corpus exclusion not verified'] + ([f'Download of {spec["download"]} was required for this checkpoint'] if spec['download'] else []),
                  status='passed', checkpoint=checkpoint, model_id=spec['model'], revision=spec['revision'], download_warning=spec['download'],
                  origins=[r['origin'] for r in per_origin], per_origin=per_origin, engine_baselines=engine_scores, test_mae=per_origin[-1]['median_mae'], test_coverage=per_origin[-1]['coverage'],
                  mean_latency_s=float(np.mean(latencies)), quantiles=quantiles, samples=samples)
