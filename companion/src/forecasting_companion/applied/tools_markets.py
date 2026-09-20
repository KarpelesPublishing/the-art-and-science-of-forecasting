"""Chapter 1: predeclared price rules, tested honestly.

Persistence, momentum and mean reversion as one-step rules on closing prices at
expanding origins, directional hit rates with a binomial test against a coin, and
a Benford first-digit check on a chosen column. Price-error evaluation only.
"""
import numpy as np
import pandas as pd
from scipy import stats
from .core import time_frame, integer, finish

RULES = ('persistence', 'momentum', 'mean_reversion')


def benford(values):
    v = np.abs(np.asarray(values, float)); v = v[np.isfinite(v) & (v > 0)]
    if len(v) < 30:
        raise ValueError('Benford check needs at least 30 positive values')
    digits = np.array([int(f'{x:e}'[0]) for x in v])
    observed = np.array([(digits == k).sum() for k in range(1, 10)], float)
    expected = np.log10(1 + 1 / np.arange(1, 10)) * len(v)
    chi, p = stats.chisquare(observed, expected)
    return dict(n=int(len(v)), observed=(observed / len(v)).round(4).tolist(), expected=(expected / len(v)).round(4).tolist(), chi_square=float(chi), p_value=float(p))


def rule_backtest(d, c):
    rules = list(c.get('rules', RULES))
    if not rules or any(r not in RULES for r in rules):
        raise ValueError(f'rules must be a nonempty subset of {RULES}')
    k = integer(c, 'k', 5, 2); frac = float(c.get('train_fraction', 0.7)); column = c.get('benford_column', 'close')
    if not 0.2 <= frac <= 0.95:
        raise ValueError('train_fraction must be in [0.2, 0.95]')
    f, _ = time_frame(d, c, columns=('open', 'high', 'low', 'close'), minimum=30)
    if np.any(f.low > f[['open', 'close']].min(axis=1)) or np.any(f.high < f[['open', 'close']].max(axis=1)) or np.any(f.low > f.high):
        raise ValueError('OHLC bounds are inconsistent')
    if column not in f:
        raise ValueError(f'benford_column {column!r} not in data')
    y = f.close.to_numpy(float); n = len(y); start = max(k + 1, int(n * frac))
    idx = np.arange(start, n)
    pred = {'persistence': y[idx - 1], 'momentum': y[idx - 1] + (y[idx - 1] - y[idx - 1 - k]) / k, 'mean_reversion': np.array([y[t - k:t].mean() for t in idx])}
    actual = y[idx]; prev = y[idx - 1]; direction = np.sign(actual - prev)
    table = pd.DataFrame({'timestamp': f.timestamp.iloc[start:].to_numpy(), 'actual': actual, **{r: pred[r] for r in rules}, 'actual_direction': direction})
    mae = {r: float(np.abs(actual - pred[r]).mean()) for r in rules}
    hit = {}; hit_p = {}
    for r in rules:
        if r == 'persistence':
            continue
        call = np.sign(pred[r] - prev); valid = (direction != 0) & (call != 0)
        hits = (call[valid] == direction[valid]); table[f'{r}_hit'] = (call == direction).astype(int)
        m = int(valid.sum())
        hit[r] = float(hits.mean()) if m else None
        hit_p[r] = float(stats.binomtest(int(hits.sum()), m, 0.5).pvalue) if m else None
    bf = benford(f[column])
    best = min(mae, key=mae.get)
    interpretation = (f'One-step rules scored on {len(idx)} test closes after a {frac:.0%} training share. MAE: ' + ', '.join(f'{r} {v:.4g}' for r, v in mae.items()) + f'; best {best}. '
                      + ' '.join(f'{r} calls direction {hit[r]:.1%} of the time (binomial p vs coin {hit_p[r]:.2f}).' for r in hit if hit[r] is not None)
                      + f' Benford first-digit chi-square p on {column}: {bf["p_value"]:.3g} (prices are not expected to obey Benford; the test is a data-integrity habit, not a signal). '
                      + 'Price error is not net return; nothing here is a trading result.')
    return finish(table, method='Predeclared one-step price rules with directional hit rates', interpretation=interpretation,
                  assumptions=['Rules declared before scoring', 'Closing prices are comparable across the sample (no unadjusted splits)', 'Zero-change periods excluded from hit rates'],
                  not_done=['No returns, transaction costs or position sizing', 'No session or corporate-action checks', 'No out-of-sample period beyond this series'],
                  status='passed', rules=rules, k=k, train_fraction=frac, test_rows=int(len(idx)), mae=mae, hit_rate=hit, hit_rate_p_value=hit_p, benford=bf)
