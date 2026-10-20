# EVN first build: review of D-96 to D-101 and the framework gaps

**Status: recommendations put to Stephen, 20 October 2026. Nothing below is ruled until he says so.**
Companion to `resource_lifecycle_and_mining_drivers.md` (the paper). Figures for EVN come from
`resource_valuation_sets.yaml` (set `evn`). Market facts were checked on 20 October 2026; sources at the end.

## 1. D-99 first: the gold, copper and AUD/USD paths

### The problem

1. **Every scenario has gold falling or flat in real terms.** At year 10 the highest path is
   Fragmentation at US$4,200, about today's spot (US$4,156 close, 16 Oct 2026). Muddle Through falls
   16% to US$3,500; Orderly Convergence falls 28% to US$3,000. No scenario has gold above spot at year 10.
   The set is not centred on anything observable; it is centred on a decline.
2. **Muddle Through's stated reason does not produce a decline.** Its basis says real rates stay about
   1% and official-sector buying persists, so the price "eases from its 2026 high". But the 2026 high
   (about US$5,590, 28 January 2026) is already 26% behind us. Spot has done the easing. Holding real
   rates and official buying steady is a reason for the real price to hold, not to fall another 16%.
3. **The observable market price does not fall.** The gold futures curve sits above spot (contango,
   the cost of carry). That is not a forecast, but it is the price a producer could lock in today. The
   paths sit below it in every scenario.
4. **This is the input that matters.** The WACC moves Muddle Through by about A$0.25 a share per
   point. Holding today's spot flat in real terms moves it from A$4.18 to A$6.55. The gap to the
   A$12.09 market price is mainly a gold-path question.
5. **Copper has the same tilt** (Muddle Through 12,000 a tonne against about 14,750 today, minus 19%),
   but copper is a smaller share of revenue.
6. **AUD/USD is fine.** Muddle Through at 0.70 matches today's 0.697. The spread across scenarios
   (0.63 to 0.74) follows each scenario's currency story, and the natural hedge (weak AUD with high
   gold) is in the right direction.

### Recommendation

Change D-99 so the commodity paths follow the same discipline as the other macro paths (D-73: a path
is a declared anchor plus a stated deviation).

1. **Anchor:** year 0 is the observed spot at the valuation date (D-94), in real terms.
2. **Muddle Through holds the anchor flat in real terms**, unless its own narrative names a mechanism
   that moves the price. A real price that drifts needs a written reason, as D-90 requires for a
   non-flat offset.
3. **The other five scenarios are stated deviations from Muddle Through**, each with its mechanism
   (real rates, reserve diversification, safe-haven demand, the AUD story).
4. **Balance check:** at least one scenario must end above the anchor and at least one below. A set
   where every path falls is a view on the price, and a view needs its own decision.
5. **Copper the same way.** AUD/USD stays as built.

Effect, on numbers already computed: Muddle Through goes from A$4.18 to about A$6.55 (spot flat real).
The other five would be re-set around it and re-sized. The gap to market stays large (about 46% below
on Muddle Through) and stays disclosed, not reconciled (D-92's principle).

## 2. D-96, D-97, D-98, D-100, D-101

1. **D-96, a fourth engine. Rule as proposed.** EVN fits none of the three engines. The new engine
   reuses the stub, mid-period discounting, single WACC and equity bridge, and names no company.
2. **D-97, the depletion run-off as the terminal, then zero-NPV replacement. Rule as proposed.** It
   follows from D-43a (an ore body is a rent) and fits inside D-71 (ten explicit years; a multi-phase
   terminal is allowed). The five-year extension sensitivity is the right disclosure for the
   alternative view that EVN keeps replacing ounces at a profit.
3. **D-98, inventory and capital. Rule with one change: treat E22 consistently.** Charging E22's
   capital without its metal is one-sided, and the paper notes the charge may also be short of the
   company's A$545m. Under D-97's own logic an unquantified project sits at zero NPV, like Carnaby and
   Marsden. Recommendation: take E22 out of both capital and volume, and disclose it as excluded. Fixed
   inventory across scenarios is acceptable for now: Orderly Convergence's lowest A$ gold price (about
   A$4,050 real at year 10) is still above the A$3,000 reserve price, so the stated lives stay economic.
