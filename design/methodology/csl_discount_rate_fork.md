# CSL discount-rate fork — FCFF at Ke, or FCFF at WACC?

**Status: OPEN — owner decision required. Nothing has been changed in the engine.**
Raised as finding 6 of the 13 August 2026 full-project review; magnitude re-derived
during triage the same day and found to be roughly double the reviewer's estimate.

This is the largest single open item in the project. It does not touch DNL or WBC.

---

## 1. What the engine does today

`segment_engine.py` builds **unlevered free cash flow to the firm** — EBIT × (1 − tax)
+ D&A − capex − ΔWC, with no interest anywhere in the build — discounts it at the
**cost of equity** of 8.75% (Rf 4.50% + β 0.85 × ERP 5.00%), and then deducts USD 9,100m
of net debt in the bridge to reach equity value.

The docstring is candid about it (`segment_engine.py:3-5`): *"discount unlevered free
cash flow to the firm at the cost of equity (CSL discounts at Ke, not WACC — it carries
modest net debt and the framework prices the equity claim directly)."*

## 2. Why it is inconsistent

There are two internally consistent pairings, and this is neither:

1. **FCFF ↔ WACC.** Cash flow available to all capital providers, discounted at the
   blended required return of all capital providers, giving enterprise value; then
   deduct debt to reach equity.
2. **FCFE ↔ Ke.** Cash flow available to equity after interest and debt movements,
   discounted at the equity required return, giving equity value directly. No bridge.

Discounting FCFF at Ke charges for the debt twice. Ke is the return required on an
*all-equity* claim on those cash flows; using it as the discount rate has already
priced the enterprise as though it were unlevered and fully equity-funded. Deducting
net debt afterwards removes the debt a second time.

The framework's own §3.5 wording is *"one discount rate matched to the cash-flow
definition"*. Today the discount rate and the cash-flow definition are not matched, and
the only place the choice is justified is a code docstring — not the methodology.

## 3. What it is worth

Re-derived from the live engine on 13 August 2026 (Muddle Through, all other inputs
unchanged):

| Pre-tax cost of debt | D/V | Implied WACC | CSL MT (AUD) | Change |
|---|---|---|---|---|
| *(current — Ke)* | — | 8.75% | **203.83** | — |
| 4.5% | 21.4% | 7.66% | 257.96 | **+26.6%** |
| 5.0% | 21.4% | 7.74% | 252.76 | **+24.0%** |
| 5.5% | 21.4% | 7.83% | 247.73 | **+21.5%** |

D/V uses net debt USD 9,100m against a market capitalisation of USD 33,354m
(478.9m shares × AUD 105.53 ÷ 1.5152), and a 19% tax shield.

The effect is large because it lands almost entirely on the terminal, which is 75.2%
of CSL's EV. At g = 3.0%, moving the rate from 8.75% to 7.74% widens the capitalisation
spread (k − g) from 5.75% to 4.74% — a 21% uplift on the terminal before any change to
the explicit years.

**Consequence for the market gap:** CSL currently sits +93% above market. A consistent
WACC takes it to roughly **+135% to +145%**. The 13 August review asserted that this
finding pushed CSL *down*; it does the opposite, and the direction matters because
§16.3 obligations get harder, not easier.

For reference, the reverse-DCF: the market price of AUD 105.53 is consistent with a
discount rate of **13.05%** on the current cash-flow path. That is the number a sceptic
will quote back, and it is 430bp above Ke and 530bp above the WACC.

## 4. Option A — ratify FCFF at Ke as a deliberate convention

**What it means.** Write the fork into the methodology as an explicit, named,
conservative convention for segment-level valuations: unlevered FCFF discounted at Ke,
with the net-debt deduction retained, accepted as a deliberate downward bias rather than
an oversight.

**The case for it.**

1. It is conservative, and CSL is already the one company where the framework sits far
   above market. Adopting the treatment that *narrows* an uncomfortable gap, on a
   company where the framework is the outlier, is defensible discipline rather than
   convenience.
2. CSL's leverage is genuinely modest — 1.8× EBITDA, D/V 21% at a depressed share
   price. At a *normal* CSL market capitalisation the D/V would be closer to 12-14% and
   the WACC-vs-Ke wedge correspondingly smaller. The current 21% is partly an artefact
   of the stock having fallen 61% from its 52-week high.
3. It sidesteps the circularity in market-value weights: D/V computed on a market price
   the framework believes is 93% wrong is not an independent input. A WACC built on that
   price imports the market's view into a valuation whose whole purpose is to disagree
   with it.
4. Zero implementation risk. No engine change, no workbook change, no base-tie
   movement. One methodology paragraph and one docstring edit.
5. §3.5 already establishes a single-rate discipline per valuation; this keeps CSL on
   one rate and keeps the three companies' *discounting mechanics* comparable even where
   the cash-flow definition differs.

**The case against it.**

1. It is a known error described as a convention. A reviewer who spots it will not read
   "deliberately conservative"; they will read "they discounted FCFF at Ke". The label
   does not repair the arithmetic.
2. Conservatism applied at the *discount rate* is untraceable. It bundles an unstated
   haircut into the one parameter that ought to be pure, where it cannot be separated
   from the genuine cost-of-capital estimate. If the framework wants to be conservative
   about CSL, the honest place to do it is in the cash flows or the terminal margin,
   where the reason is visible.
