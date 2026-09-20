# Data for the workshops

`registry.json` records public-domain dataset metadata, source URLs, package version,
transformations and checksums. `observed/` contains bundled historical observations;
`examples/chNN.csv` (JSON for chapter 10) contains explicitly seeded synthetic input
examples. These files are examples of schemas, not the reader's business forecasts.

The real-data applications use monthly Niño 1+2 sea-surface temperatures (degrees
Celsius) and annual Nile flow (10^8 cubic metres). Macrodata, Grunfeld investment,
and June manufacturing-strike durations are included for documented exercises and
extensions. These are historical snapshots, not archived real-time release vintages.
The package's original dataset metadata is preserved in the registry. For source
policy see https://www.statsmodels.org/stable/dev/dataset_notes.html.

Do not force available data into an unrelated method. The package does not contain
verified expert forecasts, Delphi panels, primary-market OHLC, causal experiments,
retail promotion schedules, adoption cohorts, marketing spend, or epidemic reporting
vintages. Those workshops use controlled simulations and require reader-supplied
observations for real applications. An observed outcome is not an archived forecast.

Grunfeld has only 20 years per firm and is not enough to certify neural performance.
Nile regime changes do not identify a causal intervention. Strike durations are a
narrow June-only reference class, not project-overrun evidence. No claim is made
that synthetic uncertainty is calibrated on real business data.

Chapter 27 now uses synthetic reference products with explicit trial/repeat
assumptions; it does not import the legacy reconciliation example. The standard
trial denominator is the author-confirmed 24-month horizon. Model weights for the
pinned Chronos checkpoint are downloaded separately and are not redistributed.

Rebuild these snapshots/examples with `companion/.venv/bin/python
companion/scripts/build_workshop_data.py`. This intentionally rewrites bundled data;
it is a maintainer command, not needed for reader execution.
