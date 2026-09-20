"""Chapter 24: when the past stops describing the present.

Changepoint dating by binary segmentation on the mean with a BIC penalty, the best
single Welch-t split, a one-sided CUSUM alarm with reset, drift metrics against the
calibration window, and a comparison of frozen, rolling, expanding and alarm-adaptive
forecasting policies scored only on observations after the calibration window.
"""
import numpy as np
import pandas as pd
from scipy import stats
from .core import time_frame, integer, finish


def binary_segmentation(y, min_segment=8, max_breaks=5):
    """Mean-shift changepoints. Penalty 3*log(n)*sigma2 (about a 1 percent false split rate on white noise) with sigma2 from the MAD of first differences."""
    y = np.asarray(y, float); n = len(y)
    if n < 2 * min_segment:
        return []
    diffs = np.diff(y); sigma = 1.4826 * np.median(np.abs(diffs - np.median(diffs))) / np.sqrt(2) if n > 2 else np.std(y)
    sigma2 = max(sigma ** 2, 1e-12); penalty = 3 * np.log(n) * sigma2
    def sse(a, b):
        seg = y[a:b]; return float(np.sum((seg - seg.mean()) ** 2)) if len(seg) else 0.0
    breaks = []
    segments = [(0, n)]
    while len(breaks) < max_breaks:
        best = None
        for a, b in segments:
            if b - a < 2 * min_segment:
                continue
            base = sse(a, b)
            for k in range(a + min_segment, b - min_segment + 1):
                gain = base - sse(a, k) - sse(k, b)
                if gain > penalty and (best is None or gain > best[0]):
                    best = (gain, k, (a, b))
        if best is None:
            break
        _, k, (a, b) = best
        breaks.append(int(k)); segments.remove((a, b)); segments.extend([(a, k), (k, b)])
    return sorted(breaks)


def best_split(y, min_seg=4):
    """Single most significant mean split by Welch t statistic."""
    y = np.asarray(y, float); best = (None, 0.0)
    for k in range(min_seg, len(y) - min_seg + 1):
        a, b = y[:k], y[k:]
        t = abs(a.mean() - b.mean()) / np.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b) + 1e-12)
        if t > best[1]:
            best = (int(k), float(t))
    return best