3. It breaks the reusability claim. The next segment-level company inherits a
   convention that is only defensible at low leverage; nothing in the engine enforces
   the low-leverage precondition.
4. It makes the CSL number non-comparable with DNL's, which *is* a proper FCFF/WACC
   build. Two companies, two definitions of the same discount step.

## 5. Option B — build a CSL WACC

**What it means.** Construct a WACC from the debt stack and market-value weights,
discount the existing unlevered FCFF at it, keep the net-debt bridge, and accept the
+24%.

**The case for it.**

1. It is simply correct. FCFF ↔ WACC is the pairing the cash-flow build already implies;
   the engine computes an unlevered stream and then prices it as if levered.
2. It is what the framework's own §3.5 says to do — match the rate to the cash-flow
   definition. Right now CSL is the only company breaking a rule the project wrote down.
3. It removes the last discount-rate irregularity across the three archetypes: DNL on
   WACC, WBC on Ke with a genuine equity cash-flow stream (§15 — no FCFF, so no
   mismatch), CSL on WACC. Every fork then has a principled reason.
4. The inputs are obtainable. CSL's debt is largely USD private placements and bank
   facilities with disclosed coupons; a cost of debt within the 4.5-5.5% band used above
   is defensible from the interest expense already in the data
   (`net_interest_fy25: -409.5` against USD 9,100m of net debt implies about 4.5%).

**The case against it.**

1. It takes CSL from +93% to +140% above market, and the §16.3 "why we differ" burden
   grows with it. The honest answer becomes harder to write, not easier.
2. The market-value D/V weight is circular in exactly the way described above, and at a
   61%-off share price it is at its least stable. A target/through-cycle capital
   structure would be more defensible than spot, but that is another judgement to
   document.
3. It is the larger piece of work: a WACC build sheet in the workbook, a
   `cost_of_capital` block in `csl.yaml`, the engine plumbing, a re-tie of the audited
   v4 workbook, and every downstream number (UI, scenarios, multiples) moves. The
   Muddle Through tie of USD 134.52 / AUD 203.83 — currently an independently audited
   oracle — is retired and replaced.
4. It fixes half the inconsistency and leaves the other half. If the concern is that the
   engine prices an equity claim, the *fully* consistent alternative is FCFE at Ke —
   which is why finding 4 (the unused `net_interest_fy25` / `net_interest_decline`
   fields, `segment_engine.py:45-46`) is downstream of this decision and not independent
   of it.

## 6. Option C — FCFE at Ke

Worth naming even though I would not recommend it. Build levered free cash flow to
equity (subtract after-tax interest and net debt movements), discount at Ke, and drop
the net-debt bridge entirely. This is the *other* consistent pairing, it would put the
two orphaned `net_interest_*` fields to work, and it would keep CSL on the same rate it
uses today.

Against: it requires a debt schedule (drawdowns, repayments, refinancing) that the
project does not have and would have to invent; it makes the value sensitive to
financing policy in a way that obscures the operating story; and the framework's other
FCFF company (DNL) would then be the odd one out. Enterprise-level FCFF is the right
frame for a segment build. Listed for completeness.

## 7. Interaction with other open items

1. **Finding 1 (CSL valuation-date anchoring)** is independent and small: ±2% depending
   on which of the two repairs is chosen. It does not change this decision.
2. **Finding 4 (`net_interest_*` unused)** resolves automatically: delete under A or B,
   wire under C.
3. **Finding 10 (§16.3 market-gap treatment)** and the proposed CSL gap panel (UI item
   35) should both wait for this. Writing "why we differ from the market" before knowing
   whether the difference is 93% or 140% is wasted work.
4. **Market-price staleness.** The AUD 105.53 is struck at 15 June 2026 — two months
   old, against a 50-day moving average of 115.28 and a 200-day of 161.95. Both the D/V
   weight in Option B and the gap in finding 10 depend on it. Worth refreshing before
   either is finalised.

## 8. Recommendation

**Option B, with two qualifications**, if you want my view.

The inconsistency is real, it is written down in the project's own §3.5, and it is going
to be the first thing a technical reviewer finds. Ratifying it as a convention is the
cheaper answer but not the more durable one — a deliberate, undocumented-in-the-workbook
haircut buried in the discount rate is the kind of thing the SSOT protocol exists to
stop.

The two qualifications:

1. **Use a target capital structure, not spot D/V**, and say so. Something in the
   12-15% D/V range reflecting CSL's through-cycle leverage rather than 21.4% struck on
   a distressed price. That both reduces the circularity and moderates the uplift —
   likely +12% to +16% rather than +24%.
2. **Do it after the engine lock is in place** (the 18 pinned goldens landed today), and
   treat the resulting per-share number as a new independently audited oracle: rebuild
   the v4 workbook against the WACC and re-tie, rather than letting the engine become
   self-certifying.

If the +24% (or +14%) is unpalatable because of what it does to the market gap, that is
a legitimate reason to *pause*, but it is not a reason to prefer Option A. The gap is
either a real disagreement with the market or a signal that something else in the CSL
build is too optimistic — and Option A's effect is to hide which.
