"""Generate the harness tasks with hidden truth. Deterministic; rerun after changing a generator.

Each task folder holds only what the assistant sees (task.md and data files); the hidden truth
lives in harness/truth/<task>.csv, outside the folders an assistant is given. score.py compares
the assistant's outputs with the truth.
Tasks A (hierarchy), B (launch) and C (intermittent) carry their original data; D to G are built here.
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
TASKS = HERE / 'tasks'
TRUTH = HERE / 'truth'          # kept outside the task folders so an assistant given a task folder cannot see it
rng = np.random.default_rng(2026)


def write_task(name, text):
    (TASKS / name).mkdir(parents=True, exist_ok=True)
    (TASKS / name / 'task.md').write_text(text.strip() + '\n')


def task_d():
    """Daily store traffic, two years plus a hidden 28 days: weekly and yearly cycles, national holidays, a promotion calendar known in advance."""
    n = 730 + 28; t = np.arange(n)
    dates = pd.date_range('2024-01-01', periods=n, freq='D')
    import holidays
    us = holidays.US(years=[2024, 2025, 2026])
    hol = np.array([d.date() in us for d in dates])
    promo = np.zeros(n, bool); promo[rng.choice(n, 40, replace=False)] = True
    weekly = np.array([0.0, -4, -6, -3, 5, 22, 18])[dates.dayofweek]
    y = 160 + 0.02 * t + weekly + 25 * np.sin(2 * np.pi * (t - 200) / 365.25) - 45 * hol + 30 * promo + rng.normal(0, 6, n)
    y = np.round(np.maximum(y, 0))
    frame = pd.DataFrame({'timestamp': dates.strftime('%Y-%m-%d'), 'target': y, 'promo': promo.astype(int)})
    frame.iloc[:730].to_csv(TASKS / 'D-daily-multiseasonal/data.csv', index=False) if (TASKS / 'D-daily-multiseasonal').mkdir(parents=True, exist_ok=True) is None else None
    frame.iloc[730:][['timestamp', 'promo']].to_csv(TASKS / 'D-daily-multiseasonal/future_promo.csv', index=False)
    frame.iloc[730:][['timestamp', 'target']].to_csv(TRUTH / 'D-daily-multiseasonal.csv', index=False)
    write_task('D-daily-multiseasonal', '''
# Task D: daily store visits for the next four weeks

`data.csv` has two years of daily visits to one store (`timestamp,target,promo`; `promo` is 1 on days a
promotion ran). `future_promo.csv` gives the promotion days already scheduled for the next 28 days.
The store manager needs a daily staffing plan: how many visits each day for the 28 days after the last
date in the file, with a range, and a note on which days are uncertain. Being understaffed costs about
three times as much as being overstaffed. Deliver `forecast.csv` with `timestamp,forecast,lower,upper`
(28 rows, a stated coverage level) and `report.md`.
''')


def task_e():
    """Ten binary questions with a base-rate table and evidence; truth is the outcome. Brier against the base rate."""
    events = []
    truth = []
    base = 0.3
    for i in range(10):
        p_true = float(np.clip(base + rng.normal(0, 0.25), 0.05, 0.95))
        outcome = int(rng.random() < p_true)
        strength = 'strong' if abs(p_true - base) > 0.25 else 'weak'
        direction = 'for' if p_true > base else 'against'
        events.append(dict(event_id=f'E{i+1:02d}', question=f'Will project {i+1} ship its next release within its committed quarter?',
                           evidence=f'Track record of this team: {strength} signal {direction} on-time delivery (see notes).',
                           notes=f'Team {i+1}: last four releases were {"on time" if p_true > base else "late"} {int(round(4 * (p_true if p_true > base else 1 - p_true)))} of 4 times; scope this quarter is {"similar" if strength == "weak" else "much smaller" if p_true > base else "much larger"} than usual.'))
        truth.append(dict(event_id=f'E{i+1:02d}', outcome=outcome, generating_probability=round(p_true, 3)))
    (TASKS / 'E-event-probability').mkdir(parents=True, exist_ok=True)
    pd.DataFrame(events).to_csv(TASKS / 'E-event-probability/events.csv', index=False)
    json.dump(dict(reference_class='release-on-time rate across the company, last three years', base_rate=base, cases=214), open(TASKS / 'E-event-probability/base_rate.json', 'w'), indent=2)
    pd.DataFrame(truth).to_csv(TRUTH / 'E-event-probability.csv', index=False)
    write_task('E-event-probability', '''
# Task E: ten yes/no questions

`events.csv` lists ten questions with the evidence available today; `base_rate.json` gives the
reference-class rate. Give a probability for each (`probabilities.csv`: `event_id,probability`) and a
`report.md` that states the base rate you started from, how each probability was reached, and how you
would score yourself when the outcomes are known. The decision: a portfolio manager will intervene on
any project below 40 percent.
''')


def task_f():
    """Twenty monthly points; the honest answer is a provisional baseline that names what is missing."""
    t = np.arange(20 + 12)
    y = np.round(80 + 1.5 * t + 12 * np.sin(2 * np.pi * t / 12) + rng.normal(0, 3, len(t)), 1)
    dates = pd.date_range('2024-05-01', periods=len(t), freq='MS')
    (TASKS / 'F-short-history').mkdir(parents=True, exist_ok=True)
    pd.DataFrame({'timestamp': dates[:20].strftime('%Y-%m-%d'), 'target': y[:20]}).to_csv(TASKS / 'F-short-history/data.csv', index=False)
    pd.DataFrame({'timestamp': dates[20:].strftime('%Y-%m-%d'), 'target': y[20:]}).to_csv(TRUTH / 'F-short-history.csv', index=False)
    write_task('F-short-history', '''
# Task F: a new product line, twenty months in

`data.csv` has twenty months of unit sales for a line launched in May 2024. Finance wants twelve
monthly numbers for the next fiscal year with a range. Deliver `forecast.csv` (`timestamp,forecast,lower,upper`)
and `report.md`. Say plainly what the data can and cannot support.
''')


def task_g():
    """A level shift eight months before the end; the future continues at the new level."""
    n = 120; t = np.arange(n + 12)
    y = 300 + 0.5 * t + 20 * np.sin(2 * np.pi * t / 12) + rng.normal(0, 5, len(t))
    y[112:] -= 60                                   # a store closed nearby; the last eight observed months and the future are at the new level
    y = np.round(y, 1)
    dates = pd.date_range('2016-01-01', periods=len(t), freq='MS')
    (TASKS / 'G-level-shift').mkdir(parents=True, exist_ok=True)
    pd.DataFrame({'timestamp': dates[:n].strftime('%Y-%m-%d'), 'target': y[:n]}).to_csv(TASKS / 'G-level-shift/data.csv', index=False)
    pd.DataFrame({'timestamp': dates[n:].strftime('%Y-%m-%d'), 'target': y[n:]}).to_csv(TRUTH / 'G-level-shift.csv', index=False)
    write_task('G-level-shift', '''
# Task G: ten years of monthly sales, twelve months ahead

`data.csv` has ten years of monthly unit sales for a regional product. Nothing else is known; the
planner mentions "things changed a bit this year" but has no detail. Deliver twelve monthly forecasts
with a range (`forecast.csv`: `timestamp,forecast,lower,upper`) and `report.md`. Purchase commitments
are made on the annual total; overcommitting by more than 10 percent triggers a write-off.
''')


def tasks_abc():
    write_task('A-hierarchy', '''
# Task A: regional and total sales, twelve months ahead

`data.csv` has six years of monthly sales for three regions (North, South, West) and their Total, in
long form (`node,timestamp,target`). The planner needs twelve monthly forecasts for each region and for
the total, and the regional numbers must add up to the total. Deliver `forecast.csv`
(`node,timestamp,forecast,lower,upper`, 48 rows, a stated coverage level) and `report.md`.
''')
    write_task('B-launch', '''
# Task B: a new product with no sales history

`brief.md` describes a ready-to-drink coffee launch. Forecast year-one unit and dollar volume, say how
confident the number deserves to be, and rank the inputs by how much they move it. Deliver `report.md`
with the headline numbers, the method, every input you had to assume, and a sensitivity table. There is
no truth file: this task is scored on process (brief, inputs listed with sources, two routes reconciled
or the gap explained, scenarios labelled as scenarios, a scoring date).
''')
    write_task('C-intermittent', '''
# Task C: a slow-moving spare part

`data.csv` has 144 weeks of demand for a spare part; most weeks are zero. Stores replenish weekly with a
two-week lead time and want 95 percent cycle service. Deliver the next 13 weekly forecasts
(`forecast.csv`: `timestamp,forecast`), an order-up-to level stated in `report.md` as "order-up-to: N",
and the reasoning.
''')


if __name__ == '__main__':
    TRUTH.mkdir(exist_ok=True)
    for old in TASKS.glob('*/truth.csv'):
        old.rename(TRUTH / f'{old.parent.name}.csv')
    tasks_abc(); task_d(); task_e(); task_f(); task_g()
    print('tasks written:', sorted(p.name for p in TASKS.iterdir()))
