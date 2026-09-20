"""Chapter 21: from an intermittent forecast to an inventory policy, and the bullwhip.

Croston, SBA and TSB one-step forecasts (pre-update), a bootstrapped lead-time demand
distribution, an order-up-to policy simulated with a pipeline and carried backlog
(cycle service, fill rate, on-hand, backlog, cost), and an N-echelon bullwhip simulator
comparing local ordering with shared end-consumer information.
"""
import numpy as np
import pandas as pd
from .core import time_frame, numeric, integer, finish


def intermittent(y, alpha=0.15):
    size = max(y[0], 1); interval = 5.; prob = .2; gap = 1; rows = []
    for v in y:
        rows.append(dict(Croston=size / interval, SBA=(1 - alpha / 2) * size / interval, TSB=prob * size))
        prob = (1 - alpha) * prob + alpha * (v > 0)
        if v > 0:
            size = (1 - alpha) * size + alpha * v; interval = (1 - alpha) * interval + alpha * gap; gap = 1
        else:
            gap += 1
    return pd.DataFrame(rows)


def echelons(demand, n_echelons=3, lead=3, alpha=0.5, shared=False, warmup=50):
    """Order-up-to chain. Each echelon sees its downstream orders (local) or the consumer signal (shared)."""
    demand = np.asarray(demand, float); T = len(demand); stages = []
    incoming = demand.copy()
    for _ in range(n_echelons):
        signal_src = demand if shared else incoming
        est = signal_src[:max(1, warmup)].mean() if T > 0 else 0.
        inv = est * (lead + 1); pipeline = [est] * lead; orders = np.zeros(T)
        for t in range(T):
            est = alpha * signal_src[t] + (1 - alpha) * est
            inv += pipeline.pop(0); inv -= incoming[t]
            target = est * (lead + 1)
            order = max(0., target - inv - sum(pipeline)); orders[t] = order; pipeline.append(order)
        stages.append(orders); incoming = orders
    ratios = [float(np.var(s[warmup:]) / max(np.var(demand[warmup:]), 1e-9)) for s in stages]
    return stages, ratios


def inventory_policy(d, c):
    f, _ = time_frame(d, c, minimum=30); numeric(f, ['target'], True); y = f.target.to_numpy(float); n = len(y)
    cu = float(c.get('underage_cost', 9)); co = float(c.get('overage_cost', 3))
    if not np.isfinite([cu, co]).all() or min(cu, co) <= 0:
        raise ValueError('Positive finite underage and overage costs required')
    lead = integer(c, 'lead_time', 2, 0); review = integer(c, 'review_period', 1, 1)
    service = float(c.get('service_level', 0.95))
    if not 0 < service < 1:
        raise ValueError('service_level must lie in (0,1)')
    window = integer(c, 'bootstrap_window', min(52, n // 2), 5); samples = integer(c, 'samples', 2000, 100)
    holding = float(c.get('holding_cost', co)); backorder = float(c.get('backorder_cost', cu))
    n_ech = integer(c, 'echelons', 3, 1); seed = integer(c, 'seed', 21, 0); rng = np.random.default_rng(seed)
    fc = intermittent(y); start = max(10, n // 2, window)
    protection = lead + review
    # policy simulation over the test period
    on_hand = float(np.mean(y[:start])) * (lead + 1); backlog = 0.; pipeline = [0.] * lead
    rows = []; served = 0.; demanded = 0.; stockouts = 0; cycles = 0; cost = 0.
    for t in range(start, n):
        hist = y[max(0, t - window):t]
        draws = rng.choice(hist, size=(samples, protection), replace=True).sum(axis=1)
        s_up = float(np.quantile(draws, service))
        cost_q = float(np.quantile(draws, cu / (cu + co)))
        arrived = pipeline.pop(0); on_hand += arrived
        # serve backlog first, then today's demand
        fill_backlog = min(on_hand, backlog); on_hand -= fill_backlog; backlog -= fill_backlog
        demand = y[t]; served_today = min(on_hand, demand); on_hand -= served_today; short = demand - served_today; backlog += short
        served += served_today; demanded += demand
        if (t - start) % review == 0:
            cycles += 1; stockouts += int(short > 0)
            position = on_hand - backlog + sum(pipeline); order = max(0., s_up - position); pipeline.append(order)
        else:
            order = 0.; pipeline.append(0.)
        cost += holding * on_hand + backorder * backlog
        rows.append(dict(timestamp=f.timestamp.iloc[t], actual=demand, Croston=fc.Croston.iloc[t], SBA=fc.SBA.iloc[t], TSB=fc.TSB.iloc[t],
                         order_up_to=s_up, cost_optimal_order_up_to=cost_q, on_hand=on_hand, backlog=backlog, order=order))
    table = pd.DataFrame(rows)
    stages_local, ratios_local = echelons(y, n_ech, lead, shared=False, warmup=min(50, n // 3))
    stages_shared, ratios_shared = echelons(y, n_ech, lead, shared=True, warmup=min(50, n // 3))
    mae = {k: float(abs(table[k] - table.actual).mean()) for k in ['Croston', 'SBA', 'TSB']}
    fill_rate = float(served / demanded) if demanded > 0 else 1.0
    cycle_service = float(1 - stockouts / cycles) if cycles else 1.0
    not_done = ['Lead time treated as fixed; no supplier variability or capacity limits', 'Demand treated as uncensored sales; stockouts in history are not corrected', 'Costs are per period on-hand and backlog only']
    interpretation = (f'Intermittent forecasts MAE: ' + ', '.join(f'{k} {v:.3g}' for k, v in mae.items()) + f'. Order-up-to policy at {service:.0%} target over a {protection}-period protection window: '
                      f'cycle service {cycle_service:.0%}, fill rate {fill_rate:.0%}, mean on-hand {table.on_hand.mean():.3g}, mean backlog {table.backlog.mean():.3g}. '
                      f'Bullwhip variance ratios by echelon, local {[round(r, 2) for r in ratios_local]} vs shared signal {[round(r, 2) for r in ratios_shared]}.')
    return finish(table, method='Intermittent-demand forecasts, bootstrapped order-up-to policy simulation, N-echelon bullwhip', interpretation=interpretation,
                  assumptions=[f'Lead time {lead}, review period {review}', 'Demand during protection window bootstrapped from the trailing window', 'Unmet demand is backordered, not lost'],
                  not_done=not_done, status='passed', mae=mae, lead_time=lead, review_period=review, service_level=service, achieved_cycle_service=cycle_service, fill_rate=fill_rate,
                  mean_on_hand=float(table.on_hand.mean()), mean_backlog=float(table.backlog.mean()), mean_cost=float(cost / max(len(table), 1)),
                  bullwhip=dict(echelons=n_ech, local_variance_ratios=ratios_local, shared_variance_ratios=ratios_shared), training_quantile_order=float(np.quantile(y[:start], cu / (cu + co))))
