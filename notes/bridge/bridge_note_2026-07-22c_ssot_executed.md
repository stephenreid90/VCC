Continuing VCC. Read `CLAUDE.md`, then `WORKING_NOTES.md` — start at the block headed
"22 July 2026 (c) (SSOT protocol EXECUTED for DNL · CI fixed)", then read the (b) block below it,
then `design/single_source_of_truth.md` in full. Run `git status` and `git log --oneline -4` before
assuming anything about commit state.

WHERE WE ARE. The single-source-of-truth protocol is no longer a draft — it is EXECUTED for DNL and
guarded by a lint. This session: committed M1, fixed CI, split DNL's data into layers, deleted a
stored derived value, and added the lint. 68 tests green (was 63). The split was proven value-neutral
by adversarial audit: 50 YAML leaves in, 49 out, only `computed_wacc` removed, no value changed,
smoke-test output byte-identical.

DO NOT REOPEN THESE — they are settled:
- β is NOT decided and is Stephen's call. An earlier claim that re-levering vindicates 0.95 and
  retires 1.10 was WITHDRAWN as cherry-picked; proper triangulation gives ~0.96–1.05, excluding BOTH.
- Genuine drift was four quantities (β, shares, WACC, base margin), not eight. Revenue 3,400 vs 3,905
  is continuing-ops vs incl. Phosphate Hill — NOT drift, already ruled on.
- The register needs no new file: `data/financials/` is machine-written (layer 1), `data/companies/`
  is hand-written judgement (layer 2). This is DONE for DNL.
- One β and one WACC per company per valuation date. The workbook is an export, not a repository.

WHAT THE DNL SPLIT LOOKS LIKE NOW (so you don't re-derive it):
- `data/financials/dnl.yaml` — layer 1. `normalised_baseline` is GONE; `wacc_observed_inputs` holds
  risk_free_rate, beta_measured, beta_peer_dataset, equity/debt market values.
- `data/companies/dnl.yaml` — layer 2. `normalised_baseline` (margin, net debt, capex, tax, D&A,
  terminal growth) + nested `wacc_method` (ERP, beta_selected + rationale, active beta, cost of debt).
- `computed_wacc` DELETED (was a stored layer-3 value off a superseded β 1.15).
- `translator.resolve_normalised_baseline(inputs)` rejoins the two into the legacy `wacc_build` shape,
  so consumers are unaffected. CSL falls back to the old financials location until it is split.

THE LINT (`tests/test_ssot_lint.py`): check 1 = no stored derived value in either layer (found and
recorded two pre-existing offenders in csl.yaml + wbc.yaml as visible debt); check 2 = no
normalised_baseline left in a layer-1 file; check 3 = value-keyed ratchet, 124 duplicates baselined,
new ones fail. Regenerate the baseline DOWNWARD only via `scripts/ssot_lint_baseline.py`. Documented
limits: value-keyed not path-keyed (updating `beta` but not `beta_selected` is invisible); scans .py
only; skips years/small ints. These are fine for now; the fix needs the layer-2 schema.

PICK THIS UP NEXT (nothing blocks anything else — choose by appetite):
1. CSL split — mirrors DNL. Two calls: is `group_revenue` layer 1 or 2, and how to split
   `cost_of_equity_build` (csl.yaml is `workbook_reverse_engineered`, so its layer 1 is hand-curated
   from an export). Clearing `computed_cost_of_equity` is part of this.
2. WBC — no `data/financials/wbc.yaml` exists; only `data/companies/wbc.yaml`. Clear its stored
   `cost_of_equity` when WBC work comes up.
3. β + share count — now cheap (method registered, so a decision propagates). LIVE PROBLEM:
   `equity_market_value: 6802.0` is blessed as layer-1 observed data but derives from 1,884 shares,
   contradicting `share_statistics: 1,875.9` in the same file — ~6.4% error in the equity weight until
   the share count is settled. Ben owes a reconciliation (feed's own market cap 6,390.4 ÷ 3.6061 =
   1,772, not 1,875.9) and the real EODHD peer pull (gearings/tax exist only in the MOCK beta_data.py).
4. Remaining §8 items: peer-exclusion reasons + capital_structure_rationale arguably belong in layer 2
   (pending the "where does peer data live" call); workbook generator scope; valuation-date stamping;
   basis labels; supersession log; export proliferation; specify the layer-2 schema.
5. Then M2 (wire AssumptionSet → FcfEngineInputs). This protocol is ADJACENT to M2, not its front
   half — computing β on demand needs a new peer-triangulation derivation + a layer-1 peer feed.

CI / HOUSEKEEPING: root `conftest.py` now makes Actions pass — don't delete it. `deploy-web.yml` only
runs tests (its deploy step is a placeholder echo); `test.yml` covers `models` not `src` so M1 shows
0% coverage; `setup.py` still says author 'Ben Watson'. New fine-grained PAT goes in `.github-token`
(now gitignored); revoke the old one.

HOUSE RULES: Australian English; number multi-point lists; ask via AskUserQuestion if a brief is
unclear; don't hand-patch the generator (the five non-MT scenario values can't be re-derived by hand
until the scenario engine exists); prefer sandbox-side writes for large files; swap chats ~20 exchanges.
