VCC — resuming. Read CLAUDE.md then WORKING_NOTES.md from the top (the "ALL THREE COMPLETE"
block, then "Possible next threads" and the "OUTSTANDING" item). `git fetch`; HEAD `f91497c`,
all pushed. Suite **122** green (`pip install pytest pydantic pyyaml scipy numpy --break-system-packages`;
`python3 -m pytest -q`). Ratchet 8.

STATE: all three test companies are engine-wired end to end — headline + six scenarios + build-up
+ narrative + per-year workings, each tying its audited workbook, plus a base64-embedded full
formula workbook on each download button. Numbers: DNL (industrial FCFF, WACC) 3.073; WBC (bank
DDM on equity, Ke, §15) 30.03; CSL (multi-segment FCFF, M3, USD→AUD) USD 134.52 / AUD 203.83.
Three archetype engines in `src/vcc_valuations/dcf/` (fcf_engine, bank_engine, segment_engine),
each with `.derivation()` + `.per_year_derivation()`. Archetype schema formalised (§7.4-v2 — all
five industry files validate). Generated HTML/cfgs are gitignored — rebuild with
`build_cfgs.py && gen_ui.py`.

OUTSTANDING / NEXT (all optional, nothing blocking):
1. BLOCKED on Ben's EODHD/broker feed — peer `det`/`mfin` in `beta_data.py` for the comparability-
   metrics + peer-multiples grid (WBC needs a bank P/E–P/B set; CSL the DNL `det`+`mfin` shape).
2. DEFERRED to Stephen (methodology) — formally wiring the DNL revenue-chain `dm_inflation` to the
   scenario-file CPI (would move the valuation).
3. PARKED — user-written world scenarios (build phase).
4. COSMETIC — a consolidated `biopharmaceuticals.yaml` (CSL loads with `archetype=None`, fine).

HOUSE RULES: AU English; number multi-point lists. Edit `build_cfgs.py` / `gen_ui.py` SANDBOX-SIDE via
Python string replacement (the Edit tool corrupts these large files); after regen run `node --check`
on all three inlined scripts + confirm base ties 3.073 / 30.03 / 203.83. Keep domain numbers out of
`.py` prose (the ratchet scanner is comment-blind). Commit sandbox-side (`mv .git/index.lock` aside on
the create-but-not-delete mount); push via the `x-access-token` URL then `git fetch` (the local
`origin/main` ref lags). Run `sandbox_cleanup.cmd` from a normal cmd window to clear orphaned
`.git/*.lock.dead*`, `.git/objects/**/tmp_obj_*` and `_*_full.xlsx` files.
