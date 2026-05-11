# Five Forces Question Bank

**Status:** Draft. Buyer Power worked example only — other four forces to be drafted once shape is confirmed.
**Source:** Aligned to Michael E. Porter, *"The Five Competitive Forces That Shape Strategy"*, Harvard Business Review, January 2008. Sub-determinants and structure track Porter's 2008 articulation directly; question wording is ours.
**Companion to:** `design/architecture.md` §7.4 (industry archetype schema, `five_forces` block) and §7.5 (how Five Forces feeds the rest of the framework).

---

## Purpose

A standardised set of questions used to interview each industry archetype and each subject company within it. Two parallel question sets per force:

- **Industry-level** questions populate the `five_forces.<force>.{rating, rationale}` block in the industry archetype YAML (§7.4).
- **Company-level** questions populate the company's `moat`, `franchise_assets`, and `competitive_position` blocks in the company positioning YAML (§8.2).

Run the bank once per archetype-review and once per company-review. Pair the answers so that when an industry-level "buyer concentration is high" rating is recorded, the matching company-level question — "is this company more or less exposed to buyer concentration than the industry average?" — is answered in the same sitting.

## How to use

1. **Per force, work through the sub-determinants in order.** Each sub-determinant has a paired industry / company question.
2. **Record an answer shape per question.** The default shape is a `low | moderate | high` rating plus 2-3 sentences of rationale. Some questions naturally take a list answer (e.g. naming the substitutes); the question prompt will say so.
3. **Cite evidence.** Where the answer is a judgement on a sourced fact (e.g. buyer concentration ratio), record the source as `evidence_refs` per the §10.4 convention (`source_id`, `location`, `date_accessed`).
4. **Roll up to the schema.** After working through all sub-determinants for a force, settle on the overall force rating (`low | moderate | high`) for the `five_forces.<force>.rating` field, and write a one-paragraph `rationale` synthesising the sub-determinant findings. The synthesis should explicitly call out which sub-determinants are doing the most work in the rating.
5. **Cross-check against the §7.5 linkages.** Once all five forces are populated, confirm consistency with the archetype's `lifecycle_stage`, default driver ranges, and `scenario_sensitivity` block.

## Convention

- *Industry-level* answers describe the archetype as a whole — "how does the industry's buyer base look in aggregate?"
- *Company-level* answers describe the subject company's specific position relative to the industry pattern — "is this company more or less exposed than the industry average, and why?"
- Where company-level positioning *flips* the industry-level rating (e.g. industry has high buyer power but this company has unusually weak buyer power because of long-term contracts), the flip should be captured both here and as a `franchise_assets` entry in §8.2.

---

## 1. Buyer Power

**Definition (Porter 2008).** "Powerful customers — the flip side of powerful suppliers — can capture more value by forcing down prices, demanding better quality or more service (thereby driving up costs), and generally playing industry participants off against one another, all at the expense of industry profitability."

**Two-axis framing.** Porter defines buyer power as the intersection of two distinct dimensions: a buyer group is powerful only if it has both **negotiating leverage** *and* **price sensitivity**. A concentrated buyer that is highly price-insensitive (e.g. a hospital buying a critical patented drug) is *not* powerful. Both axes must be assessed independently before rolling up.

**Distinct buyer groups.** "There may be distinct groups of customers who differ in bargaining power." Where this is the case, treat each group separately and aggregate to a force rating that reflects the segment mix.

### Negotiating leverage

The first axis. A buyer group has leverage where one or more of the following sub-determinants holds.

#### 1.1 Buyer concentration / volume per buyer

**Industry:** Are there few buyers, or do individual buyers purchase in volumes large relative to a single vendor's size? Porter notes large-volume buyers are particularly powerful in industries with high fixed costs (high fixed + low marginal costs amplifies the pressure on rivals to keep capacity filled through discounting).
*Answer shape: rating `low | moderate | high` (buyer concentration), plus quantification (e.g. "top 5 buyers = 65% of industry revenue") with source. Note industry fixed-cost intensity if material.*

**Company:** Is this company's buyer base more or less concentrated than the industry average? Name the top buyers and their estimated share of company revenue.
*Answer shape: rating `low | moderate | high` (relative to industry), plus list of top buyers with revenue share.*

#### 1.2 Standardisation / undifferentiation of industry product

**Industry:** Are the industry's products standardised or undifferentiated, such that buyers believe they can always find an equivalent product and play vendors off against one another?
*Answer shape: rating `low | moderate | high` (degree of standardisation), plus narrative on the basis of differentiation if any (specs, quality tiers, brand).*

**Company:** Does this company differentiate more or less than the industry norm? Where does the company sit on the differentiation spectrum vs peers?
*Answer shape: rating `low | moderate | high` (relative to industry differentiation), plus narrative on differentiation basis.*

#### 1.3 Buyer switching costs

**Industry:** Do buyers face switching costs in changing vendors — technical re-engineering, contractual lock-in, training, integration, certification?
*Answer shape: rating `low | moderate | high` (switching cost), plus narrative naming the dominant switching-cost type.*

**Company:** What switching costs has this company built into its customer relationships beyond industry norms — long-term contracts, embedded technology, deep integration, certification, customer-specific assets?
*Answer shape: rating `low | moderate | high` (relative to industry), plus list of company-specific switching-cost mechanisms.*

#### 1.4 Backward-integration credibility

