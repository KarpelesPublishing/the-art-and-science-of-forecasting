# Benchmarks

Public datasets fetched by `scripts/benchmark.py` with SHA-256 verification (nothing is bundled). Each route runs the engine at its default of five selection origins on a fixed-seed subset and is scored on the untouched test period. The floor the tests hold the engine to: MASE no worse than seasonal naive, and the delivered 80 percent band (`band_lower/upper`: the model band, the conformal band, or their midpoint when the holdout showed one too narrow and the other too wide) between 70 and 95 percent coverage; the model and conformal bands are reported beside it. Published references are context only; subsets, horizons and pre-processing differ.

| Route | Series | Horizon | Engine MASE | Seasonal naive MASE | Engine sMAPE | Seasonal naive sMAPE | Model band 80% | Conformal band 80% | Delivered band 80% | s per series | Reference |
|---|---|---|---|---|---|---|---|---|---|---|---|
| m4-hourly:multiseasonal | 40 | 48 | 1.073 | 1.089 | 7.88 | 9.63 | 71% | 79% | 78% | 11.0 | M4 Theta sMAPE 18.14 (hourly); winner (Smyl) 9.33 |
| m4-monthly:full | 32 | 18 | 0.860 | 1.084 | 10.50 | 13.36 | 80% | 79% | 81% | 5.5 | M4 Theta sMAPE 13.00 (monthly), Comb benchmark 13.43; winner (Smyl) 12.13 |
| m4-quarterly:full | 37 | 8 | 1.230 | 1.410 | 12.61 | 12.21 | 77% | 85% | 85% | 2.1 | M4 Theta sMAPE 10.31 (quarterly) |
| m4-weekly:full | 34 | 13 | 0.448 | 1.195 | 5.12 | 12.37 | 88% | 67% | 70% | 13.6 | M4 Theta sMAPE 9.09 (weekly) |
| tourism:full | 39 | 24 | 1.502 | 1.659 | 21.12 | 23.53 | 87% | 77% | 83% | 6.4 | Tourism competition: seasonal naive and damped ETS were hard to beat on monthly series |

Per-series rows are in the `*-series.csv` files beside this file; `results.json` is what `tests/test_benchmark_floor.py` reads.

M3 is listed in `benchmark_sources.json` but not fetched: forecasters.org returns 403 to scripted downloads. Place `M3C.xls` in `data/benchmarks/` by hand and `python scripts/benchmark.py m3` uses its monthly sheet.
