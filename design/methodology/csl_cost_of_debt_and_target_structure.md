# CSL WACC — the debt stack, the cost of debt, and the target capital structure

**Status: OPEN — owner decision on two parameters. No engine or workbook change made.**
Written 20 August 2026 at Stephen's request. Follows the decision to build a CSL WACC
on a target capital structure (`csl_discount_rate_fork.md`, option B with
qualifications).

Two numbers are needed: **the pre-tax cost of debt** and **the target D/V weight**.
This sets out what the register can and cannot support for each.

---

## 1. What the register actually holds on CSL's debt

Everything, in full:

| Field | Value | Source |
|---|---|---|
| `net_debt` | USD 9,100m | `financials/csl.yaml:54`, 1H26 close (31 Dec 2025) |
| `net_debt_ebitda` | 1.8× | `companies/csl.yaml:46`, per FY25 presentation |
| `net_interest_fy25` | USD −409.5m | `companies/csl.yaml:647` |
| `net_interest_decline` | 5% p.a. | `companies/csl.yaml:648` |

**That is the entire debt stack.** There is no gross debt figure, no cash balance, no
maturity ladder, no coupon, no facility detail, no credit rating. Compare WBC, where
the register carries a full RWA composition, CET1 ratios, AT1 face value and hybrid
call dates.

This is itself a finding: **a WACC cannot be built from CSL's register as it stands
without adding at least one judgement input.** That is not a reason to abandon the
WACC — it is a reason to be explicit about which number is observed and which is
assumed, per the layer-1/layer-2 discipline.

## 1a. The protocol already exists — corrected 20 August 2026

> **Correction.** The first draft of §2 and §3 invented a cost-of-debt spread and a
> "target D/V" from first principles. It should not have: the framework already
> specifies both, and DNL already follows them. Stephen caught this. The sections
> below are rewritten against the actual protocol; the earlier reasoning survives only
> where it happens to agree.

**The specification.** `architecture.md:788-802` lists the financial drivers in order,
and three of them are directly on point:

| # | Driver | Class |
|---|---|---|
| 3 | **Capital structure target** (net-debt / EBITDA, or D/E) | primary input |
| 4 | **Cost of debt, pre-tax** | primary input |
| 11 | WACC | **derived** from cost of equity + after-tax cost of debt + capital structure |

Two things follow immediately. Capital structure is specified as a **target ratio**,
not a spot market weight — so the share-price circularity the earlier draft agonised
over is not a problem the framework asked us to solve. And the WACC is derived, never
stored, exactly like the cost of equity.

**The worked precedent.** DNL implements the cost-of-debt protocol at
`data/companies/dnl.yaml:549`:

```yaml
cost_of_debt_pretax: 0.0600
cost_of_debt_pretax_rationale: >
  AUD investment-grade BBB-tier corporate spread ~170bps over
  10-year sovereign. IPL pre-demerger BBB+/Baa1; post-demerger
  DNL likely BBB given smaller scale and concentrated cyclical
  exposure.
```

Three moves, in order:

1. **Establish the rating** — actual where one exists, notional where it must be
   inferred, with the inference reasoned in the open. DNL: IPL was BBB+/Baa1
   pre-demerger; DNL is smaller and more cyclical, so notionally BBB.
2. **Take the spread on comparably rated paper** over the sovereign of the cash-flow
   currency, at a tenor matching the valuation. DNL: ~170bp for AUD BBB-tier.
3. **kd = risk-free rate + spread**, using the *same* risk-free rate as the
   cost-of-equity build so the two sides of the WACC are internally consistent.

This is a better protocol than the spread-from-nowhere the earlier draft proposed,
because it is repeatable: any company can be placed on a rating scale and any rating
has an observable spread. It also degrades gracefully — an unrated company gets a
notional rating with stated reasoning rather than a shrug.

## 2. The cost of debt

### 2.1 What the data implies, and why it is not the answer

Net interest ÷ net debt = 409.5 ÷ 9,100 = **4.50%**.

Two problems with using that figure:

1. **It is not a rate on anything.** Net interest nets interest income against interest
   expense; net debt nets cash against gross debt. Those two nettings do not cancel.
   Where cash earns less than debt costs — always — the ratio comes out *above* the
   true effective rate on gross debt. So 4.50% is an upper bound on CSL's historical
   book rate, not an estimate of it.
2. **It is a historical average, and a WACC needs a marginal rate.** The figure
   reflects debt raised across a decade that included the zero-rate era. What matters
   for a discount rate is what CSL would pay to borrow *today*.

