"""Look at the data before any model: what a good forecaster does in the first five minutes.

`profile_series(frame, config)` returns a plain dict that a skill can print and a router can act
on: frequency, length, gaps and what to do about them, zero share and the Syntetos-Boylan
demand class, seasonal periods detected from the data (not declared), trend, outliers, a break
hint, positivity, a recommended transform, the data floor for the declared horizon, and a
recommended route. It never modifies the data and never fits a forecasting model.
"""
import numpy as np
import pandas as pd
import warnings

CANDIDATE_PERIODS = {'H': [24, 168], 'D': [7, 365], 'B': [5, 261], 'W': [52], 'M': [12], 'Q': [4], 'Y': [1]}
QUADRANTS = {'smooth': 'regular demand every period', 'erratic': 'demand every period, sizes vary a lot',
             'intermittent': 'many zero periods, steady sizes', 'lumpy': 'many zero periods and volatile sizes'}


def _freq_code(freq):
    """Map a pandas offset alias to one of H, D, B, W, M, Q, Y."""
    f = str(freq).upper()
    for code in ('H', 'B', 'D', 'W', 'Q', 'M', 'Y', 'A'):
        if f.startswith(code) or (code in ('M',) and f in ('MS', 'ME')) or (code == 'Q' and f.startswith('QS')) or (code == 'Y' and f.startswith(('YS', 'YE', 'AS'))):
            return 'Y' if code == 'A' else code
    return 'M' if f in ('MS', 'ME') else f[:1]


def infer_frequency(timestamps):
    ts = pd.to_datetime(pd.Series(timestamps), utc=True, errors='coerce')
    if ts.isna().any():
        return dict(frequency=None, regular=False, reason='unparseable timestamps')
    ts = ts.sort_values().reset_index(drop=True)
    if len(ts) < 3:
        return dict(frequency=None, regular=False, reason='fewer than three timestamps')
    freq = pd.infer_freq(pd.DatetimeIndex(ts))
    deltas = ts.diff().dropna()
    modal = deltas.mode().iloc[0]
    if freq is None:
        # irregular or gappy: guess from the modal gap
        days = modal.total_seconds() / 86400
        guess = 'H' if days < 1 / 12 else 'D' if days < 1.5 else 'W' if days < 10 else 'MS' if days < 45 else 'QS' if days < 120 else 'YS'
        expected = pd.date_range(ts.iloc[0], ts.iloc[-1], freq=guess)
        missing = expected.difference(pd.DatetimeIndex(ts))
        extra = pd.DatetimeIndex(ts).difference(expected)
        return dict(frequency=guess, regular=False, inferred_from='modal gap', gaps=int(len(missing)), off_grid=int(len(extra)),
                    gap_positions=[str(t.date()) for t in missing[:12]], longest_gap=int(_longest_run(expected, missing)))
    return dict(frequency=freq, regular=True, gaps=0, off_grid=0, gap_positions=[], longest_gap=0)


def _longest_run(expected, missing):
    if len(missing) == 0:
        return 0
    flags = expected.isin(missing).astype(int)
    best = run = 0
    for f in flags:
        run = run + 1 if f else 0
        best = max(best, run)
    return best


def classify_intermittency(y):
    """Syntetos-Boylan quadrants from the average demand interval and the CV^2 of nonzero sizes."""
    y = np.asarray(y, float); nz = y[y != 0]
    zero_share = float(np.mean(y == 0)) if len(y) else 0.0
    if len(nz) < 2:
        return dict(zero_share=zero_share, adi=None, cv2=None, quadrant='intermittent' if zero_share > 0 else 'smooth', note='too few nonzero values to classify')
    idx = np.flatnonzero(y != 0)
    adi = float(np.mean(np.diff(idx))) if len(idx) > 1 else float(len(y))
    cv2 = float((np.std(nz, ddof=1) / np.mean(nz)) ** 2) if np.mean(nz) else None
    if adi < 1.32 and (cv2 is None or cv2 < 0.49):
        q = 'smooth'
    elif adi < 1.32:
        q = 'erratic'
    elif cv2 is None or cv2 < 0.49:
        q = 'intermittent'
    else:
        q = 'lumpy'
    return dict(zero_share=zero_share, adi=adi, cv2=cv2, quadrant=q, meaning=QUADRANTS[q])


