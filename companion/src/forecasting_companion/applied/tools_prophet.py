"""Chapter 16: Prophet with an event calendar and known regressors.

Chooses additive or multiplicative seasonality on training data, tunes the changepoint
prior on earlier origins, ablates the calendar and the regressors at the same origins,
scores the untouched holdout with nominal 80 percent bands, and forecasts the future
only when the regressors it needs are supplied.
"""
import warnings
import numpy as np
import pandas as pd
from .core import require, integer, time_frame, finish


def _split_future(d, regressors):
    d = d.copy()
    if 'target' not in d:
        raise ValueError('Missing columns: target')
    empty = d.target.isna() | (d.target.astype(str).str.strip() == '')
    if empty.any():
        hist = d[~empty].copy()
        future = d[empty].copy()
        if not empty[empty].index.equals(d.index[-len(future):]):
            raise ValueError('Rows with empty target must be trailing future rows')
        return hist, future
    return d, d.iloc[0:0].copy()


def _fit(frame_ds_y, holidays, regressors, prior, mode, weekly, yearly, seed, uncertainty=200):
    from prophet import Prophet
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        m = Prophet(changepoint_prior_scale=prior, seasonality_mode=mode, holidays=holidays,
                    weekly_seasonality=weekly, yearly_seasonality=yearly, daily_seasonality=False,
                    uncertainty_samples=uncertainty, interval_width=0.8)
        for r in regressors:
            m.add_regressor(r)
        import logging
        logging.getLogger('cmdstanpy').setLevel(logging.ERROR)
        m.fit(frame_ds_y, seed=seed)
    return m


