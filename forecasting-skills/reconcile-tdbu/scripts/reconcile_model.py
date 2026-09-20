"""
Top-down / bottom-up new-product volume reconciliation model.

This is the author's top-down bottom-up triangulation model for forecasting a new product's first year
without a test market. Two engines forecast the same volume from the same
inputs:

  bottom_up   penetration given -> market size solved  (trial and repeat)
  top_down    market size given -> penetration solved  (market share)

They agree only when the supplied penetration and market size tell a consistent
story about the category. `reconcile()` drives them into agreement by fixed-point
iteration on category purchase frequency and penetration.

ABOUT THE CONSTANTS. Every coefficient and curve constant in this file is an
illustrative starting value. None comes from a published study, a vendor model
or a client dataset; they are generic numbers, set by judgment, that put an
ordinary packaged-goods launch in the right ballpark. They are meant to be
tuned: fit them to your own launch history if you have one, otherwise adjust
them until the model reproduces launches you know, and record what you changed.
The architecture is the durable part.

Usage as a library:

    from reconcile_model import Inputs, run, reconcile
    inp = Inputs(repeat_units=1.43, category_purchases_year=20.0,
                 distribution=0.63, penetration=0.53,
                 population_mm=118.0, market_size_mm=415.0)
    res = run(inp)
    sol = reconcile(inp)

Usage from the command line:

    python reconcile_model.py --inputs inputs.json            # single pass
    python reconcile_model.py --inputs inputs.json --reconcile
    python reconcile_model.py --selftest                      # check the reference case
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from dataclasses import dataclass, field, asdict, replace
from typing import Any, Dict, List, Optional

# --------------------------------------------------------------------------
# Model constants: illustrative starting values, meant to be tuned
# --------------------------------------------------------------------------

# Build speed: month in which trial activity peaks is the index + 1 (2 to 6).
BUILD_SPEEDS: Dict[str, int] = {
    "very fast": 1,
    "somewhat fast": 2,
    "standard": 3,
    "somewhat slow": 4,
    "very slow": 5,
}

# Share of eventual triers who try within the first year, as a polynomial in the peak month.
TRIERS_POLY = (
    0.9625,        # peak^0
    0.05042,       # peak^1
    -0.01924,      # peak^2
    0.001124,      # peak^3
    -0.00000384,   # peak^4
    -0.00000143,   # peak^5
    0.000000032,   # peak^6
)

# Repeats per repeater in year one, from purchase frequency and build speed.
REPEAT_CURVE_SCALE = 2.65
REPEAT_CURVE_EXPONENT = -0.31

# First-repeat rate as a function of the category purchase cycle.
REPEAT_RATE_SLOPE = -11.7
REPEAT_RATE_INTERCEPT = 50.0
REPEAT_RATE_DIVISOR = 7.0

# Derived share-of-choice upper bound.
SOC_HIGH_LOG_TERM = 0.02

# Trial detector: seven judged attributes, each scored on an index where 100 is
# roughly the category norm, weighted and passed through a curve.
TRIAL_INTERCEPT = -15.5
TRIAL_COEFFS: Dict[str, float] = {
    "differentiation": 0.27,
    "relevance": 0.23,
    "share_of_leader": 0.30,
    "visibility": 0.28,
    "brands_80pct_share": -0.22,
    "brands_evoked_set": -3.0,
    "expensiveness": -0.15,
}
TRIAL_OFFSET = 10.0
TRIAL_BASE = 1.75
TRIAL_POWER = 1.5
TRIAL_DIVISOR = 10.0

# Awareness from a media plan: a logistic in rating points, purchase frequency,
# brand-name recall, ad-driven trial, weeks on air and distribution.
AW_SCALE = 26.5
AW_BRANDING_LX = 1.32        # applied when branding == "LX" (line extension)
AW_FREQ_COEF = 0.012
AW_BNR_EXP = 1.95
AW_TRIAL_EXP = 0.63
AW_WD_EXP = 0.9
AW_HORIZON_EXP = -0.28
AW_GRP_COEF = 0.00044
AW_OUTER_EXP = -0.77

# Shelf-presence uplift on media awareness.
SHELF_A = 0.66
SHELF_B = 0.33
SHELF_C = 0.9
SHELF_CAP = 0.3

SURVEY_DEFLATOR = 3.0   # the (n - 1) / 3 + 1 correction on claimed purchase frequency
DAYS_PER_YEAR = 365.0


# --------------------------------------------------------------------------
# Inputs
# --------------------------------------------------------------------------


@dataclass
class TrialInputs:
    """The seven judged attributes behind the trial detector (100 is roughly the category norm)."""

    differentiation: float = 122.0
    relevance: float = 98.0
    share_of_leader: float = 25.0
    visibility: float = 55.0
    brands_80pct_share: float = 22.0
    brands_evoked_set: float = 5.0
    expensiveness: float = 114.0


@dataclass
class AwarenessInputs:
    """The media-plan inputs behind the awareness model."""

    branding: str = "LX"            # "LX" line extension or "NB" new brand
    brand_name_recall: float = 0.55
    horizon_weeks: float = 52.0      # weeks on air in the forecast year
    spend_mm: float = 4.6            # media spend in $MM
    cost_per_grp: float = 10000.0


@dataclass
class Overrides:
    """Optional replacements for derived values. None keeps the model's own default."""

    volume_equiv_category: Optional[float] = None
    volume_equiv_product: Optional[float] = None
    price_per_volume_category: Optional[float] = None
    price_per_volume_product: Optional[float] = None
    range_width_category: Optional[float] = None
    range_width_product: Optional[float] = None
    repeats_per_repeater: Optional[float] = None
    first_repeat_rate: Optional[float] = None
    units_at_trial: Optional[float] = None
    share_of_choice: Optional[float] = 0.25
    triers_try_first_year: Optional[float] = None
