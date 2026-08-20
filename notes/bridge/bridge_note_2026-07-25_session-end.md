Continuing VCC. Read CLAUDE.md, then WORKING_NOTES.md — start at the "25 July 2026 (d)" block
and read down through (c), (b), and the CSL-split block. Run `git status && git log --oneline -6`
before assuming commit state.

WHERE WE ARE. Five commits pushed this session, 68 tests green throughout:
- aafa878  DNL layer split + SSOT lint (the 22 Jul (c) work, finally in history).
- 2227c8f  CSL layer split (cost-of-equity discipline; value-neutral).
- 72d1520  share-count/net-debt anchoring convention surfaced (CLAUDE.md conv 6 + SSOT §8).
- 772ceea  β decision recorded = 1.10 (real-gearing triangulation).
- ed7e756  UI: single WACC presented in the DNL/WBC/CSL scenario interface.

SETTLED — DO NOT REOPEN:
- SSOT layering executed + lint-enforced for DNL and CSL: layer 1 (observed) in data/financials,
  layer 2 (method/selection) in data/companies, layer 3 (derived) computed by the engine and never
  stored. translator.resolve_normalised_baseline rejoins the layers for consumers.
- Share/net-debt anchoring = methodology §5: latest REPORTED count, both paired to the same
  balance-sheet date, buyback not projected (fair-value buyback is value-neutral). DNL anchored
  count ~1,770m @ 31 Mar 2026. Now CLAUDE.md cross-cutting convention 6. (The live 1,754m is
  post-anchor buyback — ignore it.)
- β = 1.10, ratified 25 Jul, on a real-gearing triangulation (unlever peers at real D/E Orica 0.18 /
  Yara 0.36 / ICL 0.30 → asset β ~0.93/0.98 → re-lever at DNL 0.28 → 1.11–1.17, shaded to the top of
  1.05–1.10 for DNL's lowest-in-set operating leverage). The old "0.96–1.05 excludes 1.10" was a
  MOCK-gearing artefact.
- Single WACC (one β and one WACC per company per valuation date; scenarios differ in cash flows, not
  the discount rate) — now encoded in the UI. Per-scenario discount-rate override is allowed but
  flagged as a deliberate deviation.

UI STATE (design/ui_design_brief.md is the spec; "HTML is the contract"):
- The scenario-interface workbench spine is BUILT: add user scenarios, per-input overrides on all five
  drivers, global-vs-per-scenario toggle, live reduced-form recompute, localStorage.
- This session PRESENTED the single WACC: always-visible metric card; two-column build+apply in the β
  workbench; inline β-regression plots.
- The reduced-form (computeVals) is a multiplicative APPROXIMATION, not the engine — M2 swaps it. The
  six scenario per-share values are still generator-hand-calibrated.
- Generator mechanics: edit ui_prototypes/_generator/*.py SANDBOX-SIDE, python3 build_cfgs.py &&
  python3 gen_ui.py, verify node --check + base tie (DNL 3.48). Never hand-edit the HTML. Stephen
  eyeballs the render; his UI has had disappearing AskUserQuestion prompts, so prefer plain-text
  numbered questions.

OPEN — pick by appetite:
1. UI next (Stephen wants all three): Workstream A+C (content/layout richness), rest of B (other
   drivers live; wire Five-Forces overrides into the number — currently saved but disconnected), or D
   (β workbench depth). All ultimately lean on the engine swap (M2).
2. dnl.yaml §5.3 share-count fix: shares_outstanding_at 2026-03-31 + shares 1,770m + source;
   equity_market_value 6,802 → ~6,390. This MOVES the E/V weight → WACC → valuations, so it needs an
   engine re-run, NOT a hand-patch of scenario values. β is settled, so it is unblocked.
3. WBC split (clear its stored cost_of_equity — the last KNOWN_STORED_DERIVED offender); CSL layer-1
   circularity; implement the §5.4 validator (shares_outstanding_at == net_debt_at). Then M2 (wire
   engine ↔ UI).
4. Ben still owes: real peer gearings/tax (mock in ui_prototypes/_generator/beta_data.py); optionally
   the exact reported 31 Mar 2026 issued share count from the 1H26 PDF.

HOUSE: Australian English; number multi-point lists; ask via AskUserQuestion if a brief is unclear
(but prefer plain-text numbered questions — Stephen's UI drops the prompts). Commit sandbox-side
(.git/index.lock is create-but-not-delete → mv aside; `git push origin main` needs the .github-token
URL: x-access-token:$TOKEN). Don't hand-patch the generator. Swap chats ~20 exchanges.
