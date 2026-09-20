"""Chapter 23: nowcasting under reporting delay, and an SEIR forecast checked against persistence.

Estimates the delay law from cohorts old enough to be complete, nowcasts recent dates
with binomial-completeness uncertainty, evaluates archived nowcasts by reporting age
against final counts, and (given a population) fits SEIR transmission on data up to each
origin and scores its horizon forecasts against persistence.
"""
import numpy as np
import pandas as pd
from scipy import stats
from scipy.integrate import solve_ivp
from scipy.optimize import least_squares
from .core import require, numeric, integer, finish


def estimate_delay_law(triangle, mature_age, max_delay):
    """Empirical delay distribution from cohorts aged >= mature_age, truncated at max_delay."""
    mature = triangle[triangle.age >= mature_age]
    if mature.event_date.nunique() < 10:
        raise ValueError(f'Need at least 10 cohorts aged {mature_age}+ to estimate the delay law; supply delay_prob instead')
    counts = np.zeros(max_delay + 1)
    for lag, g in mature.groupby('lag'):
        if lag <= max_delay:
            counts[int(lag)] += g['count'].sum()
    if counts.sum() <= 0:
        raise ValueError('No reports in mature cohorts')
    return counts / counts.sum(), int(mature.event_date.nunique())


def seir_fit(incidence, population, gamma, sigma_fixed=None):
    """Fit beta (and sigma) so that model incidence tracks observed incidence from the first case."""
    n = len(incidence)
    def simulate(beta, sigma, days):
        i0 = max(incidence[0], 1.0); e0 = i0
        def rate(t, v):
            S, E, I, R = v
            return [-beta * S * I / population, beta * S * I / population - sigma * E, sigma * E - gamma * I, gamma * I]
        sol = solve_ivp(rate, (0, days), [population - e0 - i0, e0, i0, 0.], t_eval=np.arange(days + 1), rtol=1e-6, atol=1e-6)
        S = sol.y[0]; return np.maximum(-np.diff(S), 0)   # new infections per day
    if sigma_fixed is None:
        res = least_squares(lambda p: simulate(p[0], p[1], n) - incidence, [0.3, 0.25], bounds=([1e-4, 0.05], [5, 1.0]))
        beta, sigma = res.x
    else:
        res = least_squares(lambda p: simulate(p[0], sigma_fixed, n) - incidence, [0.3], bounds=([1e-4], [5]))
        beta, sigma = res.x[0], sigma_fixed
    return float(beta), float(sigma), simulate