There is also a tell that the number is not usable as-is: **4.50% is exactly the
risk-free rate** in CSL's own cost-of-equity build (Rf 4.50% + β 0.85 × ERP 5.00%).
A corporate borrowing at precisely the sovereign rate implies a zero credit spread,
which is not a thing. The coincidence is confirmation that the implied figure is
measuring something other than the marginal cost of debt.

### 2.2 The build-up, per the §1a protocol

**Step 1 — the rating.** CSL is not rated in the register, so a notional rating is
required with the reasoning stated, exactly as DNL's was. The relevant facts the
register does hold: net debt / EBITDA **1.8× and de-levering** (`csl.yaml:46-49`),
large-cap scale, and an essential-medicines franchise with low demand cyclicality.
Against DNL's notional **BBB** — set there for smaller scale and concentrated cyclical
exposure — CSL sits **two to three notches higher**, in the **BBB+/A− band**. Every
input to that comparison is in the register; the notch judgement is not, and is
recorded as such.

**Step 2 — the spread on comparably rated paper.** DNL's anchor is ~170bp for **AUD**
BBB-tier over the 10-year sovereign. CSL borrows in **USD**, a deeper market that
prices investment-grade paper more tightly, and sits one to two notches better.
Calibrating off DNL's own anchor rather than an outside assertion puts CSL at roughly
**100–130bp**.

**Step 3 — kd = Rf + spread = 4.50% + 100–130bp = 5.50% to 5.80%.**

**I would take 5.5%**, the bottom of that range. It is the conservative choice for
this decision — a *lower* cost of debt raises the WACC's equity weight less and so
produces a *smaller* uplift — and it sits at the BBB+/A− boundary rather than assuming
the better rating.

> **Layer discipline.** The rating and the spread are layer-2 judgements; kd is
> derived. Store in `companies/csl.yaml` mirroring the DNL block shape:
> `cost_of_debt_pretax` with its rationale naming the notional rating, the spread and
> the sovereign it is measured over. The engine adds Rf. Never store the WACC —
> `architecture.md:1130` makes it a derived identity.

**What would retire the judgement:** CSL's actual agency rating and any disclosed
facility margin or coupon. Both are ordinary disclosures. Add to the outstanding data
request alongside the peer financials.

> **Note on scenario-conditionality.** The scenario library carries a
> `financial_conditions.credit_spreads` descriptor (`architecture.md:285`), so it is
> tempting to flex the spread by world. Don't. §3.5 fixes one discount rate per
> company per valuation date; scenarios differ in cash flows, not in the rate. The
> scenario spread descriptor informs the *choice* of the single spread, it does not
> vary it.

## 3. The target capital structure

### 3.1 The framework already specifies the form

`architecture.md:791` calls for a **capital structure target expressed as net-debt /
EBITDA or D/E** — not a spot market weight. That disposes of the problem the earlier
draft spent a page on: we were never meant to weight the WACC with today's share
price. CSL's target is already in the register at **1.8×**
(`csl.yaml:46`, FY25 reported and described as de-levering).

For the record, the objections to spot weighting stand and are why the framework
specifies a target: at AUD 105.53 the spot D/V is 21.4%, the most leveraged reading
CSL has had in years and 61% below its 52-week high, and using it would mean a falling
share price mechanically lowering the WACC and raising the valuation — a feedback loop
pointing the wrong way.

### 3.2 Converting the target to a D/V weight

The WACC identity needs a weight, so the target ratio has to be converted:

**D/V = (net debt / EBITDA) ÷ (EV / EBITDA)**

At CSL's 1.8× target and implied EBITDA of USD 5,056m (9,100 ÷ 1.8, which
cross-checks against FY25 revenue 15,558 × (27.5% EBIT margin + 6% D&A) = 5,212m):

| EV / EBITDA used | Implied EV (USD m) | D/V |
|---|---|---|
| 8.4× — current market | 42,467 | 21.4% |
| 12× | 60,667 | 15.0% |
| 14× | 70,778 | 12.9% |
| 14.6× — model implied | 73,811 | 12.3% |
| 16× | 80,889 | 11.2% |

**The honest point: this relocates the judgement, it does not remove it.** Expressing
the target as net debt / EBITDA makes the *leverage* observable, but the conversion
still needs an EV/EBITDA multiple, and picking one is the same decision as picking a
D/V in different clothing. Using the model's own EV (14.6×) is internally consistent
but circular; using the current market multiple (8.4×) reimports the depressed price.

It is nonetheless a better place for the judgement to sit, for two reasons:

