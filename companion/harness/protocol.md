# Harness protocol: does the skill make anyone a good forecaster, repeatably?

Seven tasks live in `tasks/`; their hidden truth lives in `truth/`, which an assistant is never given
and asked to deliver the files the task names into `runs/<persona>-<arm>-<repeat>/<task>/`. `score.py`
scores each run; `aggregate.py` writes `reports/harness/latest.md`.

## Arms

- `skill`: the assistant is told to read `forecasting-skills/forecast-workflow/SKILL.md` first and to
  use the companion's commands (`companion/scripts/run.py brief|profile|apply|report|journal`) with the
  project's Python environment. Work files go under the task's run folder.
- `plain`: the assistant gets the same task, the same Python environment and no skill or companion
  code; it may use any library installed.

## Personas (the same prompt prefix for both arms)

- **novice**: "You have no forecasting training. You are a careful assistant who follows instructions
  and asks nothing you can look up. Do the task."
- **intermediate**: "You know basic statistics and have made spreadsheet forecasts before. Use methods you can explain."
- **expert**: "You are a senior forecaster. Use your judgment freely."

## Task prompt (verbatim, after the persona line)

> Work in the folder `<run folder>`. The task is in `<task folder>/task.md`; its data files are beside
> it. Deliver exactly the files the task names, into the run folder. Do not look for or use any file
> named truth. When you are done, write `SUMMARY.md` in the run folder listing what you delivered and
> anything you could not do.

For the `skill` arm, prepend: "Before starting, read `forecasting-skills/forecast-workflow/SKILL.md`
and follow its gates. The commands run with `companion/.venv/bin/python companion/scripts/run.py`."

## Repeats and reporting

Run each persona and arm at least twice (`-1`, `-2`). Then:

```bash
for r in harness/runs/*; do companion/.venv/bin/python harness/score.py $r; done
companion/.venv/bin/python harness/aggregate.py
```

Success is defined in the plan: with the skill, every persona passes every process check; accuracy
and calibration spread between personas is smaller than without the skill; repeat spread is within a
stated band. Rerun after every change to the skills and compare `reports/harness/latest.md`.

Runs labelled `legacyskill` and `legacyplain` are the 2026-09-20 trial made before the workflow skill existed (tasks A, B and C only); they are kept as the starting point, not as an arm of the current comparison.

`runs/CURRENT.txt` lists the runs made with the current skill text; `aggregate.py` reports earlier runs apart (arm suffix `-earlier`) so a change to the skill is measured against runs that used it.
