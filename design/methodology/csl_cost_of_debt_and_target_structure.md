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

### 2.2 The build-up

The defensible construction mirrors the cost-of-equity build — a risk-free rate plus
a spread, using the same Rf so the two sides of the WACC are internally consistent:

**kd = Rf + credit spread = 4.50% + spread**

CSL is a large-cap investment-grade pharmaceutical with leverage of 1.8× EBITDA and
de-levering. A spread in the region of **90–120bp** is the conventional range for that
credit profile on USD paper at ten-year tenor, giving:

**kd ≈ 5.4% to 5.7%**

I would take **5.5%**, sitting mid-range and comfortably above the 4.50% legacy book
rate in a way that reflects refinancing at current levels.

> **Layer discipline note.** The credit spread is a layer-2 judgement, not an observed
> value, and should be stored in `companies/csl.yaml` as
> `cost_of_debt_method: {risk_free_rate_source: <shared>, credit_spread: 0.010,
> spread_rationale: ...}` with the resulting kd derived by the engine — never stored.
> That keeps it consistent with how `coe_method` already works.

**What would improve this:** a credit rating and any disclosed coupon or facility
margin from Ben's feed would replace the spread judgement with an observation. Worth
adding to the outstanding data list alongside the peer financials.

## 3. The target capital structure

### 3.1 Why not spot

Spot D/V is 21.4% (net debt 9,100 against a market capitalisation of USD 33,354m at
AUD 105.53). Two objections:

1. **Circularity.** Weighting a valuation with a market price that the same valuation
   says is 93% too low imports the market's view into a number whose purpose is to
   disagree with it. The lower the price falls, the higher the debt weight, the lower
   the WACC, and the higher the valuation — a feedback loop pointing the wrong way.
2. **The price is at an extreme.** CSL trades 61% below its 52-week high. Spot D/V is
   the most leveraged reading the company has had in years, and treating it as the
   through-cycle structure builds a distressed moment into a perpetuity assumption.

### 3.2 The range

D/V at various share prices, holding net debt at 9,100:

| Reference | Price (AUD) | Market cap (USD m) | D/V |
|---|---|---|---|
| Spot (15 Jun 2026) | 105.53 | 33,354 | 21.4% |
| 50-day moving average | 115.28 | 36,436 | 20.0% |
| **200-day moving average** | **161.95** | **51,187** | **15.1%** |
| Model Muddle Through | 203.83 | 64,423 | 12.4% |
| 52-week high | 269.15 | 85,069 | 9.7% |

The 12–15% range proposed in the fork note brackets the **200-day moving average
(15.1%)** at its top and the **framework's own central case (12.4%)** at its bottom.
That is a defensible span: the upper bound is an observable one-year average price
rather than a spot extreme, and the lower bound is internally consistent with what the
model itself concludes the equity is worth.

**I would take 13.5%** — the midpoint, which corresponds to a share price of roughly
AUD 185, between the 200-day average and the model value. It is also close to what
1.8× EBITDA implies for a company on a mid-teens EV/EBITDA multiple, which is a
sense-check independent of the share price entirely.

> **Circularity caveat, stated plainly.** Using the model's own value as the lower
> bound of the target range is itself mildly circular. It is less circular than spot,
> because the model value is not moved by the price, but it is not clean. The cleanest
> anchor available is the 200-day average at 15.1%, at the cost of a slightly larger
> uplift. If you want the most defensible-to-a-sceptic number rather than the most
> balanced one, take 15.1%.

## 4. What each combination is worth

CSL Muddle Through, currently AUD 203.83 at Ke 8.75%:

| Target D/V | kd 4.5% | kd 5.0% | kd 5.5% |
|---|---|---|---|
| 12.0% | 231.29 (+13.5%) | 228.87 (+12.3%) | **226.50 (+11.1%)** |
| 13.5% | 235.19 (+15.4%) | 232.39 (+14.0%) | **229.65 (+12.7%)** |
| 15.0% | 239.21 (+17.4%) | 236.01 (+15.8%) | **232.89 (+14.3%)** |

My recommended cell — **D/V 13.5%, kd 5.5% → WACC 8.17%, AUD 229.65, +12.7%** — is
the most conservative of the mid-range options, because it pairs the midpoint leverage
weight with the top of the cost-of-debt build. Given the direction of this change is
already uncomfortable (it widens the market gap from +93% to +118%), taking the
conservative corner of a defensible range is the right posture.

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

| | Recommendation | Alternative |
|---|---|---|
| **Cost of debt** | **5.5%** (Rf 4.50% + 100bp spread) | 5.0% if you think the spread is tighter; 4.5% only if you want to use the implied book rate, which I would argue against for the reasons in §2.1 |
| **Target D/V** | **13.5%** (midpoint, ≈ AUD 185 share price) | 15.1% if you prefer the 200-day average as a purely observable anchor and accept +14.3% |

Both recommendations together: **WACC 8.17%, CSL MT AUD 229.65 (+12.7%).**
