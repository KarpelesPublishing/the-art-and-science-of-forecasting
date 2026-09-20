# The Art and Science of Forecasting: executable companion

**Reader guide: [Start Here](START-HERE.md).** This file is the technical setup
and reproduction guide, not the first thing a nontechnical reader needs to study.

This package connects the book's figures to 27 executed Jupyter notebooks,
27 chapter skills and the **Complete Forecasting Skill**, `all-chapters-forecasting`.
The latter is the 28th integrated entry point, not a requirement to run all methods. Start with
[chapter progress](reports/progress.md) for the verified counts, or open a notebook
from the [chapter map](../forecasting-skills/all-chapters-forecasting/references/chapter-map.md).

## The book

*The Art and Science of Forecasting* by Jason Karpeles. Book website, with the audiobook and additional material: <https://karpeles.com/publishing/the-art-and-science-of-forecasting>. This repository is the free companion; it does not contain the book text.

## Data and method scope

Most lessons use seeded synthetic data so readers can run them without licensed
datasets or credentials. They teach the method; they do not reconstruct original
Walmart, Dojima, wartime, election or clinical observations. Chapter 27 calibrates
across synthetic established products and adapts to a launch using horizon-explicit
gamma trial timing and separate repeat cohorts. Modes 3/4/5 months and the standard
80% year-one trial convention reflect the author's stated practice, not a universal
law. The worked example explicitly uses a 24-month denominator and also shows the
eventual-trial alternative as a nonstandard comparison. The author confirmed
the 24-month denominator for the standard model.
Awareness/distribution development supplies all delays; no extra ramp is applied.

Chapter 10 saves an event journal and scores eligible resolved events. Chapter 20
compares attribution stability under alternative backgrounds and Gaussian priors,
checks pre-window carryover, and runs a small launch-calibration example. Chapter 22
demonstrates a causal failure despite identical pre-intervention observations.

Chapter 13 runs actual LightGBM. Chapter 14 trains an actual small probabilistic
autoregressive neural network; its MLP architecture is explicitly distinguished
from DeepAR. Chapter 15 runs pretrained Chronos-T5-Tiny. Chapter 16 runs Prophet.
Notebook limitations and the method audit identify advanced named methods that
are outside each executable core. Do not describe this package as implementing
every algorithm mentioned anywhere in the book.

The accompanying skills preserve essential method checks and explain how to adapt
the notebooks to new inputs. A chart is counted once, regardless of its three
export formats or multiple panels.

## Set up

Run these commands from the book project directory (the directory containing
`companion`, `manuscript` and `forecasting-skills`). Python 3.12 is the tested target.

```bash
uv venv companion/.venv --python 3.12
uv pip sync --python companion/.venv/bin/python companion/requirements.lock
```

The lock records the full tested environment, including heavier models and test
tools. A lighter environment may install `companion` with its core dependencies
and use `--profile core`, but chapters 13–16 will be explicitly skipped.

