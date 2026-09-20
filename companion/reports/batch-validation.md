# Local batch runner validation

Validated on 2026-09-18, Apple M4 Max / arm64,128 GiB physical RAM, Python 3.12,
NumPy 2.5.3, pandas 3.0.6. No cloud instances or paid services were used.

## Run it

From the book workspace, with the companion environment installed:

```sh
PYTHONPATH=companion/src companion/.venv/bin/python -m forecasting_companion.batch \
  --input panel.csv --output companion/results/batch \
  --horizon 12 --frequency MS --workers 4 --resume --as-of 2025-12-01
```

CSV columns are `series_id,timestamp,target`. IDs are read as literal strings,
including leading zeros and strings such as `NA`. The cutoff is inclusive and
interpreted in UTC; a date-only cutoff means midnight at the start of that day.
Observations after the cutoff do not enter fitting, validation, or input hashes.
Invalid dates cannot be safely placed on either side of a cutoff and cause a
per-series failure. Series with fewer than eight retained observations fail.
Duplicates, nonnumeric/nonfinite targets, frequency gaps, and off-grid timestamps
also fail individually. Missing required columns and invalid global configuration
raise an error before forecasting. Horizon must be 1–10,000 and workers 1–64.

The output directory contains:

- `forecast.csv`: one row per series, future timestamp, and requested quantile
  (0.1, 0.5, 0.9), with origin, horizon step, selected model, point forecast,
  value, status, band method, and residual count.
- `metrics.csv`: one row per series, including failures; successful rows contain
  validation MAE, origin counts, pair counts, and all candidate scores.
- `failures.json`: structured per-series errors. Failed series do not contribute
  fabricated rows to `forecast.csv`; their status remains visible in metrics.
- `run.json`: configuration, counts, runtime, and code fingerprint.
- `checkpoints/`: atomically published per-series JSON records.

## Forecast and uncertainty contract

The candidates are naive, endpoint drift, seasonal naive when history spans at
least two seasons, and an equal-weight ensemble of the eligible baseline models.
The ensemble weights are fixed. Monthly seasonality is 12, daily 7, business-day
5, hourly 24, and quarterly 4. Other or multiplied frequencies use no guessed
seasonality. There is no automatic frequency inference or missing-data filling.

Model selection uses pooled absolute error from up to five chronological,
expanding-window origins. Each forecast at each origin sees only prior values.
Ties favor the earliest candidate (naive first). Origins with fewer remaining
observations evaluate shorter horizons, so validation is not equally weighted
over horizons. The selected model is refit implicitly using the full retained
history before its final forecast is generated.

Bands use signed out-of-origin residual quantiles separately by forecast horizon.
For a horizon longer than any validated horizon, residuals from the longest
available horizon are scaled by the square root of the horizon ratio and marked
`empirical_signed_residual_sqrt_extrapolation`. This is an explicit heuristic.
The `point` column is the selected model's unadjusted point forecast; quantile
`value` adds the empirical residual quantile, so the 0.5 value need not equal
`point`. Quantiles remain ordered but the point need not lie within their range.

These are empirical residual bands, **not guaranteed calibrated prediction
intervals**. At most five residuals exist at a given horizon, sometimes just one;
origins overlap, residuals can be dependent, and the same validation outcomes
select the model and estimate its bands. Model-selection optimism is possible.
No final-test coverage claim is made. For operational interval calibration,
reserve more origins or an independent calibration period.

## Reuse and bounded concurrency

Checkpoint keys include the literal series ID, sorted retained input rows,
horizon, normalized frequency, cutoff, NumPy/pandas versions, and a SHA-256 hash
of the complete batch implementation. A changed series invalidates only itself;
changed configuration or code invalidates all affected records. Worker count
does not change mathematical results and is not part of the key. Checkpoint
contents have a separate integrity digest; corrupt records are recomputed.
Failed series are also checkpointed and reused until their input/config changes.
Old checkpoint versions are retained rather than deleted.

The runner uses a fixed thread pool and submits at most twice the worker count
at once. It reads the input and collects final output in memory; it is not a
streaming, distributed, or cloud-scale system. It does not impose hard per-series
timeouts: Python threads cannot be safely terminated, and these fixed baseline
calculations do not call external model services. Interrupted runs can reuse
completed checkpoints. Aggregate CSV publication is not transactional, so after
an interruption rerun with `--resume` before consuming aggregate outputs. Two
independent processes should not write the same output directory concurrently.

## Measured execution

Input: 1,000 seeded synthetic monthly series, 48 observations each (48,000 input
rows), 12-step forecasts, four workers. Each series combined a linear trend,
12-month sine wave, and independent Gaussian noise, using seed 20260918. The
result contained 36,000 forecast rows and 1,000 successful metrics records, with
zero failures. This is a mechanics/load test, not an accuracy benchmark.

| Run | Runner time | CLI wall time | Approximate runner throughput | Peak resident memory |
| --- | ---: | ---: | ---: | ---: |
| Compute all 1,000 | 2.081 s | 2.25 s | 480 series/s | 122.9 MiB |
| Resume all 1,000 | 0.375 s | 0.55 s | 2,670 records/s | 131.8 MiB |

Runtime comes from `perf_counter`; CLI wall time and process maximum resident
set size come from macOS `/usr/bin/time -l` (reported memory converted from bytes).
These are single local observations, not repeated confidence intervals. Other
workspace tests were running during the compute measurement. Filesystem caching,
machine load, history length, horizon, and checkpoint size affect performance.
Resume still reads/checks input and rewrites aggregate output, so it consumes
memory and does not have zero cost. No multi-worker speedup claim is made.

## Automated checks

`companion/.venv/bin/python -m pytest companion/tests/test_batch.py -q`

The 11 test cases execute the actual 1,000-series run and its complete resume;
verify finite ordered quantiles and literal IDs; inject duplicate keys,
nonfinite/nonnumeric targets, gaps, invalid dates, and short histories; assert
successful series survive neighboring failures; test input/config/code cache
invalidation; test corrupted checkpoint recovery; reject invalid horizons,
frequency, and worker counts; and prove that changing post-cutoff targets cannot
change an as-of forecast or invalidate its checkpoint.
