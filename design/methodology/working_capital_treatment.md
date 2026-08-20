# Working capital — definition, derivation and enforcement

**Status: PROPOSED — for ratification. Owner decision 20 August 2026 to adopt the
broad (non-cash working capital) definition; this document specifies it.**

Purpose: one repeatable working-capital calculation that applies to any company,
derived from data rather than hand-authored, and enforced so that company four cannot
silently inherit a zero.

---

## 1. The definition

**Non-cash working capital (NCWC) = (current assets − cash and equivalents) −
(current liabilities − interest-bearing debt)**

Everything on the current side of the balance sheet that is *not* a financing item is
operating working capital, by construction. Nothing is judged in or out line by line.

The **intensity** is NCWC ÷ revenue, and the forecast rule is:

**ΔWC(year) = intensity × ΔRevenue(year)**, with the terminal carrying
**intensity × g × Revenue(final)**.

### Why this definition rather than trade working capital

An earlier draft used receivables + inventory − payables. It was rejected for three
reasons:

1. **It requires a judgement the data cannot settle.** "Other current assets" and
   "other current liabilities" hold accruals, prepayments, provisions and deferred
   revenue at a level of aggregation that does not say what is inside. Excluding them
   is an argument from ignorance, not from principle. For DNL they net to −115.4m —
   3.1pp of intensity — so the judgement is not immaterial.
2. **It is not reliably feedable.** Total current assets, total current liabilities,
   cash and short-term debt are four lines every provider carries. Receivables /
   inventory / payables splits are usually but not always available, and their
   definitions differ between providers. Repeatability breaks at the first company
   where the split is missing or defined differently.
3. **It is incomplete.** Accruals, prepayments and deferred revenue genuinely tie up
   or release operating cash. Omitting them because they are awkward biases the
   measure in a direction nobody chose.

## 2. The carve-outs — standing rules

The definition only stays repeatable if the exclusions are mechanical. Three rules:

1. **Every interest-bearing item is excluded from current liabilities** — short-term
   debt, the current portion of long-term debt, **and the current portion of lease
   liabilities**. The lease point is not optional: the equity bridge already treats
   AASB 16 leases as debt (Approach A), so a current lease portion left inside working
   capital is counted twice against the same valuation. Providers routinely bury the
   current lease portion inside "other current liabilities", so this has to be an
   explicit instruction rather than an assumed one.
2. **Assets and liabilities held for sale are excluded**, both sides. Otherwise a
   pending divestment registers as a working-capital swing. DNL is the live case —
   mid-separation, with the Phosphate Hill items already handled as §4.2 equity-bridge
   adjustments; leaving them in working capital would double-count them too.
3. **All cash is excluded, including operating float.** Strictly, some cash is
   operating and belongs in working capital. In practice no feed distinguishes it, and
   the net-debt bridge already carries the whole balance. The approximation is
   recorded here rather than hidden: it slightly overstates working-capital efficiency
   for cash-intensive retail-type businesses, and is immaterial for the archetypes in
   scope.

## 3. The archetype fork — banks are exempt

A bank has no operating working capital in this sense: its current assets and
liabilities *are* its business, and netting them would produce a meaningless number.
`archetype_class: bank` is therefore **exempt by rule, not by returning zero**.

This matters because of how the terminal-share warning failed: a check that simply did
not exist on two of three engines looked identical, from the outside, to a check that
was passing. An exemption must be declared and visible, so that "no working capital"
is always distinguishable from "working capital not implemented here".

## 4. Layering — where each number lives

Per `design/single_source_of_truth.md` and standing rule 1:

| Quantity | Layer | Where | Stored or derived? |
|---|---|---|---|
| Current assets, current liabilities, cash, interest-bearing current debt | 1 (observed) | `data/financials/<id>.yaml` | **Stored** — reported balance-sheet lines |
| Archetype baseline WC intensity | 2 (method) | `data/industries/<archetype>.yaml` | Stored — a judgement |
| Company offset vs the archetype | 2 (method) | `data/companies/<id>.yaml` | Stored — a judgement, with rationale |
| **Applied WC intensity** | 3 (derived) | nowhere | **Derived by the engine — never stored** |
| ΔWC per year | 3 (derived) | nowhere | Derived by the engine |

