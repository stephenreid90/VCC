VCC — FULL-PROJECT REVIEW (use the strongest model; select Opus for this chat).

You are reviewing the entire VCC Valuations project to date with fresh, critical, skeptical eyes.
This is an assessment pass — produce a findings report, do NOT change code unless I ask.

SETUP: `git fetch` (HEAD f91497c, all pushed). Install + run the suite:
`pip install pytest pydantic pyyaml scipy numpy --break-system-packages` then `python3 -m pytest -q`
(expect 122 passing). Ratchet: `python3 -m pytest tests/test_ssot_lint.py -q` (8).

READ ORDER: CLAUDE.md → WORKING_NOTES.md (top: "ALL THREE COMPLETE" + "Possible next threads" +
"OUTSTANDING") → design/architecture.md → design/build_plan.html → the three engines in
src/vcc_valuations/dcf/ (fcf_engine.py, bank_engine.py, segment_engine.py) → src/vcc_valuations/
translator.py → the audited workbooks in analyses/{dnl,wbc,csl}/valuations/ → tests/.

WHAT WAS BUILT (verify, don't take on trust): three test companies valued end-to-end by
archetype-appropriate engines, each tying its audited workbook, with engine-wired scenario UIs and
base64-embedded formula workbooks. DNL — industrial single-segment FCFF, WACC, EV→equity bridge →
3.073. WBC — bank residual-income / dividend-discount on equity, Ke, no WACC/EV bridge (methodology
§15) → 30.03. CSL — multi-segment FCFF (M3), per-segment build → group FCFF → Ke → USD→AUD →
USD 134.52 / AUD 203.83. Each engine exposes .derivation() + .per_year_derivation(). Archetype schema
was evolved to §7.4-v2 so bank + biopharma files validate strictly. Generated HTML/cfgs are gitignored;
rebuild with `build_cfgs.py && gen_ui.py`.

REVIEW DIMENSIONS (be critical; flag issues with file:line; distinguish MUST-FIX from nice-to-have):
1. Methodology soundness. Do the three approaches correctly implement the intended methods? Scrutinise
   terminal-value construction, mid-period discounting, the equity bridges, the bank ROE-fade terminal,
   CSL's binding-terminal-margin + terminal-capex=D&A, the USD→AUD FX handling, single-discount-rate
   discipline, β peer-triangulation.
2. Engine correctness. Read the three engines; re-derive the MT numbers and the six scenarios against
   the workbooks (recalc with LibreOffice if useful). Any hidden hardcodes, off-by-one, sign errors,
   or recursion mistakes? Do the goldens actually pin the engine, or are they circular?
3. Data integrity / single-source-of-truth. Is the layer-1 (observed) / layer-2 (judgment) split clean?
   Any stored-derived values, circularity, or duplication the ratchet misses? Is workbook discipline
   (yellow-cell inputs, everything else a formula, industry-baseline vs company-offset as separate rows)
   actually honoured in the generated workbooks?
4. Traceability. Do the Derivations cover the whole build, or are there gaps between what the workbook
   shows and what the engine can explain?
5. Test quality. 122 tests — what's under-tested? Are the six-scenario and per-year assertions meaningful?
6. Archetype-fork + schema. Was the §7.4-v2 additive relaxation sound, or did making blocks optional
   weaken validation too far (e.g. is it now possible to author an invalid archetype that passes)?
7. Standalone-UI + base64 workbook. Correctness and risks of the approach; the gitignore/untrack decision;
   the reduced-form in-browser approximation vs the engine.
8. Known caveats to probe: mock peer data (beta_data.py det/mfin nulls — comparability/multiples grids
   not built for WBC/CSL); the DM-inflation basis (chain 2.5% normalising vs scenario 3.0% CPI, deferred);
   CSL loads with archetype=None (no consolidated biopharmaceuticals.yaml); the "Tara Reid" cosmetic
   leftover in design/build_plan.html header.
9. UI / UX — the scenario-interface prototype (ui_prototypes/{dnl,wbc,csl}_scenario_interface.html; these
   are gitignored build outputs — rebuild with build_cfgs.py && gen_ui.py, or open the local files). This
   is the standalone shareable HTML that goes to Ben and reviewers, so I want concrete SUGGESTIONS, not
   just a critique: information hierarchy and first-glance clarity (does the headline + scenario spread +
   asymmetry land in 5 seconds?); the scenario-bar chart, the build-up drill-down, the per-year workings
   table, the Five-Forces / discount-rate / assumptions panels; navigation between tabs; how well the
   "one source of truth / audited-workbook" story is conveyed; consistency across the three companies;
   the download-to-Excel affordance; accessibility, mobile/narrow-width behaviour, and visual polish.
   Propose specific, prioritised improvements (quick wins vs larger reworks) that would make it more
   persuasive and easier to navigate for a non-author reviewer. Note the generator mechanics: content is
   built in build_cfgs.py, rendered by gen_ui.py into a single self-contained HTML — suggestions should be
   framed so they can be implemented there.

DELIVERABLE: a prioritised findings report — correctness bugs first, then methodology concerns, then
data/test/code-quality, then improvement opportunities, then a dedicated UI/UX suggestions section
(prioritised, quick-wins-first). Cite file:line. Recommend a fix order. Assessment first; no code changes
until I confirm.

HOUSE: AU English; number multi-point lists so I can reply by number. If a brief is unclear, ask before
starting. (Working-file mechanics if you do later edit: build_cfgs.py/gen_ui.py SANDBOX-SIDE only;
node --check + base ties 3.073/30.03/203.83 after regen; commit sandbox-side, push x-access-token,
then git fetch; sandbox_cleanup.cmd for orphaned files.)
