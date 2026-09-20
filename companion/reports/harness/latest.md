# Harness: uplift and repeatability

16 scored runs.

| Persona | Arm | Runs | Process (mean) | Process (min) | MAE/baseline (mean over series tasks) | Band coverage (mean) | Delivered |
|---|---|---|---|---|---|---|---|
| expert | legacyplain-earlier | 1 | 33% | 33% | 0.67 | 71% | 100% |
| expert | legacyskill-earlier | 1 | 48% | 48% | 0.70 | 81% | 100% |
| expert | plain | 2 | 37% | 32% | 0.56 | 89% | 100% |
| expert | skill | 2 | 100% | 100% | 0.50 | 88% | 100% |
| expert | skill-earlier | 1 | 90% | 90% | 0.58 | 72% | 100% |
| intermediate | plain | 2 | 41% | 40% | 0.55 | 85% | 100% |
| intermediate | skill | 2 | 100% | 100% | 0.50 | 88% | 100% |
| novice | plain | 2 | 32% | 32% | 0.50 | 83% | 100% |
| novice | skill | 2 | 99% | 99% | 0.44 | 55% | 100% |
| novice | skill-earlier | 1 | 95% | 95% | 0.74 | 48% | 100% |

## Spread

- expert plain: process across 2 repeats ranges 32% to 43%.
- expert skill: process across 2 repeats ranges 100% to 100%.
- intermediate plain: process across 2 repeats ranges 40% to 43%.
- intermediate skill: process across 2 repeats ranges 100% to 100%.
- novice plain: process across 2 repeats ranges 32% to 32%.
- novice skill: process across 2 repeats ranges 99% to 100%.
- skill: process scores range 99% to 100% across personas; MAE/baseline range 0.44 to 0.50.
- plain: process scores range 32% to 41% across personas; MAE/baseline range 0.50 to 0.56.

Rows marked `-earlier` are runs made before the current skill text (the assumption ledger, the level-shift rule, the multi-run claim check) and are kept as history; `CURRENT.txt` names the runs of the current version. Success means: with the skill every persona passes every process check (minimum at or above 95 percent), the spread between personas is smaller than without the skill, and repeats agree.
