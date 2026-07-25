# Single-source-of-truth protocol

**Status:** draft for owner review · 22 July 2026 · not in force
**Owner ruling embedded:** one β and one WACC per company per valuation date (22 July 2026)

The rule: **whenever a number is needed, there is exactly one place the answer can come from.**

---

## 1. What went wrong

β *was* settled. But the settled answer lived in cell B71 of an `.xlsx`, and nothing in the
system can read a spreadsheet cell. So every consumer that needed a β made its own copy. None
could tell it was stale, because a stored number carries no link back to what produced it.

Two failures compound.

1. **We stored answers rather than methods.** Had we stored the *method* — peer triangulation
   over a named cluster, stated exclusions, stated index, Hamada unlever then re-lever at subject
   gearing — there would only ever have been one β, computed on demand rather than typed.
2. **The store was in a format its consumers cannot read.** A number only a human can look up
   will be copied by every machine that needs it.

Why storing answers fails, in one line: β depends on gearing, gearing on equity market value,
equity market value on the share count. Under a stored-method regime, settling the share count
*recomputes* β. Under the regime we have, it silently leaves β wrong.

### 1.1 What is actually drifting

Not every disagreement between artefacts is drift. Three different things look alike on a grep
and need different remedies.

**(a) Genuine drift — one quantity, one date, two or more stored values.**

| Figure | Engine + workbook | `data/financials/dnl.yaml` | UI generator + HTML |
|---|---|---|---|
| β | 0.95 | 1.10 | 1.10 |
| Shares outstanding | 1,770 | 1,875.9 (and 1,884 at `:182`) | 1,884 |
| WACC | 8.2755% | 8.68% / 8.82% | 8.68% |
| Base EBIT margin | 14.1% | 13.5% (`:44`) | 13.5% |

Four quantities, not eight. Read strictly on *structured fields* — which cross-cutting convention 3
makes the source of truth — only β and margin genuinely agree between `dnl.yaml` and the UI; the
1,884 and 8.68% attributed to `dnl.yaml` appear only inside prose rationale strings (`:182`,
`:151-155`), while its structured values are 1,875.9 and `computed_wacc: 0.0882`. So the tidy
"workbook versus everything else" framing does not survive contact with the file: `dnl.yaml` is
**internally inconsistent with itself**, carrying a WACC derived from a β it no longer states.

The EBIT-margin row also needs care: the UI holds *both* 13.5% (`build_cfgs.py:146`, labelled
"normalised") and 14.1% (`:165`, `baseMargin` in the Muddle Through block), resting on different
revenue bases — so it is arguably a basis mismatch per (b) rather than clean drift.

**(b) Basis mismatch — different quantities wearing the same name.** No storage rule fixes these.

1. **Revenue 3,400 vs 3,905** is not drift: continuing operations excluding Phosphate Hill versus
   TTM including it, the gap being that business. Already ruled on. (4,139 is FY27, not a base.)
2. **Net debt 1,260.8 / 1,300 / 1,512 / 1,810** — anchor-date ex-leases; normalised steady state;
   lease-inclusive; reported at 30 September 2025.
3. **EV 7,736.6 / 8,064 / 7,681.5** — bottom-up DCF; reduced-form reconstruction; market EV.

**(c) Date mismatch.** Leases 194.3 (31 March 2026) versus 211.5 (30 September 2025).

Basis mixing, not stale copying, looks like the more persistent failure — which is why §5 treats
basis labelling as a first-class rule rather than a nicety.

**Also found:** the UI simultaneously asserts single-WACC discipline (`build_cfgs.py:72,142`) and
offers per-scenario assessed rates (`dnl_scenario_interface.html:418`).
`src/vcc_valuations/dcf/fcf_engine.py` carries no company-specific *data* — only dataclass defaults
(`wacc: … = 0.085`, `terminal_growth: … = 0.025`) and `0.141` in a docstring. Substantially compliant,
though those defaults should arguably be removed so a missing input fails loudly rather than silently.

---

## 2. The three layers

Every number belongs to exactly one. Most of the drift above is a layer-2 quantity stored as
though it were layer 1.

