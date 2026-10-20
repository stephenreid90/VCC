# EVN: the resource engine against the company's own numbers, 20 October 2026

Review item: `design/methodology/evn_review_2026-10-20.md` §3 item 2. Every model figure below
comes from `scripts/check_resource_engine_vs_company.py` (standing rule 4). Its full output is
at the end of this note. Nothing was tuned to close a gap.

## Summary

1. **Gold sensitivity: passes.** A$100/oz more gold lifts the engine's FY27 operating cash
   flow by A$66m. The company says A$65-70m. After 30% tax the engine's change is A$46m.
2. **Backcast: explained, not a defect.** At FY26 prices the engine gives EBITDA A$2,903m
   (company A$3,171m), net mine cash flow A$1,675m (A$2,079m) and group cash flow A$879m
   (A$1,389m). Each gap traces to a named cause. The two big ones are higher FY27 capital
   (A$286m) and full accrued tax against FY26's lagged cash tax (A$241m).
3. **A stale figure in the review.** The review says year-1 FCFF is A$1,008m. The engine and
   the committed sizing set (`resource_valuation_sets.yaml`, `y1_fcff`) both give A$1,170m.
   Also, the engine's "Y1" is FY28, not FY27. FY27 is the stub period (20 Oct 2026 to
   30 Jun 2027). The review compared an FY28 figure with FY26 actuals.

## Sources quoted

1. Gold sensitivity. FY26 results presentation, slide 14 ("Cost drivers and sensitivities"),
   PDF page 15: "FY27 cash flow sensitivities (A$M) ... Gold price (+/- $100/oz) 65-70".
   The same table is on slide 9 (PDF page 10), beside the chart "Operating mine cash flow
   ($B)", with footnote 3: "FY27 cash flow estimate based on Group guidance midpoint at spot
   prices ~A$6,200/oz (gold)". The slide does not define the measure further. The placement
   says it is **operating mine cash flow**: after royalty and site costs, before capital,
   corporate costs and tax. The arithmetic agrees (about 690koz x A$100, less royalty).
2. FY26 actuals. FY26 results release (`evn_fy26_full_year_financial_results_and_final_dividend.pdf`)
   p2 table: "Underlying EBITDA $M 3,171", "Operating mine cash flow $M 3,394", "Net mine
   cash flow $M 2,079", "Group cash flow4 $M 1,389". Footnote 4: "Cash flow before
   dividends, debt repayments, equity raises and any acquisitions or divestments." Page 1:
   "Record Group cash flow of $1,389 million". Presentation slide 15 repeats all three.
3. The FY26 bridge lines (sustaining, major capital, non-operational, stream delivery,
   corporate and discovery, interest, working capital, tax paid) are from the June 2026
   quarterly report, p4, "Group cash flow ($M)" table, FY26 column.

## (a) Gold sensitivity

1. Method. Add A$100/oz to every period of the Muddle Through gold path (the same as
   US$100 times the scenario AUD/USD in each year). Read the change in FY27.
2. Result (A$m): revenue +68.1, royalty -2.1, operating cash flow and EBITDA +66.0,
   tax -19.8, FCFF +46.2. FY28 is the same, because nothing else moves with gold.
3. Why revenue is A$68m, not A$70m: 695koz of FY27 gold less 14.2koz of Northparkes stream
   ounces that Triple Flag takes at 10% of spot.
4. Gap to the company: none. A$66m sits inside A$65-70m. The company's figure is pre-tax;
   the engine's after-tax FCFF change (A$46m) is the one the valuation uses.
5. Caveat. This only tests revenue, royalty and stream. In the engine no cost moves with
   gold (review item 3). The company's range may hold a little of that too; this check
   cannot tell.

## (b) Backcast at FY26 prices

1. Inputs. The data files hold FY26 achieved prices (gold A$6,023/oz, copper A$18,051/t,
   `royalties_fy26`) but **not** FY26 mine-by-mine volumes, costs or capital. So the run
   uses FY27 guidance midpoints for those, at FY26 prices. It is "FY27 at FY26 prices", not
   a true FY26 rerun.
2. Results against the company (A$m): EBITDA 2,903 vs 3,171 (gap -268); operating mine
   cash flow 3,050 vs 3,394 (-344); net mine cash flow 1,675 vs 2,079 (-404); group cash
   flow (engine FCFF) 879 vs 1,389 (-510).

### Why operating mine cash flow is A$344m lower

1. Stream (-A$82m). The engine takes the stream out of revenue. The company shows it lower
   down as "stream delivery" (A$108m). It is a placement difference.
2. Mt Rawdon (-A$44m). It earned A$44m in FY26 and closed in the September 2026 quarter.
3. Unit cost (-A$101m). FY27 guidance costs are higher than FY26. The engine's FY27
   all-in sustaining cost works out at A$1,943/oz against A$1,717/oz achieved in FY26.
4. Volume (-A$63m). FY27 guidance is 695koz of gold; FY26 sold 709.5koz.
5. Mine exploration (-A$123m). The engine charges site exploration here. The saved
   documents do not say whether the company's operating mine cash flow does, or whether it
   capitalises some of it. Unconfirmed.
6. Residual (+A$69m). Sold against produced ounces and items not separable from the saved
   documents.

### From operating mine cash flow to net mine cash flow (-A$404m)

1. Capital (-A$286m). FY27 guidance capital is A$1,375m (sustaining A$295m, major A$1,080m).
   FY26 actual was A$1,089m. This is capital timing: E22, Bert, Cowal and mine development
   all step up in FY27.