@dataclass
class Inputs:
    """Everything the model needs: six typed inputs plus settings."""

    # the six typed inputs
    repeat_units: float = 1.43
    category_purchases_year: float = 20.0       # C3, survey claimed
    distribution: float = 0.63
    penetration: float = 0.53
    population_mm: float = 118.0
    market_size_mm: Optional[float] = 415.0     # C9, None means "let the bottom-up decide"

    # settings
    build_speed: str = "standard"
    price: float = 3.99
    use_external_frequency: bool = True
    external_frequency: float = 14.0 / 3.0
    calculate_awareness: bool = True
    calculate_trial: bool = True
    soc_simulator: bool = True
    # Manual figures used when the corresponding toggle is off
    awareness_manual: Optional[float] = None
    trial_manual: Optional[float] = None
    trial_inputs: TrialInputs = field(default_factory=TrialInputs)
    awareness_inputs: AwarenessInputs = field(default_factory=AwarenessInputs)
    overrides: Overrides = field(default_factory=Overrides)

    # penetration-solve denominator, normally 1
    penetration_denominator: float = 1.0


# --------------------------------------------------------------------------
# Trial detector and awareness model
# --------------------------------------------------------------------------


def trial_index(t: TrialInputs) -> float:
    """Weighted attribute index plus intercept, before the trial curve."""
    total = sum(getattr(t, k) * v for k, v in TRIAL_COEFFS.items())
    return total + TRIAL_INTERCEPT + TRIAL_OFFSET


def trial_probability(t: TrialInputs) -> float:
    """Trial probability among aware buyers who can find the product, as a fraction."""
    idx = trial_index(t)
    if idx < 0.001:
        return 0.01
    pct = round(TRIAL_BASE + (idx ** TRIAL_POWER) / TRIAL_DIVISOR, 1)
    return pct / 100.0


def grps(a: AwarenessInputs) -> float:
    """Gross rating points bought by the plan."""
    return a.spend_mm * 1_000_000.0 / a.cost_per_grp


def awareness_from_media(
    a: AwarenessInputs, adjusted_frequency: float, trial_rate: float, distribution: float
) -> float:
    """Awareness generated by media alone, before the shelf effect."""
    lam = AW_BRANDING_LX if a.branding.upper() == "LX" else 1.0
    wd = distribution * 100.0
    media = grps(a) * AW_GRP_COEF + adjusted_frequency * AW_FREQ_COEF
    horizon = a.horizon_weeks ** AW_HORIZON_EXP
    recall = math.exp(a.brand_name_recall) ** AW_BNR_EXP
    trial_term = math.exp(trial_rate / a.brand_name_recall) ** AW_TRIAL_EXP
    dist_term = wd ** AW_WD_EXP
    inner = media * horizon * recall * trial_term * dist_term
    return 1.0 / (1.0 + lam * AW_SCALE * inner ** AW_OUTER_EXP)


def awareness_with_shelf(base: float) -> float:
    """Add what the package earns at shelf on top of media awareness."""
    if base <= 0:
        return base
    lift = (1.0 - base) / base * SHELF_A * SHELF_B * SHELF_C * max(1.0 - base / SHELF_CAP, 0.0)
    return base * (1.0 + lift)


# --------------------------------------------------------------------------
# Derived quantities
# --------------------------------------------------------------------------


def adjusted_frequency(claimed: float) -> float:
    """Claimed purchase frequency deflated for survey overstatement."""
    return (claimed - 1.0) / SURVEY_DEFLATOR + 1.0


def purchase_cycle_days(claimed: float) -> float:
    """Category purchase cycle in days."""
    return DAYS_PER_YEAR / adjusted_frequency(claimed)


def repeats_per_repeater(model_frequency: float, peak: float) -> float:
    """Repeat purchases per repeater in year one, floored at zero."""
    value = (
        DAYS_PER_YEAR
        * (1.0 / (DAYS_PER_YEAR / model_frequency))
        * math.log(REPEAT_CURVE_SCALE * peak ** REPEAT_CURVE_EXPONENT)
    ) - 1.0
    return max(value, 0.0)


