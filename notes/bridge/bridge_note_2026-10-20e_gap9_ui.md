# Bridge note, 20 October 2026 (late): cost-price link landed, next is gap 9 (EVN in the main UI)

**This is a snapshot. `WORKING_NOTES.md` is the live record and wins where they differ.**

Read first: `CLAUDE.md`, then the top of `WORKING_NOTES.md` (the 20 Oct COST-PRICE LINK block), then
`DECISIONS.md` D-102 to D-104, then `design/methodology/resource_lifecycle_and_mining_drivers.md`
§2 D-104 and §6 gap 9.

## Where we are

1. D-104 is implemented and on main. EVN levels (A$/share): OC 5.07, MT 6.57, AI Lag 7.47, Frag 10.02,
   DCC 7.19, Stag 9.72, against A$12.09; gold multiple 1.48.
2. The five build choices under D-104 (linear form, scenario period-0 reference, unscaled spot for the
   market-implied path, real A$ price, cash cost and sustaining capital only) were confirmed by Stephen
   on 20 Oct. Settled; do not reopen.
3. The review page "EVN Valuation Review" (claude.ai/artifact/4RgKRBZewHUADMjEokSJmV) carries the
   re-pinned row files.

## Next sitting: gap 9 (serious, its own chat)

EVN in the main prototype UI (`ui_prototypes/_generator/`). The generator is built around the three
going-concern engines (D-23: no JS port, so the page must read engine output). Needs: an EVN entry in the
build config, the resource engine's output shape mapped to what the page reads, the D-62 disclosures
replaced by the run-off share, life and value per inventory basis (paper §6 gap 7), and the two
risk-free dates said on the cross-company view (gap 8).

For Ben: observed betas for EVN and five peers (D-101); an industry cost curve; a consensus commodity feed.
