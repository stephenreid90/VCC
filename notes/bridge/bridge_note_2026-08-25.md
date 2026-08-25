VCC VALUATIONS — bridge note, session ending 25 August 2026.

FIRST, BEFORE ANYTHING ELSE: run `land_vcc.cmd` from a normal cmd window — one command, it never changes, see "Landing a session" in CLAUDE.md. Then `session_start.cmd`. Then read CLAUDE.md (standing rule 3 is NEW), the HANDOVER block at the top of WORKING_NOTES.md, DECISIONS.md, and then `design/methodology/horizon_and_terminal_convergence.md`, which is where this session's work actually lives — fifteen sections, thirteen decisions, seven of them ruled.

Do NOT assert that data, a document, a protocol or a prior decision does not exist until you have surveyed the directory that would hold it. Curated .yaml files in data/ are SUMMARIES; raw multi-year statements live in data/financials/.csv and data/financials/historical/<company>/. This session that directive paid off five times — see below.

STATE: suite 270 (+2 opt-in, `pytest -m libreoffice`), ratchet 12, bases unchanged 2.831 / 30.03 / 195.78. NO ENGINE CHANGE and nothing in data/ moved. This was a paper, not a build.

STANDING RULE 3, NEW IN CLAUDE.md — READ IT: Stephen does not use CMD or git directly. Give him ONE complete pasteable command, in a copy-button widget, say what "finished" looks like, and then VERIFY THE RESULT YOURSELF over the device bridge. Never ask him to copy terminal output back. The per-session landing scripts are gone; `land_vcc.cmd` is permanent and gitignored, and `sandbox_cleanup.cmd` now sweeps `.git` locks recursively (a stale `.git/refs/heads/incoming.lock` silently defeated `git branch -D` and cost a landing on 24 August).

WHAT THIS SESSION FOUND. DNL's explicit period ends with the gas roll-off still ramping, so all six scenarios capitalise a margin that was falling 0.50pp a year. Chasing that led to the terminal return, which nobody had ever computed: every DNL scenario implies a terminal ROIC of 37–80%, four to nine times WACC, and CSL 61–73%. WBC, whose engine declares terminal ROE explicitly, runs a sane 1.12–1.37x Ke. architecture.md §11.4.2 already requires ROIC ≈ WACC and claims it is "enforced at translation time"; it is not — `terminal_roic` appears once in the codebase, as a driver-delta mapping.

FIVE THINGS ARE SPECIFIED, POPULATED AND READ BY NOTHING: `time_profile`, `fade_period_length`, the year-10 macro anchors in the scenario files, `terminal_roic`, and the §9.9 terminal-growth convention. Assume there are more.

RULINGS STEPHEN MADE — DO NOT REOPEN THEM:

1. D-44. Invested capital = net PP&E + intangibles + non-cash working capital. Goodwill EXCLUDED — a demerged business is not charged in perpetuity for capital its predecessor deployed. DNL: 3,681.1m, ROIC 10.09% against a WACC of 8.877%. The construction is to be disclosed in the UI.
2. D-45. Of terminal growth, terminal return and reinvestment, only two are free. Pin g (macro/scenario work) and ROIC (Porter/moat work); DERIVE reinvestment. Terminal growth gets a declared basis — it has never had one, and the three companies currently run 3.5% / 3.0% / 2.5% on three unstated anchors. Alternative bases appear in the UI as DISCLOSURE, never as a user-selectable input (D-23).
3. D-46. A regulatory setting is assumed indefinite unless it is CURRENTLY UNDER PUBLIC DEBATE — an observable field with a source and a date, not a judgement about how long a licence lasts. WBC's moat horizon is therefore perpetual, with the named threat and a finite-horizon sensitivity attached.
4. D-47. A terminal excess return is DATED — not capped at the cost of capital, and not exempted by archetype. The decay table in paper §12 is what settles it.
5. D-40. DNL's gas roll-off HOLDS at −1.5pp; only the phasing moves, to concentrate in the FY2028–FY2030 window the archetype states and complete FY2032.
6. D-41. Disorderly Climate capex is an arc: +3.0pp through Y5, decaying across Y6–Y8 to a persistent +1.0pp.
7. D-06 stays PROVISIONAL (reconsidered and retained). D-19: market prices refresh, and everything re-tests, AFTER the UI work lands.

STILL PROPOSED, NOT RATIFIED: D-35 horizon rule, D-36 growth fade, D-37 archetype ten-year macro paths, D-38 capex convergence, D-39 terminal capex from the final explicit year, D-42 the terminal-return diagnostic, D-43 decay horizon derived from the Five Forces plus a tiered moat_source.

THE FIRST THING TO SETTLE NEXT SESSION: the rulings create an inconsistency. D-44 puts terminal capex at 8.6–9.2% of revenue while the explicit-period capex path converges to 7.0%. A company reinvesting 7.0% cannot be growing the ruled capital base at the explicit period's 6.155%, let alone at g. The explicit path and the terminal are now struck on different reinvestment logic, and D-38 needs revisiting in that light.

THEN, IN THIS ORDER: build D-42 (compute terminal ROIC and ROE, display them against the cost of capital, change no behaviour) — cheap, uncontroversial, and it makes the largest assumption in every valuation visible for the first time. Then the horizon and fade. Then the UI disclosure piece, which has grown into the pivot: terminal return, terminal growth basis, invested-capital construction and the working-capital methodology all disclosed in one place. Then re-pin all eighteen goldens ONCE, with the workbook re-tie.

DO NOT RATIFY THE TWELVE GOLDENS from 23 August. They will move again. Under the ruled assumptions DNL lands at 3.2366 / 2.7471 / 2.7035 / 1.9122 / 1.4378 / 0.6316 — four moving less than 4%, Disorderly Climate −15.5%, Stagflation Persists −21.6%. Muddle Through 2.7471 is 23.9% below the 3.61 market reference.

TWO NUMBERS WORTH ARGUING WITH. First, WBC's terminal growth of 3.5% has NO rationale anywhere — no field, nothing in DECISIONS.md, nothing in wbc.md. Second, CSL's model value of 195.78 sits 85.5% ABOVE a market reference of 105.53, while the market implies a terminal ROIC of 5.5%, below CSL's own WACC. Part of that gap is a depressed frozen price — the 200-day average is 161.95 — and part is the terminal-return artefact.

METHOD THAT PAID OFF: build a scratch replica of the engine's DCF and validate it against the real engine before trusting any sizing. Every number in the paper comes from a harness that ties to FcfEngine at 1e-15 on all six live DNL scenarios. It made it safe to test a dozen structural variants without touching the engine.

HOUSE RULES: Australian English. Number any list of 2+ points so Stephen can reply by number. Ask via AskUserQuestion if a brief is unclear rather than guessing. Render anything Stephen needs to copy — especially CMD commands, EVERY time — in a widget with a copy button, not a blockquote. Read design/writing_style.md before drafting prose meant for readers.

EDIT MECHANICS: work in the CLOUD CONTAINER clone, not on the mount — the mount cannot delete or replace any file, so git merge / checkout -- / branch -D all fail there. The cloud container cannot push. Finished work travels as `session.bundle` written to the repo root, and Stephen runs `land_vcc.cmd`. Both are gitignored so they never collide with the merge they carry. Keep domain numbers out of .py prose — the SSOT ratchet is comment-blind.