The applied intensity is a computed answer. Storing it is the `computed_wacc: 0.0882`
defect, and the SSOT lint will flag it.

**Industry baseline plus company offset as separate rows** is required by standing
rule 1, and is right on the merits here: working-capital intensity is strongly
archetype-characteristic — industrial explosives, plasma fractionation and grocery
retail sit in genuinely different places — while company-level variation reflects
payment terms, customer concentration and inventory policy. The same shape as the WBC
AIEA/NIM chain: archetype anchor, company offset, applied figure derived.

## 5. Enforcement — five steps to bake it in

1. **This document**, referenced from `architecture.md` §11, is the durable statement.
2. **Schema.** Add the four balance-sheet fields to the layer-1 financials schema, and
   `working_capital_intensity_offset` (+ rationale) to the company schema. Add
   `working_capital_intensity_baseline` to the archetype schema.
3. **Translator.** A `working_capital_intensity_from_data(inputs)` function alongside
   the existing `revenue_growth_from_data`, so the intensity is computed for every
   company on every run. **This is the step that makes it automatic rather than
   remembered** — a hand-authored intensity is a hand-authored intensity no matter how
   good the methodology document is.
4. **Engine.** `build_*_inputs_from_data` populates `delta_wc` from the derived
   intensity for all FCFF engines, and the terminal carries `intensity × g × revenue`.
   No engine may default `delta_wc` to zeros.
5. **Ratchet.** A new lint check: every company whose archetype is not exempt must
   produce a derived intensity, or carry an explicit `working_capital_exemption` with
   a reason. Fails loudly, so company four cannot inherit silence.

## 6. Known state of the data

| Company | Can the calculation run today? | Note |
|---|---|---|
| **DNL** | **Yes** | Full current assets/liabilities at 30 Sep 2025. NCWC = (2,122.7 − 647.2) − (1,591.3 − 626.3) = **510.5m**, intensity **13.76%** of FY25 revenue. |
| **WBC** | Exempt | Bank archetype. |
| **CSL** | **No** | `data/financials/csl.yaml` holds `balance_sheet: {net_debt: 9100}` and nothing else. No current assets, no current liabilities. |

**CSL's current 10% is therefore a hand-typed judgement with no balance-sheet
derivation behind it.** It was not wrong to use a placeholder, but it should not be
mistaken for a derived figure, and it will not survive step 5 above without either the
data or a declared exemption.

**Add to the outstanding data request (Ben):** for CSL, and for every future company —
total current assets, total current liabilities, cash and equivalents, short-term
debt, current portion of long-term debt, current portion of lease liabilities, and
assets/liabilities held for sale.

## 7. Evidence quality — a caution that applies to DNL specifically

DNL's intensity rests on **one** reported balance sheet. FY21–FY24 in the generator are
explicitly labelled mock placeholders pending Ben's export, so nothing tests whether
13.76% is representative or a post-demerger artefact. The FY25 cash-flow statement
cannot arbitrate either — its working-capital line folds in separation mechanics.

Where more than one year is available, the intensity should be struck on a **multi-year
average** rather than a single balance-sheet date, because working capital is seasonal
and period-end balances are the most manageable numbers on any balance sheet. Single-
observation intensities should be flagged in the decision record as provisional.

## 8. What this does not decide

Adopting the definition does not by itself settle whether DNL's forecast should carry
it. That remains an owner decision, because it retires the audited Muddle Through
oracle and moves all eighteen scenario goldens. What it does settle is that the
*answer* — whatever it is — is derived from the balance sheet by a rule that will
apply identically to the fourth company and the fortieth.
