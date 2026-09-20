"""The dash converter must never disturb numbers, times, quotes or spacing around them."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from strip_em_dashes import convert  # noqa: E402

D = '\u2014'


def test_numbers_times_and_quotes_survive():
    out = convert(f'It cost 1,198 dollars {D} at 10:50 p.m. {D} and 8,000 more, a ratio of 3:1.')
    assert out == 'It cost 1,198 dollars, at 10:50 p.m., and 8,000 more, a ratio of 3:1.'
    assert convert(f'or "we should watch this closely," that doctor {D} the one {D} is forecasting.') == 'or "we should watch this closely," that doctor, the one, is forecasting.'
    assert convert(f'A total of 1,000,000 units {D} roughly {D} shipped.') == 'A total of 1,000,000 units, roughly, shipped.'


def test_every_dash_is_replaced_and_no_double_spaces_appear():
    samples = [f'They can be thin {D} when there are few participants, a single large trader can distort prices.',
               f'The SIR model {D} Susceptible, Infected, Recovered {D} the workhorse of epidemiology, is simple.',
               f'"But if the quantification is unreliable{D}"', f'He said it plainly {D} "we are not ready."',
               f'The point is not that physics is irrelevant {D} it is that the frontier can be described.']
    for s in samples:
        out = convert(s)
        assert D not in out and '  ' not in out and ' ,' not in out and ' .' not in out and ', "' not in out.replace(', "we', '')
    assert convert(samples[1]) == 'The SIR model (Susceptible, Infected, Recovered), the workhorse of epidemiology, is simple.'
    assert convert(samples[2]) == '"But if the quantification is unreliable..."'


def test_text_without_dashes_is_untouched():
    text = 'Figures like 12,345.67 and 09:30, "quoted," (parenthetical) stay exactly as written: no change.'
    assert convert(text) == text