def first_repeat_rate(claimed_frequency: float) -> float:
    """First-repeat rate from the category purchase cycle. Uses the claimed frequency, not the adjusted one."""
    inner = ((DAYS_PER_YEAR / claimed_frequency - 1.0) / SURVEY_DEFLATOR + 1.0) / REPEAT_RATE_DIVISOR
    return (REPEAT_RATE_SLOPE * math.log(inner) + REPEAT_RATE_INTERCEPT) / 100.0


def units_at_trial(repeat_units: float) -> float:
    """Units bought on the trial occasion."""
    return 1.0 + (repeat_units - 1.0) / 2.0


def soc_bounds(rate: float) -> tuple:
    """Derived share-of-choice low and high bounds, in percent."""
    low = 100.0 / ((3.0 / rate) - 2.0)
    high = 100.0 * (rate - SOC_HIGH_LOG_TERM * math.log(101.0))
    return low, high


def triers_try_first_year(peak: float) -> float:
    """Share of eventual triers who try within the first year."""
    return sum(c * peak ** i for i, c in enumerate(TRIERS_POLY))


def units_to_volume_boost(
    range_product: float,
    range_category: float,
    vol_category: float,
    vol_product: float,
    price_category: float,
    price_product: float,
) -> float:
    """Units-to-volume adjustment for pack size, price and range differences."""
    return (
        (range_product / range_category) ** 0.2
        * (vol_category / vol_product) ** 0.5
        / ((vol_category / price_category) / (vol_product / price_product))
    )


def _pick(override: Optional[float], default: float) -> float:
    """An override replaces the derived default when supplied."""
    return default if override is None else override


# --------------------------------------------------------------------------
# The two engines
# --------------------------------------------------------------------------


@dataclass
class EngineResult:
    """One engine's output."""

    market_size: float
    units_per_occasion: float
    repeat_base: float
    repeat_base_first_year: float
    maximum_units: float
    repeat_units_total: float
    after_awareness: float
    after_distribution: float
    share_build: float            # D12, the market-share build-up
    trial_volume: float           # I17 / I18
    repeat_volume: float          # I18 / I19
    tr_build: float               # D16, the trial-and-repeat build-up
    average: float
    penetration: float
    implied_market_size: float
def _volume_chain(
    market_size: float,
    model_frequency: float,
    repeat_units: float,
    trial_prob: float,
    triers_first_year: float,
    share_of_choice: float,
    dynamics_ratio: float,
    awareness: float,
    distribution: float,
    trial_units: float,
    boost: float,
) -> Dict[str, float]:
    """The shared volume chain: buyers, triers, repeaters, units. Identical in both engines."""
    h3 = (market_size / model_frequency) / repeat_units
    h6 = (market_size / repeat_units - h3) * trial_prob
    h7 = triers_first_year * h6
    h8 = share_of_choice * h6
    h9 = dynamics_ratio * h8 * repeat_units + h3 * trial_prob * triers_first_year * trial_units
    h10 = awareness * h9
    h11 = distribution * h10
    return {
        "units_per_occasion": h3,
        "repeat_base": h6,
        "repeat_base_first_year": h7,
        "maximum_units": h8,
        "repeat_units_total": h9,
        "after_awareness": h10,
        "after_distribution": h11,
        "share_build": h11 * boost,
    }


def bottom_up(d: Dict[str, Any]) -> EngineResult:
    """Bottom-up engine. Penetration is given; market size is solved."""
    pen = d["penetration"]
    pop = d["population_mm"]
    ru = d["repeat_units"]
    freq = d["model_frequency"]

    # market size implied by the penetration you supplied
    implied = d["vol_equiv_category"] * (pen * pop * ru + pen * pop * (freq - 1.0) * ru)
    chain = _volume_chain(
        market_size=implied,
        model_frequency=freq,
        repeat_units=ru,
        trial_prob=d["trial_prob"],
        triers_first_year=d["triers_first_year"],
        share_of_choice=d["share_of_choice"],
        dynamics_ratio=d["dynamics_ratio"],
        awareness=d["awareness"],
        distribution=d["distribution"],
        trial_units=d["units_at_trial"],
        boost=d["boost"],
    )

    # penetration appears inline in both terms here
    common = pop * pen * d["trial_prob"] * d["awareness"] * d["distribution"]
    trial_vol = common * d["triers_first_year"] * d["units_at_trial"]
    repeat_vol = (
        common * (freq - 1.0) * d["share_of_choice"] * d["dynamics_ratio"] * ru
    )
    tr_build = (trial_vol + repeat_vol) * d["boost"]

    return EngineResult(
        market_size=implied,
        share_build=chain["share_build"],
        trial_volume=trial_vol,
        repeat_volume=repeat_vol,
        tr_build=tr_build,
        average=(chain["share_build"] + tr_build) / 2.0,
        penetration=pen,
        implied_market_size=implied,
        **{k: v for k, v in chain.items() if k != "share_build"},
    )


