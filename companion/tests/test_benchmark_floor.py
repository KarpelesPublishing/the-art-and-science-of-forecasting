"""When benchmark results exist, the engine must clear its floor on every route it claims."""
from pathlib import Path
import json
import pytest

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / 'reports/benchmarks/results.json'


@pytest.mark.skipif(not RESULTS.exists(), reason='run scripts/benchmark.py first')
def test_engine_clears_the_floor_on_every_benchmarked_route():
    results = json.loads(RESULTS.read_text())
    assert results, 'no benchmark rows'
    for key, r in results.items():
        if r.get('scored', 0) < 10:
            continue
        assert r['mase_engine'] <= r['mase_snaive'] * 1.02, f'{key}: engine MASE {r["mase_engine"]:.3f} worse than seasonal naive {r["mase_snaive"]:.3f}'
        covs = [c for c in (r.get('coverage_model'), r.get('coverage_conformal')) if c is not None]
        if covs:
            assert max(covs) >= 0.65, f'{key}: the best 80% band covered only {max(covs):.0%}'