def detect_seasonality(y, candidates):
    """Evidence per candidate period: ACF at the lag against a 2/sqrt(n) band, periodogram share, and STL
    seasonal strength (Hyndman's F_s) when the series is long enough. A period counts when the ACF is
    significant and the strength is at least 0.3, or the strength alone is at least 0.6."""
    y = np.asarray(y, float); n = len(y); out = []
    if n < 8:
        return dict(periods=[], evidence=[], multiple=False, note='too short to test seasonality')
    band = 2 / np.sqrt(n)
    spectrum = np.abs(np.fft.rfft(y - y.mean())) ** 2
    freqs = np.fft.rfftfreq(n)
    from .engine import seasonal_strength
    accepted = []
    for m in sorted(candidates):
        if m <= 1 or n < m + 30:
            out.append(dict(period=m, acf=None, strength=None, testable=False, note='needs at least period + 30 observations')); continue
        # remove the seasonal means of periods already accepted, so a long lag does not echo a short cycle
        w = y.copy()
        for a in accepted:
            means = np.array([w[i::a].mean() for i in range(a)]); w = w - means[np.arange(n) % a] + w.mean()
        z = w - w.mean(); denom = float(np.dot(z, z)) or 1.0
        acf = float(np.dot(z[:-m], z[m:]) / denom * n / (n - m))   # rescaled so long lags are not penalised for fewer pairs
        target = 1.0 / m
        k = int(np.argmin(np.abs(freqs - target))) if len(freqs) else 0
        share = float(spectrum[k] / spectrum[1:].sum()) if spectrum[1:].sum() > 0 else 0.0
        strength = None
        if n >= 3 * m:
            with warnings.catch_warnings():
                warnings.simplefilter('ignore')
                try:
                    strength = float(seasonal_strength(w, m))
                except Exception:
                    strength = None
        significant = acf > max(band, 0.15)
        seasonal = (significant and (strength is None or strength >= 0.3)) or (strength is not None and strength >= 0.6)
        if seasonal:
            accepted.append(m)
        out.append(dict(period=m, acf=round(acf, 3), acf_band=round(band, 3), periodogram_share=round(share, 3), strength=None if strength is None else round(strength, 3), testable=True, seasonal=bool(seasonal)))
    periods = [e['period'] for e in sorted([e for e in out if e.get('seasonal')], key=lambda e: -(e['strength'] or 0))]
    return dict(periods=periods, evidence=out, multiple=len(periods) > 1)


def detect_trend(y):
    """Mann-Kendall sign test for monotonic trend plus the KPSS-based differencing recommendation."""
    y = np.asarray(y, float); n = len(y)
    if n < 10:
        return dict(direction='unknown', mann_kendall_p=None, note='too short')
    i, j = np.triu_indices(n, 1)
    s = float(np.sum(np.sign(y[j] - y[i])))
    var = n * (n - 1) * (2 * n + 5) / 18
    zstat = (s - np.sign(s)) / np.sqrt(var) if var > 0 else 0.0
    from scipy.stats import norm
    p = float(2 * (1 - norm.cdf(abs(zstat))))
    direction = 'up' if (p < 0.05 and s > 0) else 'down' if (p < 0.05 and s < 0) else 'none detected'
    slope = float(np.polyfit(np.arange(n), y, 1)[0])
    return dict(direction=direction, mann_kendall_p=round(p, 4), slope_per_period=slope)


