"""A pre-launch volume forecaster that needs no test market.

This is the author's top-down bottom-up triangulation model, the same model that ships as the `reconcile-tdbu`
skill in forecasting-skills/ (tests hold the two equal). Every consumer measurement a
simulated test market would supply (awareness, trial, repeat, share of choice,
build speed) has a model-derived default, and every default has an override so a
real measurement can replace it. Two engines then compute year-one volume from
the same inputs: one holds category penetration fixed and solves for market size
(bottom-up); the other holds market size fixed and solves for penetration
(top-down). The model also reports what each typed input *should* be given
the others (the implication check); feeding implications back into the inputs
converges in a couple of passes.

ABOUT THE COEFFICIENTS. Every coefficient and curve constant in this module is an
illustrative starting value. None was taken from a published study, a vendor
model or a client dataset; they are generic numbers, set by judgment, that put a
launch forecast in the right ballpark for an ordinary packaged-goods category.
They are meant to be replaced. If you have your own launch history, fit the
trial and awareness relationships to it; if you do not, adjust these values
until the model reproduces launches you know, and record what you changed. The
architecture (the two engines, the implication check, the overrides) is the
durable part. The numbers are placeholders with sensible magnitudes.

Units: the engines produce millions of units. Multiplying by price gives millions
of dollars. Dividing dollars by a unit-volume market size gives a mixed-unit
"share" that is only a volume share when price is 1; this port reports units,
dollars and both share definitions separately so the distinction stays visible.
"""
from __future__ import annotations

from dataclasses import dataclass, field, replace
import math
from typing import Optional

BUILD_SPEEDS = ["Very Fast", "Somewhat Fast", "Standard", "Somewhat Slow", "Very Slow"]


# --------------------------------------------------------------------------
# Inputs
# --------------------------------------------------------------------------
@dataclass
class HardInputs:
    """The six typed inputs. Everything else is derived or overridden."""
    repeat_units_per_purchase: float = 1.43   # survey
    category_purchases_per_year: float = 20.0  # survey, as claimed
    distribution: float = 0.63                 # client
    category_penetration: float = 0.53         # client data or a category model
    population_mm: float = 118.0               # households, millions
    market_size_mm_volume: float = 415.0       # category unit volume, millions


@dataclass
class TrialDetector:
    """Seven judgment scores and the illustrative coefficients that turn them into a trial rate.

    Scores are indexed attributes (100 is roughly the category norm) that a
    brand team can set by judgment or from a concept test. The output is the
    probability of trial among aware buyers who can find the product, as a
    percentage. The coefficients are generic starting values, not estimates
    from any dataset; replace them with your own calibration when you have one.
    """
    differentiation: float = 122.0
    relevance: float = 98.0
    share_of_leader: float = 25.0
    visibility: float = 55.0
    brands_at_80_share: float = 22.0
    brands_in_evoked_set: float = 5.0
    expensiveness: float = 114.0
    coefficients: dict = field(default_factory=lambda: {
        "differentiation": 0.27,
        "relevance": 0.23,
        "share_of_leader": 0.30,
        "visibility": 0.28,
        "brands_at_80_share": -0.22,
        "brands_in_evoked_set": -3.0,
        "expensiveness": -0.15,
    })
    intercept: float = -15.5

    def scores(self) -> dict:
        return {k: getattr(self, k) for k in self.coefficients}

    def index(self) -> float:
        """Weighted attribute index plus intercept, before the trial transform."""
        return sum(self.scores()[k] * c for k, c in self.coefficients.items()) + self.intercept + 10

    def trial_percent(self) -> float:
        """Trial probability among aware buyers with the product available, in percent."""
        bracket = self.index()
        if bracket < 0.001:
            return 1.0
        return round(1.75 + bracket ** 1.5 / 10, 1)

    def contributions(self) -> dict:
        """Points each attribute adds to or removes from the index."""
        return {k: self.scores()[k] * c for k, c in self.coefficients.items()}


