# novice-skill-3 summary

## Task G (level shift), folder `G-level-shift/`

Workflow followed: `forecasting-skills/forecast-workflow/SKILL.md`, all seven gates, commands run from the project root with the companion venv. Nothing under `companion/harness/truth` was opened. No files outside the run folder were modified.

### Delivered

- `forecast.csv` (timestamp,forecast,lower,upper): twelve months, 2026-01 to 2026-12, taken from the `break_scenario`, `break_scenario_low` and `break_scenario_high` columns of `run/results.csv`, as the workflow's level-shift rule directs when nothing says the shift will reverse. Annual total 3,582 units, range 3,504 to 3,660.
- `report.md`: my interpretation followed by the two rendered reports (chapter 12 and chapter 24) verbatim.
- `interpretation.md`: the interpretation alone; `run.py report --run run --check interpretation.md --also run-ch24` reports every number supported.
- `brief.json` (gate 1), `profile.json` and `config.json` (gate 2), `run/` (chapter 12 engine: summary.json, results.csv, report.md, claims.json with 88 sourced numbers, diagnostic.png, run.json), `run-ch24/` (chapter 24 structural breaks, same file: summary.json, results.csv, report.md, claims.json), `journal.jsonl` (one entry, id cd404555086d, scoring date 2027-01-01).

### What the evidence said

- Profile: 120 monthly observations, season 12 found from the data, trend up, no gaps or outliers, route `engine`, warning of a level shift 8 periods before the end (328.1 to 291.9).
- Chapter 12: selected Combination(top3), status `passed`, validation MAE 3.855 vs 7.508 seasonal naive at five origins, but holdout MAE 39.88 vs 39.3 for the baseline because the holdout contains the shift. Its own twelve-month total is 3,513.
- Chapter 24: last changepoint dated 2025-05-01 (agrees with the profile), strongest split 2025-08-01; adaptive policy best (MAE 16.86 vs frozen 25.42).
- Bands: conformal holdout coverage 0.3333 against nominal 0.8; every band predates the shift, so the delivered range is labelled a scenario, not an interval.

### What I could not do, and caveats

- `report.py` claims only the `forecast` and `conformal_*` columns, not `break_scenario*`. The scenario totals in my interpretation therefore pass the claim check only because they fall within its 2 percent tolerance of the model's claimed totals (3,582 vs 3,513; 3,504 vs 3,513). I state their provenance (run/results.csv columns) in the text. The scenario upper total (3,660) and the shift size (54.1) are not within tolerance and were written in words instead.
- `journal add` records the model's `forecast` rows (Combination(top3), total 3,513), not the delivered break-scenario rows; the tool has no option to journal the scenario column. The journal note says so.
- Checking the assembled `report.md` (rather than `interpretation.md`) flags `-54.1` and `12.5`: both are in the tools' own rendered `interpretation` strings (summary.json of run and run-ch24), not in my prose. I left the rendered reports verbatim.
- Chapter 24 was run on the raw seasonal series (its skill says deseasonalise first); I had no way to do that within the workflow's commands, so only its last changepoint, which agrees with the profile, is relied on. Its ten CUSUM alarms are not treated as ten breaks.
- The cost of undercommitting is unknown; the brief records "unknown" and the report says the median is reported for want of a cost asymmetry. The write-off rule (over 10 percent) is the only asymmetry used.

### Command failures

- None. All commands exited 0 except the two intended `--check` runs that listed unsupported numbers (exit 4), which were then fixed in `interpretation.md`; the final check on `interpretation.md` exits 0.
