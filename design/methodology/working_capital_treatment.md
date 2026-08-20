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

## 6. State of the data

> **Correction, 20 August 2026.** An earlier draft of this section said CSL could not
> run the calculation because `data/financials/csl.yaml` holds only `net_debt`. That
> was wrong: the curated YAML is a summary, and the raw feed sits beside it in the
> same directory. `data/financials/csl_eodhd_fundamentals_2026-06-15.csv` carries a
> **six-year annual balance sheet**, and `data/financials/historical/csl/` holds the
> FY22–FY25 statutory accounts and the 1H26 accounts as source PDFs. **CSL is the
> best-documented company in the project, not the worst.** The company with only one
> balance sheet is DNL.

| Company | Can the calculation run? | Basis |
|---|---|---|
| **CSL** | **Yes — six years** | EODHD annual balance sheet FY20–FY25, plus FY22–FY25 + 1H26 statutory accounts in `historical/csl/` |
| **DNL** | **One observation only** | 30 Sep 2025 in `financials/dnl.yaml`. No EODHD export exists (the DNL/IPL feed is the one still outstanding), and `historical/` has no DNL directory. |
| **WBC** | Exempt | Bank archetype. (`historical/wbc/` holds FY22–FY25 reports regardless.) |

### 6.1 CSL — the derived intensity

NCWC = (total current assets − cash & short-term investments) − (total current
liabilities − short-term debt), USD m:

| FY | Revenue | NCWC | Intensity |
|---|---|---|---|
| FY25 | 15,430 | 5,682 | **36.8%** |
| FY24 | 14,690 | 5,105 | **34.8%** |
| FY23 | 13,174 | 5,708 | 43.3% |
| FY22 | 10,493 | 4,886 | 46.6% |
| FY21 | 10,332 | 2,849 | 27.6% |
| FY20 | 9,406 | 3,309 | 35.2% |

Six-year mean **37.4%**; excluding the Vifor-acquisition years FY22–FY23, **33.6%**;
the two clean post-Vifor years FY24–FY25, **35.8%**.

**CSL's assumed 10% is understated by roughly 3.5×.** That is not a rounding
difference — plasma is a genuinely working-capital-heavy business (FY25 inventory
alone is 6,466m, 42% of revenue, reflecting a fractionation cycle measured in
quarters). A 10% intensity implicitly assumes CSL funds growth like a software company.

**Proposed: 35%**, on the FY24–FY25 post-Vifor basis, with the six-year range
disclosed. Effect on Muddle Through: **AUD 203.83 → 195.20, −4.2%** — modest, because
CSL's revenue grows slowly enough that ΔRevenue is small, and it partly offsets the
WACC change in the opposite direction.

### 6.2 The two companies fail differently

1. **CSL has the mechanism and understates the input** — `wc_change_pct_revenue_change:
   0.10` is wired through the engine correctly; the number is just wrong by 3.5×.
2. **DNL omits the mechanism entirely** — `delta_wc` is a vector of zeros.

Both are caught by step 5's lint, but they are different defects and worth naming
separately: one is a bad assumption, the other is an absent one.

### 6.3 Still outstanding (Ben)

DNL only, and it is the existing DNL/IPL EODHD export already on the list. Until it
lands, DNL's intensity rests on a single post-demerger balance sheet — see §7.

## 7. Evidence quality — a caution that applies to DNL specifically

DNL's intensity rests on **one** reported balance sheet. FY21–FY24 in the generator are
explicitly labelled mock placeholders pending Ben's export, so nothing tests whether
13.76% is representative or a post-demerger artefact. The FY25 cash-flow statement
cannot arbitrate either — its working-capital line folds in separation mechanics.

Where more than one year is available, the intensity should be struck on a **multi-year
average** rather than a single balance-sheet date, because working capital is seasonal
and period-end balances are the most manageable numbers on any balance sheet. Single-
observation intensities should be flagged in the decision record as provisional.

### 7.1 Use the level intensity, not the observed marginal rate — CSL proves why

A reasonable objection to the constant-intensity rule is that we could measure the
incremental rate directly: regress ΔNCWC on ΔRevenue year by year. CSL's six years
show why that fails:

| Year on year | ΔRevenue | ΔNCWC | Implied marginal rate |
|---|---|---|---|
| FY24 → FY25 | 740 | 577 | 78.0% |
| FY23 → FY24 | 1,516 | −603 | −39.7% |
| FY22 → FY23 | 2,681 | 821 | 30.6% |
| FY21 → FY22 | 161 | 2,037 | 1,264% |
| FY20 → FY21 | 926 | −460 | −49.7% |

The marginal rate is pure noise on any realistic sample: acquisitions land in one
year, inventory cycles are lumpy, period-end balances are managed, and the denominator
goes near zero whenever revenue is flat (FY21→FY22). Meanwhile the **level** intensity
over the same six years sits in a 27.6–46.6% band and the two clean years are 34.8%
and 36.8% — stable enough to use.

**Standing rule: strike the intensity on the level, averaged over the available years,
and apply it to ΔRevenue. Never fit the marginal rate directly.** State the number of
years and the range in the decision record so the reader can see the dispersion.

## 8. What this does not decide

Adopting the definition does not by itself settle whether DNL's forecast should carry
it. That remains an owner decision, because it retires the audited Muddle Through
oracle and moves all eighteen scenario goldens. What it does settle is that the
*answer* — whatever it is — is derived from the balance sheet by a rule that will
apply identically to the fourth company and the fortieth.