@dataclass
class AwarenessModel:
    """Awareness from a media plan, with a shelf-presence uplift.

    Constants are illustrative starting values, not fitted estimates.
    """
    branding: str = "LX"              # "LX" line extension or "NB" new brand
    brand_name_recall: float = 0.55
    forecast_weeks: float = 52.0      # weeks on air in the forecast year
    spending_mm: float = 4.6          # media spend, millions
    cost_per_grp: float = 10000.0
    # illustrative curve constants
    scale: float = 26.5
    lx_multiplier: float = 1.32
    coef_frequency: float = 0.012
    coef_recall: float = 1.95
    coef_ad_trial: float = 0.63
    coef_distribution: float = 0.9
    coef_weeks: float = -0.28
    coef_grp: float = 0.00044
    exponent: float = -0.77
    shelf_a: float = 0.66
    shelf_b: float = 0.33
    shelf_c: float = 0.9
    shelf_cap: float = 0.3

    def grps(self) -> float:
        """Gross rating points bought by the plan."""
        return self.spending_mm * 1_000_000 / self.cost_per_grp

    def media_awareness(self, adjusted_frequency: float, trial_rate: float,
                        distribution_pct: float) -> float:
        """Awareness generated by media alone. Distribution enters as a percentage (0 to 100)."""
        x = ((self.grps() * self.coef_grp + adjusted_frequency * self.coef_frequency)
             * self.forecast_weeks ** self.coef_weeks
             * math.exp(self.brand_name_recall) ** self.coef_recall
             * math.exp(trial_rate / self.brand_name_recall) ** self.coef_ad_trial
             * distribution_pct ** self.coef_distribution)
        lam = self.lx_multiplier if self.branding == "LX" else 1.0
        return 1 / (1 + lam * self.scale * x ** self.exponent)

    def with_shelf_effect(self, media: float) -> float:
        """Add what the package earns at shelf on top of media awareness."""
        uplift = (1 - media) / media * self.shelf_a * self.shelf_b * self.shelf_c \
            * max(1 - media / self.shelf_cap, 0)
        return media * (1 + uplift)


@dataclass
class Options:
    """Switches and settings: price, build speed, which measurements the models supply."""
    price: float = 3.99
    build_speed: str = "Standard"
    soc_simulator: float = 1.0                # 1 uses the derived share-of-choice bracket
    enter_frequency: bool = True              # use the observed panel frequency instead of the deflated survey claim
    calculate_awareness: bool = True
    calculate_trial: bool = True    
    external_frequency: float = 4.666666666666666  # observed category purchase frequency, per year
    awareness_if_supplied: Optional[float] = None  # a measured awareness, used when calculate_awareness is off
    trial_if_supplied: Optional[float] = None      # a measured trial rate, used when calculate_trial is off
    detector: TrialDetector = field(default_factory=TrialDetector)
    awareness: AwarenessModel = field(default_factory=AwarenessModel)

    @property
    def peak(self) -> int:
        """Month in which trial activity peaks, 2 to 6."""
        return BUILD_SPEEDS.index(self.build_speed) + 2


@dataclass
class Overrides:
    """Optional replacements for derived values. None means use the model default."""
    volume_equiv_category: Optional[float] = None
    volume_equiv_new_product: Optional[float] = None
    price_per_volume_category: Optional[float] = None
    price_per_volume_test: Optional[float] = None
    range_width_category: Optional[float] = None
    range_width_test: Optional[float] = None
    repeats_per_repeater: Optional[float] = None
    first_repeat_rate: Optional[float] = None
    units_at_trial: Optional[float] = None
    share_of_choice: Optional[float] = 0.25            # the one override in the worked example
    triers_try_first_year: Optional[float] = None


# --------------------------------------------------------------------------
# Derived defaults
# --------------------------------------------------------------------------
def adjusted_frequency(claimed: float) -> float:
    """Deflate a claimed purchase frequency: (n - 1) / 3 + 1. A standard convention, not a law."""
    return (claimed - 1) / 3 + 1


