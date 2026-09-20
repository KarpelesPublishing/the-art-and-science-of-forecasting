"""Chronos inference in its own process.

torch and lightgbm each ship an OpenMP runtime; loading both into one process
aborts on macOS. The foundation tool and the engine's foundation candidates send
contexts to this worker over stdin as JSON and read quantiles back from stdout.
Two families: Chronos-T5 (sampled paths, `predict`) and Chronos-Bolt (direct
quantiles, `predict_quantiles`).
"""
import json
import sys
import time


def main():
    job = json.load(sys.stdin)
    import numpy as np
    import torch
    torch.manual_seed(int(job['seed'])); torch.set_num_threads(1)
    model = job['model']; qs = [float(q) for q in job['quantiles']]
    bolt = 'bolt' in model
    if bolt:
        from chronos import BaseChronosPipeline
        pipeline = BaseChronosPipeline.from_pretrained(model, revision=job.get('revision'), device_map='cpu', dtype=torch.float32)
    else:
        from chronos import ChronosPipeline
        pipeline = ChronosPipeline.from_pretrained(model, revision=job.get('revision'), device_map='cpu', dtype=torch.float32)
    out = []
    for ctx in job['contexts']:
        start = time.perf_counter()
        with torch.inference_mode():
            if bolt:
                q, _ = pipeline.predict_quantiles([torch.tensor(ctx, dtype=torch.float32)], prediction_length=int(job['horizon']), quantile_levels=qs)
                arr = q[0].numpy()                       # (horizon, len(qs))
                quantiles = {str(lvl): arr[:, i].tolist() for i, lvl in enumerate(qs)}
            else:
                draws = pipeline.predict([torch.tensor(ctx, dtype=torch.float32)], prediction_length=int(job['horizon']), num_samples=int(job['samples'])).numpy()[0]
                quantiles = {str(lvl): np.quantile(draws, lvl, axis=0).tolist() for lvl in qs}
        out.append(dict(quantiles=quantiles, latency_s=time.perf_counter() - start))
    sys.stdout.write(json.dumps(out))


if __name__ == '__main__':
    main()
