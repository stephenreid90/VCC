# EVN: do mine costs move with the gold price? Evidence note, 20 October 2026

Research only. No model change. Answers the "known gap" in `evn_review_2026-10-20.md` section 3 item 3 and DECISIONS.md D-102: costs move with CPI (consumer price index, general inflation) plus a scenario escalator, but not with the gold price.

## 1. Bottom line

1. Over FY22 to FY26 the achieved gold price rose 148%. Reported AISC rose 36%. AISC is all-in sustaining cost: cash cost, plus royalties, sustaining capital and head-office cost, per ounce sold.
2. Take out royalties and the rise is 28%. That is an elasticity of about 0.2 to 0.3 (elasticity = percentage change in cost for each 1% change in price). This is in nominal dollars. It still includes general inflation and mine-mix changes, so the pure gold-price effect is lower.
3. Royalties are fully price-linked, as the model already assumes. Royalty and selling costs held at 3.3% to 3.6% of revenue in every year (section 4).
4. The reports hold only FY22 to FY26. FY19 to FY21 are NOT FOUND (section 6).
5. There are only five annual points, and the gold price rose in every year. The evidence cannot say what happens when the price falls.

## 2. Table: group gold, price and unit costs

All A$. "Sold" oz is the base for AISC. Page numbers are PDF page numbers (the printed page can differ by one or two). File abbreviations: AR23, AR24, AR25 = `2023-08-17 Annual Report FY23.pdf`, `2024-08-14 Annual Report FY24.pdf`, `2025-08-13 Annual Report FY25.pdf`; JQ = `2026-07-15 Quarterly Report Jun 2026.pdf`.

| Item | FY19 | FY20 | FY21 | FY22 | FY23 | FY24 | FY25 | FY26 |
|---|---|---|---|---|---|---|---|---|
| Gold produced (oz) | NOT FOUND | NOT FOUND | NOT FOUND | 640,275 | 651,155 | 716,700 | 750,512 | 714,728 (692,661 continuing ops) |
| Gold sold (oz) | NOT FOUND | NOT FOUND | NOT FOUND | 641,413 | 647,999 | 718,224 | 748,752 | 709,541 (687,324 continuing ops) |
| Achieved gold price ($/oz) | NOT FOUND | NOT FOUND | NOT FOUND | 2,425 | 2,592 | 3,190 | 4,300 | 6,023 (6,017 continuing ops) |
| AISC ($/oz sold) | NOT FOUND | NOT FOUND | NOT FOUND | 1,259 | 1,450 | 1,477 | 1,653 (1,572 continuing ops) | 1,717 (continuing ops) |
| C1 cash cost ($/oz) | NOT FOUND | NOT FOUND | NOT FOUND | 864 | 937 | 837 | 1,013 | 914 (per sold oz) |
| Royalty and selling costs ($000) | NOT FOUND | NOT FOUND | NOT FOUND | 68,072 | 72,627 | 116,288 | 156,089 | royalties only: 242 $/sold oz |
| Sustaining capital ($000) | NOT FOUND | NOT FOUND | NOT FOUND | 147,057 | 198,049 | 209,006 | 222,897 | 339 $/sold oz (about 239M) |
| Copper produced (t) | NOT FOUND | NOT FOUND | NOT FOUND | 38,834 | 47,348 | 67,862 | 76,261 | 65,636 |
| Achieved copper price ($/t) | NOT FOUND | NOT FOUND | NOT FOUND | 12,546 | 12,500 | 13,657 | 14,470 | 18,051 |

C1 cash cost = what it costs to mine, process and sell an ounce, after copper and silver by-product credits (copper and silver sold alongside the gold, counted as a cost offset).

Sources for each figure:

