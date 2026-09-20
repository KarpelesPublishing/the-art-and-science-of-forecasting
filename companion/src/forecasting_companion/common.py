"""Small transparent utilities; chapter-specific calculations live in notebooks."""
from pathlib import Path
import json
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
plt.rcParams.update({'figure.figsize': (4.3, 2.8), 'font.size': 8,
    'axes.spines.top': False, 'axes.spines.right': False,
    'axes.prop_cycle': matplotlib.cycler(color=['#163d59','#ba561a','#477666','#87475b']),
    'savefig.dpi': 240, 'axes.grid': True, 'grid.alpha': .18,
    'pdf.fonttype': 42, 'svg.fonttype': 'none'})

def begin(chapter):
    """Reset the per-chapter artifact journal for a complete run."""
    out = Path(os.environ.get('FORECAST_OUTPUT', ROOT))
    (out/'results').mkdir(parents=True, exist_ok=True)
    (out/'results'/f'ch{chapter:02d}-figures.json').write_text('[]')
    return np.random.default_rng(20260918 + chapter)

def print_ready(fig):
    """Add redundant encodings and external legends without changing chart data.

    This is a print baseline, not a substitute for inspecting every exported chart.
    Custom legends are retained when their labels cannot be mapped to artists.
    """
    from matplotlib.container import BarContainer
    styles = ['-', '--', ':', '-.']
    markers = ['o', 's', '^', 'D', 'x', '+']
    for ax in fig.axes:
        ax.set_axisbelow(True)
        lines = [line for line in ax.lines if not line.get_label().startswith('_')]
        if len(lines) > 1:
            signatures = {(line.get_linestyle(), line.get_marker()) for line in lines}
            if len(signatures) < len(lines):
                for i, line in enumerate(lines):
                    line.set_linestyle(styles[i % len(styles)])
                    line.set_linewidth(max(1., line.get_linewidth()))
                    if len(line.get_xdata()) > 2:
                        line.set_marker(markers[i % len(markers)])
                        line.set_markersize(3)
                        line.set_markevery(max(1, len(line.get_xdata())//10))
        groups = [c for c in ax.containers if isinstance(c, BarContainer)
                  and not c.get_label().startswith('_')]
        if len(groups) > 1:
            for i, group in enumerate(groups):
                for patch in group:
                    patch.set_hatch(['', '///', 'xx', '..', '\\\\'][i % 5])
                    patch.set_facecolor(['.25', 'white', '.8', 'white', '.65'][i % 5])
                    patch.set_edgecolor('black')
                    patch.set_linewidth(.6)
        legend = ax.get_legend()
        if legend is not None:
            labels = [t.get_text() for t in legend.get_texts()]
            handles, actual_labels = ax.get_legend_handles_labels()
            lookup = dict(zip(actual_labels, handles))
            if all(label in lookup for label in labels):
                columns = 2 if len(labels) > 2 else 1
                rows = (len(labels)+columns-1)//columns
                if len(fig.axes) == 1:
                    fig.set_figheight(max(fig.get_figheight(), 2.8+.19*rows))
                ax.legend([lookup[label] for label in labels], labels,
                          loc='lower center', bbox_to_anchor=(.5, 1.02),
                          ncol=columns, fontsize=7, frameon=False,
                          borderaxespad=0, columnspacing=.9, handlelength=2.6)
                if ax.get_title():
                    ax.set_title(ax.get_title(), y=1.09+.13*rows, fontsize=9)
    fig.tight_layout()

def save(chapter, number, title, caption, anchor, fig=None):
    """Export one distinct figure in three formats and log its provenance."""
    fig = fig or plt.gcf()
    print_ready(fig)
    out = Path(os.environ.get('FORECAST_OUTPUT', ROOT))
    folder = out/'figures'/f'ch{chapter:02d}'
    folder.mkdir(parents=True, exist_ok=True)
    stem = f'fig-{chapter:02d}-{number:02d}'
    for ext in ('png', 'pdf', 'svg'):
        fig.savefig(folder/f'{stem}.{ext}', bbox_inches='tight')
    journal = out/'results'/f'ch{chapter:02d}-figures.json'
    records = json.loads(journal.read_text())
    if any(r['id'] == stem for r in records):
        raise ValueError(f'duplicate figure ID: {stem}')
    records.append(dict(id=stem, chapter=chapter, title=title, caption=caption,
        anchor=anchor, alt=f'{title}. {caption}', seed=20260918+chapter,
        data='Seeded synthetic educational example unless caption states otherwise',
        outputs={ext: f'figures/ch{chapter:02d}/{stem}.{ext}' for ext in ('png','pdf','svg')}))
    journal.write_text(json.dumps(records, indent=2)+'\n')
    from IPython.display import display, Image
    display(Image(filename=str(folder/f'{stem}.png')))
    plt.close(fig)

def _paired(a,b):
    a,b=np.asarray(a,dtype=float),np.asarray(b,dtype=float)
    if a.shape!=b.shape or a.ndim!=1 or not a.size:
        raise ValueError('Scores require nonempty aligned one-dimensional arrays')
    if not np.isfinite(a).all() or not np.isfinite(b).all():
        raise ValueError('Scores require finite values')
    return a,b

def mae(y, forecast):
    if np.ndim(forecast)==0: forecast=np.full(np.shape(y),forecast)
    y,forecast=_paired(y,forecast)
    return float(np.mean(np.abs(y-forecast)))

def brier(p, y):
    p, y = _paired(p,y)
    if np.any((p < 0)|(p > 1)) or not np.all(np.isin(y, [0,1])):
        raise ValueError('Brier requires probabilities in [0,1] and binary outcomes')
    return float(np.mean((p-y)**2))

def mase(y, forecast, train, season=1):
    train = np.asarray(train,dtype=float)
    if not isinstance(season,int) or isinstance(season,bool) or season<1 or train.ndim!=1 or len(train)<=season or not np.isfinite(train).all():
        raise ValueError('MASE needs finite training data longer than a positive integer season')
    scale = np.mean(np.abs(train[season:]-train[:-season]))
    return float('nan') if scale == 0 else mae(y, forecast)/scale

def seasonal_series(rng, n=144):
    t = np.arange(n)
    return 40 + .12*t + 8*np.sin(2*np.pi*t/12) + rng.normal(0, 2, n)