**Layer 1 — Observed data.** Facts we did not choose: reported financials, net debt at a date, the
share register, market price, peer betas and gearings, statutory rates.
*Lives in* `data/financials/<company>.yaml` and the feed exports beside it.
*Machine-written, never hand-edited.* Overwritten wholesale on refresh. Carries an as-at date and
a source, nothing more.

**Layer 2 — Method and selection.** The repeatable rules and the choices that parameterise them:
that β is derived by peer triangulation; which peers and why each exclusion; which index; the
margin-glide construction; the revenue basis; the tax-glide convention.
*Lives in* `data/companies/<company>.yaml`, with the rules themselves in `design/methodology/`.
*Hand-written, never machine-written.* Changes deliberately; supersession is explicit.
Carries rationale, methodology reference, decided-on date, status.

Layer 2 is **not** a register of numbers. If a value can be computed from layer 1 by a stated
rule, the rule belongs here and the value does not.

**Layer 3 — Derived values.** Everything the engine computes: β, cost of equity, WACC, the FCFF
vector, EV, the equity bridge, value per share.
*Written by the engine and nothing else.* Recomputed on demand. Anything persisted is a **cache**,
stamped with the inputs that produced it and regenerable by a documented command. Never
hand-typed anywhere, including in prose and comments.

---

## 3. Where things live

An earlier draft proposed a new `data/method/` register. **That was wrong and is withdrawn** — it
would have created a third home for content that already has one. The split this protocol needs
already exists in the directory structure; we simply have not been honouring it.

```
data/financials/<company>.yaml   layer 1   machine-written  (header already reads
data/financials/*_eodhd_*.csv    layer 1   machine-written   "data_source: EODHD fundamentals")
data/companies/<company>.yaml    layer 2   hand-written, reviewed
design/methodology/*.md          layer 2   the rules themselves
src/vcc_valuations/              engine    no company numbers, ever
tests/dcf/golden/*.json          cache     pinned oracle, regenerated deliberately
ui_prototypes/_generator/        export    consumes engine output
analyses/**/*.xlsx               export    generated rendering, not a source
```

**The one concrete migration — and it is a split, not a move.** `data/financials/dnl.yaml` lines
42–199 hold `normalised_baseline`: margin, net debt, capex, tax, D&A, the whole `wacc_build`
including β, and terminal growth. It sits in a file whose header declares it a machine-generated
EODHD export.

But the block is not uniformly layer 2 — it is a microcosm of the whole problem, containing all
three layers at once:

| Content | Layer | Disposition |
|---|---|---|
| `ebit_margin`, `net_debt`, `capex_pct_revenue`, `tax_rate`, `da_pct_revenue`, `terminal_growth`, β selection rationale | 2 | move to `data/companies/` |
| `risk_free_rate`, `beta_measured`, `beta_peer_dataset_v0_6_backport`, `equity_market_value` (`:179`), `debt_market_value` | 1 | stay in `data/financials/`, sourced from the feed |
| `computed_wacc: 0.0882` (`:189`) | 3 | **delete** — the engine computes it |

That last row is worth dwelling on. `computed_wacc: 0.0882` sits eleven lines below `beta: 1.10`,
and its own preceding comment derives it from `4.30% + 1.15 × 5.00%` — a **superseded** β. A stored
derived value, wrong, adjacent to the input that should have updated it. Also `beta_measured: 0.36`
(`:105`) duplicates `market_data.beta: 0.359` (`:341`) in the same file.

Two consumers repoint: `src/vcc_valuations/translator.py:225` and `scripts/run_smoke_test.py:45,74`.

`csl.yaml` needs the same treatment (its `normalised_baseline` includes `shares_outstanding: 478.9`,
observed). **There is no `data/financials/wbc.yaml`** — only `data/companies/wbc.yaml` — so WBC has
nothing to migrate.