1. FY22 and FY23 production, C1, AISC, prices, revenue, sustaining capital: AR23 p97, "Key Business Metrics" table (FY23 and FY22 columns). FY22 production 640,275 and FY22 copper 38,834 are in the same table. Sold ounces: AR23 p98, "increase in sold ounces for the year to 647,999oz (30 June 2022: 641,413oz)".
2. FY22 and FY23 royalty and selling costs: AR23 p117, cost of sales note, "Royalty and other selling costs 72,627 68,072" (FY23, FY22).
3. FY24 production, C1, AISC, prices, sustaining capital: AR24 p135, "Key Business Metrics" ("Cash (C1) operating cost 837", "All in sustaining cost 1,477", "Gold price achieved 3,190", sustaining capital 209,006). Sold ounces: AR24 p139, "718,224oz". FY24 royalty and selling costs 116,288: AR25 p75, cost of sales note, comparative column.
4. FY25 production, C1, AISC, prices: AR25 p33, "Key Business Metrics": "Gold production 750,512", "Cash (C1) operating cost 1,013", "All in sustaining cost 1,653", "Gold price achieved 4,300". Sold ounces 748,752: AR25 p37. Royalty and selling costs 156,089: AR25 p75. Sustaining capital 222,897 (excludes $3.9M corporate): AR25 p33.
5. FY25 AISC of 1,572 on a continuing basis (excludes Mt Rawdon, which stopped mining in FY25): AR25 p4 highlights and its footnote 1; also AR25 p5, "sector leading AISC of $1,572 per ounce". The 1,653 includes Mt Rawdon (AISC 3,121 $/oz, AR25 p36).
6. FY26: JQ Appendix 2 (pages 11 and 12): "Gold produced oz ... 714,728", "Achieved gold price $/oz ... 6,017 6,023", "C1 Cash Cost $/sold oz ... 914", "Royalties $/sold oz ... 242", "Sustaining capital $/sold oz ... 339", "All-in Sustaining Cost $/sold oz ... 1,717". The AISC, C1, royalty and sustaining capital rows have no Mt Rawdon column, so they are continuing-operations figures. By-product credits: "(1,867)" $/produced oz. Corporate G&A (head office cost) 186 $/sold oz.
7. The FY26 AISC bridge adds up: 914 + 242 - 10 + 339 + 46 + 186 = 1,717 (C1, royalties, metal-in-circuit adjustment, sustaining capital, reclamation, corporate).

Not like for like: the "royalty and selling costs" for FY22 to FY25 come from the accounts and include selling costs and copper royalties. The FY26 242 $/oz is royalties only. NOT FOUND: a royalty-only figure for FY22 to FY25 (the annual reports do not split it).

## 3. Elasticity of AISC to the achieved gold price

Method: percentage change in AISC divided by percentage change in price. A "log" version uses natural logs and is less sensitive to big moves. All figures are nominal (not adjusted for CPI).

| Step | Price | AISC | Elasticity (simple / log) |
|---|---|---|---|
| FY22 to FY23 | +6.9% | +15.2% | 2.20 / 2.12 (distorted, see section 5 item 1) |
| FY23 to FY24 | +23.1% | +1.9% | 0.08 / 0.09 |
| FY24 to FY25 | +34.8% | +11.9% | 0.34 / 0.38 |
| FY25 to FY26 (like for like, 1,572 to 1,717) | +40.1% | +9.2% | 0.23 / 0.26 |
| FY25 to FY26 (mixed basis, 1,653 to 1,717) | +40.1% | +3.9% | 0.10 / 0.11 (not recommended: Mt Rawdon drop-out flatters it) |
| Whole span FY22 to FY26 | +148.4% | +36.4% | 0.25 / 0.34 |
| FY23 to FY26 (skips the FY23 flood year) | +132.4% | +18.4% | 0.14 / 0.20 |

## 4. Royalty split

Royalty and selling costs as a share of revenue (revenue from the same key-results tables):

1. FY22: 68,072 / 2,064,928 = 3.30%. FY23: 3.26%. FY24: 3.62%. FY25: 3.59%.
2. Per sold ounce: FY22 106, FY23 112, FY24 162, FY25 208, FY26 242 (royalties only). That is +128% against a price rise of +148%, an elasticity of about 0.86 (log 0.91). Royalty is therefore already close to a fixed share of price, which supports the model treating it as price-linked.

AISC with royalty removed (AISC minus royalty per sold ounce):

| | FY22 | FY23 | FY24 | FY25 | FY26 |
|---|---|---|---|---|---|
| AISC ex-royalty ($/oz) | 1,153 | 1,338 | 1,315 | 1,445 | 1,475 |