def top_down(d: Dict[str, Any], market_size: float) -> EngineResult:
    """Top-down engine. Market size is given; penetration is solved."""
    pop = d["population_mm"]
    ru = d["repeat_units"]
    freq = d["model_frequency"]

    chain = _volume_chain(
        market_size=market_size,
        model_frequency=freq,
        repeat_units=ru,
        trial_prob=d["trial_prob"],
        triers_first_year=d["triers_first_year"],
        share_of_choice=d["share_of_choice"],
        dynamics_ratio=d["dynamics_ratio"],
        awareness=d["awareness"],
        distribution=d["distribution"],
        trial_units=d["units_at_trial"],
        boost=d["boost"],
    )

    # penetration is deliberately factored out of both terms, which is what
    # makes it solvable in one step instead of circular.
    common = pop * d["trial_prob"] * d["awareness"] * d["distribution"]
    trial_vol = common * d["triers_first_year"] * d["units_at_trial"]
    repeat_vol = (
        common * (freq - 1.0) * d["share_of_choice"] * d["dynamics_ratio"] * ru
    )
    i16 = trial_vol + repeat_vol

    denom = i16 * d["penetration_denominator"]
    solved = 1.0 if denom == 0 else min(1.0, chain["share_build"] / denom)
    tr_build = i16 * solved          # no volume boost applied on this route
    implied = solved * pop * ru + solved * pop * (freq - 1.0) * ru

    return EngineResult(
        market_size=market_size,
        share_build=chain["share_build"],
        trial_volume=trial_vol,
        repeat_volume=repeat_vol,
        tr_build=tr_build,
        average=(chain["share_build"] + tr_build) / 2.0,
        penetration=solved,
        implied_market_size=implied,
        **{k: v for k, v in chain.items() if k != "share_build"},
    )


# --------------------------------------------------------------------------
# Full model run
# --------------------------------------------------------------------------


@dataclass
class Result:
    inputs: Inputs
    derived: Dict[str, float]
    bottom_up: EngineResult
    top_down: EngineResult
    forecast_units_mm: float        # Dashboard E12 / E13
    forecast_value_mm: float        # Dashboard C12 / C13
    volume_share: float             # Dashboard G12 / G13
    gap: float                      # Dashboard C15
    implied_purchases_year: float   # Dashboard E3
    implied_penetration: float      # Dashboard E7
    implied_market_size: float      # Dashboard E9
    warnings: List[str]

    def converged(self, tolerance: float = 0.10) -> bool:
        return self.gap < tolerance


def validate(inp: Inputs) -> None:
    """Reject inputs that cannot be what they claim to be. Fractions are fractions."""
    problems = []
    for name in ("distribution", "penetration"):
        v = getattr(inp, name)
        if not (0.0 < v <= 1.0):
            problems.append(f"{name} must be a fraction between 0 and 1, got {v} (did you enter a percentage?)")
    if not (0.0001 <= inp.repeat_units <= 5.0):
        problems.append(f"repeat_units must be between 0.0001 and 5, got {inp.repeat_units}")
    if not (0.01 <= inp.category_purchases_year <= 1000.0):
        problems.append(f"category_purchases_year must be between 0.01 and 1000, got {inp.category_purchases_year}")
    if not (0.01 <= inp.population_mm <= 2000.0):
        problems.append(f"population_mm must be between 0.01 and 2000 (millions), got {inp.population_mm}")
    if inp.market_size_mm is not None and not (0.01 <= inp.market_size_mm <= 2_000_000.0):
        problems.append(f"market_size_mm must be between 0.01 and 2,000,000 (millions), got {inp.market_size_mm}")
    if inp.price <= 0:
        problems.append(f"price must be positive, got {inp.price}")
    for name in ("awareness_manual", "trial_manual"):
        v = getattr(inp, name)
        if v is not None and not (0.0 < v <= 1.0):
            problems.append(f"{name} must be a fraction between 0 and 1, got {v}")
    o = inp.overrides
    for name in ("first_repeat_rate", "share_of_choice", "triers_try_first_year"):
        v = getattr(o, name)
        if v is not None and not (0.0 < v <= 1.0):
            problems.append(f"overrides.{name} must be a fraction between 0 and 1, got {v}")
    if o.units_at_trial is not None and not (1.0 <= o.units_at_trial <= 5.0):
        problems.append(f"overrides.units_at_trial must be between 1 and 5, got {o.units_at_trial}")
    if problems:
        raise ValueError("Invalid inputs:\n  - " + "\n  - ".join(problems))


