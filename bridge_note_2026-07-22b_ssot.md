Continuing VCC. Read `CLAUDE.md`, then `WORKING_NOTES.md` — start with the block headed
"22 July 2026 (b) (single-source-of-truth protocol · β claim withdrawn)", then read
`design/single_source_of_truth.md` in full.

Where we are. Last session did NOT decide β. It re-diagnosed the re-anchor problem as an
architecture problem — we store answers, not methods, in a format consumers can't read — and
drafted the protocol to fix it. That draft is `design/single_source_of_truth.md`: not in force,
awaiting my review of §3 and §8. M1 (the per-year DCF engine, 63 tests green) should now be
committed; check `git status` before assuming.

Do not re-derive β. An interim claim that re-levering the peer cluster vindicates the workbook's
0.95 and retires 1.10 was withdrawn as cherry-picked. Proper triangulation gives ~0.96–1.05,
which excludes BOTH stored answers. β is open and is my call.

Corrected facts to carry forward. Genuine drift is four quantities — β, share count, WACC, base
EBIT margin. Revenue 3,400 vs 3,905 is NOT drift (continuing ops vs incl. Phosphate Hill, already
ruled on). Net debt has four definitions, EV three, leases two dates. Basis mixing, not stale
copying, is the more persistent failure. `dnl.yaml` is internally inconsistent: `beta: 1.10` but
`computed_wacc: 0.0882`, derived from a twice-superseded β 1.15.

Decisions in force. One β and one WACC per company per valuation date — scenarios differ in cash
flows, not the discount rate. Three layers: observed data / method and selection / derived values;
store the method, never the answer. No new register file — `data/financials/` is machine-written
(it holds the EODHD CSVs), `data/companies/` is hand-written judgement; the fix is to stop
judgement leaking into the first. The workbook is an export, not a repository.

Pick this up first. The one concrete migration: `data/financials/dnl.yaml` lines 42–199
(`normalised_baseline`) hold all three layers at once. Layer 2 moves to `data/companies/dnl.yaml`;
layer 1 stays; `computed_wacc` is deleted. Repoint `src/vcc_valuations/translator.py:225` and
`scripts/run_smoke_test.py:45,74`. Same for `csl.yaml`; there is no `data/financials/wbc.yaml`.
Then the lint. Then β and the share count — with the method registered, so it propagates.

Open and unresolved: the twelve items in §8, several needing my call — peer-data home, workbook
generator scope, valuation-date stamping, basis labels, supersession log, export proliferation.
Ben still owes the real EODHD peer pull (gearings and tax rates exist only in the MOCK
`beta_data.py`) and a reconciliation of shares 1,770 vs 1,875.9 (the feed's own market cap implies
1,772). My new fine-grained PAT goes in `.github-token`, now correctly gitignored.

House rules unchanged: Australian English, number multi-point lists, ask via AskUserQuestion if a
brief is unclear, don't hand-patch the generator, prefer sandbox-side writes for large files.
