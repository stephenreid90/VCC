# Bridge note, 16 October 2026 (late evening) -- VCC Valuations

`WORKING_NOTES.md` is the authoritative statement of where things are. This note is a snapshot.

Paste this at the start of the next chat.

Continue the VCC Valuations model (DNL, WBC, CSL). Read WORKING_NOTES.md (top block, including "Batch 1 progress" and Stephen's rulings) and design/open_items.json first. Repo is on my device under the vcc-valuations folder; git is handled in the background, never ask me about it. Standing rules: every number from committed code and pinned by a test; goldens in tests/dcf/test_scenario_goldens.py; sizing sets from scripts/size_*.py; SSOT lint tests/test_ssot_lint.py; grade work mild / medium / serious; the DCF test folder takes about two minutes, run it in one call. Australian spelling, short plain sentences, numbered lists, confirm before deleting.

Where we are: batch 1 (items 1 to 4) landed, plus R16-7 closed and D-92 / D-93 ruled. Last commit e532a3e, pushed. Base ties DNL 2.006 / WBC 33.93 / CSL 211.15 (CSL moved under D-93: moat band 15-25 years, midpoint 20). Suite green (DCF 428 / other 331 / lint 14).

Decisions already made, do not reopen: no market price refresh, the 15 June prices stand and the gap is disclosed not reconciled (D-92); CSL fade 20 years (D-93); CSL segment anchors stay in csl.yaml as the declared exception; Q4 13.76% and Q8 35% confirmed; Q6 option b; Q7 placeholder tabs after Ben's feed; item 35 after item 10.

What to do now: batch 2, one agent at a time, verify each (tests, lint, tracker) before accepting, commit and push, bring me only decisions.

| # | Item | Model | Needs me? |
|---|---|---|---|
| 1 | Item 10: write the section 16.3 note (assumptions that differ, the D-63 band, no reconciliation) | Sonnet | No |
| 2 | D-42 warning wording: quote the governing return, not the new-capital figure | Haiku | No |
| 3 | M5, 21, 22, 31 UI integrity; also the CSL prototype DCF build-up (hand-typed 203.83) and the 105.53 in CSL prose | Sonnet | No |
| 4 | 23-30, 33, 34 UI polish, and Q6 option b (item 24) | Sonnet | No |
| 5 | 36, 37 backlog (print stylesheet, side-by-side) | Haiku | No |
| 6 | 32 / Q7 placeholder tabs | Haiku | Waits on Ben's feed |
