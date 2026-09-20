# Harness: uplift and repeatability

9 scored runs.

| Persona | Arm | Runs | Process (mean) | Process (min) | MAE/baseline (mean over series tasks) | Band coverage (mean) | Delivered |
|---|---|---|---|---|---|---|---|
| expert | legacyplain | 1 | 33% | 33% | 0.67 | 71% | 100% |
| expert | legacyskill | 1 | 48% | 48% | 0.70 | 81% | 100% |
| expert | plain | 1 | 43% | 43% | 0.56 | 87% | 100% |
| expert | skill | 2 | 95% | 90% | 0.55 | 79% | 100% |
| novice | plain | 1 | 32% | 32% | 0.52 | 84% | 100% |
| novice | skill | 3 | 98% | 95% | 0.54 | 52% | 100% |

## Spread

- skill: process scores range 95% to 98% across personas; MAE/baseline range 0.54 to 0.55.
- plain: process scores range 32% to 43% across personas; MAE/baseline range 0.52 to 0.56.

Success means: with the skill every persona passes every process check, and the spread between personas is smaller than without the skill.