def model_frequency(hard: HardInputs, opt: Options) -> float:
    """The purchase frequency the engines actually use."""
    return opt.external_frequency if opt.enter_frequency else adjusted_frequency(hard.category_purchases_per_year)


def default_repeats_per_repeater(freq: float, peak: int) -> float:
    """Repeat purchases per repeater in year one, from frequency and build speed."""
    value = freq * math.log(2.65 * peak ** (-0.31)) - 1
    return max(value, 0.0)


def default_first_repeat_rate(claimed_frequency: float) -> float:
    """First-repeat rate as a function of the category purchase cycle."""
    cycle_ratio = ((365 / claimed_frequency - 1) / 3 + 1) / 7
    return (-11.7 * math.log(cycle_ratio) + 50) / 100


def default_triers_first_year(peak: int) -> float:
    """Share of eventual triers who try within the first year, from build speed."""
    p = peak
    return (0.000000032 * p ** 6 - 0.00000143 * p ** 5 - 0.00000384 * p ** 4
            + 0.001124 * p ** 3 - 0.01924 * p ** 2 + 0.05042 * p + 0.9625)


def soc_bracket(first_repeat_rate: float) -> tuple[float, float]:
    """Derived share-of-choice low and high, in percent."""
    low = 100 / ((3 / first_repeat_rate) - 2)
    high = 100 * (first_repeat_rate - 0.02 * math.log(101))
    return low, high


# --------------------------------------------------------------------------
# Resolved inputs: what the engines consume
# --------------------------------------------------------------------------
@dataclass
class Resolved:
    population_mm: float
    category_penetration: float
    market_size_mm_volume: float
    distribution: float
    repeat_units: float
    claimed_frequency: float
    adjusted_frequency: float
    model_frequency: float
    awareness_media: float
    awareness: float
    trial: float
    trial_index: float
    trial_contributions: dict
    units_at_trial: float
    triers_first_year: float
    repeats_per_repeater: float
    dynamics_ratio: float
    first_repeat_rate: float
    soc_low: float
    soc_high: float
    share_of_choice: float
    units_to_volume_boost: float
    peak: int
    price: float


def resolve(hard: HardInputs, opt: Options, ov: Overrides) -> Resolved:
    def pick(override, default):
        return default if override is None else override

    peak = opt.peak
    freq = model_frequency(hard, opt)
    adj = adjusted_frequency(hard.category_purchases_per_year)

    # trial
    if opt.calculate_trial:
        trial_pct = opt.detector.trial_percent()
    else:
        if opt.trial_if_supplied is None:
            raise ValueError("calculate_trial is off; supply trial_if_supplied")
        trial_pct = opt.trial_if_supplied * 100
    trial = trial_pct / 100

    # awareness
    media = opt.awareness.media_awareness(adj, trial, hard.distribution * 100)
    if opt.calculate_awareness:
        aware = opt.awareness.with_shelf_effect(media)
    else:
        if opt.awareness_if_supplied is None:
            raise ValueError("calculate_awareness is off; supply awareness_if_supplied")
        aware = opt.awareness_if_supplied

    # derived values and their overrides
    c18 = pick(ov.volume_equiv_category, 1.0)
    c19 = pick(ov.volume_equiv_new_product, 1.0)
    c20 = pick(ov.price_per_volume_category, 1.0)
    c21 = pick(ov.price_per_volume_test, 1.0)
    c22 = pick(ov.range_width_category, 1.0)
    c23 = pick(ov.range_width_test, 1.0)
    repeats = pick(ov.repeats_per_repeater, default_repeats_per_repeater(freq, peak))
    first_repeat = pick(ov.first_repeat_rate, default_first_repeat_rate(hard.category_purchases_per_year))
    units_at_trial = pick(ov.units_at_trial, 1 + (hard.repeat_units_per_purchase - 1) / 2)
    low, high = soc_bracket(first_repeat)
    soc = pick(ov.share_of_choice, opt.soc_simulator * (low + high) / 2 / 100)
    triers = pick(ov.triers_try_first_year, default_triers_first_year(peak))
    boost = (c23 / c22) ** 0.2 * (c18 / c19) ** 0.5 / ((c18 / c20) / (c19 / c21))

    return Resolved(
        population_mm=hard.population_mm,
        category_penetration=hard.category_penetration,
        market_size_mm_volume=hard.market_size_mm_volume,
        distribution=hard.distribution,
        repeat_units=hard.repeat_units_per_purchase,
        claimed_frequency=hard.category_purchases_per_year,
        adjusted_frequency=adj,
        model_frequency=freq,
        awareness_media=media,
        awareness=aware,
        trial=trial,
        trial_index=opt.detector.index() if opt.calculate_trial else float("nan"),
        trial_contributions=opt.detector.contributions() if opt.calculate_trial else {},
        units_at_trial=units_at_trial,
        triers_first_year=triers,
        repeats_per_repeater=repeats,
        dynamics_ratio=repeats / freq,
        first_repeat_rate=first_repeat,
        soc_low=low,
        soc_high=high,
        share_of_choice=soc,
        units_to_volume_boost=boost,
        peak=peak,
        price=opt.price,
    )


