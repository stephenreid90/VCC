Continuing VCC. Read CLAUDE.md, then WORKING_NOTES.md — start at the "25 July 2026 (b)"
block, then the CSL-split block below it. Run `git status && git log --oneline -5` before
assuming commit state.

WHERE WE ARE. Three commits pushed this session: aafa878 (DNL layer split + lint — the
22 Jul (c) work, finally in history), 2227c8f (CSL layer split, value-neutral: 95 numeric
leaves in, 93 out; only computed_cost_of_equity + group_ebit_margin_fy25 removed), and the
share-count convention consolidation (CLAUDE.md conv 6 + SSOT §8 note + WORKING_NOTES).

SETTLED — DO NOT REOPEN:
- Share/net-debt anchoring is methodology §5: latest REPORTED count, paired to net debt at
  the SAME balance-sheet date, buyback NOT projected (fair-value buyback = value-neutral per
  share). DNL's anchored count is ~1,770m at 31 Mar 2026 (§5.3). The live 1,754.1m (3 Jul,
  ASX Appendix 3G) is post-anchor — ignore it. Now CLAUDE.md cross-cutting convention 6.
- CSL split done + committed (mirrors DNL; cost_of_equity_build = coe_observed_inputs [L1] +
  coe_method [L2] via translator; computed_cost_of_equity deleted).
- β is NOT decided — Stephen's call. ~0.96–1.05, excludes both 0.95 and 1.10.

OPEN — THE DNL β RE-ANCHOR PASS (next focused chat, in order):
1. Stephen picks β.
2. Bring data/financials/dnl.yaml into §5.3 compliance: shares_outstanding_at 2026-03-31,
   shares_outstanding 1,770m + source; fix equity_market_value 6,802 → ~6,390 (=1,770×3.61)
   or derive it; add derived_metrics.net_debt_at; implement the §5.4 validator
   (shares_outstanding_at == net_debt_at).
3. Then re-anchor generator/UI engine-driven — do NOT hand-patch scenario values.
Ben still owes: real peer gearings/tax (mock in ui_prototypes/_generator/beta_data.py);
optionally the exact reported 31 Mar 2026 issued count from the 1H26 half-year PDF.
Then WBC (clear its stored cost_of_equity — last KNOWN_STORED_DERIVED offender), remaining
SSOT §8 items, then M2.

HOUSE: Australian English; number multi-point lists; ask via AskUserQuestion if a brief is
unclear; 68 tests green. Commit sandbox-side (.git/index.lock is create-but-not-delete → mv
aside; `git push origin main` needs the .github-token URL — x-access-token:$TOKEN). Don't
hand-patch the generator.
