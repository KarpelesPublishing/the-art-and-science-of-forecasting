"""Pretrained models as candidates at the same origins as everything else.

Chronos-T5 tiny is cached and pinned; Chronos-Bolt small is about 190 MB and downloads only when
the environment variable FORECAST_ALLOW_DOWNLOADS=1 is set, so a run never fetches weights without
the reader agreeing. Both run in the worker subprocess (torch and LightGBM cannot share a process
on macOS). Quantile output gives the model its own 80 percent band.
"""
import os
import numpy as np

MODELS = {
    'Chronos': dict(model='amazon/chronos-t5-tiny', revision='29d808298f1a62493e7b9a5e08529d0d930fa189', download=None, samples=64),
    'Chronos-Bolt': dict(model='amazon/chronos-bolt-small', revision=None, download='about 190 MB', samples=0),
}


def _predict(name, y, h):
    from .applied.tools_foundation import chronos_predict
    spec = MODELS[name]
    if spec['download'] and os.environ.get('FORECAST_ALLOW_DOWNLOADS') != '1':
        raise ValueError(f'{name} needs a {spec["download"]} download; set FORECAST_ALLOW_DOWNLOADS=1 after the reader agrees')
    (q, _), = chronos_predict([np.asarray(y, float)], model=spec['model'], revision=spec['revision'], horizon=int(h), samples=spec['samples'], quantiles=[0.1, 0.5, 0.9], seed=15)
    return q


def _fit(name):
    def fit(y, h, s, spec, freq):
        from .engine import Fit
        if len(y) < 20:
            raise ValueError('foundation candidates want at least 20 observations of context')
        q = _predict(name, y, h)
        return Fit(np.asarray(q[0.5], float), np.asarray(q[0.1], float), np.asarray(q[0.9], float))
    fit.__name__ = f'fit_{name.lower().replace("-", "_")}'
    return fit


fit_chronos = _fit('Chronos')
fit_chronos_bolt = _fit('Chronos-Bolt')
