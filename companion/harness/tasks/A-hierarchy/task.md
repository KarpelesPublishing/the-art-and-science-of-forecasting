# Task A: regional and total sales, twelve months ahead

`data.csv` has six years of monthly sales for three regions (North, South, West) and their Total, in
long form (`node,timestamp,target`). The planner needs twelve monthly forecasts for each region and for
the total, and the regional numbers must add up to the total. Deliver `forecast.csv`
(`node,timestamp,forecast,lower,upper`, 48 rows, a stated coverage level) and `report.md`.
