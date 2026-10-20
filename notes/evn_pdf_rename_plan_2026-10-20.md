# EVN PDF rename plan (proposal, not applied)

**Status: plan only, 20 October 2026. Nothing has been renamed.** Folder: `data/financials/historical/evn/`.
Format: `YYYY-MM-DD Description.pdf`. Each date was read from the document itself (first page text, or the
auditor's signing date for the annual reports), using pypdf on 20 October 2026.

## 1. Rename table

| # | Current name | Proposed name | Date | Date source (read from the PDF) |
|---|---|---|---|---|
| 1 | `Annual_Report_2023.pdf` | `2023-08-17 Annual Report FY23.pdf` | 2023-08-17 | Auditor's independence declaration signed 17 August 2023 (PDF p113). No release date is printed on the cover. |
| 2 | `Annual_Report_2024.pdf` | `2024-08-14 Annual Report FY24.pdf` | 2024-08-14 | Auditor's independence declaration signed 14 August 2024 (PDF p170). Same basis as row 1. |
| 3 | `Annual_Report_2025.pdf` | `2025-08-13 Annual Report FY25.pdf` | 2025-08-13 | Auditor's independence declaration signed 13 August 2025 (PDF p65). Same basis as row 1. |
| 4 | `December_2025_Quarterly_Report.pdf` | `2026-01-21 Quarterly Report Dec 2025.pdf` | 2026-01-21 | "ASX Announcement 21 January 2026" (PDF p1). |
| 5 | `March_2026_Quarterly_Report.pdf` | `2026-04-15 Quarterly Report Mar 2026.pdf` | 2026-04-15 | "ASX Announcement 15 April 2026" (PDF p1). |
| 6 | `june-2026-quarterly-report.pdf` | `2026-07-15 Quarterly Report Jun 2026.pdf` | 2026-07-15 | "ASX Announcement 15 July 2026" (PDF p1). |
| 7 | `September_2026_Quarterly_Report.pdf` | `2026-10-14 Quarterly Report Sep 2026.pdf` | 2026-10-14 | "ASX Announcement 14 October 2026" (PDF p1). |
| 8 | `EVN_FY26_Half_Year_Results_Presentation.pdf` | `2026-02-11 FY26 Half Year Results Presentation.pdf` | 2026-02-11 | Cover: "11 February 2026" (PDF p1). |
| 9 | `EVN_FY26_Full_Year_Financial_Results_Presentation.pdf` | `2026-08-19 FY26 Full Year Results Presentation.pdf` | 2026-08-19 | "ASX Announcement 19 August 2026" (PDF p1). |
| 10 | `evn_fy26_full_year_financial_results_and_final_dividend.pdf` | `2026-08-19 FY26 Full Year Results and Final Dividend.pdf` | 2026-08-19 | "ASX Announcement 19 August 2026" (PDF p1). |
| 11 | `EVN_2026_Investor_Briefing_Presentations.pdf` | `2026-09-15 Investor Briefing Presentations.pdf` | 2026-09-15 | "ASX Announcement 15 September 2026" (PDF p1). |
| 12 | `annual_mineral_resources_and_ore_reserves_statement.pdf` | `2026-05-01 Mineral Resources and Ore Reserves Statement.pdf` | 2026-05-01 | "ASX Announcement 1 May 2026" (PDF p1). |

Open points before renaming:
- Rows 1 to 3 use the auditor's signing date. The release date is not printed in the file. If the
  ASX lodgement date is wanted, it must come from the ASX announcements page, not from this folder.
- Rows 10 and 9 share a date. The suffix keeps them apart.
- The PDF metadata dates are not used. For example, the June quarterly metadata reads 12 October 2026,
  which does not match its printed 15 July 2026.

## 2. References to the current names (to update with the rename)

Nothing is renamed yet, so each reference below will break on the day the rename happens.

| File | Line(s) | Current name it holds |
|---|---|---|
| `data/companies/evn_documents.yaml` | 11 to 22 | `filename:` for all twelve PDFs. This is the register of the folder and needs every row changed. |
| `data/financials/evn.yaml` | 52 | `EVN_FY26_Full_Year_Financial_Results_Presentation.pdf` (slide 7 source) |
| `data/financials/evn.yaml` | 162 | `annual_mineral_resources_and_ore_reserves_statement.pdf` (Cowal JORC source) |
| `data/financials/evn.yaml` | 178 | `Annual_Report_2025.pdf` (Note 22 source) |
| `data/financials/historical/evn/_extract_notes_2026-10-20.md` | 8 to 12 | Eight of the names, written as the short names MROR, FYR, FYP, HYP, JQ, SQ, IB and AR25 |
| `design/methodology/evn_cost_vs_gold_evidence_2026-10-20.md` | 15 | `Annual_Report_2023/2024/2025.pdf` and `june-2026-quarterly-report.pdf` (short names AR23, AR24, AR25, JQ) |
| `design/methodology/evn_review_2026-10-20.md` | 110 | `evn_fy26_full_year_financial_results_and_final_dividend.pdf` |

Not affected by the rename (they name the folder only, not a file):
- `data/companies/evn_documents.yaml` line 8 and `data/financials/evn.yaml` line 3 (the folder, and
  `_extract_notes_2026-10-20.md`, which is not renamed)
- `notes/bridge/bridge_note_2026-10-20c_evn_batch3.md` line 31
- `notes/bridge/bridge_note_2026-10-20_evn.md` line 13
- `REPO_MAP.md` line 400

No script in `scripts/` or `src/` names a file in this folder or globs it. Checked with grep for each
name and for `historical/evn`.
