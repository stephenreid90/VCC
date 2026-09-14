VCC VALUATIONS — bridge note, session ending 25 August 2026 (second sitting).

FIRST, BEFORE ANYTHING ELSE: run `land_vcc.cmd` from a normal cmd window — one command, it never changes, see "Landing a session" in CLAUDE.md. Then `session_start.cmd`. Then read CLAUDE.md, the HANDOVER block at the top of WORKING_NOTES.md, DECISIONS.md, and `design/methodology/horizon_and_terminal_convergence.md`.

Do NOT assert that data, a document, a protocol or a prior decision does not exist until you have surveyed the directory that would hold it. Curated .yaml files in data/ are SUMMARIES; raw multi-year statements live in data/financials/*.csv and data/financials/historical/<company>/.

STATE: suite 288 (+2 opt-in, `pytest -m libreoffice`), ratchet 12, bases unchanged 2.831 / 30.03 / 195.78. NO ENGINE CHANGE, no production change, nothing in data/ moved. Two commits.

WHAT THIS SITTING DID.
1. The scratch harness from the first sitting was gone, so it was rebuilt and COMMITTED: `tests/dcf/harness/replica.py` plus `tests/dcf/test_replica_ties_engine.py`. Eighteen tests, six DNL scenarios, floating-point equality against FcfEngine. Variants are one-change transforms of the tying plan — `extend`, `fade_growth`, `converge_capex`, `reshape_margin`, `capex_arc`, `hold_capital_intensity`, and four ways of striking terminal capex. Use it; do not rebuild it again.
2. Two terminal-boundary conventions are now pinned as tests. The terminal's working-capital drag is struck one year ahead of the explicit period's — a factor of (1+g). And explicit flows discount mid-year while the terminal is an end-of-year Gordon value, so converting a terminal year into a steady-state explicit year RAISES EV by about 0.26%. D-35's "surplus years cost nothing" is true to a quarter of a per cent, not exactly.

THE FINDING, AND IT IS THE BIG ONE. Item 11 is not a rounding-level inconsistency between 7.0% and 8.7%. Under the ruled build, invested capital falls from 108.3% of revenue today to 67.5–85.8% at Y10 (Muddle Through 72.6%). Capex converging to 7.3% IS D&A, so DNL adds no net fixed capital across ten years while revenue compounds about 50%. That thinning of the base — not a moat — is what produces the terminal ROIC of 14.6%. Nobody decided it.

WHAT THE COHERENT ALTERNATIVE COSTS. Holding capital intensity flat, so capex funds growth rather than only replacement: Orderly 3.1793 → 1.9804 (−37.7%), Muddle Through 2.6956 → 1.7675 (−34.4%), AI Lag 2.6558 → 1.8629 (−29.9%), Fragmentation 1.8629 → 0.9497 (−49.0%), Disorderly 1.5294 → 0.4898 (−68.0%), Stagflation 0.5841 → −0.1998. Terminal ROIC then lands at 9.8% against a WACC of 8.877% — which is what architecture.md §11.4.2 actually asks for. The coherent version of the framework's own rule takes a third off the company.

RECONSTRUCTION CAVEAT: the rebuilt harness lands within about 2% of the first sitting's ruled table (Muddle Through 2.6956 against the paper's 2.7471). The residual could not be reconciled because the original harness no longer exists. Every number above is from the committed harness.

STILL OPEN, AND BLOCKING: item 11 is UNRULED. Three positions were put and none taken — (a) declare a Y10 target capital intensity and derive the capex path, (b) hold intensity flat, (c) accept the fall and disclose it as a stated judgement. Nothing should be built on the ruled numbers until this is settled; it moves DNL further than every other open item combined. The evidence question underneath it is also unanswered: how much of DNL's 6.155% nominal revenue growth is volume (needs capacity) versus price (does not).

EVERYTHING FROM THE FIRST SITTING STANDS. Rulings D-40, D-41, D-44, D-45, D-46, D-47 are FIRM — do not reopen. D-35, D-36, D-37, D-38, D-39, D-42, D-43 remain PROPOSED. Do not ratify the twelve goldens from 23 August. D-42 (the terminal-return diagnostic), the horizon and fade, and the UI disclosure piece are all queued behind item 11.

HOUSE RULES: Australian English. Number any list of 2+ points so Stephen can reply by number. Standing rule 3 — Stephen does not use CMD or git directly: give him ONE complete pasteable command, in a copy-button widget, say what "finished" looks like, and VERIFY THE RESULT YOURSELF over the device bridge. Read design/writing_style.md before drafting prose meant for readers.

EDIT MECHANICS: work in the CLOUD CONTAINER clone, not on the mount — the mount cannot delete or replace any file. The cloud container cannot push. Finished work travels as `session.bundle` in the repo root and Stephen runs `land_vcc.cmd`. Keep domain numbers out of .py prose — the SSOT ratchet is comment-blind.
