"""The forecasting brief: the questions a good forecaster settles before touching the data.

A `Brief` is the first gate of the workflow. It is saved as `brief.json`, attached to every run
record, and rendered at the top of every report, so the number is never separated from the
decision it serves. `Brief.interview()` returns only the questions still unanswered, in the
order they should be asked; `Brief.validate()` refuses a brief that cannot support a forecast.
"""
from dataclasses import dataclass, field, asdict
from pathlib import Path
import json
import re

QUESTIONS = [
    ('target', 'What exactly is being forecast? Name the quantity and the entity (for example "weekly unit sales of SKU 1234 in region West").'),
    ('units', 'In what units will the number be read (units, dollars, cases, visits, probability)?'),
    ('decision', 'What decision will this forecast change, and who makes it?'),
    ('horizon', 'How far ahead, in how many periods, does the decision need the number?'),
    ('frequency', 'What is one period: a day, a week, a month, a quarter?'),
    ('as_of', 'What is the cutoff date: the last date whose data may be used?'),
    ('cost_of_over', 'What does it cost to forecast too high (unsold stock, idle staff, missed target)?'),
    ('cost_of_under', 'What does it cost to forecast too low (stockouts, overtime, lost sales)?'),
    ('known_in_advance', 'What will be known before the forecast period that could move the number (prices, promotions, holidays, launches, weather)? Say "nothing" if nothing.'),
    ('outcome_date', 'When will the actual outcome be known, so the forecast can be scored?'),
    ('audience', 'Who will read the forecast and what do they need: one number, a range, or a probability?'),
]
FREQUENCIES = {'H': 'hourly', 'D': 'daily', 'B': 'business daily', 'W': 'weekly', 'M': 'monthly', 'MS': 'monthly', 'ME': 'monthly', 'Q': 'quarterly', 'QS': 'quarterly', 'Y': 'yearly', 'YS': 'yearly'}
_ALIASES = {'hour': 'H', 'hourly': 'H', 'day': 'D', 'daily': 'D', 'week': 'W', 'weekly': 'W', 'month': 'MS', 'monthly': 'MS', 'quarter': 'QS', 'quarterly': 'QS', 'year': 'YS', 'yearly': 'YS', 'annual': 'YS'}


@dataclass
class Brief:
    target: str = ''
    units: str = ''
    decision: str = ''
    horizon: int = 0
    frequency: str = ''
    as_of: str = ''
    cost_of_over: str = ''
    cost_of_under: str = ''
    known_in_advance: str = ''
    outcome_date: str = ''
    audience: str = ''
    source: str = ''
    notes: list = field(default_factory=list)

    @classmethod
    def load(cls, path):
        data = json.loads(Path(path).read_text())
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})

    def save(self, path):
        Path(path).write_text(json.dumps(asdict(self), indent=2) + '\n')
        return Path(path)

    def normalized_frequency(self):
        f = str(self.frequency).strip()
        return _ALIASES.get(f.lower(), f.upper() if f else '')

    def interview(self):
        """The unanswered questions, in order. Ask these and nothing else."""
        pending = []
        for key, question in QUESTIONS:
            value = getattr(self, key)
            if value in ('', 0, None) or (isinstance(value, str) and not value.strip()):
                pending.append((key, question))
        return pending

    def validate(self):
        """Problems that make a forecast unsafe to produce; empty when the brief is usable."""
        problems = []
        if not str(self.target).strip():
            problems.append('target is empty: say what quantity, for which entity')
        if not str(self.units).strip():
            problems.append('units are empty: a number without units cannot be checked later')
        if not str(self.decision).strip():
            problems.append('decision is empty: a forecast nobody will act on cannot be scored for usefulness')
        try:
            h = int(self.horizon)
        except (TypeError, ValueError):
            h = 0
        if h < 1:
            problems.append('horizon must be a positive number of periods')
        if not self.normalized_frequency():
            problems.append('frequency is empty: say what one period is')
        if self.as_of and not re.match(r'^\d{4}-\d{2}-\d{2}', str(self.as_of)):
            problems.append('as_of must be an ISO date (YYYY-MM-DD)')
        if self.outcome_date and not re.match(r'^\d{4}-\d{2}-\d{2}', str(self.outcome_date)):
            problems.append('outcome_date must be an ISO date (YYYY-MM-DD)')
        if not str(self.outcome_date).strip():
            problems.append('outcome_date is empty: a forecast with no scoring date is never scored')
        return problems

    def config_overrides(self):
        """The configuration keys the brief settles, so a run cannot contradict it."""
        out = {}
        if int(self.horizon or 0) > 0:
            out['horizon'] = int(self.horizon)
        if self.normalized_frequency():
            out['frequency'] = self.normalized_frequency()
        if self.as_of:
            out['as_of'] = str(self.as_of)
        if self.units:
            out['units'] = self.units
        if self.source:
            out['source'] = self.source
        if self.outcome_date:
            out['outcome_due'] = str(self.outcome_date)
        return out

    def asymmetry(self):
        """A one-line reading of the cost asymmetry, used to pick a quantile for the reported number."""
        over = str(self.cost_of_over).strip(); under = str(self.cost_of_under).strip()
        if not over or not under:
            return 'costs of over- and under-forecasting not stated; the median is reported'
        return f'too high: {over}; too low: {under}'

    def describe(self):
        lines = [f'Target: {self.target} ({self.units})', f'Decision: {self.decision}', f'Horizon: {self.horizon} periods, {FREQUENCIES.get(self.normalized_frequency(), self.frequency)}, data up to {self.as_of or "(unstated)"}',
                 f'Costs: {self.asymmetry()}', f'Known in advance: {self.known_in_advance or "(unstated)"}', f'Outcome known: {self.outcome_date or "(unstated)"}; audience: {self.audience or "(unstated)"}']
        if self.source:
            lines.append(f'Data source: {self.source}')
        return '\n'.join(lines)
