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
   the committed sizing set (`resource_valuation_sets.yaml`, `fy28_fcff`) both give A$1,170m.
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
2. FY26 actuals. FY26 results release (`2026-08-19 FY26 Full Year Results and Final Dividend.pdf`)
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
3. **Labelling: "Y1" is FY28.** The sizing set's `fy28_fcff` and `y1_ebitda` are FY28. Anyone
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

## FY26 actuals rerun

Added 20 October 2026, after the owner saved the FY26 Appendix 4E and financial report
(`data/financials/historical/evn/2026-08-19 FY26 Appendix 4E and Financial Report.pdf`).
Page references are PDF page, then the printed page in brackets (printed = PDF minus 2).

### What the report holds

1. **Mine-by-mine actuals: yes, mostly.** Note 1(b) "Segment information", PDF p56 (p54), gives
   each mine's revenue, segment EBITDA, sustaining, major and total capital. The Directors'
   report "Mining operations" tables, PDF p11-13 (p9-11), give each mine's gold and copper
   produced, AISC, AIC, operating mine cash flow, non-operational costs and net mine cash
   flow. **Not in the report for any mine:** D&A, royalty, site exploration, cash (C1) cost,
   mill throughput, grade, gold sold (Mungari's 186koz sold is in text only).
2. **Exploration treatment: yes.** Exploration is its own operating segment (Note 1(a), PDF p56),
   so site exploration is **not** in any mine's EBITDA, capital or operating mine cash flow.
   Policy, Note 7(c)(iii), PDF p70 (p68): capitalised by area of interest while tenure is
   current and the cost is expected to be recouped (or reserves cannot yet be assessed),
   otherwise expensed. FY26: A$12.5m expensed, on its own income-statement line below cost
   of sales (PDF p49 (p47)), and inside underlying EBITDA through "Corporate, admin,
   exploration and other costs (excluding D&A) (105,652)" (PDF p10 (p8)). A$60.0m
   capitalised (Note 7 E&E additions, PDF p67 (p65)), an investing cash flow outside the
   A$1,090m segment capital.
3. Royalties: A$186.4m "Royalty and other selling costs", group only (Note 2(e), PDF p60 (p58)).
4. Cash tax paid: A$408.6m (cash flow statement, PDF p52 (p50)). Tax expense A$712.6m.
5. Hedging: 50,000oz delivered at A$3,234/oz in FY26; "no further gold or copper hedges in
   place" (PDF p8 (p6)). The only remaining hedge is the cross-currency swap on the US$ notes.
6. Every figure, with its page and table, is in `data/financials/actuals/evn_fy26_actuals.yaml`.
   It sits in a subfolder because the lint treats every top-level YAML in `data/financials/`
   as a company financials file.

**For D-100:** rehabilitation provision at 30 June 2026 **A$583.7m** (current 6.8 + non-current
576.9; Note 14, PDF p77, printed p75). Lease liabilities at 30 June 2026 **A$35.8m** (current
15.5 + non-current 20.3; balance sheet PDF p50, printed p48; total in Note 6(c), PDF p65, printed p63).

### Method

`python scripts/check_resource_engine_vs_company.py --fy26-actuals`. One full year at FY26
achieved prices (gold A$6,023/oz, copper A$18,051/t). Per mine: FY26 gold and copper produced,
FY26 AISC, sustaining capital, major capital; Mt Rawdon included; site exploration nil (its
own segment). Corporate overheads A$93.2m and expensed exploration A$12.5m. Group D&A A$755.5m
spread per ounce (tax depends only on the total). Kept from the data files because the report
lacks them: royalty rate 3.15% (it only moves cost between the royalty and cost lines, since
AISC already holds the actual royalty), Northparkes stream cash price 10% of spot, 30% tax on
accrual. Northparkes stream share is FY26 actual: 17,151oz delivered of 27,299oz produced.
Nothing was tuned.

### Results (A$m)

1. **EBITDA 3,184 vs 3,171 underlying (+13).** Close.
2. **Net mine cash flow 2,200 vs 2,079 (+121).** The gap is the company's A$118m of one-off
   non-operational costs (Ernest Henry flood 45.4, Mungari commissioning and bought-in ore 70.5,
   other 1.6). Before those, the company's figure is 2,197: a gap of +4.
3. **Group cash flow (engine FCFF) 1,366 vs 1,389 (-23).** Close, but only because large
   items offset. Put on the company's basis (add capitalised exploration -60, working
   capital -112, interest and other income -24, the one-offs -118, and cash tax paid instead
   of accrued tax +320), the engine gives 1,371: a gap of -18.

### Remaining gaps, in plain words

1. **Northparkes stream (placement only).** Engine operating mine cash flow is A$109m below the
   company's at Northparkes. The engine takes the stream out of revenue; the company deducts
   the A$108m stream payment below operating mine cash flow. After it, the two agree
   (net mine cash flow 233.9 vs 234.5).
2. **One gold price for every mine.** The engine gives each mine the group price, A$6,023/oz.
   The company's revenue per ounce produced is A$6,208 at Cowal, A$6,335 at Red Lake, but
   A$5,469 at Mungari, which carried the 50,000oz hedge. So the engine is high at Mungari
   (+127 operating mine cash flow) and low at Cowal (-54) and Red Lake (-43). These offset at
   group level. With no hedges from FY27, this mix error goes away.