def detect_outliers(y, period=None, threshold=4.0, intermittent=False):
    """Residual screen: STL residuals when a period is usable, else a Hampel window; a point is flagged beyond
    `threshold` MAD units. Skipped for intermittent demand, where zeros and spikes are the pattern. Reported, never edited."""
    y = np.asarray(y, float); n = len(y)
    if intermittent:
        return dict(count=0, positions=[], method='skipped', note='intermittent demand: spikes are the signal, not outliers')
    if n < 12:
        return dict(count=0, positions=[], method='none', note='too short')
    def residuals(series):
        """Residual of `y` against a fit made on `series` (the two differ once flagged points are masked)."""
        if period and period > 1 and n >= 3 * period:
            from statsmodels.tsa.seasonal import STL
            with warnings.catch_warnings():
                warnings.simplefilter('ignore')
                try:
                    fit = STL(series, period=period).fit()
                    return y - (fit.trend + fit.seasonal), series - (fit.trend + fit.seasonal), f'STL residuals (period {period}), two passes'
                except Exception:
                    pass
        w = max(3, min(11, n // 4)); med = pd.Series(series).rolling(2 * w + 1, center=True, min_periods=w).median().to_numpy()
        return y - med, series - med, 'Hampel window, two passes'
    def flag(resid, scale_from):
        mad = 1.4826 * np.median(np.abs(scale_from - np.median(scale_from)))
        if mad <= 0:
            return np.array([], int)
        return np.flatnonzero(np.abs(resid - np.median(scale_from)) / mad > threshold)
    resid, own, method = residuals(y)
    first = flag(resid, own)
    if len(first) == 0:
        return dict(count=0, positions=[], share=0.0, method=method, threshold=threshold)
    # second pass: refit with the flagged points interpolated away, so an outlier cannot echo into the seasonal component
    masked = pd.Series(y.copy()); masked.iloc[first] = np.nan; masked = masked.interpolate(limit_direction='both').to_numpy()
    resid, own, method = residuals(masked)
    pos = [int(i) for i in flag(resid, own)]
    return dict(count=len(pos), positions=pos[:20], share=round(len(pos) / n, 4), method=method, threshold=threshold)


def break_hint(y, periods=(), min_segment=8):
    """A single mean shift in the series after removing the seasonal means and a linear trend, so that a
    trending or seasonal series does not read as broken. The hint names where and by how much."""
    from .applied.tools_breaks import binary_segmentation
    y = np.asarray(y, float); n = len(y)
    if n < 2 * min_segment + 4:
        return dict(found=False, note='too short')
    z = y.copy()
    for season in periods:
        if season and season > 1 and n >= 2 * season:
            means = np.array([z[i::season].mean() for i in range(season)]); z = z - means[np.arange(n) % season] + z.mean()
    t = np.arange(n); z = z - np.polyval(np.polyfit(t, z, 1), t)
    breaks = binary_segmentation(z, min_segment=min_segment, max_breaks=1)
    if not breaks:
        return dict(found=False)
    k = breaks[0]
    return dict(found=True, position=int(k), periods_since=int(len(y) - k), level_before=float(y[:k].mean()), level_after=float(y[k:].mean()))


def recommend_route(profile, has_regressors=False):
    """The route a good forecaster would take on this profile, with the reason."""
    n = profile['observations']; floor = profile['minimum_for_engine']
    reasons = []
    if profile['frequency']['frequency'] is None:
        return 'unusable', ['timestamps could not be parsed or are too few']
    if profile['gaps']['action'] == 'refuse':
        return 'unusable', [profile['gaps']['reason']]
    quad = profile['intermittency']['quadrant']
    if quad in ('intermittent', 'lumpy') or profile['intermittency']['zero_share'] > 0.3:
        return 'intermittent', [f"{profile['intermittency']['zero_share']:.0%} zero periods, {quad} demand: Croston-family methods scored on scale-free error, then an inventory policy (chapters 21 and 12)"]
    if has_regressors:
        return 'regressors', ['known-in-advance drivers were supplied: regression with ARIMA errors, LightGBM with covariates, Prophet with holidays (chapter 13 or 16)']
    if profile['seasonality']['multiple']:
        return 'multiseasonal', [f"two seasonal periods detected {profile['seasonality']['periods']}: MSTL, Fourier ARIMA, TBATS, Prophet (chapter 12, multiseasonal pool)"]
    if n < floor:
        if n >= 3 * (profile['season'] or 1) and n >= 12:
            return 'short', [f'{n} observations, below the engine floor of {floor}: a provisional baseline, or a pretrained model as a labelled scenario (chapter 15)']
        return 'too_short', [f'{n} observations cannot support a validated forecast; use judgment, reference classes (chapter 25) or a base rate (chapter 2)']
    if profile['break']['found'] and profile['break']['periods_since'] < 2 * (profile['season'] or 1):
        reasons.append(f"a level shift {profile['break']['periods_since']} periods ago: check chapter 24 before trusting older history")
    reasons.insert(0, 'a regular series with enough history: the chapter 12 engine (smoothing, ARIMA, Theta, STL, LightGBM, combinations) at rolling origins')
    return 'engine', reasons


def profile_series(frame, config=None, target='target'):
    config = dict(config or {})
    key = next((k for k in ('series_id', 'node') if k in frame.columns), None)
    if key is not None and frame[key].nunique() > 1:
        return profile_panel(frame, config, key, target)
    if 'timestamp' not in frame.columns or target not in frame.columns:
        raise ValueError(f'profile needs timestamp and {target} columns')
    f = frame[['timestamp', target]].copy()
    f['timestamp'] = pd.to_datetime(f['timestamp'], utc=True, errors='coerce')
    f = f.sort_values('timestamp').reset_index(drop=True)
    if config.get('as_of'):
        f = f[f.timestamp <= pd.to_datetime(config['as_of'], utc=True)]
    y_raw = pd.to_numeric(f[target], errors='coerce')
    missing_values = int(y_raw.isna().sum())
    y = y_raw.dropna().to_numpy(float)
    n = int(len(y))
    freq = infer_frequency(f['timestamp'])
    code = _freq_code(freq['frequency']) if freq['frequency'] else None
    candidates = list(CANDIDATE_PERIODS.get(code, [])) if code else []
    declared = config.get('season')
    if isinstance(declared, int) and declared > 1 and declared not in candidates:
        candidates.append(declared)
    inter = classify_intermittency(y)
    seas = detect_seasonality(y, candidates)
    tested = [e for e in seas['evidence'] if e.get('testable')]
    season = seas['periods'][0] if seas['periods'] else (declared if isinstance(declared, int) else (1 if tested else (candidates[0] if candidates and candidates[0] > 1 else 1)))
    gaps_total = freq.get('gaps', 0) + missing_values
    if freq['frequency'] is None:
        gaps = dict(count=gaps_total, action='refuse', reason=freq.get('reason', 'irregular timestamps'))
    elif gaps_total == 0:
        gaps = dict(count=0, action='none')
    elif gaps_total <= max(2, 0.05 * (n + gaps_total)) and freq.get('longest_gap', 0) < 2 * max(season, 1):
        gaps = dict(count=gaps_total, action='zero' if inter['quadrant'] in ('intermittent', 'lumpy') else 'interpolate',
                    reason='few short gaps: fill inside training slices only, never across a holdout', positions=freq.get('gap_positions', []))
    else:
        gaps = dict(count=gaps_total, action='refuse', reason=f'{gaps_total} missing periods (longest run {freq.get("longest_gap", 0)}): resolve the source before forecasting', positions=freq.get('gap_positions', []))
    h = int(config.get('horizon', 12))
    from .applied.series import minimum_history
    floor = int(minimum_history(h, season))
    from .engine import choose_log
    log, lognote = choose_log(y) if n else (False, {})
    profile = dict(
        observations=n, missing_values=missing_values, start=str(f.timestamp.iloc[0].date()) if len(f) else None, end=str(f.timestamp.iloc[-1].date()) if len(f) else None,
        frequency=freq, season=int(season), declared_season=declared, horizon=h, minimum_for_engine=floor,
        gaps=gaps, intermittency=inter, seasonality=seas, trend=detect_trend(y), outliers=detect_outliers(y, season if season > 1 else None, intermittent=inter['quadrant'] in ('intermittent', 'lumpy')),
        **{'break': break_hint(y, seas['periods'] or [season])}, positive=bool(n and np.all(y > 0)), nonnegative=bool(n and np.all(y >= 0)),
        recommended_transform='log' if log else 'none', transform_note=lognote,
        summary_stats=dict(mean=float(y.mean()) if n else None, median=float(np.median(y)) if n else None, min=float(y.min()) if n else None, max=float(y.max()) if n else None, last=float(y[-1]) if n else None))
    regressors = [c for c in frame.columns if c not in ('timestamp', target, 'series_id')]
    route, reasons = recommend_route(profile, has_regressors=bool(config.get('future_regressors')) or bool(config.get('regressors')))
    profile.update(route=route, route_reasons=reasons, extra_columns=regressors)
    profile['warnings'] = _warnings(profile)
    return profile


def profile_panel(frame, config, key, target='target'):
    """Long-form input: one profile per series, plus a panel summary a router can act on."""
    per = {str(k): profile_series(g.drop(columns=[key]), config, target) for k, g in frame.groupby(key)}
    routes = sorted({p['route'] for p in per.values()})
    seasons = sorted({p['season'] for p in per.values()})
    first = next(iter(per.values()))
    summary = dict(panel=True, key=key, series=len(per), routes=routes, seasons=seasons, observations=first['observations'], frequency=first['frequency'], season=first['season'], horizon=first['horizon'],
                   minimum_for_engine=first['minimum_for_engine'], route=('hierarchy' if key == 'node' else 'panel'), route_reasons=[f'{len(per)} series in long form: ' + ('chapter 18 reconciles a hierarchy of node histories with child-parent edges' if key == 'node' else 'the batch runner (per series or global) or chapter 13/14 for pooled models')],
                   warnings=sorted({w for p in per.values() for w in p['warnings']}), per_series=per)
    return summary


def _warnings(p):
    w = []
    if p['route'] in ('short', 'too_short'):
        w.append(f"only {p['observations']} observations; the engine floor for horizon {p['horizon']} at season {p['season']} is {p['minimum_for_engine']}")
    if p['gaps']['action'] not in ('none',):
        w.append(f"gaps: {p['gaps']['count']} ({p['gaps']['action']})")
    if p['outliers'].get('count'):
        w.append(f"{p['outliers']['count']} outlying observations by {p['outliers']['method']}; check them, do not delete them")
    if p['break']['found']:
        w.append(f"possible level shift {p['break']['periods_since']} periods before the end (from {p['break']['level_before']:.4g} to {p['break']['level_after']:.4g})")
    if p['declared_season'] and p['seasonality']['periods'] and p['declared_season'] != p['seasonality']['periods'][0]:
        w.append(f"declared season {p['declared_season']} but the data show {p['seasonality']['periods'][0]}")
    if p['declared_season'] and not p['seasonality']['periods']:
        w.append(f"declared season {p['declared_season']} is not visible in the data; the engine will still test seasonal candidates")
    if not p['positive'] and p['nonnegative'] and p['intermittency']['zero_share'] > 0:
        w.append('zeros present: multiplicative models and log transforms are excluded')
    return w


def describe(profile):
    """A short reading of the profile for a notebook or the command line."""
    p = profile
    if p.get('panel'):
        lines = [f"Panel of {p['series']} series keyed by {p['key']}: routes {p['routes']}, seasons {p['seasons']}", f"Route: {p['route']}"] + [f'  - {r}' for r in p['route_reasons']]
        for name, q in p['per_series'].items():
            lines.append(f"  {name}: {q['observations']} obs, season {q['season']}, {q['intermittency']['quadrant']}, route {q['route']}")
        if p['warnings']:
            lines += ['Warnings:'] + [f'  - {w}' for w in p['warnings']]
        return '\n'.join(lines)
    s = p['seasonality']
    lines = [f"Observations: {p['observations']} ({p['start']} to {p['end']}), frequency {p['frequency']['frequency']}{'' if p['frequency']['regular'] else ' (irregular)'}",
             f"Season: {p['season']} " + (f"detected from the data {s['periods']}" if s['periods'] else 'not detected; using the frequency default'),
             f"Demand class: {p['intermittency']['quadrant']} ({p['intermittency']['zero_share']:.0%} zeros)",
             f"Trend: {p['trend'].get('direction')}; transform: {p['recommended_transform']}; outliers: {p['outliers'].get('count', 0)}",
             f"Floor for horizon {p['horizon']}: {p['minimum_for_engine']} observations",
             f"Route: {p['route']}"] + [f"  - {r}" for r in p['route_reasons']]
    if p['warnings']:
        lines += ['Warnings:'] + [f'  - {w}' for w in p['warnings']]
    return '\n'.join(lines)
