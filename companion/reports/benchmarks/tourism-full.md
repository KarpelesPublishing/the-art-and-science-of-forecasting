# Benchmark: tourism with pool `full`

39 of 40 series scored (1 errors), horizon 24, season 12, 6.4 s per series.

| Measure | Engine | Seasonal naive |
|---|---|---|
| sMAPE | 21.12 | 23.53 |
| MASE | 1.502 | 1.659 |

Band coverage at nominal 80%: model band 87%, conformal 77%, empirical quantiles 53%.

Selected models: {'ETS(auto)': 7, 'Airline ARIMA': 6, 'Theta': 5, 'Equal ensemble': 5, 'Weighted ensemble': 5, 'ARIMA(auto)': 4, 'Seasonal naive': 2, 'Combination(top3)': 2, 'Damped Holt': 1, 'Drift': 1, 'STL+ETS': 1}. Baseline forced by the robustness rule on 5% of series.

Published reference (context, not a like-for-like comparison; subsets and horizons differ): Tourism competition: seasonal naive and damped ETS were hard to beat on monthly series

Every series row is in the companion CSV beside this file.
