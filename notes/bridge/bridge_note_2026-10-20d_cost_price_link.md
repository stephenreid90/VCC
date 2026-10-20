# Bridge note, 20 October 2026 (evening): batch 3 landed, next is the cost-price link (D-104)

**This is a snapshot. `WORKING_NOTES.md` is the live record and wins where they differ.**

Read first: `CLAUDE.md`, then the top of `WORKING_NOTES.md` (the 20 Oct BATCH 3 block), then
`DECISIONS.md` D-98 to D-104, then `design/methodology/evn_cost_vs_gold_evidence_2026-10-20.md`
and `design/methodology/resource_lifecycle_and_mining_drivers.md`.

## Where we are

1. Batch 3 is landed on main (commits 809c717 to 0003d3b, pushed). EVN levels (A$/share): OC 4.99,
   MT 6.57, AI Lag 7.51, Frag 10.21, DCC 7.15, Stag 9.85, against A$12.09; gold multiple 1.44.
2. Ruled today: D-103 (E22 out of capital and volume by the A$545M/5-year allocation rule, implemented)
   and D-104 (cost-price link rule, NOT yet implemented). D-100 updated from the FY26 financial report.
   D-101 (beta) still held for observed betas.
3. Engine checks against the company pass: gold sensitivity +A$66m per A$100/oz (company 65-70); true
   FY26 backcast within about 1% at every level. `scripts/check_resource_engine_vs_company.py`.
4. Engine year 1 is FY28 (FY27 is the stub). Sizing-set keys are `fy28_*`.
5. Review page "EVN Valuation Review" (claude.ai/artifact/4RgKRBZewHUADMjEokSJmV) refreshed to 0003d3b.

## Next sitting: cost-price link (serious, Opus or Fable, its own chat)

D-104: non-royalty real unit costs (cash cost plus sustaining capital) move 1.5% for each 10% real move
in the primary commodity price, one-year lag, cap 20% above the base cost path, symmetric. Range 0.5-3.0%
as a sensitivity. Royalties stay as modelled. Build it in `resource_engine.py` / `resource_translator.py`
as an archetype-level parameter (no company name in code), with the elasticity, lag and cap declared in
the gold_producers archetype and overridable per company; add tests; re-pin set `evn`, goldens, review
page; write the method into `resource_lifecycle_and_mining_drivers.md`; show the before/after levels and
the 0.5% and 3.0% sensitivities. Expect Orderly Convergence to rise and the high-gold scenarios to fall.

After that: gap 9 (EVN in the main prototype UI, serious, its own chat).

For Ben: observed betas for EVN and five peers (D-101); an industry cost curve; a consensus commodity feed.