def _prepare(inp: Inputs) -> Dict[str, Any]:
    """Compute every derived quantity the engines need."""
    validate(inp)
    o = inp.overrides
    warnings: List[str] = []

    key = inp.build_speed.strip().lower()
    if key not in BUILD_SPEEDS:
        raise ValueError(
            f"build_speed must be one of {sorted(BUILD_SPEEDS)}, got {inp.build_speed!r}"
        )
    peak = BUILD_SPEEDS[key] + 1.0
    adj_freq = adjusted_frequency(inp.category_purchases_year)
    model_freq = inp.external_frequency if inp.use_external_frequency else adj_freq
    # trial probability: modelled, or the manual figure
    if inp.calculate_trial:
        trial_prob = trial_probability(inp.trial_inputs)
    else:
        if inp.trial_manual is None:
            raise ValueError("calculate_trial is False, so trial_manual must be supplied")
        trial_prob = inp.trial_manual

    # awareness: modelled, or the manual figure
    if inp.calculate_awareness:
        base_aw = awareness_from_media(
            inp.awareness_inputs, adj_freq, trial_prob, inp.distribution
        )
        awareness = awareness_with_shelf(base_aw)
    else:
        if inp.awareness_manual is None:
            raise ValueError(
                "calculate_awareness is False, so awareness_manual must be supplied"
            )
        base_aw = inp.awareness_manual
        awareness = inp.awareness_manual

    vol_cat = _pick(o.volume_equiv_category, 1.0)
    vol_prod = _pick(o.volume_equiv_product, 1.0)
    price_cat = _pick(o.price_per_volume_category, 1.0)
    price_prod = _pick(o.price_per_volume_product, 1.0)
    range_cat = _pick(o.range_width_category, 1.0)
    range_prod = _pick(o.range_width_product, 1.0)
    t24 = repeats_per_repeater(model_freq, peak)
    repeats = _pick(o.repeats_per_repeater, t24)
    dynamics_ratio = repeats / model_freq
    t25 = first_repeat_rate(inp.category_purchases_year)
    repeat_rate = _pick(o.first_repeat_rate, t25)
    trial_units = _pick(o.units_at_trial, units_at_trial(inp.repeat_units))
    low, high = soc_bounds(t25)
    t27 = (1.0 if inp.soc_simulator else 0.0) * (low + high) / 2.0 / 100.0
    share_of_choice = _pick(o.share_of_choice, t27)
    triers = _pick(o.triers_try_first_year, triers_try_first_year(peak))
    boost = units_to_volume_boost(
        range_prod, range_cat, vol_cat, vol_prod, price_cat, price_prod
    )
    if o.repeats_per_repeater is not None and o.triers_try_first_year is not None:
        warnings.append(
            "Repeats per repeater and triers-try-first-year are both overridden, "
            "so the build-speed setting no longer affects anything."
        )

    derived = {
        "peak": peak,
        "adjusted_frequency": adj_freq,
        "purchase_cycle_days": DAYS_PER_YEAR / adj_freq,
        "model_frequency": model_freq,
        "trial_probability": trial_prob,
        "awareness_media_only": base_aw,
        "awareness": awareness,
        "grps": grps(inp.awareness_inputs),
        "repeats_per_repeater": repeats,
        "dynamics_ratio": dynamics_ratio,
        "first_repeat_rate": repeat_rate,
        "units_at_trial": trial_units,
        "soc_low": low,
        "soc_high": high,
        "share_of_choice": share_of_choice,
        "triers_try_first_year": triers,
        "units_to_volume_boost": boost,
        "category_buyers_mm": inp.penetration * inp.population_mm,
    }

    bundle: Dict[str, Any] = {
        "penetration": inp.penetration,
        "population_mm": inp.population_mm,
        "repeat_units": inp.repeat_units,
        "model_frequency": model_freq,
        "trial_prob": trial_prob,
        "triers_first_year": triers,
        "share_of_choice": share_of_choice,
        "dynamics_ratio": dynamics_ratio,
        "awareness": awareness,
        "distribution": inp.distribution,
        "units_at_trial": trial_units,
        "boost": boost,
        "vol_equiv_category": vol_cat,
        "vol_equiv_product": vol_prod,
        "penetration_denominator": inp.penetration_denominator,
    }
    return {"derived": derived, "bundle": bundle, "warnings": warnings}


def run(inp: Inputs) -> Result:
    """One pass of the model."""
    prep = _prepare(inp)
    d = prep["bundle"]
    derived = prep["derived"]
    warnings = list(prep["warnings"])

    bu = bottom_up(d)

    # the market size the reader gave, or the bottom-up figure when none was given
    if inp.market_size_mm is None:
        ms = bu.market_size
    else:
        ms = inp.market_size_mm * d["vol_equiv_category"]
    td = top_down(d, ms)

    if td.penetration >= 1.0:
        warnings.append(
            "Solved penetration hit its 100% cap. The balancing variable is "
            "saturated, so the two engines cannot be reconciled at these inputs."
        )

    e12, e13 = bu.tr_build, td.share_build
    avg = (e12 + e13) / 2.0
    gap = abs(e12 - e13) / avg if avg else 0.0

    # what each typed input would have to be for the others to hold
    ms_for_implied = inp.market_size_mm if inp.market_size_mm is not None else bu.market_size
    denom = inp.population_mm * inp.penetration * inp.repeat_units
    raw = (ms_for_implied / d["vol_equiv_category"]) / denom if denom else 0.0
    implied_purchases = max(0.0, (raw - 1.0) * SURVEY_DEFLATOR + 1.0)
    implied_market = (
        derived["adjusted_frequency"]
        * inp.repeat_units
        * inp.population_mm
        * inp.penetration
        * d["vol_equiv_category"]
    )

    value = e12 * d["vol_equiv_product"] * inp.price
    # Share is units over the category's unit volume. When no market size was
    # given, the bottom-up engine's solved market size is the only denominator
    # available, and the share is then a consistency check rather than a forecast.
    share_denominator = ms_for_implied if inp.market_size_mm is not None else bu.market_size
    share = avg / share_denominator if share_denominator else 0.0
    if inp.market_size_mm is None:
        warnings.append(
            "No market size was entered, so share is measured against the market "
            "size the bottom-up engine solved for. There is nothing independent to "
            "reconcile against."
        )

    return Result(
        inputs=inp,
        derived=derived,
        bottom_up=bu,
        top_down=td,
        forecast_units_mm=avg,
        forecast_value_mm=value,
        volume_share=share,
        gap=gap,
        implied_purchases_year=implied_purchases,
        implied_penetration=td.penetration,
        implied_market_size=implied_market,
        warnings=warnings,
    )


