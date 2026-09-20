# Benchmark: m4-quarterly with pool `full`

37 of 40 series scored (3 errors), horizon 8, season 4, 2.1 s per series.

| Measure | Engine | Seasonal naive |
|---|---|---|
| sMAPE | 12.61 | 12.21 |
| MASE | 1.230 | 1.410 |

Band coverage at nominal 80%: model band 77%, conformal 85%, empirical quantiles 49%.

Selected models: {'ARIMA(auto)': 8, 'Naive': 5, 'Drift': 4, 'Airline ARIMA': 4, 'Equal ensemble': 3, 'Damped Holt': 3, 'Theta': 2, 'STL+ETS': 2, 'Holt': 2, 'Seasonal naive': 2, 'SES': 1, 'ETS(auto)': 1}. Baseline forced by the robustness rule on 0% of series.

Published reference (context, not a like-for-like comparison; subsets and horizons differ): M4 Theta sMAPE 10.31 (quarterly)

Every series row is in the companion CSV beside this file.