| Step | Price | Ex-royalty AISC | Elasticity (simple / log) |
|---|---|---|---|
| FY22 to FY23 | +6.9% | +16.1% | 2.33 / 2.24 (flood-distorted) |
| FY23 to FY24 | +23.1% | -1.7% | -0.07 / -0.08 |
| FY24 to FY25 | +34.8% | +9.8% | 0.28 / 0.31 |
| FY25 to FY26 (mixed basis; see snippet for like for like) | +40.1% | +2.1% | 0.05 / 0.06 |
| FY25 to FY26 (like for like, 1,572 - 208 to 1,717 - 242) | +40.1% | +8.1% | 0.20 / 0.23 |
| Whole span FY22 to FY26 | +148.4% | +27.9% | 0.19 / 0.27 |
| FY23 to FY26 | +132.4% | +10.2% | 0.08 / 0.12 |
| C1 cash cost only, FY22 to FY26 | +148.4% | +5.8% (864 to 914) | 0.04 / 0.06 |

Reading: after royalties, unit costs rose a small fraction of the price rise. C1 barely moved, partly because copper by-product credits grew with the copper price (see section 5).

## 5. Confounders (things that move cost other than gold price)

1. Ernest Henry weather event in FY23. Ernest Henry gold fell from 85,145 oz to 64,725 oz and its AISC went from (1,680) to (2,334) (AR23 p97 and p98, "AISC was impacted"). That is why FY22 to FY23 shows a cost jump in a small price year. Treat that step as noise.
2. Mine mix. Northparkes was acquired on 16 December 2023 (AR25 p35, "period from 16 December 2023"), so FY24 holds only about half a year and FY25 the first full year. Northparkes has a large negative AISC ((2,514) in FY25, (8,314) in FY26) because of copper credits, which pulls the group figure down. Mt Rawdon (high AISC, 3,121 in FY25) stopped mining in FY25, which lowers FY26 group AISC. Cowal underground ramp-up (FY24 start, AR25 p34) and the Mungari mill expansion (AR25 p36) also change mix. Red Lake is in every year shown. The date Red Lake was acquired is NOT FOUND in the saved files, and it is before FY22 anyway.
3. Copper by-product credits. Group credits were (1,867) $/produced oz in FY26 (JQ App 2). Copper price rose from 12,500 $/t (FY23) to 18,051 $/t (FY26) and copper tonnes rose from 47,348 to 65,636. Higher copper lowers reported AISC, so the AISC elasticities above are understated against gold-only cost. By-product credits for FY22 to FY25: NOT FOUND. A copper-free AISC cannot be built from these files without estimating.
4. General inflation. The reports say costs rose with "labour costs linked to inflation and market conditions, as well as higher maintenance consumable costs and royalties" (AR25 p37). A CPI series is NOT FOUND in the saved EVN files, so the nominal elasticities above are an upper bound on the real response. Stephen needs to supply the CPI series, or the model's own CPI history, to finish the real calculation. The snippet has a slot for it.
5. Grade and throughput. Grade by year for the group is NOT FOUND in these files. AR25 p36 says Mt Rawdon AISC rose because of lower head grades; JQ App 2 gives FY26 grades by mine only. Lower grade raises cost per ounce regardless of price. Higher gold price also lets miners mine lower grades (lower cut-off grade), which raises cost per ounce. That is a real price-linked channel, and this data cannot separate it.
6. Basis. FY25 AISC is 1,653 (all operations) or 1,572 (continuing). FY26 is continuing only. The like-for-like step uses 1,572.
7. Hedging. EVN delivered into hedges at below-spot prices in FY23 to FY26 (for example 50,000 oz at $3,140 in FY25, AR25 p37), so achieved prices rose a little less than spot. This slightly raises the measured elasticity.

## 6. What the reports do not hold

1. FY19 to FY21: no group table in the three annual reports or FY26 documents. The 2026 results slides have FY19 to FY26 axes, but only for dividends and gearing (FY26 results presentation, slide 8). The investor briefing AISC chart starts at FY22 (slide 8).
2. FY22 to FY25 royalty-only figures, by-product credits, grade, and CPI.
3. FY26 comparative detail on royalty and selling costs from the accounts (Appendix 4E and the FY26 annual report are not saved).

## 7. Arithmetic (reproduce)

