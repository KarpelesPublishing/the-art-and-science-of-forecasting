# A number with no series: events and judgment forecasts

Some questions have no history to profile: will the contract renew, will the launch slip, how many
units will a new channel sell in its first quarter. The seven gates still apply; the profile gate is
replaced by a base rate and the method gate by chapter 10's decomposition.

1. **Brief.** Same command. The target is the event or quantity, the units are "probability" or the
   quantity's units, the outcome date is when the question resolves. Insist on a resolution rule the
   reader can write down: what counts as "yes".
2. **Base rate instead of profile.** Find the reference class (chapter 25 for quantities, chapter 2 for
   rates from successes and trials): how often did things like this happen before? Record the class,
   its size and its rate in `work/base-rate.md`. If no class exists, say so; the forecast is then
   judgment with no anchor, and the report must say that.
3. **Baseline.** The base rate is the baseline. State it before any updating.
4. **Method.** Chapter 10: decompose the question into parts that can be estimated, update the base
   rate with evidence by likelihood ratios, and write each step down. For a quantity, chapter 7 turns
   the component ranges into a distribution of the total. For a crowd of estimates, chapter 11. Record
   every revision in the chapter 10 journal (`run.py apply --chapter 10` scores it later).
5. **Validation.** There is no holdout. The check is the reader's own track record (chapter 9 scoring of
   past journal entries) and the Brier score against the base rate. Without a track record, say the
   probability is unscored judgment.
6. **Uncertainty.** A probability is its own uncertainty statement; do not attach a band to it. For a
   quantity, the chapter 7 distribution's quantiles are the range, labelled as a scenario range built
   from stated inputs, not a measured interval.
7. **Report and journal.** Render the chapter 7 or 10 run's report as usual. Every judgment number in
   the interpretation (the prior's strength, each likelihood ratio, an override) goes on an `Assumption:`
   line with its reason, so `run.py report --check` accepts it as declared judgment and the reader can
   see exactly where the number came from. The journal entry is the
   chapter 10 event journal; score it on the resolution date, and read the calibration bins with counts.

The chapter 26 tool turns the probability into an action under the brief's costs: act when the
probability exceeds cost-of-false-alarm over the sum of the two costs. Tell the reader that this is
Bayes-optimal only if their probabilities are calibrated, which the journal will eventually show.
