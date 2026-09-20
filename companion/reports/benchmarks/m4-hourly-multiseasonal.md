# Benchmark: m4-hourly with pool `multiseasonal`

40 of 40 series scored (0 errors), horizon 48, season 24, 11.0 s per series.

| Measure | Engine | Seasonal naive |
|---|---|---|
| sMAPE | 7.88 | 9.63 |
| MASE | 1.073 | 1.089 |

Band coverage at nominal 80%: model band 71%, conformal 79%, empirical quantiles 59%.

Selected models: {'Seasonal naive': 14, 'Combination(top3)': 9, 'MSTL+ARIMA': 8, 'Fourier ARIMA': 5, 'Prophet': 4}. Baseline forced by the robustness rule on 5% of series.

Published reference (context, not a like-for-like comparison; subsets and horizons differ): M4 Theta sMAPE 18.14 (hourly); winner (Smyl) 9.33

Every series row is in the companion CSV beside this file.
