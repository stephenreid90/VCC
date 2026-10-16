# Bridge note, 16 October 2026 (evening) — VCC Valuations

Paste this at the start of the next chat.

Continue the VCC Valuations model (DNL, WBC, CSL). Read `WORKING_NOTES.md` (top block, 16 Oct
evening) and `design/open_items.json` first. Repo is on my device under the vcc-valuations folder;
git is handled in the background, never ask me about it. Standing rules: every number from
committed code and pinned by a test; goldens in `tests/dcf/test_scenario_goldens.py`; sizing sets from
`scripts/size_*.py`; SSOT lint `tests/test_ssot_lint.py`; grade work mild / medium / serious; tests
in the DCF folder take about two minutes, run them in one call. Australian spelling, short plain
sentences, numbered lists, no git questions, confirm before deleting.

Where we are: D-88 to D-91 landed and pushed (last commit d97ed0a). Base ties DNL 2.006 / WBC 33.93 /
CSL 226.66. Suite green.

What to do now: run the batch plan. Hand each item to a separate agent on the model shown, one at a
time (they share one repo), brief it with the standing rules, verify its result (tests, lint,
tracker) before accepting, commit and push, then bring me only the decisions.

| # | Item | Model | Needs me? |
|---|---|---|---|
| 1 | R16-6 move level anchors to archetypes (schema, script, generator, five tests; no value change) | Sonnet | No |
| 2 | D-86 goodwill-inclusive return and sensitivity band in workbook and reports | Sonnet | No |
| 3 | Q5 close (answered by D-60) | Haiku | No |
| 4 | M6, M7, M11 workbook defects | Sonnet | No |
| 5 | M5, 21, 22, 31 UI integrity | Sonnet | No |
| 6 | 23-30, 33, 34 UI polish | Sonnet | No |
| 7 | 36, 37 backlog (print stylesheet, side-by-side) | Haiku | No |
| 8 | R16-7 terminal returns: confirm D-86 closed it | Haiku to frame | Yes |
| 9 | Item 10: CSL 93% above market, structural-reason treatment | Fable | Yes |
| 10 | M10 market price refresh (all three struck 15 Jun 2026) | Sonnet | Yes, when |
| 11 | Q4 / Q8 working-capital confirmations (DNL 13.76%, CSL about 35%) | Haiku | Yes |
| 12 | 32, 35, Q6, Q7 UI design choices | Haiku to frame | Yes |

Start with items 1 to 4. Come back to me with items 8 to 12 as one decision list.
