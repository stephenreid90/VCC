# Bridge note, 16 October 2026 (night) -- VCC Valuations

`WORKING_NOTES.md` is the authoritative statement of where things are. This note is a snapshot.

Paste this at the start of the next chat.

Continue the VCC Valuations model (DNL, WBC, CSL). Read WORKING_NOTES.md (top block, "Batch 2 progress") and design/open_items.json first. Repo is on my device under the vcc-valuations folder; git is handled in the background, never ask me about it. Standing rules: every number from committed code and pinned by a test; goldens in tests/dcf/test_scenario_goldens.py; sizing sets from scripts/size_*.py; SSOT lint tests/test_ssot_lint.py; grade work mild / medium / serious; the DCF test folder takes about two minutes, run it in one call. Australian spelling, short plain sentences, numbered lists, confirm before deleting.

Where we are: batch 2 (items 1 to 5) landed and pushed. Last commit 557b856. Base ties DNL 2.006 / WBC 33.93 / CSL 211.15, unchanged. Suite green (DCF 439 / 1 skipped, other 358, lint 14). Item 10 is DONE (section 16.3 note: design/methodology/csl_market_gap_note_2026-10-16.md). UI items M5, 21, 22, 23, 24, 26 to 31, 33, 34, 36, 37 are DONE.

Decisions already made, do not reopen: D-92 (no price refresh, gap disclosed not reconciled), D-93 (CSL fade 20 years), CSL segment anchors stay in csl.yaml, Q4 and Q8 confirmed, Q6 option b (built), Q7 placeholder tabs after Ben's feed, item 35 after item 10 (now unblocked).

What is left:
1. Item 35: the CSL market-gap panel in the UI, content from the section 16.3 note and its set (csl_market_gap_set.yaml). Sonnet, mild. No decision needed.
2. Item 32 / Q7: placeholder explore tabs for WBC and CSL. Waits on Ben's peer feed.
3. DNL market price 3.61 has no reference date (a "Wall St target"). Needs a dated close from Ben's feed; not a tracker item yet.
4. The CSL beta workbench in the prototype still runs in cost-of-equity mode (a calculation, not a label). Decide whether to move it to the WACC. Medium.
5. The CSL thesis (analyses/csl/thesis.md) is stale: cost of equity 8.75%, "+86%", v4 workbook. A rewrite is a separate sitting. Serious.
