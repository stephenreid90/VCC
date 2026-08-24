# REPO_MAP — what exists, and where

_Generated 2026-08-24 by `scripts/repo_inventory.py`. **Regenerate at the start of
a session, before reasoning about what data exists.** Do not hand-edit._

- HEAD: `9abd544 Batch 6: close all thirteen correctness, methodology and test-gap items` on `main`
- Unpushed commits: **5**
- Tracked files: 294
- Untracked files: 1

> **The rule this file exists to enforce:** a curated `*.yaml` in `data/` is a
> SUMMARY, not the source. Before concluding that data does not exist, check the
> raw feed exports in `data/financials/*.csv` and the primary documents in
> `data/financials/historical/<company>/`. Absence in the yaml is not absence.

## Per-company sources

### DNL

| Path | Present | What it is |
|---|---|---|
| `data/companies/dnl.yaml` | yes (37.4KB) | company position + layer-2 method (judgement) |
| `data/companies/dnl.md` | yes (13.5KB) | company narrative |
| `data/companies/dnl_documents.yaml` | yes (8.5KB) | document register |
| `data/financials/dnl.yaml` | yes (11.1KB) | curated layer-1 financials (a SUMMARY — check for raw sources too) |
| `data/financials/dnl_*.csv` | **NO** | RAW feed export — multi-year statements live here, not in the yaml |
| `data/financials/historical/dnl/` | **7 document(s)** | primary source PDFs (annual reports, statutory accounts, presentations) |
| `analyses/dnl/` | yes | 14 workbook(s); subdirs: scenarios, valuations |

### WBC

| Path | Present | What it is |
|---|---|---|
| `data/companies/wbc.yaml` | yes (35.9KB) | company position + layer-2 method (judgement) |
| `data/companies/wbc.md` | yes (7.6KB) | company narrative |
| `data/companies/wbc_documents.yaml` | yes (19.9KB) | document register |
| `data/financials/wbc.yaml` | yes (1.9KB) | curated layer-1 financials (a SUMMARY — check for raw sources too) |
| `data/financials/wbc_*.csv` | **1 file(s)** | RAW feed export — multi-year statements live here, not in the yaml |
| `data/financials/historical/wbc/` | **10 document(s)** | primary source PDFs (annual reports, statutory accounts, presentations) |
| `analyses/wbc/` | yes | 6 workbook(s); subdirs: valuations |

### CSL

| Path | Present | What it is |
|---|---|---|
| `data/companies/csl.yaml` | yes (33.4KB) | company position + layer-2 method (judgement) |
| `data/companies/csl.md` | **NO** | company narrative |
| `data/companies/csl_documents.yaml` | yes (8.3KB) | document register |
| `data/financials/csl.yaml` | yes (7.6KB) | curated layer-1 financials (a SUMMARY — check for raw sources too) |
| `data/financials/csl_*.csv` | **1 file(s)** | RAW feed export — multi-year statements live here, not in the yaml |
| `data/financials/historical/csl/` | **7 document(s)** | primary source PDFs (annual reports, statutory accounts, presentations) |
| `analyses/csl/` | yes | 6 workbook(s); subdirs: valuations |

