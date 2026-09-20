# Start here: the book, notebooks and skills

You do not need to learn 30 folder names. There are two ways to use this companion:
**learn one chapter** or **apply the book to your own forecasting problem**.

| Resource | What it is | Who uses it? |
|---|---|---|
| Book chapter | Explanation, examples and limitations | You read it |
| Chapter notebook | A runnable worked lesson, with editable inputs, code, charts and results | You or your AI run it |
| Chapter skill | Written instructions that help an AI apply that chapter and check its assumptions | Your AI reads it |
| Forecast Workflow | The front door: seven gates from question to scored forecast, each leaving a file | Your AI follows it for any forecast |
| Complete Forecasting Skill | The map and router: coordinates whichever chapter methods fit your problem | Your AI uses it inside the workflow |

A skill is **not an app or a notebook**. Opening `SKILL.md` shows its instructions;
it does not run a forecast. The notebook does the demonstrated computations.

## 1. I am learning a chapter

Open the [chapter directory](../forecasting-skills/all-chapters-forecasting/references/chapter-map.md).
Each of its 27 rows links a chapter skill and its matching notebook.

For example, chapter 20 has:

- [Marketing-mix notebook](notebooks/20-marketing-mix.ipynb): run and examine the examples.
- [Marketing-mix skill](../forecasting-skills/forecasting-ch20-marketing-mix/SKILL.md): give these instructions to your AI when learning or applying the chapter.

Example request: “Use the chapter 20 skill to walk me through its notebook. Explain
each input, what each chart establishes, and what it does not establish.”

Notebooks use mostly synthetic teaching data. They are starting examples, not
forecasts for your business until you supply appropriate data and adapt the model.

## 2. I have a forecasting problem

Start with the [Forecast Workflow](../forecasting-skills/forecast-workflow/SKILL.md).
You do **not** have to work through the chapter skills first. The workflow has seven
gates, and each one leaves a file the next command needs, so it cannot be skipped
whatever you or your assistant know about forecasting:

1. **Brief**: what number, for what decision, by when (`run.py brief`).
2. **Profile**: what the data are, and the route they recommend (`run.py profile`).
3. **Baseline**: the number a method must beat, stated before modelling.
4. **Method**: chosen from the profile, run with the brief attached (`run.py apply --brief`).
5. **Validation**: did it beat the baseline; what was not done.
6. **Uncertainty**: a range with measured coverage, or an honest scenario.
7. **Report and journal**: rendered from the run's own files, every number sourced
   (`run.py report`); recorded for scoring when the actuals arrive (`run.py journal`).

In a runtime that has discovered the skills, an example request is:

```text
Use $forecast-workflow to forecast my product's next 24 months from sales.csv.
Take me through the gates; ask me the brief's questions one at a time.
```

### Your first forecast in thirty minutes

[first-forecast.md](../forecasting-skills/forecast-workflow/references/first-forecast.md)
walks one complete pass on the shipped file `data/examples/first-forecast.csv`, with the
commands and the numbers they print. Do it once on that file, then once on your own.

For the author's established-product-to-new-launch method, the main working
example is [chapter 27's notebook](notebooks/27-directed-forecasting.ipynb).
Chapter 20 explains the marketing context; chapter 25 helps with reference classes.

For 100 or more historical sales series, the integrated skill can use the local
batch runner described in [the technical guide](README.md#forecast-many-series).
With `--engine full` that runner fits the smoothing and ARIMA families, Theta, STL+ETS, LightGBM and combinations per series, selected by rolling-origin validation with measured interval coverage; it does not use regressors, hierarchies or causal designs.

## Why do I see 30 skill folders?

```text
Reader-facing book skills: 29
  Forecast Workflow: the front door, seven gates from question to scored forecast
  Complete Forecasting Skill: the map and router across the chapters
  Chapter skills 01 to 27: one per chapter

Top-down bottom-up forecasting model: 1
  reconcile-tdbu, the top-down bottom-up triangulation model from chapters 20 and 27,
  usable on its own when there is no sales history yet
```

The front door is `forecast-workflow`; `all-chapters-forecasting`, displayed as
**Complete Forecasting Skill**, is the map it routes through. The technical folder
names differ from the reader-facing names.

## Keep the package together

The 28th skill's folder alone is **not a standalone installation**. It links to
the chapter skills, the top-down bottom-up triangulation model and the notebooks. Keep the supplied folders
in their relative layout:

```text
book-project/
  forecasting-skills/  AI instructions (27 chapters, the complete skill, reconcile-tdbu)
  companion/
    START-HERE.md      This reader guide
    notebooks/         The 27 runnable lessons
    lessons/           Editable source used to regenerate notebooks
    src/               Shared calculation and chart helpers
    assets/            Required illustration assets
```

For local setup and skill discovery, follow [the technical guide](README.md#set-up).
The supplied installer links all 30 skills for Codex (`.agents/skills`) and Claude Code
(`.claude/skills`); that does not mean you must invoke
all of them. If your AI cannot discover installed skills, explicitly provide the
relevant `SKILL.md` and its linked resources. An assistant without code execution
can explain the instructions but cannot truthfully claim to have run the notebooks.

The book website (<https://karpeles.com/publishing/the-art-and-science-of-forecasting>)
has articles, additional material and the audiobook; this guide describes the local
companion package, which runs on your machine without any online service.

## What a full workshop gives you

Each chapter notebook now continues beyond the original figures into a guided
workshop: work through a small calculation, run a supplied input example, inspect
its actual results, and complete three exercises with worked solutions. You can
read the explanation without understanding every Python statement.

To use your own data, ask your AI to read the chapter skill's **Executable interface**
section and its longer workshop reference, check your input against the schema,
and run the `apply` command into a new folder. The sample configuration shows the
supported settings. The resulting summary explains what was calculated and what
was not established. A provisional forecast or a request for more evidence is a
valid outcome; a confident invented number is not. For a single monthly series the
series tools want 2 seasons + 4 horizons of history (six years for a 12-month
horizon, four for six months); with less you get a persistence placeholder that
says how much more history it needs.

The [coverage matrix](reports/upgrade/coverage.md) lists what each chapter actually
executes. The [technical guide](README.md#expanded-workshops-learn-then-apply)
provides a working command and explains the saved results.