**Industry:** Can buyers credibly threaten to integrate backward and produce the industry's product themselves? Porter cites soft-drink and beer producers controlling packaging-manufacturer power by threatening to make packaging themselves.
*Answer shape: rating `low | moderate | high`, plus historical examples or stated intent if any.*

**Company:** Does this company face credible backward-integration threats from any major buyer specifically? Are there buyers whose scale, capability, or strategic posture makes self-supply realistic?
*Answer shape: rating `low | moderate | high`, plus named buyers if any.*

### Price sensitivity

The second axis. A buyer group is price sensitive where one or more of the following sub-determinants holds.

#### 1.5 Industry product as fraction of buyer's costs

**Industry:** Does the industry's product represent a significant fraction of the buyer's cost structure or procurement budget? Where it does, buyers shop around and bargain hard. Where it is a small fraction, buyers are usually less price sensitive.
*Answer shape: rating `low | moderate | high` (typical share of buyer cost), plus quantification or buyer archetype example if available.*

**Company:** Does this company sell into buyer segments where its product is a large or small share of the buyer's cost base? Different segments may differ.
*Answer shape: rating `low | moderate | high` (relative to industry), plus segmentation.*

#### 1.6 Buyer profitability and financial pressure

**Industry:** Does the buyer group earn low profits, run cash-strapped, or face structural pressure to trim purchasing costs? Highly profitable or cash-rich buyers tend to be less price sensitive (provided the input isn't a large fraction of their cost base).
*Answer shape: rating `low | moderate | high` (buyer financial pressure), plus narrative on buyer-side economics.*

**Company:** Does this company sell into more or less financially pressured buyer segments than the industry average?
*Answer shape: rating `low | moderate | high` (relative to industry), plus segmentation.*

#### 1.7 Effect of industry product on buyer's product quality

**Industry:** How much does the industry's product affect the quality of the buyer's own product or service? Where quality is materially affected (Porter's example: motion-picture producers buying production cameras), buyers are less price sensitive — quality and reliability dominate.
*Answer shape: rating `low | moderate | high` (effect on buyer quality), plus example.*

**Company:** Does this company's offering matter more or less for buyer-product quality than the industry typical? Are there segments where the company's offering is mission-critical to the buyer's output?
*Answer shape: rating `low | moderate | high` (relative to industry), plus narrative.*

#### 1.8 Effect of industry product on buyer's other costs

**Industry:** Does the industry's product pay for itself many times over by improving buyer performance or reducing buyer labour, materials, or other costs (Porter's examples: tax accounting, well logging, investment banking)? Where it does, buyers prioritise capability over price.
*Answer shape: rating `low | moderate | high` (savings / value-creation potential for buyer), plus example.*

**Company:** Does this company's value proposition deliver more or less buyer-side cost saving than the industry typical?
*Answer shape: rating `low | moderate | high` (relative to industry), plus narrative.*

### Special case: intermediate customers and channels

Porter notes intermediate customers (assemblers, distributors, retailers — buyers who are not the end user) "gain significant bargaining power when they can influence the purchasing decisions of customers downstream." Producers diminish channel clout via exclusive arrangements with particular distributors / retailers, by marketing directly to end users, or by creating downstream brand pull (Porter's DuPont Stainmaster example).

#### 1.9 Channel power

**Industry:** Where the industry sells through intermediate customers, do those intermediaries hold meaningful influence over end-customer purchasing decisions? How concentrated is the channel itself?
*Answer shape: rating `low | moderate | high` (channel power), plus list of dominant channel intermediaries.*

**Company:** Does this company have differentiated channel access vs the industry — direct-to-end-user relationships, exclusive arrangements, downstream brand pull, channel-bypass capability?
*Answer shape: rating `low | moderate | high` (relative to industry), plus narrative.*

### 1.10 Synthesis

After working through 1.1-1.9:

1. **Two-axis intersection.** Roll up the four leverage sub-determinants (1.1-1.4) and the four price-sensitivity sub-determinants (1.5-1.8) separately. The overall buyer-power rating is driven by the *minimum* of the two axes — Porter's logic is that high leverage with low price sensitivity does not yield buyer power, and vice versa. Channel power (1.9) is a modifier where the industry sells through intermediaries.
2. **Industry rollup.** Record `five_forces.buyer_power.rating` (`low | moderate | high`) with a one-paragraph `rationale` calling out which 2-3 sub-determinants dominate the rating, and which axis (leverage / sensitivity) is the binding constraint.
3. **Distinct buyer groups.** Where the industry has materially different buyer segments (e.g. consumer vs B2B, retail vs institutional), record the rating per segment and weight to a consolidated rating by share of industry revenue.
4. **Company-level divergence.** Where the company's position diverges materially from the industry, record:
   (a) in `moat` (§8.2): switching-cost or differentiation moat sources from 1.2 / 1.3;
   (b) in `franchise_assets` (§8.2): long-term contract relationships, customer-specific assets, channel-bypass capabilities (1.3, 1.9);
   (c) in `competitive_position.differentiation_position` (§8.2): pricing power that survives buyer-power pressure (1.2, 1.7, 1.8);
   (d) in `risk_exposures.customer_concentration` (§8.2): quantified buyer concentration (1.1).

---

## 2. Supplier Power

*To be drafted once §1 shape is confirmed.*

## 3. Threat of New Entrants

*To be drafted once §1 shape is confirmed.*

## 4. Threat of Substitutes

*To be drafted once §1 shape is confirmed.*

## 5. Competitive Rivalry

*To be drafted once §1 shape is confirmed.*