3. **Mt Rawdon (-23).** Its AISC includes non-cash stockpile drawdown; the engine treats all
   AISC as cash. Mt Rawdon closed in the September 2026 quarter, so this does not carry forward.
4. **Ernest Henry (-2) and the other mines' cost lines.** Small.
5. **Revenue is A$162m lower** than reported, but this does not reach cash flow. The engine has
   no corporate-segment metal sales (A$138m, offset by matching cost) and no silver line
   (AISC already nets silver).
6. **Tax.** Engine accrued tax 728 vs FY26 expense 713 (-16). Cash paid was only 409, because
   instalments lag profit and A$78m of Canadian tax losses were used. Timing, as the first
   backcast said.
7. **Residual -21** on the company basis, not separable from the report (the report has no
   net-mine-to-group cash flow bridge).

### What this changes in the first backcast

1. The earlier "mine exploration (-A$123m)" item was a real presentation difference: the
   company keeps site exploration out of mine cash flow. It is value-neutral (cash is cash),
   but the engine's FY27 exploration (A$123m by mine plus A$22m greenfields) is about twice
   FY26's A$72.5m cash spend (12.5 expensed + 60.0 capitalised).
2. With true FY26 inputs, **the engine maths reproduces FY26 to within about 1% at every
   level.** The large gaps in the first backcast were FY27 guidance against FY26, not engine error.

### Decision for the owner

1. Whether the FY27 exploration input (about A$145m in total) is right against FY26's A$72.5m
   cash spend. Check it against the company's FY27 exploration guidance before the next run.

### Script output (FY26 actuals)

`python scripts/check_resource_engine_vs_company.py --fy26-actuals`, 20 October 2026, tree at
`19b1abe` plus this change. (The default checks (a) and (b) are unchanged in code. Their
output has moved since the run above because D-103, at `19b1abe`, changed FY27 major capital.)

```
(c) FY26 ACTUALS RERUN: engine on FY26 mine volumes, AISC, capital and achieved prices (gold A$6,023/oz, copper A$18,051/t), one full year, A$m
  source: data/financials/actuals/evn_fy26_actuals.yaml
  inputs kept from the data files: northparkes stream cash price 10% of spot (data file; not in the report); royalty rate 0.0315 of revenue (data file; the report gives only the group total); tax rate 0.30 on EBITDA less D&A (accrual; the report gives cash tax paid)
  site exploration per mine 0.0 (Exploration is its own segment); expensed exploration 12.5; corporate 130.4 A$/oz

  mine            revenue      co.   EBITDA      co.     OMCF      co.    NMCF*     co.*   non-op
  cowal            1789.0   1844.0   1166.9   1235.6   1166.9   1220.9    797.7    851.7     -0.0
  ernest_henry     1013.1    993.5    545.0    523.7    545.0    547.1    345.7    347.8    -45.4
  northparkes       574.8    616.1    322.1    297.5    322.1    430.8    233.9    342.6   -108.1
  mungari          1121.0   1017.9    778.2    662.6    778.2    651.6    563.7    437.0    -70.5
  red_lake          765.9    805.5    457.0    501.2    457.0    500.2    243.6    286.8     -0.7
  mt_rawdon         132.9    143.3     20.5     44.1     20.5     43.8     16.0     39.3     -0.9
  * NMCF before non-operational costs (company NMCF + its non-op line); company EBITDA is statutory segment EBITDA

                                                  engine   company       gap
  revenue                                         5396.6    5558.8    -162.1
  royalty (co.: royalty and other selling)        -169.8    -186.4      16.6
  corporate + expensed exploration                -105.7    -105.7       0.0
  EBITDA (co.: underlying)                        3184.0    3171.0      13.0
  operating mine cash flow                        3289.6    3394.3    -104.7
  non-operational costs (engine: none)               0.0    -225.7     225.7
  net mine cash flow                              2200.5    2079.0     121.5
  tax (co.: income taxes paid)                    -728.5    -408.6    -320.0
  tax (co.: income tax expense, accrual)          -728.5    -712.6     -16.0
  group cash flow (engine: FCFF)                  1366.3    1389.0     -22.7

  items the engine has no input for (FY26, A$m, from the actuals file):
  capitalised exploration (E&E additions)          -60.0
  corporate capital                                 -1.1
  working capital change (Note 6(a))              -112.3
  D&A used for engine tax (group, p57)            -755.5
  net interest + other income received (p52)       -24.0
  tax paid less engine accrued tax                 320.0
  non-op costs other than the stream payment      -117.6
  net mine cash flow, co. before those one-offs    2200.5    2196.6       3.9
  engine FCFF on the company's basis              1371.4    1389.0     -17.6
    of which Northparkes OMCF (stream placement)    -108.7
    stream payment, company below OMCF             108.1
    of which other five mines' OMCF                  4.1
    of which other, not separable                  -21.0

  company revenue per gold ounce produced, gold-only mines (engine uses one group price):
    cowal        A$6,208/oz
    mungari      A$5,469/oz
    red_lake     A$6,335/oz
    mt_rawdon    A$6,494/oz
```
