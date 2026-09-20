# Benchmark: m4-weekly with pool `full`

34 of 40 series scored (6 errors), horizon 13, season 52, 13.6 s per series.

| Measure | Engine | Seasonal naive |
|---|---|---|
| sMAPE | 5.12 | 12.37 |
| MASE | 0.448 | 1.195 |

Band coverage at nominal 80%: model band 88%, conformal 67%, empirical quantiles 42%.

Selected models: {'STL+ETS': 5, 'ARIMA(auto)': 4, 'Holt': 4, 'Naive': 3, 'Equal ensemble': 3, 'Drift': 3, 'LightGBM': 3, 'Combination(top3)': 3, 'Theta': 2, 'Airline ARIMA': 1, 'Damped Holt': 1, 'Weighted ensemble': 1, 'ETS(auto)': 1}. Baseline forced by the robustness rule on 0% of series.

Published reference (context, not a like-for-like comparison; subsets and horizons differ): M4 Theta sMAPE 9.09 (weekly)

Every series row is in the companion CSV beside this file.
