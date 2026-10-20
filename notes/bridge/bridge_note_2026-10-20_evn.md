# Bridge note, 20 Oct 2026: start Evolution Mining (EVN), the first miner

This is a travelling snapshot. `WORKING_NOTES.md` is the live layer and wins where they disagree. Read it first, then this.

## Prompt for the new chat

Continue the VCC Valuations model. Read WORKING_NOTES.md (top block, 20 Oct entries) and notes/bridge/bridge_note_2026-10-20_evn.md first, then design/architecture.md (archetype taxonomy, the resource_lifecycle overlay at the §7 overlays) and DECISIONS.md. Repo is on my device under the vcc-valuations folder; git is handled in the background, never ask me about it. Standing rules: every number from committed code and pinned by a test; goldens in tests/dcf/test_scenario_goldens.py; sizing sets from scripts/size_*.py; SSOT lint tests/test_ssot_lint.py; grade work mild / medium / serious; the DCF test folder takes about two minutes, run it in one call. Australian spelling, short plain sentences, numbered lists, confirm before deleting.

Where we are: last commit 72a3cd2, pushed, suite green (DCF 445 passed / 1 skipped, other 370, lint 14/14). Base ties DNL 2.006 / WBC 33.93 / CSL 211.15. Batch 2 complete except item 32 (Ben's feed). CSL thesis v3 and the CSL beta workbench on the WACC landed today. GitHub Actions is green again (the pages are built in tests/conftest.py).

Decisions made, do not reopen: D-92 (no price refresh), D-93 (CSL fade 20 years), D-84 (CSL on a WACC), D-86 (one terminal rule for every company: earned return, fade over the moat band), D-71 (ten-year explicit period, excess-return convergence then Gordon).

New work: Evolution Mining (ASX:EVN), gold, the first miner and the first use of the resource_lifecycle overlay (architecture.md names it, schema "TBD when first used"). Serious; Fable or Opus. I have saved the source documents under data/financials/historical/evn/ and any feed exports under data/financials/ (evn_*). Survey those folders before concluding anything is missing.

Order of work: (1) a methodology paper in design/methodology/ for the resource_lifecycle overlay and the mining archetype's driver set (volume, realised price, AISC and cost-curve placement, reserve life and replacement rate, jurisdiction, stranded-asset path), and how a finite mine life sits with the D-71/D-86 terminal; bring me the decisions it raises before building. (2) The industry file data/industries/ for the gold archetype. (3) The company file and the engine. Build from the industry level up, as the architecture says; do not back-fill the archetype from the company.

Questions for me before step 1 is written: price date (15 June 2026 like the others, or a fresh date under its own decision); whether Ben pulls the EODHD fundamentals and price series or we use what I downloaded; functional currency (USD revenue, AUD costs).

## Known gaps carried over (not EVN)
1. Item 32 and the DNL market price date wait on Ben's feed.
2. DNL and WBC theses are stale (DNL v3 says 2.83, engine 2.006; WBC v3 is from June). Each is its own sitting, same pattern as the CSL thesis v3 (sizing set plus pinned text).
3. CSL reverse-DCF figures withdrawn until rerun under the WACC (mild).
