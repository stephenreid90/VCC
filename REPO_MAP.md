# REPO_MAP — what exists, and where

_Generated 2026-08-21 by `scripts/repo_inventory.py`. **Regenerate at the start of
a session, before reasoning about what data exists.** Do not hand-edit._

- HEAD: `e4e862d Handover: repo inventory tooling, survey-before-you-conclude directive, session handover` on `main`
- Unpushed commits: **0**
- Tracked files: 269
- Untracked files: 19

> **The rule this file exists to enforce:** a curated `*.yaml` in `data/` is a
> SUMMARY, not the source. Before concluding that data does not exist, check the
> raw feed exports in `data/financials/*.csv` and the primary documents in
> `data/financials/historical/<company>/`. Absence in the yaml is not absence.

## Per-company sources

### DNL

| Path | Present | What it is |
|---|---|---|
| `data/companies/dnl.yaml` | yes (34.1KB) | company position + layer-2 method (judgement) |
| `data/companies/dnl.md` | yes (13.7KB) | company narrative |
| `data/companies/dnl_documents.yaml` | yes (8.7KB) | document register |
| `data/financials/dnl.yaml` | yes (9.6KB) | curated layer-1 financials (a SUMMARY — check for raw sources too) |
| `data/financials/dnl_*.csv` | **NO** | RAW feed export — multi-year statements live here, not in the yaml |
| `data/financials/historical/dnl/` | **7 document(s)** | primary source PDFs (annual reports, statutory accounts, presentations) |
| `analyses/dnl/` | yes | 14 workbook(s); subdirs: scenarios, valuations |

### WBC

| Path | Present | What it is |
|---|---|---|
| `data/companies/wbc.yaml` | yes (36.1KB) | company position + layer-2 method (judgement) |
| `data/companies/wbc.md` | yes (7.7KB) | company narrative |
| `data/companies/wbc_documents.yaml` | yes (20.3KB) | document register |
| `data/financials/wbc.yaml` | yes (1.9KB) | curated layer-1 financials (a SUMMARY — check for raw sources too) |
| `data/financials/wbc_*.csv` | **1 file(s)** | RAW feed export — multi-year statements live here, not in the yaml |
| `data/financials/historical/wbc/` | **10 document(s)** | primary source PDFs (annual reports, statutory accounts, presentations) |
| `analyses/wbc/` | yes | 6 workbook(s); subdirs: valuations |

### CSL

| Path | Present | What it is |
|---|---|---|
| `data/companies/csl.yaml` | yes (30.4KB) | company position + layer-2 method (judgement) |
| `data/companies/csl.md` | **NO** | company narrative |
| `data/companies/csl_documents.yaml` | yes (8.5KB) | document register |
| `data/financials/csl.yaml` | yes (5.5KB) | curated layer-1 financials (a SUMMARY — check for raw sources too) |
| `data/financials/csl_*.csv` | **1 file(s)** | RAW feed export — multi-year statements live here, not in the yaml |
| `data/financials/historical/csl/` | **7 document(s)** | primary source PDFs (annual reports, statutory accounts, presentations) |
| `analyses/csl/` | yes | 6 workbook(s); subdirs: valuations |