Chapter 15 downloads about 34 MB of pretrained weights on its first run. The
notebook pins `amazon/chronos-t5-tiny` to revision
`29d808298f1a62493e7b9a5e08529d0d930fa189`. It uses CPU inference; no paid service
or GPU rental is required. Subsequent executions use the local Hugging Face cache.
Network/model availability failures remain visible rather than substituting a model.
See the [official model card](https://huggingface.co/amazon/chronos-t5-tiny).

## Reproduce the chapters

```bash
companion/.venv/bin/python companion/scripts/run.py chapters --chapter 4
companion/.venv/bin/python companion/scripts/run.py chapters --all --profile complete
companion/.venv/bin/python companion/scripts/catalog.py
companion/.venv/bin/python -m pytest companion/tests -q
```

Editable notebook sources are `lessons/NN-topic.py`, using `# %%` cells. The runner
regenerates `.ipynb` files and executes them with its own Python environment in a
fresh kernel, preserving readable code and displayed figures. Edit the lesson,
not only the generated notebook. Catalog generation preserves existing reviewed
skills instead of replacing them with scaffolds. Each execution records input/code hashes,
package versions, output hashes, timing and success/failure. The catalog rejects
changed sources or assets until they have been executed again.

The figure manifest records the generating notebook and cell ID, data label,
caption, manuscript insertion anchor and exported files. Printed figure numbering
follows book order; stable asset IDs identify generating cells even when an earlier
chapter section calls for a later-produced chart.

## Forecast many series

CSV requires `series_id,timestamp,target`. Keep frequencies consistent; missing
periods, duplicate keys and invalid targets are reported rather than silently fixed.

```bash
companion/.venv/bin/python companion/scripts/run.py forecast --input data/sales.csv --horizon 12 --frequency MS --workers 4 --resume --output companion/results/sales
```

Use `--as-of YYYY-MM-DD` for historical cutoffs. Two engines: `--engine baseline`
(default) compares naive, drift, seasonal-naive when eligible, and an equal ensemble
at rolling origins, and scales to thousands of series; `--engine full` runs the real
engine in `src/forecasting_companion/engine.py` on every series (ETS with an
AICc-chosen form, Theta, STL+ETS, seasonal ARIMA with diagnostic differencing and an
automatic log transform, LightGBM where history allows, combinations), a few seconds
per series, with model intervals and their measured coverage. Both save forecasts,
per-series metrics and checkpoints; failed series do not erase successful ones.
Resume keys cover data, settings, code and library versions. [Batch validation](reports/batch-validation.md)
documents the tested 1,000-series baseline scale, injected failures and resume behavior.

Empirical residual bands are descriptive ranges based on few historical errors;
model intervals from the full engine carry their measured validation coverage, which
is the number to quote. Neither engine uses regressors, infers hierarchies, or
identifies causal effects. For those tasks, the Complete Forecasting Skill routes to
the corresponding chapter workflow.
The runner is local and in-memory with bounded threads, not a distributed service;
there is no hard per-thread timeout.

## Use the skills

Read [the Complete Forecasting Skill](../forecasting-skills/all-chapters-forecasting/SKILL.md).
Its reference map links every chapter and the `reconcile-tdbu` desk model. Once your
agent runtime discovers the skill, an example one-line request is:

```text
Use $all-chapters-forecasting to forecast my sales data for the next 12 months, compare suitable methods, and report uncertainty and validation results.
```

To expose these skills to Codex in this project, run:

```bash
companion/.venv/bin/python companion/scripts/install_skills.py
```

This creates project-local `.agents/skills/` links to the existing skill files.
Restart/open a session in the project if required for discovery. The script never
overwrites a different existing skill. For another runtime, use its documented
skill directory; preserve the sibling chapter/method folders and companion paths.

## What the checks establish

The validation report checks that notebooks executed, numerical assertions passed,
chart files exist, source hashes match, skill links resolve, and each revised
chapter contains at least three figures. The notebook samples teach workflows;
successful execution does not prove real-world forecasting accuracy, causal
identification, or the calibration of synthetic assumption bands.

## Expanded workshops: learn, then apply

Every chapter now includes a guided workshop, a hand calculation, an applied input
example, interpretation guidance, and three exercises with worked solutions. The
chapter skills contain concrete intake, diagnostic and output procedures, with
longer explanations in their `references/workshop.md` files. The
[coverage matrix](reports/upgrade/coverage.md) identifies the executed scope.

To apply a method without changing book artifacts, choose the chapter's sample
input and configuration, then replace them with your own evidence:

```bash
companion/.venv/bin/python companion/scripts/run.py apply --chapter 4 --input companion/data/observed/monthly-temperature.csv --config companion/configs/ch04-observed.json --output applied-runs/temperature
```

The output directory must be empty and outside the publication/source/data trees.
The command writes `results.csv`, `summary.json`, `diagnostic.png`, and `run.json`.
The run record includes input/configuration/code hashes and library versions.
`status: provisional` or `needs_evidence` describes forecast readiness, even when
execution itself succeeded. Unsupported configuration keys are rejected. Each
chapter's skill lists its exact adapter schema and limitations; the adapters do
not implement every professional extension discussed in the skill.

Synthetic examples are `companion/data/examples/chNN.csv` (JSON for chapter 10);
matching settings are `companion/configs/chNN.json`. Keep source and units explicit.
Eight notebooks additionally execute observed public-domain data. Read
[data provenance](data/README.md) before treating a historical snapshot as evidence
of real-time forecasting performance.

For maintainers: edit lesson sources and workshop references, synchronize with
`scripts/expand_workshops.py`, execute chapters, regenerate the catalog, rebuild,
and validate. Provenance conservatively hashes all shared code, bundled teaching
data, and configurations. Input changes therefore invalidate stale executions.