def break_analysis(d, c):
    f, _ = time_frame(d, c, minimum=80); y = f.target.to_numpy(float); n = len(y)
    warm = integer(c, 'calibration_size', 30, 10)
    if warm >= n // 2:
        raise ValueError('Reserve at least half the series for monitoring')
    min_seg = integer(c, 'min_segment', 8, 3); max_breaks = integer(c, 'max_breaks', 5, 0)
    roll_w = integer(c, 'rolling_window', 20, 3); drift_w = integer(c, 'drift_window', 20, 3)
    mu = y[:warm].mean(); sd = y[:warm].std(ddof=1)
    if sd <= 0:
        raise ValueError('Stable calibration window needs positive variability')
    # two-sided CUSUM: threshold from the 95th percentile of the larger one-sided maximum under an iid normal null
    rng = np.random.default_rng(integer(c, 'seed', 24, 0)); z = rng.normal(size=(2000, n - warm)); up = np.zeros(2000); dn = up.copy(); mx = up.copy()
    for j in range(z.shape[1]):
        up = np.maximum(0, up + z[:, j] - .5); dn = np.maximum(0, dn - z[:, j] - .5); mx = np.maximum(mx, np.maximum(up, dn))
    threshold = float(np.quantile(mx, .95))
    s_up = s_dn = 0.; last = warm; rows = []; alarms = []
    for t in range(warm, n):
        frozen = mu; rolling = y[max(0, t - roll_w):t].mean(); expanding = y[:t].mean(); adaptive = y[last:t].mean() if t > last else y[t - 1]
        zt = (y[t] - mu) / sd; s_up = max(0, s_up + zt - .5); s_dn = max(0, s_dn - zt - .5); s = max(s_up, s_dn); alarm = s > threshold
        rm = y[t - drift_w:t].mean(); rv = y[t - drift_w:t].var(ddof=1)
        rows.append(dict(timestamp=f.timestamp.iloc[t], actual=y[t], frozen=frozen, rolling=rolling, expanding=expanding, adaptive=adaptive,
                         cusum_before_reset=s, alarm=alarm, rolling_mean=rm, rolling_var=rv, mean_shift_sd=(rm - mu) / sd, variance_ratio=rv / sd ** 2))
        if alarm:
            alarms.append(int(t)); s_up = s_dn = 0.; last = t
    table = pd.DataFrame(rows)
    changepoints = binary_segmentation(y, min_seg, max_breaks)
    split_k, split_t = best_split(y, max(4, min_seg // 2))
    segment_id = np.zeros(n, int)
    for k in changepoints:
        segment_id[k:] += 1
    table['segment_id'] = segment_id[warm:]
    mae = {k: float(abs(table.actual - table[k]).mean()) for k in ['frozen', 'rolling', 'expanding', 'adaptive']}
    detection = None
    if changepoints and alarms:
        first_cp = changepoints[0]; after = [a for a in alarms if a >= first_cp]
        detection = dict(first_changepoint=str(f.timestamp.iloc[first_cp]), first_alarm_after=str(f.timestamp.iloc[after[0]]) if after else None, delay_periods=int(after[0] - first_cp) if after else None,
                         false_alarms_before=int(sum(a < first_cp for a in alarms)))
    best_policy = min(mae, key=mae.get)
    interpretation = (f'{len(changepoints)} changepoint(s) dated by binary segmentation' + (f' at {[str(f.timestamp.iloc[k].date()) for k in changepoints]}' if changepoints else '')
                      + f'; strongest single split at {str(f.timestamp.iloc[split_k].date()) if split_k else "none"} (t {split_t:.1f}). CUSUM raised {len(alarms)} alarm(s) at a threshold targeting 5% false-alarm probability over the horizon'
                      + (f'; detection delay {detection["delay_periods"]} periods' if detection and detection['delay_periods'] is not None else '')
                      + ('; repeated alarms after a reset mean the frozen reference mean no longer describes the series, which is the signal to recalibrate' if len(alarms) > 3 else '')
                      + f'. Policy MAE after the calibration window: ' + ', '.join(f'{k} {v:.3g}' for k, v in mae.items()) + f'; {best_policy} was best. Alarms are known only after the observation.'
                      + (' The series is declared seasonal (season > 1) and the segmentation works on the raw mean, so seasonal swings and trend can be dated as breaks; remove them first or read the dates as regime candidates only.' if integer(c, 'season', 1, 1) > 1 else ''))
    return finish(table, method='Changepoint dating, CUSUM alarm, drift metrics and adaptation-policy comparison', interpretation=interpretation,
                  assumptions=['Calibration window is a stable regime', 'Two-sided CUSUM threshold calibrated under an iid normal null with plug-in mean and sd', 'Mean shifts, not variance-only changes, are the dated breaks'],
                  not_done=['No multivariate or regression-based break tests', 'Variance changepoints are reported as drift metrics only, not dated'],
                  status='passed', threshold=threshold, alarm_count=len(alarms), alarms=[str(f.timestamp.iloc[a]) for a in alarms],
                  changepoints=[str(f.timestamp.iloc[k]) for k in changepoints], changepoint_positions=changepoints, best_split=dict(position=split_k, timestamp=str(f.timestamp.iloc[split_k]) if split_k else None, welch_t=split_t),
                  detection=detection, drift=dict(final_mean_shift_sd=float(table.mean_shift_sd.iloc[-1]), final_variance_ratio=float(table.variance_ratio.iloc[-1]), max_abs_mean_shift_sd=float(table.mean_shift_sd.abs().max())),
                  mae=mae, best_policy=best_policy, calibration_size=warm)
