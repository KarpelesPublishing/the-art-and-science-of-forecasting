# Benchmark: m4-monthly with pool `full`

32 of 40 series scored (8 errors), horizon 18, season 12, 5.5 s per series.

| Measure | Engine | Seasonal naive |
|---|---|---|
| sMAPE | 10.50 | 13.36 |
| MASE | 0.860 | 1.084 |

Band coverage at nominal 80%: model band 80%, conformal 79%, empirical quantiles 46%.

Selected models: {'ARIMA(auto)': 7, 'Equal ensemble': 5, 'Theta': 4, 'ETS(auto)': 2, 'Drift': 2, 'STL+ETS': 2, 'SES': 2, 'Weighted ensemble': 2, 'Airline ARIMA': 2, 'Holt': 2, 'Damped Holt': 1, 'Combination(top3)': 1}. Baseline forced by the robustness rule on 0% of series.

Published reference (context, not a like-for-like comparison; subsets and horizons differ): M4 Theta sMAPE 13.00 (monthly), Comb benchmark 13.43; winner (Smyl) 12.13

Every series row is in the companion CSV beside this file.