# --------------------------------------------------------------------------
# Reconciliation
# --------------------------------------------------------------------------


@dataclass
class ReconcileStep:
    iteration: int
    category_purchases_year: float
    implied_purchases_year: float
    penetration: float
    implied_penetration: float
    market_size: Optional[float]
    implied_market_size: float
    gap: float
    forecast_units_mm: float


@dataclass
class Solution:
    converged: bool
    iterations: int
    history: List[ReconcileStep]
    start: Result
    final: Result
    final_inputs: Inputs
    stalled: bool = False
    message: str = ""


def reconcile(
    inp: Inputs,
    max_iterations: int = 25,
    tolerance: float = 1e-9,
    lock_frequency: bool = False,
    lock_penetration: bool = False,
) -> Solution:
    """
    Drive the two engines into agreement.

    Each pass copies the model's implied purchase frequency into the claimed
    frequency and its implied penetration into the supplied penetration. On the
    reference case this settles in two passes.

    Set lock_frequency or lock_penetration to hold an input the user is
    confident about and let the other one absorb the whole adjustment.
    """
    current = replace(inp)
    start = run(current)
    history: List[ReconcileStep] = []
    converged = False
    stalled = False
    used = 0

    for i in range(max_iterations):
        res = run(current)
        history.append(
            ReconcileStep(
                iteration=i,
                category_purchases_year=current.category_purchases_year,
                implied_purchases_year=res.implied_purchases_year,
                penetration=current.penetration,
                implied_penetration=res.implied_penetration,
                market_size=current.market_size_mm,
                implied_market_size=res.implied_market_size,
                gap=res.gap,
                forecast_units_mm=res.forecast_units_mm,
            )
        )

        freq_move = 0.0 if lock_frequency else abs(
            res.implied_purchases_year - current.category_purchases_year
        )
        pen_move = 0.0 if lock_penetration else abs(
            res.implied_penetration - current.penetration
        )
        used = i + 1
        settled = freq_move < tolerance and pen_move < tolerance
        if settled and res.gap < tolerance:
            converged = True
            break
        if settled:
            # Inputs have stopped moving but the engines still disagree. Iterating
            # further changes nothing; something structural is wrong.
            stalled = True
            break

        current = replace(
            current,
            category_purchases_year=(
                current.category_purchases_year
                if lock_frequency
                else res.implied_purchases_year
            ),
            penetration=(
                current.penetration if lock_penetration else res.implied_penetration
            ),
        )

    final = run(current)

    if converged:
        message = f"Converged in {used} passes."
    elif stalled:
        message = (
            f"Stalled after {used} passes at a {final.gap:.1%} gap. The inputs have "
            "stopped moving but the engines still disagree, so iterating further "
            "will not help."
        )
        if final.implied_penetration >= 1.0:
            message += (
                " Penetration is pinned at 100%, so it has nothing left to give. "
                "Market size is almost certainly too large for this population, or "
                "repeat units are too low."
            )
        elif lock_frequency or lock_penetration:
            held = "penetration" if lock_penetration else "purchase frequency"
            message += (
                f" You held {held} fixed, so the remaining gap is the price of that "
                "lock: the free input has moved as far as it can."
            )
        else:
            message += " Check that every fraction was entered as a fraction, not a percentage."
    else:
        message = (
            f"Did not settle within {used} passes. The inputs are still moving, "
            "which usually means two of them are pulling in opposite directions."
        )

    return Solution(
        converged=converged,
        iterations=used,
        history=history,
        start=start,
        final=final,
        final_inputs=current,
        stalled=stalled,
        message=message,
    )


def sensitivity(inp: Inputs, field_name: str, values: List[float]) -> List[Dict[str, float]]:
    """Re-run the model across a range of one input. Useful for a tornado table."""
    out = []
    for v in values:
        trial = replace(inp, **{field_name: v})
        res = run(trial)
        out.append(
            {
                field_name: v,
                "forecast_units_mm": res.forecast_units_mm,
                "forecast_value_mm": res.forecast_value_mm,
                "gap": res.gap,
                "implied_penetration": res.implied_penetration,
            }
        )
    return out


