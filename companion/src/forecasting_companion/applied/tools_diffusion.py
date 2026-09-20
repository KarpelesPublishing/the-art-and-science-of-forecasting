"""Chapter 19: diffusion into sales.

Wraps the Bass fits from methods.diffusion, then turns first adoption into a sales
curve under two timing assumptions (Bass incidence and the author's gamma-shaped
launch curve, each spread with the same repeat kernel), optionally holds q fixed,
and computes a Parfitt-Collins steady-state share when trial, repeat and buying-rate
inputs are supplied.
"""
import numpy as np
import pandas as pd
from .core import numeric, integer, finish


def bass_curve(t, p, q, m):
    e = np.exp(-(p + q) * t); return m * (1 - e) / (1 + q / p * e)


def parfitt_collins(T, R, B=1.0):
    """Steady-state share = trial * repeat * buying-rate index; band from +-20 percent on repeat."""
    for name, v in (('T', T), ('R', R), ('B', B)):
        if not np.isfinite(v) or v < 0 or (name != 'B' and v > 1):
            raise ValueError('Parfitt-Collins inputs must be finite; T and R in [0,1]')
    share = T * R * B
    return dict(share=float(share), low=float(T * max(0, R * 0.8) * B), high=float(T * min(1, R * 1.2) * B))


def diffusion_sales(d, c):
    from scipy.optimize import least_squares
    from .methods import diffusion
    from ..practitioner import launch_trials, cohort_units
    table0, base = diffusion(d, c)
    a = numeric(d, ['time', 'adopters'], True); a = a[np.argsort(a[:, 0])]
    horizon = integer(c, 'sales_horizon', 24, 24); peak = integer(c, 'peak', 4, 3)
    if peak > 5:
        raise ValueError('peak must be 3, 4 or 5')
    units_at_trial = float(c.get('units_at_trial', 1.0)); kernel = list(c.get('repeat_kernel', []))
    if units_at_trial <= 0 or any((not np.isfinite(k)) or k < 0 for k in kernel):
        raise ValueError('units_at_trial must be positive and repeat_kernel nonnegative')
    kernel = ([units_at_trial] + kernel)[:horizon]
    fix_q = c.get('fix_q')
    fits = []; rows = []; comparison = []
    for fit in base['fits']:
        m = fit['ceiling']; p, q = fit['p'], fit['q']
        entry = dict(fit)
        if fix_q is not None:
            fq = float(fix_q)
            if not 0 < fq < 3:
                raise ValueError('fix_q must be in (0,3)')
            r = least_squares(lambda pars: (bass_curve(a[:, 0], pars[0], fq, m) - a[:, 1]) / m, [.03], bounds=([.00001], [2]))
            entry.update(p_fixed_q=float(r.x[0]), q_fixed=fq, fixed_q_rmse=float(np.sqrt(np.mean((bass_curve(a[:, 0], r.x[0], fq, m) - a[:, 1]) ** 2))))
            p, q = float(r.x[0]), fq
        last_t = a[-1, 0]; last_c = a[-1, 1]
        future = last_t + np.arange(1, horizon + 1)
        cum = np.maximum.accumulate(np.r_[last_c, bass_curve(future, p, q, m)])
        bass_trials = np.diff(cum)
        gamma_trials = launch_trials(float(bass_trials.sum()), peak=peak, horizon=horizon, denominator='horizon')
        bass_units = cohort_units(bass_trials, kernel); gamma_units = cohort_units(gamma_trials, kernel)
        for j in range(horizon):
            rows.append(dict(time=float(future[j]), ceiling=m, bass_trials=float(bass_trials[j]), gamma_trials=float(gamma_trials[j]), bass_units=float(bass_units[j]), gamma_units=float(gamma_units[j])))
        comparison.append(dict(ceiling=m, trial_total=float(bass_trials.sum()), bass_peak_period=int(np.argmax(bass_trials) + 1), gamma_peak_period=int(np.argmax(gamma_trials) + 1),
                               bass_units_12=float(bass_units[:12].sum()), gamma_units_12=float(gamma_units[:12].sum()), bass_units_total=float(bass_units.sum()), gamma_units_total=float(gamma_units.sum())))
        fits.append(entry)
    pc = None; not_done = ['No price, distribution or advertising drivers in the adoption curve', 'Repeat kernel is assumed, not estimated from panel data']
    if c.get('parfitt_collins') is not None:
        spec = c['parfitt_collins']
        if not isinstance(spec, dict) or 'T' not in spec or 'R' not in spec:
            raise ValueError('parfitt_collins needs T and R (and optional B)')
        pc = parfitt_collins(float(spec['T']), float(spec['R']), float(spec.get('B', 1.0)))
    else:
        not_done.append('Parfitt-Collins share needs T, R (and B) inputs')
    table = pd.DataFrame(rows)
    mid = comparison[len(comparison) // 2]
    interpretation = (base['interpretation'] + f' Sales layer: over {horizon} {c.get("time_unit", "month")}s the same trial total ({mid["trial_total"]:.0f} at ceiling {mid["ceiling"]:g}) peaks in period {mid["bass_peak_period"]} under Bass timing and period {mid["gamma_peak_period"]} under the {peak}-peak launch curve; '
                      + f'12-period units {mid["bass_units_12"]:.0f} vs {mid["gamma_units_12"]:.0f}. Timing assumptions change the year-one number even when the eventual total is identical.'
                      + (f' Parfitt-Collins steady-state share {pc["share"]:.1%} (band {pc["low"]:.1%} to {pc["high"]:.1%}).' if pc else '')
                      + (f' q held at {fix_q}.' if fix_q is not None else ''))
    return finish(table, method='Bass diffusion with sales conversion under two timing curves', interpretation=interpretation,
                  assumptions=['Cumulative adopters follow a Bass curve for each declared ceiling', 'Each trier buys units_at_trial at first purchase and the repeat kernel afterwards', 'Launch-curve peak month is a judgment input', 'sales_horizon (24 or more periods) is separate from the Bass table horizon'],
                  not_done=not_done, status='passed' if base['fits'] else 'needs_evidence',
                  fits=fits, ceilings=list(c.get('ceilings')), sales_horizon=horizon, peak=peak, kernel=kernel, timing_comparison=comparison, parfitt_collins=pc, bass_table_rows=int(len(table0)))