2. Non-operational costs (+A$118m). FY26 had one-offs (Ernest Henry flood and similar). The
   engine has none.
3. Stream (+A$108m). The company's line; the engine already took it in item 1 above.

### From net mine cash flow to group cash flow (-A$510m)

1. Corporate and discovery (-A$3m). Engine A$147m, company A$144m. Close.
2. Interest (+A$29m). Group cash flow is after net interest and other income. FCFF is before
   financing, by design.
3. Working capital (+A$109m). FY26 had a A$109m outflow. The engine has none in FY27,
   because its first period carries no change.
4. Tax (-A$241m). The engine charges 30% of EBITDA less D&A: A$650m. The company paid
   A$409m in FY26, because tax instalments lag profit and FY25 profit was much lower. Accrued
   tax on FY26's A$1,563m underlying profit is about the engine's level. FY27 cash tax will
   catch up. Timing, not a defect.
5. Hedging. None in FY27: the company says it "moved to an unhedged position at the end of
   FY26". FY26 prices already include the final hedge deliveries (Mungari's A$5,465/oz
   achieved), so the FY26 price input slightly understates spot.

### EBITDA (-A$268m)

1. The same causes as operating mine cash flow, less the A$118m of non-operational costs
   that the company's underlying EBITDA bears and the engine does not. Underlying EBITDA
   also includes non-cash stream revenue, which the engine does not model.

## Things that look like defects, not explained differences

1. **None in the engine maths.** Every gap above reconciles to a named cause.
2. **Mild: AISC is built bottom-up.** Summing the five mines' midpoints plus corporate gives
   about A$1,941/oz. The group guidance midpoint is A$1,895/oz. The mine ranges do not add
   to the group range. The engine uses the mine figures, so FY27 costs are about A$30m
   higher than the group midpoint implies.
3. **Labelling: "Y1" is FY28.** The sizing set's `y1_fcff` and `y1_ebitda` are FY28. Anyone
   comparing them with a company FY27 or FY26 figure will mis-compare. The review did.
4. **Review figure A$1,008m is stale.** It should read A$1,170m (FY28, Muddle Through).

## Decisions for the owner

1. Whether to relabel `y1_*` in `resource_valuation_sets.yaml` as FY28, or add FY27 (stub,
   annualised) figures beside them. A labelling change, not a value change.
2. Whether to ask Ben's workstream for FY26 mine-by-mine actuals, so the backcast can run on
   true FY26 inputs, and for confirmation of how the company treats site exploration in
   operating mine cash flow.

## Script output

`python scripts/check_resource_engine_vs_company.py`, 20 October 2026, tree at `841aa94`:

```
(a) GOLD SENSITIVITY: muddle_through gold path +A$100/oz in every period, A$m
  royalty rate 0.0315; tax rate 0.30; FY27 gold 695.0 koz; stream ounces sold at 10% of spot (lost value) 14.22 koz
  FY27 (stub, annualised): base gold A$5,951/oz, gold 695.0 koz
    change in revenue                               68.1
    change in royalty                               -2.1
    change in operating_mine_cf                     66.0
    change in ebitda                                66.0
    change in tax                                  -19.8
    change in fcff                                  46.2
  FY28 (engine Y1): base gold A$6,130/oz, gold 695.0 koz
    change in revenue                               68.1
    change in royalty                               -2.1
    change in operating_mine_cf                     66.0
    change in ebitda                                66.0
    change in tax                                  -19.8
    change in fcff                                  46.2
  company stated: 65-70 (FY27 cash flow, per A$100/oz)

(b) BACKCAST: FY27 guidance volumes, costs and capital at FY26 achieved prices (gold A$6,023/oz, copper A$18,051/t), A$m
  volumes: engine FY27 gold 695.0 koz, copper 66.5 kt; FY26 actual gold sold 709.5 koz, copper 65.6 kt
                                                  engine   company       gap
  revenue                                         5304.0
  royalty                                         -166.9
  operating_cost                                 -1963.8
  mine_exploration                                -123.0
  corporate_and_greenfields                       -147.1
  EBITDA                                          2903.2    3171.0    -267.8
  operating mine cash flow (pre-capex)            3050.3    3394.0    -343.7
  sustaining capital                              -295.0    -239.0     -56.0
  major capital (mine dev + project)             -1080.0    -850.0    -230.0
  non-operational costs                              0.0    -118.0     118.0
  stream delivery (engine: in revenue)               0.0    -108.0     108.0
  net mine cash flow                              1675.3    2079.0    -403.7
  corporate and discovery                         -147.1    -144.0      -3.1
  net interest + other income                        0.0     -29.0      29.0
  working capital                                   -0.0    -109.0     109.0
  tax                                             -649.5    -409.0    -240.5
  group cash flow (engine: FCFF)                   878.7    1389.0    -510.3

  operating mine cash flow gap, approximate split (A$m):
    engine AISC-equivalent A$1,943/oz; FY26 actual A$1,717/oz; FY27 guidance A$1,795-1,995/oz
  stream: engine nets it in revenue, company below     -82.3
  Mt Rawdon in FY26, closed for FY27               -44.0
  FY27 unit cost above FY26 (ex sustaining)       -101.1
  FY27 gold volume below FY26 sold                 -62.6
  mine exploration charged in engine              -123.0
  residual (sold vs produced, other)                69.4
  total gap                                       -343.7

  context: muddle_through engine Y1 (= FY28) FCFF 1169.9, EBITDA 3142.1, capex -1259.2, tax -721.2, gold A$6,130/oz
```