# --------------------------------------------------------------------------
# Reporting
# --------------------------------------------------------------------------


def format_report(res: Result, title: str = "Forecast") -> str:
    d = res.derived
    lines = [
        f"{title}",
        "=" * len(title),
        "",
        "Inputs",
        f"  Repeat units per purchase      {res.inputs.repeat_units:,.2f}",
        f"  Category purchases per year    {res.inputs.category_purchases_year:,.2f}  (claimed)",
        f"  Adjusted for overstatement     {d['adjusted_frequency']:,.2f}",
        f"  Frequency used by the engines  {d['model_frequency']:,.2f}",
        f"  Distribution                   {res.inputs.distribution:,.1%}",
        f"  Category penetration           {res.inputs.penetration:,.1%}",
        f"  Population / HHs (MM)          {res.inputs.population_mm:,.1f}",
        f"  Market size (MM)               "
        + (f"{res.inputs.market_size_mm:,.1f}" if res.inputs.market_size_mm is not None else "solved"),
        "",
        "Model-derived",
        f"  Awareness                      {d['awareness']:,.1%}  (media only {d['awareness_media_only']:,.1%})",
        f"  Probability of trial           {d['trial_probability']:,.1%}",
        f"  Triers trying in year 1        {d['triers_try_first_year']:,.1%}",
        f"  Share of choice                {d['share_of_choice']:,.1%}",
        f"  Repeats per repeater           {d['repeats_per_repeater']:,.2f}",
        f"  Dynamics ratio                 {d['dynamics_ratio']:,.3f}",
        f"  Purchase cycle (days)          {d['purchase_cycle_days']:,.1f}",
        "",
        "Engines",
        f"  Bottom-up  (penetration given) {res.bottom_up.tr_build:,.3f} MM units",
        f"  Top-down   (market size given) {res.top_down.share_build:,.3f} MM units",
        f"  Gap                            {res.gap:,.2%}   "
        + ("OK" if res.converged() else "ABOVE THE 10% TOLERANCE"),
        "",
        "Forecast",
        f"  Volume                         {res.forecast_units_mm:,.3f} MM units",
        f"  Value                          ${res.forecast_value_mm:,.2f} MM",
        f"  Share                          {res.volume_share:,.2%}",
        "",
        "What the model implies about your inputs",
        f"  Category purchases per year    {res.implied_purchases_year:,.2f}  "
        f"(you entered {res.inputs.category_purchases_year:,.2f})",
        f"  Category penetration           {res.implied_penetration:,.1%}  "
        f"(you entered {res.inputs.penetration:,.1%})",
        f"  Market size                    {res.implied_market_size:,.1f} MM  "
        + (
            f"(you entered {res.inputs.market_size_mm:,.1f})"
            if res.inputs.market_size_mm is not None
            else "(none entered)"
        ),
    ]
    if res.warnings:
        lines += ["", "Warnings"]
        lines += [f"  - {w}" for w in res.warnings]
    return "\n".join(lines)


def format_convergence(sol: Solution) -> str:
    head = (
        f"{'Pass':>4}  {'Purch/yr':>9}  {'implied':>9}  "
        f"{'Penetr':>8}  {'implied':>8}  {'Gap':>8}  {'Units MM':>9}"
    )
    rows = [head, "-" * len(head)]
    for s in sol.history:
        rows.append(
            f"{s.iteration:>4}  {s.category_purchases_year:>9,.3f}  "
            f"{s.implied_purchases_year:>9,.3f}  {s.penetration:>8,.4f}  "
            f"{s.implied_penetration:>8,.4f}  {s.gap:>8,.4%}  "
            f"{s.forecast_units_mm:>9,.4f}"
        )
    rows.append("")
    rows.append(sol.message)
    return "\n".join(rows)


# --------------------------------------------------------------------------
# Serialisation
# --------------------------------------------------------------------------


def inputs_from_dict(data: Dict[str, Any]) -> Inputs:
    data = dict(data)
    if "trial_inputs" in data:
        data["trial_inputs"] = TrialInputs(**data["trial_inputs"])
    if "awareness_inputs" in data:
        data["awareness_inputs"] = AwarenessInputs(**data["awareness_inputs"])
    if "overrides" in data:
        data["overrides"] = Overrides(**data["overrides"])
    return Inputs(**data)


def result_to_dict(res: Result) -> Dict[str, Any]:
    return {
        "inputs": asdict(res.inputs),
        "derived": res.derived,
        "bottom_up": asdict(res.bottom_up),
        "top_down": asdict(res.top_down),
        "forecast_units_mm": res.forecast_units_mm,
        "forecast_value_mm": res.forecast_value_mm,
        "volume_share": res.volume_share,
        "gap": res.gap,
        "implied_purchases_year": res.implied_purchases_year,
        "implied_penetration": res.implied_penetration,
        "implied_market_size": res.implied_market_size,
        "warnings": res.warnings,
        "within_tolerance": res.converged(),
    }