def nowcast_and_seir(d, c):
    require(d, ['event_date', 'report_date', 'count']); numeric(d, ['count'], True)
    if np.any(d['count'] != np.floor(d['count'])):
        raise ValueError('Case counts must be integers')
    if not c.get('as_of'):
        raise ValueError('as_of is required')
    asof = pd.to_datetime(c['as_of'], utc=True); f = d.copy()
    f['event_date'] = pd.to_datetime(f.event_date, utc=True); f['report_date'] = pd.to_datetime(f.report_date, utc=True)
    if (f.report_date < f.event_date).any():
        raise ValueError('Report date cannot precede event date')
    full = f.copy()
    f = f[(f.report_date <= asof) & (f.event_date <= asof)]
    if f.empty:
        raise ValueError('No reports available at cutoff')
    f['lag'] = (f.report_date - f.event_date).dt.days; f['age'] = (asof - f.event_date).dt.days
    mature_age = integer(c, 'mature_age', 7, 1); max_delay = integer(c, 'max_delay', mature_age, 1)
    not_done = []
    if c.get('delay_prob') is not None:
        p = np.asarray(c['delay_prob'], float)
        if p.ndim != 1 or not len(p) or not np.isfinite(p).all() or np.any(p < 0) or not np.isclose(p.sum(), 1):
            raise ValueError('Supply a nonnegative delay distribution summing to one')
        law_source = 'supplied'; law_cohorts = None
    else:
        p, law_cohorts = estimate_delay_law(f, mature_age, max_delay); law_source = f'estimated from {law_cohorts} cohorts aged {mature_age}+'
    rows = []
    for day, g in f.groupby('event_date'):
        age = int((asof - day).days); complete = float(p[:min(len(p), age + 1)].sum())
        if complete <= 0:
            raise ValueError('Zero completeness prevents finite nowcast')
        reported = int(g['count'].sum())
        if complete >= 1 - 1e-12:
            lo = hi = float(reported)
        else:
            # eventual total given reported ~ reported + NegBin(reported+1, complete) on the not-yet-reported part
            lo = reported + float(stats.nbinom.ppf(0.05, reported + 1, complete)); hi = reported + float(stats.nbinom.ppf(0.95, reported + 1, complete))
        rows.append(dict(event_date=day, age=age, reported=reported, completeness=complete, nowcast=reported / complete, lower=lo, upper=hi))
    table = pd.DataFrame(rows).sort_values('event_date')
    # archived evaluation: for mature cohorts, what would the nowcast have said at each younger age?
    archived = None
    final_counts = full.groupby('event_date')['count'].sum()
    mature_days = table[table.age >= mature_age].event_date
    if len(mature_days) >= 5:
        errs = {a: [] for a in range(mature_age)}
        for day in mature_days:
            reports = f[f.event_date == day]
            for a in range(mature_age):
                seen = reports[reports.lag <= a]['count'].sum(); comp = float(p[:min(len(p), a + 1)].sum())
                if comp > 0:
                    errs[a].append(abs(seen / comp - final_counts[day]))
        archived = dict(mae_by_age={int(a): float(np.mean(v)) for a, v in errs.items() if v}, cohorts=int(len(mature_days)), note='In-sample where the delay law was estimated from the same cohorts')
    else:
        not_done.append('Archived nowcast evaluation skipped: fewer than 5 mature cohorts')
    # SEIR
    seir = None; population = c.get('population')
    if population is None:
        not_done.append('SEIR forecast skipped: supply population')
    else:
        population = float(population); horizon = integer(c, 'horizon', 7, 1); n_origins = integer(c, 'origins', 3, 1)
        gamma = float(c.get('recovery_rate', 0.1)); sigma_fixed = c.get('sigma')
        inc = table[table.age >= mature_age].sort_values('event_date').nowcast.to_numpy(float)
        if len(inc) < 20 + horizon:
            not_done.append('SEIR forecast skipped: need at least 20 mature days plus the horizon')
        else:
            origins = [len(inc) - horizon - j * horizon for j in range(n_origins - 1, -1, -1)]
            origins = [o for o in origins if o >= 15]
            results = []
            for o in origins:
                beta, sigma, simulate = seir_fit(inc[:o], population, gamma, sigma_fixed)
                path = simulate(beta, sigma, o + horizon)[o:o + horizon]; actual = inc[o:o + horizon]
                results.append(dict(origin_index=int(o), beta=beta, sigma=sigma, R0=float(beta / gamma), rmse=float(np.sqrt(np.mean((path - actual) ** 2))), persistence_rmse=float(np.sqrt(np.mean((inc[o - 1] - actual) ** 2)))))
            seir = dict(origins=results, gamma=gamma, sigma_fixed=sigma_fixed, mean_rmse=float(np.mean([r['rmse'] for r in results])), mean_persistence_rmse=float(np.mean([r['persistence_rmse'] for r in results])),
                        note='Fitted on delay-adjusted mature incidence up to each origin; conditional scenario, behaviour and reporting changes are not modelled')
    young = table[table.age < mature_age]
    interpretation = (f'Delay law {law_source}: {np.round(p, 3).tolist()}. {len(young)} event dates are still incomplete at the cutoff; their nowcasts carry 90% bounds from the completeness estimate. '
                      + (f'Archived nowcast MAE by age: {archived["mae_by_age"]}. ' if archived else '')
                      + (f'SEIR mean RMSE {seir["mean_rmse"]:.3g} vs persistence {seir["mean_persistence_rmse"]:.3g} over {len(seir["origins"])} origins (R0 estimates {[round(r["R0"], 2) for r in seir["origins"]]}). ' if seir else '')
                      + 'Nowcasting answers what is happening now; the SEIR block answers what may happen next; do not read one as proof of the other.')
    return finish(table, method='Reporting-triangle nowcast with estimated delay law' + (' and SEIR forecast' if seir else ''), interpretation=interpretation,
                  assumptions=['Delay law stable across cohorts', 'Reports at the cutoff are complete for their lag', 'Eventual totals follow a negative binomial given the reported count'],
                  not_done=not_done, status='passed', delay_law=dict(probabilities=p.tolist(), source=law_source, cohorts=law_cohorts, mature_age=mature_age), archived_evaluation=archived, seir=seir, as_of=str(asof))
