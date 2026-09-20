"""Optional heavy libraries: used when installed, named when absent, never required.

`pip install -e "companion[best]"` adds statsforecast, mlforecast, hierarchicalforecast and
neuralforecast. Every use in the engine goes through `have()`, and a candidate whose package is
missing is listed under `unavailable` in the summary with the install hint, so a reader can see
what a fuller environment would have tried.
"""
from functools import lru_cache
import importlib.util

EXTRAS = {
    'statsforecast': 'pip install statsforecast   (or: pip install -e "companion[best]")',
    'mlforecast': 'pip install mlforecast   (or: pip install -e "companion[best]")',
    'hierarchicalforecast': 'pip install hierarchicalforecast   (or: pip install -e "companion[best]")',
    'neuralforecast': 'pip install neuralforecast   (or: pip install -e "companion[best]")',
    'prophet': 'pip install prophet',
    'lightgbm': 'pip install lightgbm',
    'chronos': 'pip install chronos-forecasting torch',
    'timesfm': 'pip install timesfm',
}


@lru_cache(maxsize=None)
def have(name):
    return importlib.util.find_spec(name) is not None


def hint(name):
    return EXTRAS.get(name, f'pip install {name}')


def describe_extras():
    return {name: have(name) for name in EXTRAS}