## Data directory

  - **companies/**
    - `csl.yaml` (30.4KB)
    - `csl_documents.yaml` (8.5KB)
    - `dnl.md` (13.7KB)
    - `dnl.yaml` (34.1KB)
    - `dnl_documents.yaml` (8.7KB)
    - `wbc.md` (7.7KB)
    - `wbc.yaml` (36.1KB)
    - `wbc_documents.yaml` (20.3KB)
  - **financials/**
    - `anz_eodhd_fundamentals_2026-06-15.csv` (167.3KB)
    - `cba_eodhd_fundamentals_2026-06-15.csv` (145.3KB)
    - `csl.yaml` (5.5KB)
    - `csl_eodhd_fundamentals_2026-06-15.csv` (157.7KB)
    - `dnl.yaml` (9.6KB)
    - `mqg_eodhd_fundamentals_2026-06-15.csv` (152.0KB)
    - `nab_eodhd_fundamentals_2026-06-15.csv` (179.0KB)
    - `wbc.yaml` (1.9KB)
    - `wbc_eodhd_fundamentals_2026-06-15.csv` (182.5KB)
    - **historical/**
  - **impact_matrix/**
    - **by_industry/**
      - `australian_major_banks.yaml` (19.1KB)
      - `industrial_explosives.yaml` (26.8KB)
      - `plasma_derived_therapies.yaml` (11.2KB)
      - `specialty_pharmaceuticals.yaml` (5.1KB)
      - `vaccines.yaml` (4.3KB)
  - **industries/**
    - `australian_major_banks.md` (7.4KB)
    - `australian_major_banks.yaml` (15.8KB)
    - `industrial_explosives.md` (14.6KB)
    - `industrial_explosives.yaml` (9.9KB)
    - `plasma_derived_therapies.yaml` (7.2KB)
    - `specialty_pharmaceuticals.yaml` (2.2KB)
    - `vaccines.yaml` (2.9KB)
  - **scenarios/**
    - `ai_productivity_lag.md` (8.9KB)
    - `ai_productivity_lag.yaml` (9.4KB)
    - `disorderly_climate_crystallisation.md` (8.6KB)
    - `disorderly_climate_crystallisation.yaml` (10.1KB)
    - `fragmentation.md` (7.9KB)
    - `fragmentation.yaml` (10.0KB)
    - `muddle_through.md` (8.1KB)
    - `muddle_through.yaml` (8.6KB)
    - `orderly_convergence.md` (7.0KB)
    - `orderly_convergence.yaml` (9.0KB)
    - `stagflation_persists.md` (6.9KB)
    - `stagflation_persists.yaml` (9.1KB)

## Design and methodology

  - `architecture.md` (137.0KB)
  - `build_plan.html` (15.3KB)
  - `engine_implementation_plan.md` (16.5KB)
  - `open_items.css` (3.5KB)
  - `open_items.json` (22.1KB)
  - `open_questions.json` (1.2KB)
  - `scenarios_workshop.md` (13.6KB)
  - `scenarios_workshop_prep.md` (19.7KB)
  - `single_source_of_truth.md` (16.7KB)
  - `ui_design_brief.md` (10.1KB)
  - `writing_style.md` (4.7KB)
  - **frameworks/**
    - `five_forces_questions.md` (47.8KB)
    - `payor_and_regulator.md` (17.3KB)
  - **methodology/**
    - `csl_cost_of_debt_and_target_structure.md` (13.4KB)
    - `csl_discount_rate_fork.md` (11.0KB)
    - `dnl_working_capital_derivation.md` (10.2KB)
    - `equity_bridge_and_valuation_mechanics.md` (69.6KB)
    - `working_capital_treatment.md` (15.4KB)
  - **reference/**
    - **discount_rate_iers/**
      - `Oil-Search-and-Santos Scheme-Booklet.pdf` (20.0MB)
      - `Realm Resources Ltd (4153).pdf` (305.6KB)
      - `Universal Coal Target's Statement.pdf` (7.2MB)
      - `Woodsied BHP Petroleum.pdf` (17.4MB)
  - **reviews/**
    - `full_project_review_2026-08-13.md` (23.2KB)
    - `methodology_v0_7_proposal_2026-06-25.md` (5.3KB)
    - `review_tracker_2026-08-13.html` (24.3KB)
    - `review_tracker_2026-08-13.md` (19.2KB)
    - `triage_full_project_review_2026-08-13_opus.md` (31.6KB)
    - `vcc_valuations_rev1_response_2026-05-16.md` (12.1KB)
  - **schemas/**
    - `assumption_set.schema.json` (12.0KB)
    - `company_override.schema.json` (7.9KB)
    - `company_position.schema.json` (22.2KB)
    - `driver_catalogue.schema.json` (5.7KB)
    - `driver_movement_set.schema.json` (13.2KB)
    - `impact_matrix.schema.json` (6.7KB)
    - `industry_archetype.schema.json` (26.2KB)
    - `scenario.schema.json` (11.9KB)

## Source code

  - **vcc_valuations/**
    - `__init__.py` (667B)
    - `derivation.py` (4.4KB)
    - `translator.py` (37.2KB)
    - **assumptions/**
      - `__init__.py` (775B)
      - `wacc.py` (6.0KB)
    - **dcf/**
      - `__init__.py` (51B)
      - `bank_engine.py` (10.7KB)
      - `fcf_engine.py` (20.1KB)
      - `fcf_stub.py` (10.1KB)
      - `segment_engine.py` (9.7KB)
    - **market/**
      - `__init__.py` (629B)
      - `fmp_client.py` (5.8KB)
      - `implied_emrp.py` (5.4KB)
    - **schemas/**
      - `__init__.py` (3.3KB)
      - `assumption.py` (4.1KB)
      - `common.py` (5.1KB)
      - `company.py` (11.7KB)
      - `driver.py` (4.1KB)
      - `frameworks.py` (4.5KB)
      - `industry.py` (7.6KB)
      - `linkage.py` (7.1KB)
      - `scenario.py` (5.0KB)

## Tests

  - `__init__.py` (0B)
  - `conftest.py` (1.3KB)
  - `ssot_lint_baseline.json` (6.4KB)
  - `test_adjustments.py` (1.6KB)
  - `test_archetypes_validate.py` (1.6KB)
  - `test_comps.py` (670B)
  - `test_csl_loads.py` (2.0KB)
  - `test_dcf.py` (1.4KB)
  - `test_derivation.py` (1.3KB)
  - `test_implied_emrp.py` (2.2KB)
  - `test_ssot_lint.py` (15.7KB)
  - `test_three_statement.py` (717B)
  - `test_wbc_loads.py` (2.1KB)
  - **dcf/**
    - `__init__.py` (0B)
    - `test_csl_segment.py` (2.6KB)
    - `test_dnl_all_scenarios.py` (3.5KB)
    - `test_dnl_mt_from_data.py` (9.7KB)
    - `test_dnl_mt_ratified.py` (5.3KB)
    - `test_e2e_dnl_mt.py` (4.3KB)
    - `test_per_year_derivations.py` (2.3KB)
    - `test_scenario_goldens.py` (6.5KB)
    - `test_wbc_bank.py` (2.5KB)
    - **golden/**
      - `__init__.py` (0B)
      - `_recalc.py` (4.2KB)
      - `dnl_mt_inputs.py` (4.5KB)
      - `dnl_mt_v6.json` (2.6KB)
  - **schemas/**
    - `__init__.py` (0B)
    - `test_models.py` (5.1KB)
    - `test_scenarios.py` (2.0KB)

## UI generator

  - `csl_scenario_interface.html` (190.3KB)
  - `dnl_scenario_interface.html` (235.9KB)
  - `wbc_scenario_interface.html` (190.9KB)
  - **_generator/**
    - `README.md` (893B)
    - `beta_data.py` (10.0KB)
    - `build_cfgs.py` (91.3KB)
    - `cfgs_gen.json` (207.7KB)
    - `engine_workbook.py` (82.5KB)
    - `gen_ui.py` (120.0KB)

## Analyses (workbooks)

  - **csl/**
    - `csl_discussion_v1_2026-06-25.docx` (17.8KB)
    - `csl_discussion_v1_2026-06-25.pdf` (125.4KB)
    - `thesis.md` (20.3KB)
    - **valuations/**
      - `csl_muddle_through_valuation_v1.xlsx` (14.2KB)
      - `csl_muddle_through_valuation_v2.xlsx` (16.2KB)
      - `csl_muddle_through_valuation_v3.xlsx` (16.5KB)
      - `csl_muddle_through_valuation_v4.xlsx` (16.7KB)
      - `csl_scenarios_comparison_v1.xlsx` (25.2KB)
      - `csl_scenarios_comparison_v2.xlsx` (27.3KB)
  - **dnl/**
    - `dnl_briefing_pack_2026-05-29.docx` (20.0KB)
    - `dnl_briefing_pack_2026-05-29.pdf` (149.0KB)
    - `dnl_briefing_pack_2026-05-29_v3.docx` (20.3KB)
    - `dnl_briefing_pack_2026-05-29_v3.pdf` (150.7KB)
    - `dnl_briefing_pack_v4_2026-06-09.docx` (21.3KB)
    - `dnl_briefing_pack_v4_2026-06-09.pdf` (155.1KB)
    - `dnl_discussion_2026-06-09.docx` (20.3KB)
    - `dnl_discussion_2026-06-09.pdf` (157.9KB)
    - `dnl_discussion_v2_2026-06-09.docx` (18.8KB)
    - `dnl_discussion_v2_2026-06-09.pdf` (142.5KB)
    - `dnl_discussion_v3_2026-06-09.docx` (20.9KB)
    - `dnl_discussion_v3_2026-06-09.pdf` (184.4KB)
    - `dnl_discussion_v4_2026-06-09.docx` (20.9KB)
    - `dnl_discussion_v4_2026-06-09.pdf` (184.3KB)
    - `dnl_discussion_v5_2026-06-09.docx` (22.1KB)
    - `dnl_discussion_v5_2026-06-09.pdf` (200.1KB)
    - `dnl_discussion_v6_2026-06-09.docx` (22.5KB)
    - `dnl_discussion_v6_2026-06-09.pdf` (215.2KB)
    - `thesis.md` (15.0KB)
    - **scenarios/**
      - `ai_productivity_lag.md` (7.3KB)
      - `disorderly_climate_crystallisation.md` (10.8KB)
      - `fragmentation.md` (9.2KB)
      - `muddle_through.md` (6.7KB)
      - `orderly_convergence.md` (7.4KB)
      - `stagflation_persists.md` (8.0KB)
    - **valuations/**
      - `dnl_muddle_through_valuation.xlsx` (24.1KB)
      - `dnl_muddle_through_valuation_v2.xlsx` (30.1KB)
      - `dnl_muddle_through_valuation_v3.xlsx` (30.5KB)
      - `dnl_muddle_through_valuation_v4.xlsx` (34.6KB)
      - `dnl_muddle_through_valuation_v4_5forces.xlsx` (36.4KB)
      - `dnl_muddle_through_valuation_v4_final.xlsx` (36.4KB)
      - `dnl_muddle_through_valuation_v4_updated.xlsx` (35.9KB)
      - `dnl_muddle_through_valuation_v4r.xlsx` (35.9KB)
      - `dnl_muddle_through_valuation_v5_2026-06-17.xlsx` (34.8KB)
      - `dnl_muddle_through_valuation_v6_2026-06-25.xlsx` (35.1KB)
      - `dnl_scenarios_comparison.xlsx` (22.5KB)
      - `dnl_scenarios_comparison_v2.xlsx` (24.9KB)
      - `dnl_scenarios_comparison_v3.xlsx` (18.6KB)
      - `dnl_scenarios_comparison_v4.xlsx` (15.9KB)
  - **wbc/**
    - `thesis.md` (13.3KB)
    - `wbc_discussion_v1_2026-06-16.docx` (24.7KB)
    - `wbc_discussion_v1_2026-06-16.pdf` (240.5KB)
    - `wbc_discussion_v2_2026-06-17.docx` (24.8KB)
    - `wbc_discussion_v2_2026-06-17.pdf` (240.5KB)
    - `wbc_discussion_v3_2026-06-17.docx` (26.1KB)
    - `wbc_discussion_v3_2026-06-17.pdf` (247.9KB)
    - **valuations/**
      - `wbc_muddle_through_valuation_v1.xlsx` (18.2KB)
      - `wbc_muddle_through_valuation_v2.xlsx` (19.0KB)
      - `wbc_muddle_through_valuation_v3.xlsx` (15.0KB)
      - `wbc_muddle_through_valuation_v4_formulas.xlsx` (12.5KB)
      - `wbc_scenarios_comparison_v1.xlsx` (11.6KB)
      - `wbc_scenarios_comparison_v2.xlsx` (11.6KB)

## Untracked files

Not in git. Either commit them or clear them — an untracked file is invisible
to anyone who clones the repo, and is the most common way work gets lost.

- `DECISIONS.md`
- `OPEN_ITEMS.html`
- `design/open_items.css`
- `design/open_items.json`
- `design/open_questions.json`
- `notes/archive/`
- `notes/bridge/bridge_note_2026-07-22.md`
- `notes/bridge/bridge_note_2026-07-22b_ssot.md`
- `notes/bridge/bridge_note_2026-07-22c_ssot_executed.md`
- `notes/bridge/bridge_note_2026-07-25.md`
- `notes/bridge/bridge_note_2026-07-25_session-end.md`
- `notes/bridge/bridge_note_2026-08-09.md`
- `notes/bridge/bridge_note_2026-08-11.md`
- `notes/bridge/bridge_note_2026-08-12_review.md`
- `notes/bridge/bridge_note_2026-08-12_triage.md`
- `notes/bridge/bridge_note_2026-08-21.md`
- `scripts/build_open_items.py`
- `scripts/session_start.py`
- `session_start.cmd`

