# Item (c): CSL volume/price split and US real GDP: draft for approval (15 Oct 2026)

Status: APPROVED and WIRED 15 Oct 2026 (DECISIONS.md D-82). Correction below. Stephen has said yes to the
recommendations below. Each US path still needs his approval before it is wired in.

## 1. The problem

Each CSL segment (Behring, Seqirus, Vifor) grows at one nominal rate. That rate is world
real GDP plus advanced CPI plus a gap. The model does not show how much of that growth
is more units sold (volume) and how much is higher prices (price). Pricing for healthcare
products can run ahead of CPI, so the split matters once a healthcare price view is set.

## 2. Recommendation for the price split

Use advanced CPI as the price rate for now. Volume is then world real GDP plus the gap.
The nominal sum is exactly what the model already uses, so no level moves. This adds the
split with no new view. A healthcare premium over CPI can be added later, once it has a
written basis. Until then the split changes labels only.

Type of change: medium. Code and tests change. No goldens move.

## 3. Draft US real GDP paths (percent per year, Years 1, 5, 10 unless noted)

| Scenario | Current CSL driver | Draft US path | Basis (my judgement, for approval) |
|---|---|---|---|
| AI Productivity Lag | world (2.0, 1.9, 2.0) | world + 0.2 = 2.2, 2.1, 2.2 | Narrative: AI investment is US-led |
| Fragmentation | world (2.0, 2.0, 2.0) | US-aligned bloc series already in the file = 2.0, 1.8, 1.8 | File already defines this series. It covers the US-aligned bloc, not the US alone |
| Disorderly Climate | world (2.0, 2.0, 2.2) | world - 0.3 = 1.7, 1.7, 1.9 | Carbon and stranded-asset drag on a large emitter. The size of the gap is my judgement |
| Stagflation Persists | world (2.0, 1.8, 2.0) | advanced real GDP in file = 0.8, 1.2, 1.5 (Year 10 held at 1.5) | US is the largest advanced economy. The file has no US series |

Correction (15 Oct): Muddle Through and Orderly Convergence already carry a US series, but it is not flat, so both levels DO move slightly (MT +0.03%, OC -0.04%).

Type of change: serious. Moving CSL to a US driver changes its levels in four
scenarios. The goldens, workbooks and sizing sets must be re-pinned with reasons.

## 4. Questions for Stephen

1. Approve the price rate as advanced CPI (recommended).
2. Approve, change, or reject each US path in section 3.

## 5. Note for the separate chat (serious work)

Paste this into a new chat in the VCC project:

  Continue VCC Valuations, item (c). Read notes/bridge/csl_split_and_us_gdp_draft_2026-10-15.md
  and WORKING_NOTES.md first. Stephen has approved [the price rate / the US paths: list
  which]. Step 1: add the volume/price split to the three CSL segment archetypes, with price
  = advanced CPI. Confirm no level moves and the suite still passes at 672. Step 2: wire the
  approved US paths in place of the world series for those scenarios. Re-pin the CSL goldens
  with the reason in tests/dcf/test_scenario_goldens.py, regenerate the sizing sets, and
  recalc the CSL workbook in LibreOffice. Commit and push per the standing git instruction
  in WORKING_NOTES.md.
