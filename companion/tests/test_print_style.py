import numpy as np
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from forecasting_companion import common


def test_series_distinguishable_without_color_and_values_unchanged():
    fig, ax = common.plt.subplots()
    values = np.arange(20)
    lines = [ax.plot(values, values+i, label=f'Model {i}')[0] for i in range(3)]
    ax.legend()
    assert hasattr(common, 'print_ready'), 'Missing print readability preparation'
    common.print_ready(fig)
    signatures = {(line.get_linestyle(), line.get_marker()) for line in lines}
    assert len(signatures) == 3
    for i, line in enumerate(lines):
        np.testing.assert_array_equal(line.get_ydata(), values+i)
    fig.canvas.draw()
    assert not ax.get_legend().get_window_extent().overlaps(ax.get_window_extent())
    common.plt.close(fig)


def test_grouped_bars_patterns_legend_and_heights_preserved():
    fig, ax = common.plt.subplots()
    bars = [ax.bar(np.arange(3)+i*.2, [1,2,3], width=.2, label=f'Model {i}') for i in range(3)]
    ax.legend()
    assert hasattr(common, 'print_ready'), 'Missing print readability preparation'
    common.print_ready(fig)
    assert len({group.patches[0].get_hatch() for group in bars}) == 3
    assert all([p.get_height() for p in group] == [1,2,3] for group in bars)
    assert [t.get_text() for t in ax.get_legend().get_texts()] == ['Model 0','Model 1','Model 2']
    common.plt.close(fig)
