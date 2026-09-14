VCC VALUATIONS — bridge note for a new chat, 26 August 2026. Supersedes both 25 August notes.

READ THIS FIRST, IN THIS ORDER, AND DO NOT SKIP STEP 1.

1. The second sitting's two commits are NOT PUSHED. As of the last check `origin/main` was at `df4d96a` ("Rulings of 25 August, and the session handover"). Stephen must run `land_vcc.cmd` from a normal cmd window before any cloud clone is made — one command, it never changes, see "Landing a session" in CLAUDE.md. If you clone before that, you will fork the repo and create a merge you cannot resolve from the sandbox.
2. Then `session_start.cmd`. Then CLAUDE.md (standing rule 3 is the one about Stephen and CMD), the HANDOVER block in WORKING_NOTES.md, DECISIONS.md, and `design/methodology/horizon_and_terminal_convergence.md`.
3. Do NOT assert that data, a document, a protocol or a prior decision does not exist until you have surveyed the directory that would hold it. Curated .yaml files in data/ are SUMMARIES; raw multi-year statements live in data/financials/*.csv and data/financials/historical/<company>/.

WHAT WENT WRONG, SO IT IS NOT REPEATED. The 25 August paper's numbers all came from a scratch harness that lived in /tmp in a disposable cloud container and was never committed. The paper said "sizings from a scratch harness that reproduces FcfEngine to 1e-15" without saying where it was, because it was nowhere. The second sitting could not reproduce the work, rebuilt the harness from scratch, and landed a table about 2% away with no way to reconcile the difference. THE HARNESS IS NOW COMMITTED at `tests/dcf/harness/replica.py` with `tests/dcf/test_replica_ties_engine.py` (18 tests, floating-point equality against FcfEngine). Use it. Do not rebuild it. Suite is 288.

THE RESIDUAL IS RECONCILED — this was done from the first sitting's container before it was lost, so treat it as settled rather than re-deriving it. Two causes, no mystery:

4. The first sitting held the explicit capex path at the LIVE 7.0%. The second applied D-38 and converged it to D&A at 7.3%. That explains about three-quarters of the gap. Re-running the first sitting's harness at 7.3% gives: Orderly 3.1953, Muddle Through 2.7085, AI Lag 2.6662, Fragmentation 1.8734, Stagflation 0.5944 — within 0.39% to 1.77% of the second sitting's 3.1793 / 2.6956 / 2.6558 / 1.8629 / 0.5841.
5. The remaining ~0.5% is exactly the two terminal-boundary conventions the second sitting identified and pinned as tests: the terminal's working-capital drag is struck one year ahead of the explicit period's (a factor of 1+g), and explicit flows discount mid-year while the terminal is an end-of-year Gordon value. Their work on this is correct and should stand.
6. NOT reconciled: Disorderly Climate. The second sitting reported 1.5294; the first sitting's harness gives 1.4378 with the +1pp terminal premium and 1.6375 without, at 7.0%, so their number sits between and does not pin to either. One input is needed from the committed harness — the exact capex-arc construction and whether the terminal carries the persistent +1.0pp. Resolve this before publishing any Disorderly number.

ITEM 11 IS THE BLOCKER AND IT IS UNRULED. Three positions were put and none taken: (a) declare a Y10 target capital intensity and derive the capex path, (b) hold capital intensity flat, (c) accept the fall and disclose it as a stated judgement. The second sitting is right that this is not a rounding-level inconsistency — under the ruled build invested capital falls from 108.3% of revenue today to 67.5–85.8% at Y10, because capex converging to D&A means DNL adds no net fixed capital across ten years while revenue compounds about 50%. That thinning, not a moat, is what produces the terminal ROIC. Nobody decided it.

7. THE EVIDENCE QUESTION UNDERNEATH IT IS ANSWERED — do not re-open it as unknown. The split of DNL's nominal growth into volume and price is already computed in the chain: B25 industry volume growth and B29 industry pricing growth, per scenario. Muddle Through is 3.28% volume and 2.85% pricing. Running capital growth at volume plus asset inflation (5.86% for Muddle Through) rather than at nominal revenue growth (6.155%) gives Muddle Through 1.9551, Orderly 2.2433, AI Lag 2.0202, Fragmentation 1.1794, Disorderly 0.7128, Stagflation −0.0131.
8. What that means for the ruling: the hope that most growth is price, so capacity need not follow, does not survive. Volume is over half of it and replacement assets inflate as well, so capital has to grow at close to the nominal rate regardless. On Muddle Through the three positions land at roughly 1.77 (hold intensity flat), 1.96 (volume plus inflation) and 2.75 (the ruled build, capital thinning). The first two sit close together; the ruled one is the outlier.

STATE: suite 288 (+2 opt-in, `pytest -m libreoffice`), ratchet 12, bases unchanged 2.831 / 30.03 / 195.78. NO engine change, no production change, nothing in data/ has moved across either sitting. Everything so far is paper and test scaffolding.

RULINGS THAT ARE FIRM — DO NOT REOPEN: D-40 (DNL gas roll-off holds at −1.5pp, phasing only, concentrating FY2028–FY2030 and completing FY2032), D-41 (Disorderly capex arc: +3.0pp through Y5 decaying across Y6–Y8 to a persistent +1.0pp), D-44 (invested capital = net PP&E + intangibles + non-cash working capital, goodwill EXCLUDED; DNL 3,681.1m, ROIC 10.09% vs WACC 8.877%; the construction is disclosed in the UI), D-45 (of terminal growth, terminal return and reinvestment only two are free — pin g and ROIC, derive reinvestment; terminal growth gets a declared basis; alternative bases are UI disclosure, never a user input, per D-23), D-46 (a regulatory setting is indefinite unless currently under public debate — an observable with a source, not a judgement), D-47 (a terminal excess return is dated, not capped and not exempted by archetype). D-06 stays PROVISIONAL. D-19: prices refresh and everything re-tests after the UI work.

STILL PROPOSED: D-35 horizon rule, D-36 growth fade, D-37 archetype ten-year macro paths, D-38 capex convergence, D-39 terminal capex from the final explicit year, D-42 the terminal-return diagnostic, D-43 decay horizon from the Five Forces plus a tiered moat_source.

DO NOT RATIFY THE TWELVE GOLDENS from 23 August. They will move again, and by more than any table published so far suggests.

THE ORDER OF WORK:

9. Land the second sitting (step 1 above), then clone fresh.
10. Reconcile once, on the committed harness: run the three assumption sets through it and record in the paper which set produced each published table. One survives as current; label the others superseded. Settle Disorderly per point 6.
11. Give every table in the paper an explicit assumption block above it — capex path, terminal capex source, roll-off total, arc shape, boundary conventions. This is what would have prevented the whole mess.
12. Then put item 11 to Stephen with the point 7 and 8 evidence on the table.
13. Only then: D-42 the diagnostic, the horizon and fade, the UI disclosure piece, and finally re-pin all eighteen goldens once with the workbook re-tie.

A DISCIPLINE RULE WORTH ADDING TO CLAUDE.md: any number that reaches a document must come from committed code. A scratch harness that produced published figures is a deliverable, not scaffolding. Commit it in the same change as the document that cites it.

HOUSE RULES: Australian English. Number any list of 2+ points so Stephen can reply by number. Standing rule 3 — Stephen does not use CMD or git directly: give him ONE complete pasteable command, in a copy-button widget, EVERY time, say what "finished" looks like, and then VERIFY THE RESULT YOURSELF over the device bridge rather than asking him to copy terminal output back. Ask via AskUserQuestion if a brief is unclear rather than guessing. Read design/writing_style.md before drafting prose meant for readers.

EDIT MECHANICS: work in the CLOUD CONTAINER clone, not on the mount — the mount cannot delete or replace any file, so git merge, git checkout -- and git branch -D all fail there. The cloud container cannot push. Finished work travels as `session.bundle` written to the repo root and Stephen runs `land_vcc.cmd`; both are gitignored so they never collide with the merge they carry. Keep domain numbers out of .py prose — the SSOT ratchet is comment-blind.
