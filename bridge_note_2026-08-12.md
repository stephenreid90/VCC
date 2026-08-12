VCC bridge note (12 Aug 2026). Continuing VCC — big-momentum session, don't lose it.

START: read CLAUDE.md, then WORKING_NOTES.md from the TOP (the "PLANNED NEXT — two UI features" block is
first; then blocks "12 August (f)/(g)" and down). Run `git fetch && git status && git log --oneline -8` —
HEAD should be <after this commit>, all pushed. Suite: `pip install pytest pydantic pyyaml scipy numpy
--break-system-packages` then `python3 -m pytest -q` → 99 green.

DONE THIS SESSION (all pushed):
1. M2 assembler `translator.build_engine_inputs_from_data(inputs, scenario_id)` builds the whole
   FcfEngineInputs from data — DNL Muddle Through reproduces 3.073/share with ZERO hand-typed constants.
2. Full V6 traceability via a reusable `Derivation` primitive (src/vcc_valuations/derivation.py) across FIVE
   derived sheets: revenue-growth chain, Tax Bridge (also a real SSOT fix — the stored tax glide was removed
   and is now derived), WACC Build (WaccBuild.derivation()), Equity Bridge (EquityBridge.derivation()).
3. DNL COMPLETE — all six scenarios from data (MT baseline + PARALLEL-SHIFT scenario overlay; drivers tie
   dnl_scenarios_comparison_v4 to the cent): OC 3.562 / MT 3.073 / AIPL 2.985 / Frag 2.222 / DClim 1.177 /
   Stag 1.019, ~4.2x downside skew. Data: revenue_growth_chain (shared + by_scenario.macro), engine_overlays
   (baseline + by_scenario deltas), tax_bridge — all in data/companies/dnl.yaml.
4. DNL UI WIRED TO THE ENGINE end-to-end — headline AND the "Valuation build-up" drill-down. build_cfgs.py
   `engine_pack()` (reusable, company-agnostic) computes base/bars/asymmetry/discount + narrative numbers;
   the build-up bridge, net-debt Period-A walk, lease panel and per-year operating build all come from
   equity_bridge_from_data + the engine (EV 7,009 → nd 1,224 → adjustments 152 (now its own §4.2 line) →
   leases 194 → equity 5,439 ÷ 1,770 → 3.07; operating build re-based to the ratified 3,400). WBC/CSL
   untouched (base 30.15 / 203.83). Narrative uses Stephen's Direction-2 (measured) framing.

NEXT — two features, target = STANDALONE shareable HTML (decided; a static file can't call the Python
engine at runtime, which shapes both). Full plan in the WORKING_NOTES "PLANNED NEXT" block.
- DO FIRST — #2 "download EVERYTHING to Excel": pre-generate a full FORMULA workbook with the Python engine
  at build time (openpyxl + xlsx skill; the Derivation objects ARE the rows), embed base64 in the HTML,
  download serves it. All six scenarios + DCF/WACC/Tax/Equity builds + comps + Porter's; standing rule 1
  (formulas, yellow-cell Assumptions). Bounded; reuses everything above.
- THEN — #1 user-written world scenario → macros → Porter's → company → valuation. A scenario is just a
  small pack (4 macros + 3 deltas) = one more by_scenario entry flowing the same engine path. DECISION:
  BUILD IT AT BUILD TIME in the Python engine layer; DO NOT port the engine to JS (a browser engine =
  second source of truth, the thing we just killed). For the standalone feedback file, pre-compute one or
  two ILLUSTRATIVE user scenarios at build time (e.g. the "protracted war → oil/gas escalation" example) so
  the file SHOWS the capability as worked examples; demo the live type-your-own version in Cowork (real
  engine + narrative translation). At the programming phase the live feature lives behind a thin engine
  SERVICE (UI posts narrative → server derives pack via LLM, runs engine, returns valuation) — reusable
  production foundation, not throwaway. Opportunity: make it genuinely Porter's-responsive (impact matrix +
  translation rules already exist) — richer than the six built-ins (fixed −25bps offset).

STANDALONE = right call for feedback (share with Ben etc.), no impairment to the direction PROVIDED we never
reimplement the engine in the browser. Everything pre-computed (six scenarios, analysis, comps, Excel) is
built from the engine and embedded; only live user-scenarios want runtime compute (handled per #1).

Also open (smaller): roll the engine_pack + build-up wiring onto WBC (bank fork, Ke, §15) and CSL (segment
FCFF, M3; clear the pre-existing 76-error CompanyPositionFile schema mismatch first); per-year P&L margin
Derivation (parity); human-readable workings view from Derivation.as_rows(); DM-inflation basis (workbook
2.5% normalising vs scenario CPI 3.0% sticky).

HOUSE / MECHANICS: Australian English; number multi-point lists; plain-text numbered questions (UI drops
AskUserQuestion). Generator = edit ui_prototypes/_generator/build_cfgs.py SANDBOX-SIDE via python string
replacement (Edit tool corrupts it); the engine-wiring lives in an inserted SSOT block before json.dump;
`python3 build_cfgs.py && python3 gen_ui.py`; VERIFY node --check on all three inlined scripts + base ties
(DNL 3.073 / WBC 30.15 / CSL 203.83). Keep domain NUMBERS out of .py docstrings/comments (the SSOT ratchet
regex reads them → false trips; reword to words). Commit sandbox-side (mv .git/*.lock aside; push with the
x-access-token URL from .github-token). Run sandbox_cleanup.cmd for orphaned files. beta = 1.10 ratified.