# --------------------------------------------------------------------------
# Engines
# --------------------------------------------------------------------------
@dataclass
class EngineResult:
    name: str
    trial_units_mm: float
    repeat_units_mm: float
    total_units_mm: float
    solved_market_size_mm: Optional[float] = None   # bottom-up only
    solved_penetration: Optional[float] = None      # top-down only
    penetration_capped: bool = False


def bottom_up(r: Resolved) -> EngineResult:
    """Bottom-up engine: penetration given, market size solved."""
    reach = r.population_mm * r.category_penetration * r.trial * r.awareness * r.distribution
    trial_units = reach * r.triers_first_year * r.units_at_trial
    repeat_units = reach * (r.model_frequency - 1) * r.share_of_choice * r.dynamics_ratio * r.repeat_units
    total = (trial_units + repeat_units) * r.units_to_volume_boost
    market_size = r.category_penetration * r.population_mm * r.repeat_units * r.model_frequency
    return EngineResult("Trial and Repeat (bottom-up)", trial_units, repeat_units, total,
                        solved_market_size_mm=market_size)


def top_down(r: Resolved) -> EngineResult:
    """Top-down engine: market size given, penetration solved."""
    ms = r.market_size_mm_volume
    buyers = (ms / r.model_frequency) / r.repeat_units
    repeat_base = (ms / r.repeat_units - buyers) * r.trial
    max_units = r.share_of_choice * repeat_base
    combined = (r.dynamics_ratio * max_units * r.repeat_units
                + buyers * r.trial * r.triers_first_year * r.units_at_trial)
    total = r.distribution * r.awareness * combined * r.units_to_volume_boost
    # penetration solved from the penetration-free trial and repeat terms
    base = r.population_mm * r.trial * r.awareness * r.distribution
    i17 = base * r.triers_first_year * r.units_at_trial
    i18 = base * (r.model_frequency - 1) * r.share_of_choice * r.dynamics_ratio * r.repeat_units
    raw = total / (i17 + i18)
    capped = raw > 1
    pen = min(raw, 1.0)
    # split the total in the same trial/repeat proportion for reporting
    share_trial = i17 / (i17 + i18)
    return EngineResult("Market Share Model (top-down)", total * share_trial, total * (1 - share_trial),
                        total, solved_penetration=pen, penetration_capped=capped)