## Data directory

  - **companies/**
    - `csl.yaml` (33.4KB)
    - `csl_documents.yaml` (8.3KB)
    - `dnl.md` (13.5KB)
    - `dnl.yaml` (37.4KB)
    - `dnl_documents.yaml` (8.5KB)
    - `wbc.md` (7.6KB)
    - `wbc.yaml` (35.9KB)
    - `wbc_documents.yaml` (19.9KB)
  - **financials/**
    - `anz_eodhd_fundamentals_2026-06-15.csv` (167.3KB)
    - `cba_eodhd_fundamentals_2026-06-15.csv` (145.3KB)
    - `csl.yaml` (7.6KB)
    - `csl_eodhd_fundamentals_2026-06-15.csv` (157.7KB)
    - `dnl.yaml` (11.1KB)
    - `mqg_eodhd_fundamentals_2026-06-15.csv` (152.0KB)
    - `nab_eodhd_fundamentals_2026-06-15.csv` (179.0KB)
    - `wbc.yaml` (1.9KB)
    - `wbc_eodhd_fundamentals_2026-06-15.csv` (182.5KB)
    - **historical/**
  - **impact_matrix/**
    - **by_industry/**
      - `australian_major_banks.yaml` (18.5KB)
      - `industrial_explosives.yaml` (26.1KB)
      - `plasma_derived_therapies.yaml` (11.2KB)
      - `specialty_pharmaceuticals.yaml` (5.1KB)
      - `vaccines.yaml` (4.3KB)
  - **industries/**
    - `australian_major_banks.md` (7.3KB)
    - `australian_major_banks.yaml` (15.5KB)
    - `industrial_explosives.md` (14.5KB)
    - `industrial_explosives.yaml` (9.6KB)
    - `plasma_derived_therapies.yaml` (7.1KB)
    - `specialty_pharmaceuticals.yaml` (2.1KB)
    - `vaccines.yaml` (2.8KB)
  - **scenarios/**
    - `ai_productivity_lag.md` (8.8KB)
    - `ai_productivity_lag.yaml` (9.2KB)
    - `disorderly_climate_crystallisation.md` (8.6KB)
    - `disorderly_climate_crystallisation.yaml` (9.9KB)
    - `fragmentation.md` (7.8KB)
    - `fragmentation.yaml` (9.8KB)
    - `muddle_through.md` (8.0KB)
    - `muddle_through.yaml` (8.4KB)
    - `orderly_convergence.md` (6.9KB)
    - `orderly_convergence.yaml` (8.8KB)
    - `stagflation_persists.md` (6.9KB)
    - `stagflation_persists.yaml` (8.9KB)

## Design and methodology

  - `architecture.md` (137.0KB)
  - `build_plan.html` (14.9KB)
  - `engine_implementation_plan.md` (16.5KB)
  - `open_items.css` (3.5KB)
  - `open_items.json` (23.8KB)
  - `open_questions.json` (1.2KB)
  - `scenarios_workshop.md` (13.5KB)
  - `scenarios_workshop_prep.md` (19.5KB)
  - `single_source_of_truth.md` (16.7KB)
  - `ui_design_brief.md` (10.1KB)
  - `writing_style.md` (4.6KB)
  - **frameworks/**
    - `five_forces_questions.md` (47.4KB)
    - `payor_and_regulator.md` (17.1KB)
  - **methodology/**
    - `csl_cost_of_debt_and_target_structure.md` (13.4KB)
    - `csl_discount_rate_fork.md` (11.0KB)
    - `dnl_working_capital_derivation.md` (11.2KB)
    - `equity_bridge_and_valuation_mechanics.md` (70.6KB)
    - `working_capital_treatment.md` (23.3KB)
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
    - `vcc_valuations_rev1_response_2026-05-16.md` (12.0KB)
  - **schemas/**
    - `assumption_set.schema.json` (11.5KB)
    - `company_override.schema.json` (7.6KB)
    - `company_position.schema.json` (21.4KB)
    - `driver_catalogue.schema.json` (5.5KB)
    - `driver_movement_set.schema.json` (12.7KB)
    - `impact_matrix.schema.json` (6.5KB)
    - `industry_archetype.schema.json` (25.2KB)
    - `scenario.schema.json` (11.5KB)

## Source code

  - **vcc_valuations/**
    - `__init__.py` (650B)
    - `derivation.py` (4.4KB)
    - `translator.py` (48.7KB)
    - **assumptions/**
      - `__init__.py` (775B)
      - `wacc.py` (6.0KB)
    - **dcf/**
      - `__init__.py` (50B)
      - `bank_engine.py` (10.7KB)
      - `fcf_engine.py` (25.0KB)
      - `fcf_stub.py` (9.8KB)
      - `segment_engine.py` (10.0KB)
    - **market/**
      - `__init__.py` (606B)
      - `fmp_client.py` (5.7KB)
      - `implied_emrp.py` (5.3KB)
    - **schemas/**
      - `__init__.py` (3.1KB)
      - `assumption.py` (4.0KB)
      - `common.py` (4.9KB)
      - `company.py` (11.7KB)
      - `driver.py` (4.0KB)
      - `frameworks.py` (4.4KB)
      - `industry.py` (9.1KB)
      - `linkage.py` (6.9KB)
      - `scenario.py` (4.8KB)

## Tests

  - `__init__.py` (0B)
  - `conftest.py` (1.3KB)
  - `ssot_intra_file_baseline.json` (593B)
  - `ssot_lint_baseline.json` (6.3KB)
  - `test_adjustments.py` (1.6KB)
  - `test_archetypes_validate.py` (3.5KB)
  - `test_comps.py` (653B)
  - `test_csl_loads.py` (2.0KB)
  - `test_dcf.py` (1.4KB)
  - `test_derivation.py` (1.3KB)
  - `test_engine_workbook.py` (4.6KB)
  - `test_implied_emrp.py` (2.1KB)
  - `test_ssot_lint.py` (24.1KB)
  - `test_three_statement.py` (694B)
  - `test_wbc_loads.py` (2.1KB)
  - `test_workbook_recalc_live.py` (3.3KB)
  - `test_working_capital.py` (2.8KB)
  - **dcf/**
    - `__init__.py` (0B)
    - `test_csl_segment.py` (2.9KB)
    - `test_csl_workbook_tie.py` (3.7KB)
    - `test_dnl_all_scenarios.py` (3.6KB)
    - `test_dnl_mt_from_data.py` (9.9KB)
    - `test_dnl_mt_ratified.py` (5.7KB)
    - `test_dnl_workbook_tie.py` (4.1KB)
    - `test_e2e_dnl_mt.py` (4.3KB)
    - `test_engine_input_validation.py` (3.4KB)
    - `test_per_year_derivations.py` (3.8KB)
    - `test_scenario_goldens.py` (7.7KB)
    - `test_wbc_bank.py` (2.5KB)
    - **golden/**
      - `__init__.py` (0B)
      - `_recalc.py` (4.2KB)
      - `_recalc_generated_workbooks.py` (6.3KB)
      - `csl_workbook_all_scenarios.json` (6.6KB)
      - `dnl_mt_inputs.py` (4.9KB)
      - `dnl_mt_v6.json` (2.6KB)
      - `dnl_workbook_all_scenarios.json` (10.3KB)
  - **schemas/**
    - `__init__.py` (0B)
    - `test_models.py` (4.9KB)
    - `test_scenarios.py` (2.0KB)

## UI generator

  - `csl_scenario_interface.html` (159.9KB)
  - `dnl_scenario_interface.html` (206.4KB)
  - `wbc_scenario_interface.html` (159.6KB)
  - **_generator/**
    - `README.md` (893B)
    - `beta_data.py` (10.0KB)
    - `build_cfgs.py` (91.9KB)
    - `cfgs_gen.json` (210.3KB)
    - `engine_workbook.py` (88.1KB)
    - `gen_ui.py` (88.7KB)

## Analyses (workbooks)

  - **csl/**
    - `csl_discussion_v1_2026-06-25.docx` (17.8KB)
    - `csl_discussion_v1_2026-06-25.pdf` (125.4KB)
    - `thesis.md` (21.4KB)
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
    - `thesis.md` (22.3KB)
    - **scenarios/**
      - `ai_productivity_lag.md` (7.2KB)
      - `disorderly_climate_crystallisation.md` (10.7KB)
      - `fragmentation.md` (9.1KB)
      - `muddle_through.md` (6.7KB)
      - `orderly_convergence.md` (7.3KB)
      - `stagflation_persists.md` (7.9KB)
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
    - `thesis.md` (13.2KB)
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

- `tests/ssot_intra_file_baseline.json`

