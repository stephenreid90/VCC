# Methodology v0.7 — Proposal (process discipline from the CSL build)

**Status:** ACCEPTED (25 June 2026). Folded into `design/architecture.md` as the
v0.6 → v0.7 migration note (status bumped to v0.7). Additive only; no schema breaks.
Lint (c) backported to DNL v6 and WBC v4 (both lint-clean).

**Date:** 25 June 2026.

**Provenance.** Surfaced from the CSL Muddle Through review. After pulling
sell-side consensus (16 analysts, via MarketScreener + Yahoo) and comparing it
to the framework, three problems were found that were matters of *shape and
consistency*, not long-run thesis. The single largest was a terminal EBIT
margin that was *stated* (30%) on the Assumptions sheet but never wired into any
formula — the model silently capitalised FY31's ~33.3% peak into perpetuity.
Because terminal value was ~77% of EV, that one orphaned input drove ~84% of the
USD 23/share correction once fixed. The six refinements below would have caught
or prevented each issue, and generalise to any company.

These mirror the v0.6 pattern: discipline / explicit-articulation refinements,
not analytical-substance changes.

---

## (a) §3.7 — Forecast-trajectory discipline (cycle-position split)

Every primary growth and margin driver is entered as a *trajectory* with an
explicit statement of (i) current cycle position, (ii) any live, high-certainty
disruption, and (iii) the through-cycle anchor it converges to. A flat CAGR must
be justified, not assumed as the default input shape.

**CSL example.** Behring was entered as a flat 5% CAGR — defensible as a
through-cycle number (archetype secular 5–7%) but blind to the live Medicare
Part D + China trough the archetype itself rates high-certainty (1H26 Behring
−7%). The fix was a J-curve (FY26 −1%, recovering to 5.5% by FY29). Same spirit
as the DNL gas-roll-off overlay (§3.2.1): build the headwind into the cash
flows, don't ignore it. Cross-references §3.2.1 and the §11.3 time-profile
library.

## (b) §16.5 — External reference forecast as a calibration input

Pull a consensus (or strategist) explicit-period forecast at build time and sit
it beside the model *during* construction, not as a post-hoc check. The analyst
articulates, per year and per driver, where and why the framework differs. Per
§16 the gap remains the *output* — the framework is not tuned to consensus — but
the divergence must be known and explained while building. Had the −1.1% FY26
consensus revenue been in front of us during the CSL build, the missing Behring
J-curve would have been obvious immediately.

## (c) §11.6 — Workbook-integrity checks (orphan-input + terminal-continuity)

Two automated checks, implemented as a reusable lint (`scripts/workbook_lint.py`):

1. **No orphan inputs.** Every yellow/blue input cell on the Assumptions sheet
   must be referenced by at least one formula. Structural orphans (terminal,
   discount-rate, growth, margin drivers) are errors; documentation-only anchors
   (measured beta shown for transparency, FY25 memos, reconciliation checks) are
   downgraded to warnings — and to keep them distinguishable, such cells should
   carry a memo marker in their label/note.
2. **Terminal continuity.** The terminal block must be driven by the stated
   structural assumptions, and the terminal EBIT margin must not exceed the
   explicit-period exit-year margin. Any case where it does is flagged for a
   written justification.

The CSL v1 workbook fails both (B55 orphan; effective terminal margin 33.3% vs
stated 30%); v3 passes.

## (d) §4.4.1 — Benefit-funding consistency (extends the §4.4 cost-of-closure rule)

Any modelled benefit (margin uplift, synergy) is checked against whether its
enabling spend is *also* generating modelled growth. If transformation savings
are reinvested to drive growth, you cannot also bank the full savings as margin.
The reinvestment split is made an explicit input rather than assumed away. CSL
banked the full peer-gap-closure margin uplift *and* the growth the reinvested
US$525m is meant to fund — a classic double-count.

## (e) §3.5.7 — Market-implied cost-of-capital reality check

The selected cost of equity is sanity-checked against the market-implied figure,
especially after a large drawdown. CSL's β 0.85 (defensive-healthcare peer
triangulation) sits against a 60%+ share-price fall — exactly the case where the
selected β may understate current systematic risk and warrants an explicit
cross-check.

## (f) §14.5.2 — Aggression flag (extends §14.5.1 assumption-strength tagging)

Where a `[judgment]` input sits *above* disclosed company guidance or the
archetype secular rate, it is surfaced explicitly — these are the model's
boldest, least-supported bets. CSL's +250bps Behring margin uplift and flat 5%
growth both sat above near-term guidance at a moment the street was downgrading.

---

## Implementation notes

- (c) is already built: `scripts/workbook_lint.py`, tested against CSL v1 (fails,
  exit 1) and v3 (passes, exit 0).
- (a), (d), (f) imply small schema additions to company YAMLs (trajectory block;
  reinvestment-split input; aggression tags). Additive; existing YAMLs continue
  to validate.
- (b) and (e) are process/discipline, no schema change.
- If accepted, fold into `design/architecture.md` as the v0.6 → v0.7 migration
  note with lettered items, bump status to v0.7, and backport the lint to the
  DNL and WBC workbooks.