1. **A through-cycle EV/EBITDA is an observable peer statistic.** CSL's comparables —
   Grifols, Takeda, Sanofi — already have a peer block in `beta_data.py` awaiting
   Ben's `mfin` financials. When that lands, the multiple becomes evidence rather than
   assertion. A "target D/V" would never have become evidence.
2. **Net debt / EBITDA is the ratio management actually runs the balance sheet to**,
   and the register already records it as a stated posture rather than an artefact.

**I would take 14×**, giving **D/V 12.9%** — a mid-teens multiple for a large-cap
plasma franchise, sitting just below the model's own implied 14.6× so that the weight
is not simply the model marking its own homework. That is materially the same answer
as the 13.5% the earlier draft reached by a worse route, which is mild reassurance.

**Interim status:** treat 14× as provisional and revisit when the peer financials
arrive. Flag it in the decision record as the one input in the CSL WACC with no
independent support today.

## 4. What each combination is worth

CSL Muddle Through, currently AUD 203.83 at Ke 8.75%:

| Target D/V | kd 4.5% | kd 5.0% | kd 5.5% |
|---|---|---|---|
| 12.0% | 231.29 (+13.5%) | 228.87 (+12.3%) | **226.50 (+11.1%)** |
| 13.5% | 235.19 (+15.4%) | 232.39 (+14.0%) | **229.65 (+12.7%)** |
| 15.0% | 239.21 (+17.4%) | 236.01 (+15.8%) | **232.89 (+14.3%)** |

My recommended combination after the §1a correction — **D/V 12.9%** (target 1.8× ÷ a
through-cycle 14× EV/EBITDA) with **kd 5.5%** (Rf 4.50% + 100bp at notional BBB+/A−)
— falls between the 12.0% and 13.5% rows, at roughly **AUD 228, +12%**. It is the
conservative corner of a defensible range, which is the right posture given the
direction of the change is already uncomfortable: it widens the market gap from +93%
to about +117%.

For comparison, the spot-D/V version of the same change gives AUD 248–258, +21.5% to
+26.6% — so the target-structure qualification roughly halves the uplift.

## 5. Consequences to plan for

1. **The market gap widens from +93% to +118%.** The §16.3 structural-reason treatment
   becomes more pressing, not less, and the CSL gap panel (review item 35) should be
   written against the new number.
2. **The audited v4 Muddle Through workbook retires.** USD 134.52 / AUD 203.83 ceases
   to be the oracle; the workbook needs a WACC build sheet and a re-tie at the new
   rate. Until that is done the engine would be self-certifying, which the triage plan
   explicitly warned against.
3. **All 18 scenario goldens move** and must be consciously re-pinned.
4. **Review item 4 resolves to "delete".** With CSL confirmed as FCFF/WACC, the unused
   `net_interest_fy25` and `net_interest_decline` fields have no future use and should
   be removed — interest belongs in the discount rate now, not the cash flow.
5. **`csl.yaml` gains a `cost_of_capital` block** (target D/V, credit spread,
   rationale for each), and `discount_rate_basis` at `csl.yaml:603-606` needs
   rewriting — it currently reads "FCFF discounted at the cost of equity given modest
   net leverage", which becomes false.

Estimated effort: one day including the workbook WACC sheet, the re-tie, and the data
block.

## 6. The two decisions

| | Recommendation | Basis | Alternative |
|---|---|---|---|
| **Notional rating** | **BBB+/A−** | 1.8× and de-levering, large-cap, low-cyclicality franchise; two to three notches above DNL's notional BBB | A− flat if you read the franchise as more defensive |
| **Credit spread** | **100bp** | Calibrated off DNL's own 170bp AUD BBB anchor, adjusted for USD market depth and the notch difference | 130bp at the BBB+ end |
| **Cost of debt** | **5.50%** | Rf 4.50% + 100bp, same Rf as the cost-of-equity build | 5.80% at the wider spread |
| **Capital structure target** | **1.8× net debt / EBITDA** | Already in the register as a stated posture | — (observed, not a choice) |
| **EV/EBITDA for conversion** | **14×** | Through-cycle mid-teens for a large-cap plasma franchise; below the model's own 14.6% so the weight isn't self-marking | 12× if you want a wider margin; revisit when peer financials land |
| **Implied D/V** | **12.9%** | 1.8 ÷ 14 | — (derived) |

Together: **WACC ≈ 8.2%, CSL MT ≈ AUD 228 (+12%).**

The one input with no independent support today is the EV/EBITDA multiple. Everything
else is either observed in the register or reasoned off DNL's existing precedent.