```python
from math import log
yrs = ['FY22','FY23','FY24','FY25','FY26']
px   = dict(FY22=2425, FY23=2592, FY24=3190, FY25=4300, FY26=6023)   # achieved gold price A$/oz
aisc = dict(FY22=1259, FY23=1450, FY24=1477, FY25=1653, FY26=1717)   # A$/oz sold
sold = dict(FY22=641413, FY23=647999, FY24=718224, FY25=748752)
roy_acct = dict(FY22=68072, FY23=72627, FY24=116288, FY25=156089)    # A$000, royalty and selling costs
roy_oz = {k: roy_acct[k]*1000/sold[k] for k in roy_acct}; roy_oz['FY26'] = 242   # FY26 royalties only
cpi = None   # NOT FOUND in the saved files; fill with an annual index to get the real response

def pc(a, b): return 100*(b/a - 1)
def el(p0, p1, c0, c1): return pc(c0, c1)/pc(p0, p1), log(c1/c0)/log(p1/p0)

ex = {k: aisc[k] - roy_oz[k] for k in yrs}                        # AISC ex-royalty
for a, b in zip(yrs, yrs[1:]):
    print(a, b, 'AISC', el(px[a], px[b], aisc[a], aisc[b]), 'ex-roy', el(px[a], px[b], ex[a], ex[b]))
print('whole span AISC', el(px['FY22'], px['FY26'], aisc['FY22'], aisc['FY26']))
print('whole span ex-roy', el(px['FY22'], px['FY26'], ex['FY22'], ex['FY26']))
print('FY23-26 ex-roy', el(px['FY23'], px['FY26'], ex['FY23'], ex['FY26']))
# like for like FY25 to FY26 (continuing ops): FY25 AISC 1,572
print('FY25-26 cont. AISC', el(4300, 6023, 1572, 1717))
print('FY25-26 cont. ex-roy', el(4300, 6023, 1572-roy_oz['FY25'], 1717-242))
print('royalty/oz', el(px['FY22'], px['FY26'], roy_oz['FY22'], roy_oz['FY26']))
```

## 8. Proposed rule (for decision; not code)

Rule: each year, non-royalty unit costs (cash cost and sustaining capital per ounce, before the copper credit) move by X% for each 10% move in the real gold price, measured against the prior year's real price, with a one-year lag, and capped at Y% above the CPI-plus-escalator cost path.

1. X, the response: 1.5% for each 10% real move (elasticity 0.15). Range 0.5% to 3.0% (elasticity 0.05 to 0.30).
2. Why that range. The nominal ex-royalty elasticity was 0.19 to 0.27 over the whole span, 0.08 to 0.12 from FY23, and 0.20 to 0.23 in the cleanest recent step. CPI is still inside those numbers, so the real response is lower, hence a central value below the whole-span figure. The 3.0% upper end allows for the FY24 to FY25 reading (0.28 to 0.31), which includes the Northparkes mix change.
3. Lag: one year. FY23 to FY24 showed no cost response to a 23% price rise, and the cost rise came the next year (FY24 to FY25). Two points do not prove a lag, so treat one year as a working choice. Range: 0 to 2 years.
4. Cap Y: costs no more than 20% above the base cost path. At 1.5% per 10% this cap would only bind after a real price rise of about 130%. It is a safety limit, not an evidence-based number.
5. Apply to what: cash cost and sustaining capital only. Royalty stays on its own price link. Copper credits stay on the copper price path.
6. Falling prices: apply the same response, but see choice 2 below.

## 9. What the evidence cannot settle

1. Direction. The gold price rose in every year. Nothing here shows whether costs fall back when the price falls. Mining theory says they are sticky on the way down (contracts, wage settlements, mines run lower grade).
2. Real versus nominal. No CPI in the files, so the "real" response is unmeasured.
3. Separation from copper credits, grade and mine mix. Group figures blend all of these.
4. Size at much higher prices. Group price is now around 2.5 times FY22. Outside this range the 0.15 is an extrapolation.
5. FY19 to FY21 (the earlier cycle) are not in the files. Adding them would give a longer run and the gold price in FY20 to FY21 moved sharply, so they are worth sourcing from EVN's older results releases.

## 10. Choices for the owner

1. Which X to use: 1.5% central, or a more cautious 0.5% (almost no link) or 3.0% (strong link). A higher X lowers value in every scenario with a gold price above spot.
2. Whether the response is symmetric. Costs that rise with the price and then fall when it falls (symmetric) are neutral. Costs that rise and stay up (sticky downward) are harsher on the Orderly Convergence path (gold down 10% real). The evidence is silent, so this is judgement.