4. **D-100, the equity bridge. Rule, with a data follow-up.** The 30 September anchor, the dividend
   deduction (D-88 precedent) and the stream-in-revenue treatment are right. Rehabilitation and leases
   are 30 June 2025 figures, 15 months old. The FY26 annual report (30 June 2026 balance sheet) should
   replace them; it is not in the folder.
5. **D-101, the discount rate. Rule as proposed.** Rf 5.31% at 14 October checks out (the 10-year was
   5.23% on 15 October). Beta 0.90 rests on judgement because the peer betas are not observed, which is
   the same status as the other three companies (D-02). It is not load-bearing: one point of WACC moves
   Muddle Through by about A$0.25.

## 3. The framework gaps (paper §6, plus three found in this review)

Already fixed in the build, close them: gap 5 (SSOT year-end read from layer 1) and gap 6 (the
declared `no_barrier_declared` moat field).

Recommended order for the rest:

1. **Commodity-path discipline (gaps 2 and 3, plus the D-99 change above).** Write the anchor,
   deviation and balance rules into the scenario method and the D-73 carve-out, so oil, iron ore or coal
   follow the same steps. First, because it moves EVN most and every future miner depends on it. Serious.
2. **New: check the engine against the company's own numbers.** Two tests. (a) The engine's FY27
   cash-flow change for A$100/oz of gold should land near the company's stated A$65-70m (FY26 results
   presentation, slide 14). (b) Run at FY26 prices, the engine should come close to FY26 actuals
   (EBITDA A$3,171m; net mine cash flow A$2,079m). Today year-1 FCFF is A$1,170m (engine Y1 is FY28; corrected 20 Oct from a stale A$1,008m, see evn_engine_vs_company_2026-10-20.md) against roughly
   A$1,400m of FY26 cash flow before interest and dividends; most of the difference looks like higher
   FY27 capital guidance and full tax, but it has not been reconciled. Medium.
3. **New: costs do not move with the gold price.** Only the royalty does. In practice mine costs
   (labour, contractors, cut-off grades) rise when gold is high and ease when it falls, so margins
   swing less than the model shows. This matters more once the paths are re-centred. Needs evidence
   first (EVN's own AISC against gold over several years). Pair it with item 4. Medium.
4. **Industry cost curve (gap 4).** An average and 90th-percentile AISC from a primary source (World
   Gold Council or S&P), so the "lowest-cost quartile" claim is measured. Data sourcing, possibly for
   Ben's workstream. Medium.
5. **Name the fourth engine and the depletion disclosures in `adding_a_company.md` (gaps 1 and 7).**
   After D-96 and D-97 are ruled. The disclosures for a depleting asset are the run-off share, the life,
   and value per share on each inventory basis. Mild.
6. **EVN in the UI, workbook and session-start base tie (gap 9), with the two risk-free dates shown
   (gap 8).** Its own sitting, and only after item 1, so it is built once on settled paths. Serious.
7. **Register lint: exempt guidance tables by path (gap 10).** Mild tidy-up.

## Sources

1. Gold close US$4,156.46, 16 Oct 2026: https://goldprice.org/gold-price-today/2026-10-16
2. Gold all-time high about US$5,590, 28 Jan 2026: https://metalcharts.org/precious-metals-all-time-highs
3. Futures contango is carry, not a forecast: https://www.mitrade.com/insights/news/live-news/article-2-2015333-20260820
4. Australian 10-year 5.23%, 15 Oct 2026: https://tradingeconomics.com/australia/government-bond-yield/news/592104
5. AUD/USD 0.6928 on 1 Oct 2026: https://www.exchange-rates.org/exchange-rate-history/aud-usd-2026-10-01
6. EVN FY26 results (EBITDA 3,171; group cash flow 1,389): data/financials/historical/evn/evn_fy26_full_year_financial_results_and_final_dividend.pdf
