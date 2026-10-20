# Bridge note, 20 October 2026 (late afternoon): EVN review done, batch 3 next

**This is a snapshot. `WORKING_NOTES.md` is the live record and wins where they differ.**

Read first: `CLAUDE.md`, then the top of `WORKING_NOTES.md` (the 20 Oct EVN blocks), then
`DECISIONS.md` D-94 to D-102, then `design/methodology/resource_lifecycle_and_mining_drivers.md`.

## Where we are

1. EVN (Evolution Mining) is built on the fourth engine. Rulings 20 Oct: D-94, D-95, D-96, D-97,
   D-98 (with E22 excluded, not yet implemented), D-99 (revised gold and copper paths), D-100,
   D-102 (commodity price principles; consensus shown as a scenario or option when available).
   D-101 (beta) is HELD until observed betas exist; 0.90 is the working figure.
2. EVN levels (A$/share): OC 4.88, MT 6.47, AI Lag 7.40, Frag 10.10, DCC 7.04, Stag 9.74, against
   A$12.09. Market needs the MT gold path x1.45.
3. Review page: Dashboard artifact "EVN Valuation Review", fed by
   `scripts/build_resource_review_data.py`. Rerun it and re-upload the files after any change.
4. Stephen agreed the gap order and the PDF renames (show the rename plan first).

## Batch 3: how to run it (Stephen asked to multitask)

Work that moves EVN numbers goes one at a time; the rest runs in parallel. Each agent works on its
own branch or worktree, is verified before it is accepted, and only decisions come back to Stephen.

Parallel lane (no numbers move):
1. **Engine vs company checks** (Opus, medium). Two tests: (a) FY27 cash flow change for A$100/oz
   gold vs the company's A$65-70m (FY26 results presentation slide 14); (b) the engine at FY26
   prices vs FY26 actuals (EBITDA 3,171; net mine cash flow 2,079; group cash flow 1,389). Explain
   any gap; do not tune the model to close it.
2. **Cost vs gold evidence** (Sonnet, research only). EVN's AISC and achieved gold price by year from
   the annual reports in `data/financials/historical/evn/`; measure how much cost has moved with
   gold. Bring back a proposed rule, not code.
3. **Tidy-ups** (Haiku, mild). Register lint: exempt guidance tables by path (gap 10).
   `adding_a_company.md`: name the resource engine and the miner disclosures (gaps 1 and 7).
   PDF rename plan for the twelve EVN files: show the plan to Stephen before renaming.

Serial lane (numbers move, one at a time):
4. **E22 out of capital and volume** (Sonnet, medium). Find E22's share of Northparkes' FY27
   major project capital in the documents; remove it from the run-off; disclose it as excluded.
   Re-pin set `evn`, goldens and the review page.
5. **Cost-price link** (Opus, serious), only after item 2's rule is ruled by Stephen.

For Stephen to supply: the FY26 annual report (rehabilitation and leases, D-100).
For Ben: observed betas for EVN and five peers (D-101); an industry cost curve; a consensus
commodity feed (D-102).

## The UI

The review page is enough to look at EVN now. The full company interface (gap 9, serious, its own
chat) should be built after items 1 and 4 land, so it is built once on checked numbers. It should
match the DNL/WBC/CSL pages and read precomputed engine output (D-23), with commodity sliders taken
from a grid like the review page.
