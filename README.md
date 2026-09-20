# The Art and Science of Forecasting: companion

Free companion to *The Art and Science of Forecasting* by Jason Karpeles: 27 runnable
notebooks (one per chapter), 27 chapter skills for guiding an AI assistant, the Complete
Forecasting Skill that coordinates them, and `reconcile-tdbu`, the desk model from
chapters 20 and 27 that forecasts a product launch before there is any sales history.

- Book website, errata and updates: <https://karpeles.com/publishing/the-art-and-science-of-forecasting>
- New reader? Open [companion/START-HERE.md](companion/START-HERE.md).
- Technical setup and reproduction: [companion/README.md](companion/README.md).
- Skill library overview: [SKILL-LIBRARY.md](SKILL-LIBRARY.md); the integrated entry point is
  [forecasting-skills/all-chapters-forecasting/SKILL.md](forecasting-skills/all-chapters-forecasting/SKILL.md).

## Quick start

```bash
cd companion
python3.12 -m venv .venv && .venv/bin/pip install -r requirements.lock
.venv/bin/python scripts/run.py chapters --chapter 4
.venv/bin/python -m pytest tests -q
```

Notebooks are in `companion/notebooks/`; their editable sources are `companion/lessons/`.
Most examples use seeded synthetic data so they run without any licensed dataset. Running
an example does not establish that its assumptions fit your business; validating that is
part of the work the book describes.

This repository does not contain the book text. Copyright 2026 Jason Karpeles.