# --------------------------------------------------------------------------
# Results
# --------------------------------------------------------------------------
@dataclass
class Dashboard:
    resolved: Resolved
    bottom_up: EngineResult
    top_down: EngineResult
    gap: float
    implied_frequency: float         # on the survey's claimed scale
    implied_penetration: float
    implied_market_size: float

    @property
    def units_mm(self) -> tuple[float, float]:
        return self.bottom_up.total_units_mm, self.top_down.total_units_mm

    @property
    def dollars_mm(self) -> tuple[float, float]:
        """Units times price."""
        p = self.resolved.price
        return self.bottom_up.total_units_mm * p, self.top_down.total_units_mm * p

    @property
    def volume_share(self) -> tuple[float, float]:
        """Units divided by unit market size. The clean share definition."""
        ms = self.resolved.market_size_mm_volume
        return self.bottom_up.total_units_mm / ms, self.top_down.total_units_mm / ms

    @property
    def mixed_unit_share(self) -> tuple[float, float]:
        """Dollars divided by unit volume. Mixed units unless price is 1; kept only to show the trap."""
        ms = self.resolved.market_size_mm_volume
        a, b = self.dollars_mm
        return a / ms, b / ms

    @property
    def within_tolerance(self) -> bool:
        return self.gap < 0.10


def run(hard: HardInputs | None = None, opt: Options | None = None,
        ov: Overrides | None = None) -> Dashboard:
    hard = hard or HardInputs()
    opt = opt or Options()
    ov = ov or Overrides()
    r = resolve(hard, opt, ov)
    a = bottom_up(r)
    b = top_down(r)
    gap = abs(a.total_units_mm - b.total_units_mm) / ((a.total_units_mm + b.total_units_mm) / 2)
    c18 = 1.0 if ov.volume_equiv_category is None else ov.volume_equiv_category
    denom = hard.population_mm * hard.category_penetration * hard.repeat_units_per_purchase
    implied_freq = max(0.0, ((hard.market_size_mm_volume / c18) / denom - 1) * 3 + 1)
    implied_ms = r.adjusted_frequency * hard.repeat_units_per_purchase * hard.population_mm \
        * hard.category_penetration * c18
    return Dashboard(r, a, b, gap, implied_freq, b.solved_penetration, implied_ms)


def iterate(hard: HardInputs | None = None, opt: Options | None = None,
            ov: Overrides | None = None, max_passes: int = 10, tol: float = 1e-6) -> list[tuple[HardInputs, Dashboard]]:
    """The hand-run fixed point: copy implied frequency and penetration into the inputs until nothing moves.

    Returns the (inputs, dashboard) pair for each pass, pass 0 being as typed.
    """
    hard = hard or HardInputs()
    opt = opt or Options()
    ov = ov or Overrides()
    history = []
    for _ in range(max_passes + 1):
        dash = run(hard, opt, ov)
        history.append((hard, dash))
        new = replace(hard, category_purchases_per_year=dash.implied_frequency,
                      category_penetration=dash.implied_penetration)
        moved = (abs(new.category_purchases_per_year - hard.category_purchases_per_year) > tol
                 or abs(new.category_penetration - hard.category_penetration) > tol)
        if not moved:
            break
        hard = new
    return history


# --------------------------------------------------------------------------
# Reporting
# --------------------------------------------------------------------------
def chain_table(dash: Dashboard) -> list[tuple[str, float, str]]:
    """The bottom-up build as a reader would follow it, factor by factor."""
    r = dash.resolved
    rows = [
        ("Households (MM)", r.population_mm, "client"),
        ("x category penetration", r.category_penetration, "client"),
        ("x probability of trial", r.trial, "detector" ),
        ("x awareness", r.awareness, "awareness model"),
        ("x distribution", r.distribution, "client"),
        ("x triers who try in year one", r.triers_first_year, "build speed"),
        ("x units at trial", r.units_at_trial, "derived from repeat units"),
        ("= trial units (MM)", dash.bottom_up.trial_units_mm, ""),
        ("repeat occasions per year minus one", r.model_frequency - 1, "observed frequency"),
        ("x share of choice", r.share_of_choice, "override"),
        ("x dynamics ratio", r.dynamics_ratio, "build speed"),
        ("x repeat units per purchase", r.repeat_units, "survey"),
        ("= repeat units (MM)", dash.bottom_up.repeat_units_mm, ""),
        ("= total units (MM)", dash.bottom_up.total_units_mm, ""),
        ("x price", r.price, "options"),
        ("= dollars (MM)", dash.dollars_mm[0], ""),
    ]
    return rows


