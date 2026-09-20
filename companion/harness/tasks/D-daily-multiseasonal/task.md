# Task D: daily store visits for the next four weeks

`data.csv` has two years of daily visits to one store (`timestamp,target,promo`; `promo` is 1 on days a
promotion ran). `future_promo.csv` gives the promotion days already scheduled for the next 28 days.
The store manager needs a daily staffing plan: how many visits each day for the 28 days after the last
date in the file, with a range, and a note on which days are uncertain. Being understaffed costs about
three times as much as being overstaffed. Deliver `forecast.csv` with `timestamp,forecast,lower,upper`
(28 rows, a stated coverage level) and `report.md`.
