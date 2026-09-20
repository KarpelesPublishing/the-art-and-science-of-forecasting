"""Pretrained-model inference in its own process.

torch and lightgbm each ship an OpenMP runtime; loading both into one process aborts on macOS.
The foundation tool and the engine's foundation candidates send contexts to this worker over
stdin as JSON and read 10/50/90 quantiles back from stdout. Backends: Chronos-T5 (sampled paths),
Chronos-Bolt (direct quantiles), TimesFM 2.5 (quantile head). The backend is read from the model id.
"""
import json
import sys
import time


def _chronos(job, contexts, qs):
    import numpy as np
    import torch
    model = job['model']; bolt = 'bolt' in model
    if bolt:
        from chronos import BaseChronosPipeline
        pipeline = BaseChronosPipeline.from_pretrained(model, revision=job.get('revision'), device_map='cpu', dtype=torch.float32)
    else:
        from chronos import ChronosPipeline
        pipeline = ChronosPipeline.from_pretrained(model, revision=job.get('revision'), device_map='cpu', dtype=torch.float32)
    out = []
    for ctx in contexts:
        start = time.perf_counter()
        with torch.inference_mode():
            if bolt:
                q, _ = pipeline.predict_quantiles([torch.tensor(ctx, dtype=torch.float32)], prediction_length=int(job['horizon']), quantile_levels=qs)
                arr = q[0].numpy(); quantiles = {str(lvl): arr[:, i].tolist() for i, lvl in enumerate(qs)}
            else:
                draws = pipeline.predict([torch.tensor(ctx, dtype=torch.float32)], prediction_length=int(job['horizon']), num_samples=int(job['samples'])).numpy()[0]
                quantiles = {str(lvl): np.quantile(draws, lvl, axis=0).tolist() for lvl in qs}
        out.append(dict(quantiles=quantiles, latency_s=time.perf_counter() - start))
    return out


def _timesfm(job, contexts, qs):
    """TimesFM 2.5 (200M, PyTorch): quantile head returns [mean, q10, q20, ..., q90] per step."""
    import numpy as np
    import torch
    import timesfm
    torch.set_num_threads(1)
    h = int(job['horizon']); context = int(min(2048, max(32, max(len(c) for c in contexts))))
    model = timesfm.TimesFM_2p5_200M_torch.from_pretrained(job['model'], revision=job.get('revision'))
    model.compile(timesfm.ForecastConfig(max_context=context, max_horizon=max(h, 1), normalize_inputs=True, use_continuous_quantile_head=True, fix_quantile_crossing=True))
    out = []
    for ctx in contexts:
        start = time.perf_counter()
        point, quant = model.forecast(h, [np.asarray(ctx, float)])
        arr = np.asarray(quant)[0]                     # (h, 10): column 0 is the mean, columns 1..9 are q10..q90
        quantiles = {str(lvl): arr[:h, int(round(lvl * 10))].tolist() for lvl in qs}
        out.append(dict(quantiles=quantiles, latency_s=time.perf_counter() - start))
    return out


def main():
    job = json.load(sys.stdin)
    contexts = job['contexts']; qs = [float(q) for q in job['quantiles']]
    backend = _timesfm if 'timesfm' in job['model'].lower() else _chronos
    sys.stdout.write(json.dumps(backend(job, contexts, qs)))


if __name__ == '__main__':
    main()
