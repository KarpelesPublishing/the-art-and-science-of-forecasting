"""Explicit teaching calculations for launch calibration, MMM and event journals.

Gamma timing represents awareness/distribution development, not an extra delay.
All business assumptions must be supplied and validated outside these arithmetic tools.
"""
from datetime import date, datetime
import numpy as np
from scipy.optimize import brentq
from scipy.stats import gamma


def _vector(values, nonnegative=True):
    x = np.asarray(values, dtype=float)
    if x.ndim != 1 or not x.size or not np.isfinite(x).all():
        raise ValueError('Expected a nonempty finite vector')
    if nonnegative and np.any(x < 0):
        raise ValueError('Negative values are not permitted')
    return x


def gamma_shape(horizon=24, denominator='horizon'):
    """Solve mode=4 months, year-one fraction=.8; denominator must be explicit."""
    if denominator not in ('horizon', 'eventual'):
        raise ValueError('Choose horizon or eventual denominator')
    if not isinstance(horizon, int) or isinstance(horizon, bool) or horizon < 24:
        raise ValueError('Specify an integer forecast horizon of at least 24 months')
    def objective(shape):
        scale = 4/(shape-1)
        denominator_mass = gamma.cdf(horizon, shape, scale=scale) if denominator == 'horizon' else 1.
        return gamma.cdf(12, shape, scale=scale)/denominator_mass - .8
    return brentq(objective, 1.001, 100.)


def launch_trials(total, *, peak=4, horizon=24, denominator):
    """Monthly first-trial counts. total is horizon-limited or eventual, never annual.

    The author supplies modes 3/4/5 and standard year-one share .8. Holding shape
    fixed and varying scale for fast/slow scenarios is an explicit implementation
    convention, not a recovered proprietary model. No extra ramp is multiplied in.
    """
    if not np.isfinite(total) or total < 0 or not np.isfinite(peak) or peak <= 0:
        raise ValueError('Finite nonnegative total and positive peak required')
    shape = gamma_shape(horizon, denominator)
    cumulative = gamma.cdf(np.arange(horizon+1), shape, scale=peak/(shape-1))
    if denominator == 'horizon':
        cumulative /= cumulative[-1]
    return total*np.diff(cumulative)


def trials_from_reach(total, awareness_progress, availability_given_awareness_progress):
    """Alternative to gamma timing: increments of joint cumulative reach.

    These are normalized progress-to-final-level curves, not raw ACV percentages.
    Availability is conditional; multiplying unrelated marginal reaches is invalid.
    This simple teaching model assumes trial upon joint reach, with no extra delay.
    Final awareness/availability levels belong in the potential-volume calculation.
    """
    a, d = _vector(awareness_progress), _vector(availability_given_awareness_progress)
    if a.shape != d.shape or not np.isfinite(total) or total < 0:
        raise ValueError('Aligned progress curves and nonnegative total required')
    for x in (a,d):
        if np.any(x > 1) or np.any(np.diff(x) < 0) or x[0] != 0:
            raise ValueError('Progress must start at zero, be nondecreasing and at most one')
    return total*np.diff(a*d)


def cohort_units(trials, units_by_cohort_age):
    """Age-zero trial units plus later expected repeat units per original trier."""
    trials, kernel = _vector(trials), _vector(units_by_cohort_age)
    return np.convolve(trials, kernel)[:len(trials)]


def calibrate_scale(exposure, observed_volume):
    """One shared nonnegative scale, fitted across reference products; no free per-SKU fit."""
    x,y = _vector(exposure), _vector(observed_volume)
    if x.shape != y.shape or x@x == 0:
        raise ValueError('Aligned observations and positive exposure required')
    return float(x@y/(x@x))


def evidence_weight(research_date, as_of, half_life_months):
    """Optional relevance-weight scenario; does NOT reduce demand or purchase interest."""
    age = (date.fromisoformat(as_of)-date.fromisoformat(research_date)).days/30.4375
    if age < 0 or not np.isfinite(half_life_months) or half_life_months <= 0:
        raise ValueError('Research must precede cutoff; supply positive scenario half-life')
    return float(2**(-age/half_life_months))


def _time(value):
    result = datetime.fromisoformat(value)
    if result.tzinfo is None:
        raise ValueError('Use timezone-aware ISO timestamps')
    return result


def score_journal(events, revisions, *, as_of):
    """Latest predeclared-cutoff, pre-resolution revision; equal weight per event.

    This scores supplied records; it does not authenticate timestamps or make an
    editable JSON file tamper-proof. Retain an append-only external audit history.
    """
    now = _time(as_of)
    event_map = {e['event_id']:e for e in events}
    if len(event_map) != len(events):
        raise ValueError('Duplicate event IDs')
    seen = set()
    for r in revisions:
        key = (r['event_id'],_time(r['timestamp']))
        if key in seen or r['event_id'] not in event_map:
            raise ValueError('Duplicate revision timestamp or unknown event')
        seen.add(key)
        if not np.isfinite(r['probability']) or not 0 <= r['probability'] <= 1:
            raise ValueError('Invalid probability')
    result=[]
    for event in events:
        if event['outcome'] is None or event['resolved_at'] is None:
            continue
        if event['outcome'] not in (0,1) or not 0 <= event['baseline'] <= 1:
            raise ValueError('Binary outcome and valid predeclared baseline required')
        resolution = _time(event['resolved_at'])
        if resolution > now:
            continue
        cutoff = _time(event['cutoff'])
        eligible = [r for r in revisions if r['event_id']==event['event_id']
                    and _time(r['timestamp']) <= cutoff and _time(r['timestamp']) < resolution
                    and _time(r['timestamp']) <= now]
        if not eligible:
            continue
        chosen = max(eligible,key=lambda r:_time(r['timestamp']))
        p,y=chosen['probability'],event['outcome']
        result.append(dict(event_id=event['event_id'], probability=p, outcome=y,
                           timestamp=chosen['timestamp'], brier=(p-y)**2,
                           baseline_brier=(event['baseline']-y)**2))
    return result


def adstock(values, decay, initial=0.):
    x = _vector(values)
    if not 0 <= decay < 1 or not np.isfinite(initial) or initial < 0:
        raise ValueError('Decay in [0,1) and nonnegative initial stock required')
    result=np.empty_like(x); state=float(initial)
    for i,value in enumerate(x):
        state=value+decay*state
        result[i]=state
    return result


def gaussian_update(design, outcome, prior_mean, prior_sd, noise_sd):
    """Exact Gaussian posterior conditional on fixed transforms/background/noise.

    Not a full nonlinear Bayesian MMM. Scalar independent prior SD for simplicity.
    """
    X=np.asarray(design,dtype=float); y=_vector(outcome,False); mu=_vector(prior_mean,False)
    if X.ndim != 2 or X.shape != (len(y),len(mu)) or not np.isfinite(X).all():
        raise ValueError('Invalid design dimensions or nonfinite values')
    if not np.isfinite([prior_sd,noise_sd]).all() or min(prior_sd,noise_sd)<=0:
        raise ValueError('Positive finite standard deviations required')
    precision=X.T@X/noise_sd**2+np.eye(len(mu))/prior_sd**2
    cov=np.linalg.inv(precision)
    return cov@(X.T@y/noise_sd**2+mu/prior_sd**2),cov