def prophet_calendar(d, c):
    from ..engine import choose_log
    regressors = c.get('regressors', [])
    if not isinstance(regressors, list):
        raise ValueError('regressors must be a list of column names')
    hist, future = _split_future(d, regressors)
    require(hist, ['timestamp', 'target'] + regressors)
    f, freq = time_frame(hist, c, columns=('target', *regressors), minimum=max(4 * integer(c, 'horizon', 12), 60))
    h = integer(c, 'horizon', 12); seed = integer(c, 'seed', 16, 0); np.random.seed(seed)
    priors = c.get('priors', [0.001, 0.05, 0.5])
    if not isinstance(priors, list) or not all(isinstance(p, (int, float)) and p > 0 for p in priors):
        raise ValueError('priors must be a list of positive numbers')
    n_origins = integer(c, 'origins', 2, 1)
    events = c.get('events', [])
    holidays = None
    if events:
        rows = []
        for e in events:
            if not isinstance(e, dict) or 'name' not in e or 'date' not in e:
                raise ValueError('each event needs name and date')
            rows.append(dict(holiday=str(e['name']), ds=pd.to_datetime(e['date']).tz_localize(None) if pd.to_datetime(e['date']).tzinfo else pd.to_datetime(e['date']),
                             lower_window=int(e.get('lower_window', 0)), upper_window=int(e.get('upper_window', 0))))
        holidays = pd.DataFrame(rows)
    mode = c.get('mode', 'auto')
    if mode not in ('auto', 'additive', 'multiplicative'):
        raise ValueError("mode must be 'auto', 'additive' or 'multiplicative'")
    y = f.target.to_numpy(float); n = len(y); end = n - h
    if mode == 'auto':
        use_log, note = choose_log(y[:end - n_origins * h])
        mode_used = 'multiplicative' if use_log else 'additive'
    else:
        mode_used = mode; note = {'forced': mode}
    if mode_used == 'multiplicative' and np.any(y <= 0):
        raise ValueError('multiplicative seasonality requires positive values')
    weekly = bool(c.get('weekly', False)); yearly = bool(c.get('yearly', True))
    frame = pd.DataFrame({'ds': f.timestamp.dt.tz_localize(None), 'y': y})
    for r in regressors:
        frame[r] = f[r].to_numpy(float)

    def block_mae(stop, prior, hol, regs):
        m = _fit(frame.iloc[:stop - h][['ds', 'y'] + regs], hol, regs, prior, mode_used, weekly, yearly, seed, uncertainty=0)
        pred = m.predict(frame.iloc[stop - h:stop][['ds'] + regs])
        return float(np.abs(pred.yhat.to_numpy() - y[stop - h:stop]).mean())

    origins = [end - j * h for j in range(n_origins, 0, -1)]   # blocks end at end-(j-1)*h, all before the holdout
    if origins[0] - h < max(24, 2 * integer(c, 'season', 12)):
        raise ValueError('Not enough history before the selection origins')
    validation = {}
    for prior in priors:
        validation[prior] = [block_mae(o, prior, holidays, regressors) for o in origins]
    chosen = min(priors, key=lambda p: np.mean(validation[p]))
    ablation = {'full': float(np.mean(validation[chosen]))}
    if holidays is not None:
        ablation['without_events'] = float(np.mean([block_mae(o, chosen, None, regressors) for o in origins]))
    if regressors:
        ablation['without_regressors'] = float(np.mean([block_mae(o, chosen, holidays, []) for o in origins]))
    m = _fit(frame.iloc[:end][['ds', 'y'] + regressors], holidays, regressors, chosen, mode_used, weekly, yearly, seed)
    test = m.predict(frame.iloc[end:][['ds'] + regressors])
    test_mae = float(np.abs(test.yhat.to_numpy() - y[end:]).mean())
    test_cov = float(np.mean((y[end:] >= test.yhat_lower.to_numpy()) & (y[end:] <= test.yhat_upper.to_numpy())))
    not_done = []
    if regressors and len(future) != h:
        table = pd.DataFrame({'timestamp': f.timestamp.iloc[end:].to_numpy(), 'lower': test.yhat_lower.to_numpy(), 'forecast': test.yhat.to_numpy(), 'upper': test.yhat_upper.to_numpy()})
        scope = 'holdout'
        not_done.append(f'Future forecast skipped: regressors {regressors} need exactly {h} trailing rows with empty target and known regressor values (found {len(future)})')
    else:
        final = _fit(frame[['ds', 'y'] + regressors], holidays, regressors, chosen, mode_used, weekly, yearly, seed)
        dates = pd.date_range(frame.ds.iloc[-1], periods=h + 1, freq=freq)[1:]
        fut = pd.DataFrame({'ds': dates})
        for r in regressors:
            fut[r] = pd.to_numeric(future[r], errors='raise').to_numpy(float)
        pred = final.predict(fut)
        table = pd.DataFrame({'timestamp': dates, 'lower': pred.yhat_lower.to_numpy(), 'forecast': pred.yhat.to_numpy(), 'upper': pred.yhat_upper.to_numpy()})
        scope = 'future'
    if holidays is None:
        not_done.append('No events supplied; calendar effects not modelled')
    if not regressors:
        not_done.append('No regressors supplied')
    not_done.append('Coverage measured on one holdout only; nominal 80% band is not certified')
    interpretation = (f'Prophet ({mode_used} seasonality, changepoint prior {chosen}) holdout MAE {test_mae:.4g}, nominal 80% band coverage {test_cov:.0%}. '
                      + (f'Removing events changes validation MAE from {ablation["full"]:.4g} to {ablation["without_events"]:.4g}. ' if 'without_events' in ablation else '')
                      + (f'Removing regressors changes it to {ablation["without_regressors"]:.4g}. ' if 'without_regressors' in ablation else '')
                      + f'Table scope: {scope}.')
    return finish(table, method='Prophet with event calendar and known regressors', interpretation=interpretation,
                  assumptions=[f'{mode_used} seasonality chosen ' + ('by Box-Cox on training data' if mode == 'auto' else 'by config'), 'Event dates and windows correct and known in advance', 'Regressors known for the horizon'],
                  not_done=not_done, status='passed', mode=mode_used, mode_note=note, prior=chosen, validation={str(k): v for k, v in validation.items()}, ablation=ablation,
                  test_mae=test_mae, test_coverage=test_cov, nominal=0.8, table_scope=scope, events=len(events), regressors=regressors)
