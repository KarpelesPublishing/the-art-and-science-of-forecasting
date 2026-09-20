# Your first forecast in thirty minutes

One complete pass through the seven gates on the shipped file `companion/data/examples/first-forecast.csv`:
84 months of unit sales for one product, January 2019 to December 2025. Nothing here needs prior
knowledge. Every command runs from the project root; `PY` stands for `companion/.venv/bin/python`.
The numbers below are what the commands actually printed on 2026-09-20; yours will match.

## Gate 1: the brief

```bash
$PY companion/scripts/run.py brief --output work/brief.json \
  --target "monthly unit sales of sku-01" --units units \
  --decision "how many units to order for the next six months" \
  --horizon 6 --frequency monthly --as-of 2025-12-01 \
  --cost-of-over "unsold stock, about 2 per unit per month" --cost-of-under "lost sales, about 15 per unit" \
  --known-in-advance nothing --outcome-date 2026-07-01 --audience "the owner, wants one number and a range"
```

It ends with `Usable for a forecast: yes`. Leave any answer out and it prints the question to ask.
Notice what the brief already decided: six months ahead, monthly, nothing known in advance, and
being short costs about seven times more than being long. That last fact will decide which end of the
range to order to.

## Gate 2: the profile

```bash
$PY companion/scripts/run.py profile --input companion/data/examples/first-forecast.csv --brief work/brief.json --output work
```

```text
Observations: 84 (2019-01-01 to 2025-12-01), frequency MS
Season: 12 detected from the data [12]
Demand class: smooth (0% zeros)
Trend: up; transform: none; outliers: 0
Floor for horizon 6: 48 observations
Route: engine
  - a regular series with enough history: the chapter 12 engine (smoothing, ARIMA, Theta, STL, LightGBM, combinations) at rolling origins
```

The data are monthly, seasonal with a yearly cycle, trending up, with no gaps and no outliers, and
there is enough history (84 against a floor of 48). The route is the ordinary engine. If the profile had
said `intermittent`, `multiseasonal`, `short` or `unusable`, the table in the skill says where to go.

## Gate 3: the baseline

The engine computes seasonal naive at every origin; it appears in the leaderboard after gate 4. Say it
out loud before modelling: "if next year simply repeats last year's pattern, the six months would come
to roughly the same as January to June 2025". A method earns its place only by beating that.

## Gate 4: the method

```bash
echo '{"source": "shipped example first-forecast.csv", "units": "units"}' > work/config.json
$PY companion/scripts/run.py apply --chapter 12 --input companion/data/examples/first-forecast.csv \
  --config work/config.json --output work/run --brief work/brief.json
```

No season, horizon or frequency in the config: the profile found the season, the brief set the rest.
The run writes `work/run/summary.json`, `results.csv`, `diagnostic.png`, `brief.json`, `profile.json`
and `run.json`.

## Gate 5: validation

From `summary.json`:

```text
status: passed
selected: Airline ARIMA
interpretation: Airline ARIMA had the lowest mean validation MAE (6.12); the runner-up was ETS(auto) (6.26).
                Final-holdout MAE for the selection: 11.1 against 13.5 for Seasonal naive. Validation MAE of Seasonal naive: 11.1.
leaderboard (validation MAE): Airline ARIMA 6.12, ETS(auto) 6.26, Combination(top3) 6.45, Theta 6.57, Weighted ensemble 7.65, ... Seasonal naive 11.13
holdout MAE: Airline ARIMA 11.08, Seasonal naive 13.5
not_done: no regressors or calendar effects; no hierarchy; intervals are the model's own plus empirical quantiles
```

Three sentences for the reader: the airline model beat the seasonal-naive baseline at the selection
origins and on the untouched last six months (11.1 against 13.5, about 18 percent better); the tool
did not use any drivers or calendar effects, because the brief said nothing is known in advance; the
status is `passed`, so the comparison the chapter requires was done.

## Gate 6: uncertainty

```text
test_interval_coverage: Airline ARIMA 0.5   (nominal 0.8)
```

This is the honest part. The model's own 80 percent band covered only half of the holdout months, so it
is too narrow; quote that, not the nominal 80. The table also carries `conformal_lower/upper`, a
split-conformal band built from the model's residuals at every selection origin (the report uses this
one), and `empirical_q10/q90`. With the brief's cost asymmetry (being short costs seven times more
than being long), the order should lean to the upper end of the band, not the middle. For a band
calibrated on a longer window, run chapter 17 on the same file.

## Gate 7: report and journal

```bash
$PY companion/scripts/run.py report --run work/run
$PY companion/scripts/run.py journal add --run work/run
```

`work/run/report.md` shows the six monthly numbers with their range (the first is 250.5, conformal range
238 to 263.1; the six sum to about 1,600 units), the leaderboard against the baseline, the profile, the
assumptions and the not-done list, and every one of its numbers is listed in `claims.json` with its
source. Now write two sentences of your own interpretation into `work/interpretation.md` and check them:

```bash
$PY companion/scripts/run.py report --run work/run --check work/interpretation.md
```

If you wrote "order 1,700 units", the check reports that 1,700 has no source in the run; change it to
the number the claims support, or add the reasoning (upper band, cost asymmetry) as words rather than a
new number.

On 2026-07-01 the six actuals will be known. Put them in a file with `timestamp,actual` and run:

```bash
$PY companion/scripts/run.py journal score --actuals actuals.csv
$PY companion/scripts/run.py journal calibration
```

After five scored forecasts the calibration report tells you whether your bands hold and which way
your errors lean. That is the moment you become a better forecaster than you were; nothing in the
first six gates does it for you.