**Caveat on layer-1 purity.** `csl.yaml`'s own header reads `base_year_status:
workbook_reverse_engineered` and `data_source: "curated from csl_muddle_through_valuation_v4.xlsx"`.
It is hand-curated end to end. So rule 3 describes where we are going, not where we are: for CSL,
the layer-1 file is presently a hand-authored artefact derived from an *export*, which is a
circularity that has to be broken before the refresh-safety argument holds for it.

Once split, layer 2 needs only decision dates and status added to reach the §5 provenance standard.

---

## 4. The rules

1. **No derived value is ever hand-typed** — prose, comments, test fixtures, decks and UI alike.
   Acceptance constants in tests are allow-listed explicitly, so the exemption is visible in review.
2. **Register the method, not the answer.** A stored number in layer 2 is a defect.
3. **Layer 1 is machine-written and never hand-edited**, so a feed refresh can overwrite the whole
   file with no risk to judgement. This is the structural reason the layers live in separate files:
   once refreshes are automated, care is not a mechanism.
4. **Layer 2 is hand-edited and never machine-written.**
5. **Persisted derived values are caches** — provenance-stamped and regenerable, or deleted.
6. **One β and one WACC per company per valuation date.** Scenarios differ in cash flows, not in
   discount rate. Strict reading of cross-cutting convention 1, and it removes the circularity that
   scenario-varying gearing would introduce. *Owner ruling, 22 July 2026.*
7. **Every persisted valuation quantity carries a basis label** (continuing versus reported;
   ex-lease versus lease-inclusive; DCF versus market), and the lint refuses to compare quantities
   whose labels differ. Addresses §1.1(b), which storage rules alone cannot.
8. **Every layer-2 entry carries provenance** — rationale, methodology reference, decided-on date,
   status. Schema-enforced.
9. **Exports are downstream and never authoritative** — rendered UI, generated docs, workbooks.
10. **Session overrides are recorded, scoped and labelled**, showing the method-derived value
    alongside, and never write back to layer 2. *(Distinct from the persisted company-versus-archetype
    overrides that cross-cutting convention 5 budgets at ≤20% of cells; the two senses of "override"
    need separate names before either is mechanised.)*

---

## 5. Enforcement

1. **Hardcoded-number lint** over everything outside layer 1. Note `scripts/workbook_lint.py`
   already implements orphan-input and terminal-continuity checks over the yellow/blue Assumptions
   palettes, so this extends an existing surface rather than starting one. and the pinned caches, with an
   explicit allow-list annotation for docstrings and acceptance constants.
2. **Golden-master tie** — `test_e2e_dnl_mt.py` pins engine output; regenerating the JSON is a
   deliberate, reviewed act.
3. **Layer-2 schema validation** — rationale, reference, date, status, or the build fails.
4. **Basis-label and date-pairing checks.** Note methodology §5.3 only *proposes* that
   `shares_outstanding_at` equal `net_debt_at`; neither field exists in `dnl.yaml` and no code
   checks it — itself an instance of the decay this document is about.
5. **Provenance stamps on every export**, naming engine version and input hash, so a stale
   rendering is visible rather than plausible.

---

## 6. The workbook

Standing rule 1 requires formulas rather than Python-computed values, with yellow input cells that
can be flexed by hand. A workbook that is purely a layer-3 rendering has no input cells and nothing
to flex. The resolution: **the Assumptions sheet renders layers 1 and 2 as values; every other
sheet renders as formulas referencing it** — never as engine-computed constants, and preserving the
archetype-baseline and company-offset rows as separate inputs with the company figure derived.

Three problems remain open and are not solved by this document:

1. `scripts/export_excel.py` writes EV, equity value and price per share as literal cell values —
   precisely the prohibited pattern.
2. No formula-driven workbook generator exists in `scripts/`, `src/` or the M2 scope — but one
   *partially* exists in the UI: `dnl_scenario_interface.html` embeds an OOXML writer (`VCCXLSX`)
   with a formula constructor `Ff()` that emits an Assumptions sheet plus formula-built Comparables,
   Discount-Rate and DCF sheets, including Hamada unlever/re-lever. The work is to move that
   capability server-side and point it at engine output, not to build it from nothing.
3. A workbook flexed by hand in Excel produces a number with no home under rule 9 — the
   stored-answer failure relocated downstream. Either rule 10 extends to it, or flexed workbooks are
   declared scratchpads whose outputs may not be quoted.

**Standing.** The v6 workbook currently serves as the engine's test oracle. That was a legitimate
bootstrap — it was hand-built and audited before an engine existed. Going forward it is an export,
and `golden/dnl_mt_v6.json` is the pinned oracle in its own right, frozen by decree, with
`_recalc.py` retained only as the documented regenerator against the archived v6 file. Regenerating
the oracle from an artefact the engine produces would be circular.

---

## 7. Relationship to the milestone plan

Per `design/engine_implementation_plan.md` §1.1–1.2, `linkage/` runs first (scenario + archetype +
company + impact matrix → `DriverMovementSet`, producing no numbers), then `assumptions/` translates
that against layers 1 and 2 into an `AssumptionSet`, which resolves into `FcfEngineInputs`.

**Scoping honesty.** This protocol is not simply "the input contract M2 was always going to need" —
that framing was overstated. M2 as planned is scenario-translation machinery and does not separate
observed data from method. This is adjacent work that M2 will consume. It carries one genuinely new
requirement: computing β on demand needs a peer-triangulation derivation *and* a layer-1 peer feed
(peer betas, gearings, tax rates) that no company financials file supplies. Indicative peer betas also sit in
`dnl.yaml:133-160`, but peer *gearings and tax rates* live only in
`ui_prototypes/_generator/beta_data.py`, flagged MOCK — it must move into layer 1 and
be fed by Ben's pipeline.

---

## 8. Open items

1. **Decide β.** Open, and reserved to the owner. The re-levering analysis narrows nothing: across
   the two index bases and two candidate gearings the re-levered cluster median runs roughly
   0.96–1.05. That range **excludes both stored answers** — it is neither 0.95 nor 1.10. On the world
   index, the workbook's own stated convention for >30% non-AU revenue, it returns 1.01–1.05.
   An earlier draft claimed this vindicated 0.95 and retired 1.10 as an error; **that claim is
   withdrawn as cherry-picked.** The honest reading is that the method produces a *third* number and
   both stored answers are stale — which is the protocol's thesis rather than an argument for either.
2. **Resolve 1,770 vs 1,875.9** with Ben. The feed contradicts itself: market capitalisation 6,390.4
   at price 3.6061 implies 1,772m, two lines from a stated 1,875.9m. Note 1,884 is not
   generator-only — `equity_market_value: 6802.0` (`:179`) is derived from it, with the working shown at `:182`.
3. **Peer data home** — where peer betas, gearings and tax rates live as layer 1, and when Ben's
   pull replaces the mock.
4. **Workbook generator** — scope and build it, or drop §6's formula requirement.
5. **Valuation-date stamping.** Rule 6 says one β per *valuation date*, but nothing records one.
   The related question of *which* date anchors shares and net debt is already settled by
   methodology §5 (latest reported, both paired to the same balance-sheet date; buyback not
   projected) — now surfaced as CLAUDE.md cross-cutting convention 6. Residual is **enforcement**:
   the §5.4 validator is unimplemented, and `data/financials/dnl.yaml` still lacks
   `shares_outstanding_at`/`net_debt_at`, carries a non-compliant share count (1,875.9m vs the
   §5.3 anchor of 1,770m at 31 Mar 2026) and an `equity_market_value` (6,802.0, off a phantom
   1,884m vs the compliant ~6,390 = 1,770 × 3.61). Fix belongs in the DNL β re-anchor pass.
6. **Supersession log.** Retired figures keep resurfacing in prose — 1.10, 1,884 and 3,400 appear
   across the briefing pack and four discussion-document versions with nothing marking them dead.
7. **Export proliferation.** `analyses/dnl/valuations/` holds fourteen DNL workbooks, six of them
   `_v4*`. Nothing says which is current. Most likely place a stale number is picked up next.
8. **`tests/dcf/golden/dnl_mt_inputs.py`** hand-transcribes β, shares, net debt and revenue from
   workbook cells. Bring under the protocol or allow-list as the M1 bootstrap fixture.
9. **Specify the layer-2 schema**, once the shape above is agreed.