# --------------------------------------------------------------------------
# Self-test against the reference case
# --------------------------------------------------------------------------

# The default Inputs() are the reference case used in the book (Chapters 20 and 27).
# These values are what the model must produce for it; they also match the
# companion notebooks, which use the same constants.
REFERENCE_CASE = {
    "awareness": 0.24783665713414854,
    "awareness_media_only": 0.1890425956512955,
    "trial_probability": 0.233,
    "repeats_per_repeater": 1.542439144237835,
    "dynamics_ratio": 0.33052267376525035,
    "first_repeat_rate": 0.5042550143679924,
    "units_at_trial": 1.2149999999999999,
    "triers_try_first_year": 0.925959712,
    "soc_low": 25.320489766159227,
    "soc_high": 41.19526040311672,
    "bottom_up_market_size": 417.35026666666664,
    "bottom_up_units": 3.545449402050873,
    "top_down_units": 3.5254835551028263,
    "top_down_penetration": 0.5270153575238323,
    "gap": 0.00564730200923409,
    "implied_purchases_year": 11.921160387421978,
    "implied_market_size": 655.8361333333334,
    "value_mm": 14.146343114182985,
    "volume_share": 0.00851919633392012,   # average of the two engines over market size
}


def selftest(verbose: bool = True) -> bool:
    """Run the reference case and compare against the values the book quotes."""
    res = run(Inputs())
    checks = [
        ("awareness", res.derived["awareness"]),
        ("awareness_media_only", res.derived["awareness_media_only"]),
        ("trial_probability", res.derived["trial_probability"]),
        ("repeats_per_repeater", res.derived["repeats_per_repeater"]),
        ("dynamics_ratio", res.derived["dynamics_ratio"]),
        ("first_repeat_rate", res.derived["first_repeat_rate"]),
        ("units_at_trial", res.derived["units_at_trial"]),
        ("triers_try_first_year", res.derived["triers_try_first_year"]),
        ("soc_low", res.derived["soc_low"]),
        ("soc_high", res.derived["soc_high"]),
        ("bottom_up_market_size", res.bottom_up.market_size),
        ("bottom_up_units", res.bottom_up.tr_build),
        ("top_down_units", res.top_down.share_build),
        ("top_down_penetration", res.top_down.penetration),
        ("gap", res.gap),
        ("implied_purchases_year", res.implied_purchases_year),
        ("implied_market_size", res.implied_market_size),
        ("value_mm", res.forecast_value_mm),
        ("volume_share", res.volume_share),
    ]
    ok = True
    for name, got in checks:
        want = REFERENCE_CASE[name]
        close = math.isclose(got, want, rel_tol=1e-6, abs_tol=1e-9)
        ok = ok and close
        if verbose:
            mark = "ok  " if close else "FAIL"
            print(f"{mark} {name:<26} got {got!r:<26} want {want!r}")
    sol = reconcile(Inputs())
    two_pass = sol.converged and sol.iterations <= 3  # pass 0 plus two updates
    ok = ok and two_pass
    if verbose:
        print(f"{'ok  ' if two_pass else 'FAIL'} {'reconcile':<26} {sol.message}")
        print("\nReference case reproduced." if ok else "\nMISMATCH against the reference case.")
    return ok


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------


def main(argv: Optional[List[str]] = None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--inputs", help="JSON file of model inputs")
    p.add_argument("--reconcile", action="store_true", help="iterate to convergence")
    p.add_argument("--lock-frequency", action="store_true", help="hold purchases per year fixed")
    p.add_argument("--lock-penetration", action="store_true", help="hold penetration fixed")
    p.add_argument("--json", action="store_true", help="emit JSON instead of a report")
    p.add_argument("--selftest", action="store_true", help="check the reference case")
    args = p.parse_args(argv)

    if args.selftest:
        return 0 if selftest() else 1

    if args.inputs:
        with open(args.inputs) as fh:
            inp = inputs_from_dict(json.load(fh))
    else:
        inp = Inputs()

    if args.reconcile:
        sol = reconcile(
            inp, lock_frequency=args.lock_frequency, lock_penetration=args.lock_penetration
        )
        if args.json:
            print(
                json.dumps(
                    {
                        "converged": sol.converged,
                        "stalled": sol.stalled,
                        "message": sol.message,
                        "iterations": sol.iterations,
                        "history": [asdict(s) for s in sol.history],
                        "start": result_to_dict(sol.start),
                        "final": result_to_dict(sol.final),
                        "final_inputs": asdict(sol.final_inputs),
                    },
                    indent=2,
                    default=str,
                )
            )
        else:
            print(format_report(sol.start, "Before reconciliation"))
            print("\n\nReconciliation\n==============\n")
            print(format_convergence(sol))
            print("\n")
            print(format_report(sol.final, "After reconciliation"))
        return 0

    res = run(inp)
    print(json.dumps(result_to_dict(res), indent=2, default=str) if args.json else format_report(res))
    return 0


if __name__ == "__main__":
    sys.exit(main())