def report(dash: Dashboard) -> str:
    r = dash.resolved
    a, b = dash.units_mm
    da, db = dash.dollars_mm
    va, vb = dash.volume_share
    lines = []
    lines.append("Two engines, one set of judgments (illustrative coefficients)")
    lines.append("")
    lines.append(f"Trial detector index {r.trial_index:.1f} -> trial {r.trial:.1%}")
    for k, v in sorted(r.trial_contributions.items(), key=lambda kv: kv[1]):
        lines.append(f"   {k:24s} {v:+7.2f} points")
    lines.append(f"Awareness from media {r.awareness_media:.1%}, with shelf effect {r.awareness:.1%}")
    lines.append(f"Claimed frequency {r.claimed_frequency:.2f}/yr -> adjusted {r.adjusted_frequency:.2f}/yr; "
                 f"model uses {r.model_frequency:.4f}/yr")
    lines.append(f"Share of choice bracket {r.soc_low:.1f}% to {r.soc_high:.1f}%; used {r.share_of_choice:.1%}")
    lines.append(f"Build speed peak month {r.peak}: triers in year one {r.triers_first_year:.1%}, "
                 f"repeats per repeater {r.repeats_per_repeater:.3f}, dynamics ratio {r.dynamics_ratio:.4f}")
    lines.append("")
    lines.append(f"{'':34s}{'units MM':>10s}{'$ MM':>10s}{'vol share':>11s}")
    lines.append(f"{dash.bottom_up.name:34s}{a:10.4f}{da:10.3f}{va:11.2%}")
    lines.append(f"{dash.top_down.name:34s}{b:10.4f}{db:10.3f}{vb:11.2%}")
    lines.append(f"Gap {dash.gap:.2%} (practitioner convention: under 10%)")
    lines.append("")
    lines.append("Implication column (what each input should be, given the others):")
    lines.append(f"   category purchases per year: typed {r.claimed_frequency:.2f}, implied {dash.implied_frequency:.2f}")
    lines.append(f"   category penetration:        typed {r.category_penetration:.2%}, implied {dash.implied_penetration:.2%}"
                 + ("  (capped at 100%)" if dash.top_down.penetration_capped else ""))
    lines.append(f"   market size (MM volume):     typed {r.market_size_mm_volume:.0f}, implied {dash.implied_market_size:.0f}")
    return "\n".join(lines)


def convergence_table(history: list[tuple[HardInputs, Dashboard]]) -> str:
    lines = [f"{'pass':>4s}{'freq typed':>11s}{'implied':>9s}{'pen typed':>10s}{'implied':>9s}"
             f"{'mkt implied':>12s}{'units MM':>10s}{'$ MM':>8s}{'gap':>8s}"]
    for i, (h, d) in enumerate(history):
        lines.append(f"{i:4d}{h.category_purchases_per_year:11.2f}{d.implied_frequency:9.2f}"
                     f"{h.category_penetration:10.2%}{d.implied_penetration:9.2%}"
                     f"{d.implied_market_size:12.0f}{d.units_mm[0]:10.3f}{d.dollars_mm[0]:8.2f}{d.gap:8.2%}")
    return "\n".join(lines)


def main() -> None:
    dash = run()
    print(report(dash))
    print()
    print("Bottom-up chain:")
    for label, value, src in chain_table(dash):
        print(f"   {label:40s}{value:10.4f}   {src}")
    print()
    print("Reconciliation loop (copy implied into typed, recalculate):")
    print(convergence_table(iterate()))


if __name__ == "__main__":
    main()
