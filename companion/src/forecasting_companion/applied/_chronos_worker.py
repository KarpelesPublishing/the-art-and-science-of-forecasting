"""Chronos inference in its own process.

torch and lightgbm each ship an OpenMP runtime; loading both into one process
aborts on macOS. The foundation tool therefore sends contexts to this worker over
stdin as JSON and reads the sampled quantiles back from stdout.
"""
import json
import sys
import time


def main():
    job = json.load(sys.stdin)
    import numpy as np
    import torch
    from chronos import ChronosPipeline
    torch.manual_seed(int(job['seed'])); torch.set_num_threads(1)
    pipeline = ChronosPipeline.from_pretrained(job['model'], revision=job['revision'], device_map='cpu', dtype=torch.float32)
    out = []
    for ctx in job['contexts']:
        start = time.perf_counter()
        with torch.inference_mode():
            draws = pipeline.predict([torch.tensor(ctx, dtype=torch.float32)], prediction_length=int(job['horizon']), num_samples=int(job['samples'])).numpy()[0]
        out.append(dict(quantiles={str(q): np.quantile(draws, q, axis=0).tolist() for q in job['quantiles']}, latency_s=time.perf_counter() - start))
    sys.stdout.write(json.dumps(out))


if __name__ == '__main__':
    main()
