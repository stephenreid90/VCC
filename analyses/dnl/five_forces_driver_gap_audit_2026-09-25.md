# Five Forces driver gap audit — gas, mining growth, margin_delta_pp, terminal ROIC defence

**Purpose.** Before running a fresh Five Forces interview, checked what already exists in
`analyses/dnl/scenarios/*.md`, `data/industries/industrial_explosives.md`, `data/companies/dnl.md`
and `data/impact_matrix/by_industry/industrial_explosives.yaml`, so we only go back to Stephen for
genuinely new judgment -- not to re-derive what's already been decided and just never transcribed.

Status key: **FREE** = fully drafted in existing prose, needs only transcription into the structured
YAML + Stephen's sign-off that the transcription is faithful. **GAP** = no existing analysis; needs a
real Five Forces pass (industry + company level) and a fresh scenario-specific judgment.

---

## 1. Terminal ROIC / excess-return defence (`decay_horizon`, D-42)

| Scenario | Structured YAML | Prose exists? | Status |
|---|---|---|---|
| Muddle Through | decay 10-15yr, moat=scale+switching_cost, named threat=Orica | "Fade period long (~15 years)" | done |
| Orderly Convergence | decay 10-15yr | full defence, incl. sensitivity test | done |
| AI Productivity Lag | decay 10-15yr (same as MT) | not discussed directly, consistent w/ "roughly neutral" | done |
| **Disorderly Climate** | terminal_roic direction/magnitude only, **no `excess_return_defence` block at all** | **fully specified**: "decay horizon 10-15 years (faster than non-climate scenarios); named threat = carbon pricing flow-through plus coal-customer attrition; sensitivity test = halving decay horizon to 5-7 years shows additional 15-20% terminal-value impact." Muddle Through's own `basis` text even cross-references this ("as the Disorderly Climate block does") | **FREE** -- transcribe into `excess_return_defence`, nothing new to decide |
| **Fragmentation** | no `terminal_roic` driver at all | scenario doc never discusses terminal ROIC / moat decay | **GAP** -- needs a real assessment: does Fragmentation's engine-implied terminal return sit above WACC, and if so does it get a defence or a baseline entry? |
| **Stagflation Persists** | no `terminal_roic` driver at all | scenario doc never discusses terminal ROIC / moat decay | **GAP** -- same as Fragmentation |

## 2. Gas / input-cost pass-through (feeds `gas_price_growth`, and separately D-69's `margin_gas_rolloff`)

| Scenario | Structured rating | Prose exists? | Status |
|---|---|---|---|
| Muddle Through | neutral/small | "long-term US gas contracts continue to insulate ~70%... established pass-through dynamics" | done (qualitative) |
| **Orderly Convergence** | not populated | "gas contracts hold their value; gas market normalises... input cost normalisation" | **FREE** (qualitative rating) -- draft as neutral-to-positive/small, transcribe, confirm with Stephen |
| **AI Productivity Lag** | not populated | genuinely silent -- scenario doc explicitly lists "five drivers populated" and gas/supplier power isn't one | **GAP** |
| Fragmentation | negative/moderate | "ammonium nitrate cross-bloc trade restrictions raise effective input costs... gross margin compresses 200-300bps" | done (qualitative, has a margin-impact number) |
| Disorderly Climate | negative/moderate | carbon-cost flow-through to ammonia, "gross margin compresses 200-400bps" | done (qualitative, has a margin-impact number) |
| Stagflation Persists | negative/large | most detailed of all six: "40-60% above-baseline energy/ammonia price spike... US contracts shield ~70% through 2028... EBIT margin compresses from ~14% to 8-10%" | done (qualitative, richest numeric detail) |

**Note on "the shape we already discussed":** none of these six give a `gas_price_growth` commodity
growth-*rate* time series directly -- what exists is margin-*impact* narrative (pp of EBIT/gross-margin
compression) under each scenario. That's usable as the anchor for `margin_delta_pp` (S3 below) more
directly than for the chain's `gas_price_growth` input specifically. If the "shape" you had in mind was
D-69's roll-off cumulative fractions `[0.05, 0.30, 0.60, 0.85, 0.95, 1.00]`, that's DNL's own contract
roll-off timing, not a global gas-commodity-price path -- still worth flagging for the translation-table
step whether to reuse that phasing convention for `gas_price_growth` too.

## 3. Mining volume growth (feeds `global_mining_real_growth`)

All six scenarios already have a populated `volume_growth` rating with rich prose rationale -- no gaps.
This is the one driver where "rerun the interview" is really "re-examine what's already there now that
it has to support a number, not just a flag." Worth flagging: the prose consistently frames volume as a
*function of the mining-customer capex cycle*, which itself is explicitly *not* a direct function of
world real GDP ("capex decisions lag commodity prices by 12-24 months and persist longer" -- industry
doc) -- this bears on the GDP-linkage question: the qualitative story already on file doesn't support a
simple GDP-multiple derivation either; it's capex-cycle-driven, which is its own distinct (and currently
unmodelled) time dynamic.

## 4. `margin_delta_pp`

Not currently in D-37's `required_macro_drivers` list at all (only `global_mining_real_growth`,
`dm_inflation`, `gas_price_growth` are declared). But every scenario's prose above already states an
actual **pp of margin compression/expansion**, which is exactly what this driver represents. This is
the cheapest of the four to convert to a real number -- the anchor magnitudes are already written down;
what's missing is (a) adding it to `required_macro_drivers` so D-37's check tracks it, and (b) turning
each scenario's stated *range* (e.g. Fragmentation "-200-300bps") into point estimates at years 1/3/5/7/10.

---

## Summary -- what's free vs what needs a real interview

**Free (transcription + sign-off only):**
1. Disorderly Climate's `excess_return_defence` block (fully specified in prose already).
2. Orderly Convergence's `input_cost_pass_through` qualitative rating.
3. `margin_delta_pp` anchor magnitudes for all six scenarios (already stated as pp ranges in prose) --
   plus adding it to `required_macro_drivers`.

**Genuine gaps (need a real Five Forces pass / fresh judgment):**
1. Fragmentation & Stagflation Persists -- terminal ROIC / decay horizon never assessed at all.
2. AI Productivity Lag -- gas/supplier-power impact never assessed at all.
3. For every scenario, on every driver: converting a qualitative rating (or a stated pp range) into
   actual point values at years 1/3/5/7/10 -- this is the translation-table step (task 7), not a Five
   Forces question at all.
