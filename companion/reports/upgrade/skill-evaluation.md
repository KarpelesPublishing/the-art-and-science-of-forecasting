# Executed skill and workflow evaluation

These are agent/code evaluations, not human-reader usability participants.

## Before integration corrections

Read-only review of the new adapters identified four concrete bugs: staggered-calendar
neural leakage, a baseline truncated to the context window, invalid Bass future
times, and a passed run status masking needs_evidence. Those were corrected and
regression-tested. A second contract review identified silently ignored configuration
keys and unsupported mature-sales-to-trial transfer. Unknown keys now fail; launch
conversion and repeat inputs are explicit; pending journal outcomes remain unscored.

## Final isolated spec/usefulness review

An independent agent read the current skills and exercised these inputs in memory:

- Chapter 4: 18 monthly rows returned six provisional forecasts with no invented
  validation scores. Missing periods were rejected for explicit resolution.
- Chapter 10: an eligible probability .3 scored .49 for outcome 1; a post-resolution
  .99 revision and an unresolved event did not enter that score. Pending-only input
  returned needs_evidence.
- Chapter 27: missing conversion justification, excessive trial totals and missing
  repeat assumptions were rejected. Explicit transfer produced 5,100 trials conserved
  across all timing scenarios, with separate purchase-unit totals.
- Unfamiliar chapter 25: a censored input produced P50=1.5 and unidentified upper
  quantiles as null, without silently deleting unfinished cases.

The reviewer inspected all 27 skill/workshop/lesson triads: each has chapter-specific
instructions, arithmetic, three worked exercises, an applied call and working CLI
syntax. Local links resolved. Minor heading/count issues were corrected. The separate
per-chapter evaluation.md files contain reusable scenarios and expected answers;
they are not falsely described as 81 separately executed agent sessions.

All 27 adapters are exercised by fresh notebook execution. Lightweight adapters also
have parameterized fixture tests; invalid configuration is tested across every
chapter. Selected behavioral regressions test temporal selection, missing periods,
hierarchy completeness, censoring, pending outcomes, launch assumptions, neural
calendar leakage, and output isolation.
