# Five Forces Question Bank

**Status:** Draft v1. All five forces drafted to Porter 2008 framing. Subject to refinement as we apply it to the IPL / CSL / WBC archetypes during build-plan step 5.
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

**Definition (Porter 2008).** "Powerful suppliers capture more of the value for themselves by charging higher prices, limiting quality or services, or shifting costs to industry participants. Powerful suppliers, including suppliers of labor, can squeeze profitability out of an industry that is unable to pass on cost increases in its own prices."

**Single-axis framing.** Unlike Buyer Power, Porter treats Supplier Power as a single dimension — leverage. The implicit constraint on suppliers exerting their power is the industry's ability to pass cost increases through to its own customers. Where pass-through is weak (rivalry strong, buyer power high, or substitutes available downstream), supplier-power impact on profitability is amplified. This is captured in the synthesis (§2.8), not as a separate axis.

**Distinct supplier groups.** As with buyers, an industry typically depends on multiple supplier groups (raw materials, capital equipment, labour, energy, financing). Treat each materially-exposed group separately, and aggregate weighted by the input's significance to the industry's cost base.

### 2.1 Supplier concentration relative to the industry

**Industry:** How concentrated are suppliers relative to the industry that buys from them? Supplier groups more concentrated than their customer industry have leverage. Porter's example: Microsoft's near-monopoly in operating systems vs the fragmentation of PC assemblers.
*Answer shape: rating `low | moderate | high` (supplier concentration vs industry concentration), plus naming the dominant suppliers and their share of input volume.*

**Company:** Is this company exposed to particular concentrated suppliers more or less than industry peers? Where could an alternative supplier reduce dependency?
*Answer shape: rating `low | moderate | high` (relative to industry exposure), plus narrative on supplier mix.*

### 2.2 Supplier dependence on the industry

**Industry:** Does the supplier group depend heavily on this industry for its revenues? Porter notes suppliers serving many industries "will not hesitate to extract maximum profits from each one." Where the industry accounts for a large share of supplier volume or profit, suppliers have an interest in protecting it (reasonable pricing, R&D support, lobbying).
*Answer shape: rating `low | moderate | high` (supplier independence from this industry), plus narrative on supplier customer mix.*

**Company:** Are this company's suppliers more or less dependent on the company specifically — through long-term partnerships, critical-customer status, exclusive arrangements? Higher supplier dependence on the company reduces supplier power vis-à-vis the company.
*Answer shape: rating `low | moderate | high` (relative to industry), plus list of dependence-creating arrangements.*

### 2.3 Switching costs in changing suppliers

**Industry:** What switching costs do industry participants face in changing suppliers — specialised ancillary equipment, learning costs, production-line adjacency, integration? Porter's examples: Bloomberg terminals for finance professionals; beverage producers locating production adjacent to container manufacturers.
*Answer shape: rating `low | moderate | high` (switching cost), plus narrative naming the dominant switching-cost type.*

**Company:** Has this company concentrated supplier-switching cost into its operations more or less than the norm, or built supplier optionality (multiple qualified vendors, in-housed alternatives)?
*Answer shape: rating `low | moderate | high` (relative to industry), plus narrative on company-specific arrangements.*

### 2.4 Supplier product differentiation

**Industry:** Are suppliers' products differentiated such that one cannot easily substitute another? Porter cites pharmaceutical companies offering patented drugs with distinctive medical benefits, which have more power over hospitals and HMOs than generic drug suppliers do.
*Answer shape: rating `low | moderate | high` (degree of supplier differentiation), plus narrative on the basis of differentiation.*

**Company:** Does this company's supplier mix lean toward more or less differentiated suppliers than the industry typical? Has the company gained access to differentiated supply that peers lack?
*Answer shape: rating `low | moderate | high` (relative to industry), plus narrative.*

### 2.5 Substitute availability for the input

**Industry:** Are there credible substitutes for what the supplier group provides? Porter cites pilots' unions exercising considerable supplier power over airlines partly because there is no good alternative to a well-trained pilot in the cockpit.
*Answer shape: rating `low | moderate | high` (substitute availability — high availability lowers supplier power), plus list of substitutes if any.*

**Company:** Has this company found, developed, or invested in substitutes for inputs that constrain industry peers (alternative materials, automation, in-housed capability)?
*Answer shape: rating `low | moderate | high` (relative to industry), plus narrative on substitute strategy.*

### 2.6 Forward-integration credibility

**Industry:** Can suppliers credibly threaten to integrate forward into the industry — and would they do so if the industry's profits become too attractive relative to the supplier's? Porter notes this dynamic: "if industry participants make too much money relative to suppliers, they will induce suppliers to enter the market."
*Answer shape: rating `low | moderate | high`, plus historical examples or stated supplier intent if any.*

**Company:** Does this company face credible forward-integration threats from any specific supplier? Are there suppliers whose strategic posture or capability makes downstream entry realistic?
*Answer shape: rating `low | moderate | high`, plus named suppliers if any.*

### Special case: labour as a supplier group

Porter explicitly identifies labour as a supplier group ("powerful suppliers, including suppliers of labor"). For industries where specialised labour is a critical input — pilots, surgeons, software engineers, geologists, lawyers — labour should be assessed as a distinct supplier group with its own concentration, dependence, switching cost, and substitute factors. Union dynamics and skill-supply scarcity are the dominant variables.

### 2.7 Labour as a supplier group

**Industry:** Is labour (or a specific labour category) a critical input where the supply group has leverage — through scarcity, unionisation, certification barriers, or skill specificity? Apply 2.1-2.6 to the labour group specifically.
*Answer shape: identify the relevant labour group(s), rating `low | moderate | high` (labour-as-supplier power), plus narrative on the dominant factor (scarcity, unionisation, certification).*

**Company:** Is this company more or less exposed to labour-supplier power than the industry — through workforce composition, location, employment-relations posture, or automation investment?
*Answer shape: rating `low | moderate | high` (relative to industry), plus narrative.*

### 2.8 Synthesis

After working through 2.1-2.7:

1. **Aggregate across supplier groups.** Where the industry depends on multiple materially-exposed supplier groups, rate each group separately and aggregate weighted by the input's share of the industry cost base (use `cost_structure` from §7.4 as the weighting reference).
2. **Pass-through modifier.** Where the industry has weak ability to pass cost increases through to its own customers (high buyer power downstream, strong substitute exposure, intense rivalry), the *impact* of supplier power on industry profitability is amplified — even if the leverage rating itself is unchanged. Note this in the rationale.
3. **Industry rollup.** Record `five_forces.supplier_power.rating` (`low | moderate | high`) with a one-paragraph `rationale` calling out which 2-3 sub-determinants dominate and which supplier group is the binding one.
4. **Company-level divergence.** Where the company's position diverges materially from the industry, record:
   (a) in `franchise_assets` (§8.2): long-term supplier contracts, supplier optionality, alternative-input capability, in-housed inputs (2.3, 2.5);
   (b) in `risk_exposures.commodity` and `risk_exposures.regulatory` (§8.2): concentrated-supplier exposure (2.1, 2.2);
   (c) in `competitive_position.cost_position` (§8.2): cost advantage derived from supplier relationships (2.2, 2.3);
   (d) in `archetype_specific` (§8.3): for archetypes where labour-supplier power is dominant (banking — talent supply; healthcare — clinician supply; mining — geologist / engineer supply), capture the labour-supply detail in the archetype-specific block.

---

## 3. Threat of New Entrants

**Definition (Porter 2008).** "New entrants to an industry bring new capacity and a desire to gain market share that puts pressure on prices, costs, and the rate of investment necessary to compete... The threat of entry, therefore, puts a cap on the profit potential of an industry. When the threat is high, incumbents must hold down their prices or boost investment to deter new competitors... It is the threat of entry, not whether entry actually occurs, that holds down profitability."

**Two dimensions.** Porter frames the threat of new entrants as a function of (a) the **height of entry barriers** and (b) the **expected retaliation** entrants anticipate from incumbents. High barriers OR strong expected retaliation reduces the threat. Both must be assessed.

**Frame for the company-level question.** Unlike Buyer / Supplier Power where the subject company is typically a participant subject to the force, here the subject company is usually an **incumbent**. The company-level questions accordingly flip: how *exposed* is this company to entry (relative to peers), and how much does it *contribute* to the barriers?

### Entry barriers — Porter's seven major sources

#### 3.1 Supply-side economies of scale

**Industry:** Are there meaningful supply-side scale economies in this industry — fixed costs spread over volume, more efficient technology at scale, better terms from suppliers? Where in the value chain are the dominant scale economies (R&D, manufacturing, distribution, marketing)?
*Answer shape: rating `low | moderate | high` (height of scale barrier), plus narrative on where in the value chain scale matters most.*

**Company:** Where does this company sit on the scale-economy curve relative to peers — sub-scale and exposed to entry-pressure cost disadvantage, at-scale, or super-scale and contributing to the entry barrier itself?
*Answer shape: rating `low | moderate | high` (company position relative to industry — high = company is meaningfully sub-scale and exposed), plus narrative.*

#### 3.2 Demand-side benefits of scale (network effects)

**Industry:** Does buyer willingness to pay increase with the number of other buyers using the same provider? Network effects can be direct (more users = more value to each) or indirect (more users attract more complementary providers). Porter's eBay and IBM-era examples.
*Answer shape: rating `low | moderate | high` (network-effect barrier strength), plus narrative on the network mechanism.*

**Company:** Does this company benefit from network-effect-derived position — installed base, ecosystem of complementors, trust premium — that an entrant would need to replicate at substantial cost?
*Answer shape: rating `low | moderate | high` (relative to industry), plus narrative.*

#### 3.3 Customer switching costs

**Industry:** What switching costs do customers face when changing vendors — re-specification, retraining, process / IT modification, embedded data, mission-criticality? Porter's ERP example: SAP install creates "astronomical" switching cost.
*Answer shape: rating `low | moderate | high` (customer switching-cost barrier), plus narrative on the dominant switching-cost type.*

**Company:** Has this company built customer switching costs more or less than industry peers — through deep integration, certification, customer-specific assets, embedded data, ecosystem lock-in?
*Answer shape: rating `low | moderate | high` (relative to industry), plus list of company-specific lock-in mechanisms.*

#### 3.4 Capital requirements

**Industry:** What scale of capital investment is required to compete — fixed facilities, customer credit, working capital, start-up losses, sunk advertising or R&D? Porter notes capital alone isn't a determinative barrier where industry returns are attractive and capital markets efficient (his airlines example), but unrecoverable expenditures matter most.
*Answer shape: rating `low | moderate | high` (capital barrier), plus quantification (typical entry capital required) and narrative on what proportion is sunk.*

**Company:** Has this company committed capital that creates exit costs (and therefore entry deterrence) more or less than the industry typical? Or operates capital-light relative to peers (lower entry deterrence on the company-specific dimension)?
*Answer shape: rating `low | moderate | high` (relative to industry), plus narrative.*

#### 3.5 Incumbency advantages independent of size

**Industry:** Beyond scale, what cost or quality advantages do incumbents have that an entrant cannot easily replicate — proprietary technology, preferential raw-material access, preempted geographic locations, established brand identities, accumulated learning-curve experience?
*Answer shape: rating `low | moderate | high` (height of incumbency barrier), plus list of dominant advantages.*

**Company:** Which of these incumbency advantages does this company hold to an above-average or below-average degree — proprietary tech, sourcing access, location, brand, learning curve?
*Answer shape: rating `low | moderate | high` (relative to industry), plus list with brief evidence.*

#### 3.6 Unequal access to distribution channels

**Industry:** How tied up are wholesale or retail channels by existing competitors? Are channels themselves concentrated and aligned with incumbents (Porter's supermarket-shelf example)? Where channels are blocked, must entrants bypass distribution or build their own (Porter's low-cost airlines example)?
*Answer shape: rating `low | moderate | high` (channel-access barrier), plus narrative on channel structure.*

**Company:** Does this company have differentiated channel access vs the industry — exclusive arrangements, owned channels, direct-to-customer infrastructure that an entrant would need to build?
*Answer shape: rating `low | moderate | high` (relative to industry), plus narrative.*

#### 3.7 Restrictive government policy

**Industry:** Does government policy directly limit entry (licensing, foreign-investment restrictions, regulated industries — Porter's liquor retailing, taxis, airlines), or amplify other barriers (expansive patenting, environmental / safety regulation that raises the scale entrants must achieve)? Or does policy lower barriers (subsidies, basic research funded by government)?
*Answer shape: rating `low | moderate | high` (policy-derived entry barrier), plus narrative on the dominant mechanism (licensing, capital regulation, IP, environmental, foreign-ownership).*

**Company:** Has this company secured policy-derived position more or less than peers — incumbent licences, grandfathered approvals, regulator relationships, IP estate, lobbying capability?
*Answer shape: rating `low | moderate | high` (relative to industry), plus narrative.*

### Expected retaliation

#### 3.8 Likelihood and severity of incumbent retaliation

Porter treats this as a separate dimension from the seven barriers. Newcomers are likely to fear expected retaliation if (per Porter): (a) incumbents have previously responded vigorously to new entrants; (b) incumbents possess substantial resources to fight back (excess cash, unused borrowing, available capacity, channel / customer clout); (c) incumbents seem likely to cut prices because they are committed to market-share defence or because high fixed costs motivate price-drop-to-fill; (d) industry growth is slow so newcomers can only gain volume by taking it from incumbents.

**Industry:** Aggregate the four Porter retaliation factors. Is the industry one where incumbents have a track record of vigorous defence, hold deep retaliation resources, face strong incentives to cut prices defensively, and where slow growth forces newcomers to take share from incumbents directly?
*Answer shape: rating `low | moderate | high` (expected-retaliation strength), plus narrative naming the dominant retaliation factor.*

**Company:** Is this company more or less inclined / equipped to retaliate against entrants than industry peers — through cost position, balance-sheet capacity to weather a price war, channel / customer relationships, or stated strategic posture?
*Answer shape: rating `low | moderate | high` (relative to industry), plus narrative.*

### 3.9 Synthesis

After working through 3.1-3.8:

1. **Aggregate barriers and retaliation.** Porter treats them as distinct dimensions: the threat of new entrants is reduced by *either* high barriers *or* strong expected retaliation. Roll the seven barriers into a single barrier-height assessment, and combine with the retaliation rating.
2. **Industry rollup.** Record `five_forces.new_entrants.rating` (`low | moderate | high` — the *threat*, so high barriers / retaliation give a low threat rating). One-paragraph `rationale` calling out which 2-3 sub-determinants dominate. Note explicitly whether barriers or retaliation is doing the work, since they have different policy and competitive implications.
3. **Watch the lifecycle interaction.** Per §7.3 / §7.5, low entry barriers are a primary signal that an industry's lifecycle is shortening — if scale, switching costs, or capital barriers erode (technology shift, regulatory change, capital-market shift), the industry's ability to sustain returns above cost of capital is compromised. Cross-check the rating against `lifecycle_stage` and `disruption_vectors` (§7.4) for consistency.
4. **Company-level divergence.** Where the company's position diverges materially from the industry, record:
   (a) in `moat` (§8.2): scale (3.1), network (3.2), switching cost (3.3), brand / IP / learning-curve (3.5), regulatory (3.7) moat sources;
   (b) in `franchise_assets` (§8.2): channel access (3.6), regulatory licences and approvals (3.7), incumbent advantages from 3.5;
   (c) in `competitive_position.cost_position` and `differentiation_position` (§8.2): scale-derived cost advantage (3.1), differentiation / brand premium (3.5);
   (d) in `risk_exposures.regulatory` (§8.2): exposure to policy changes that would lower entry barriers (3.7).

---

## 4. Threat of Substitutes

**Definition (Porter 2008).** "A substitute performs the same or a similar function as an industry's product by a different means... When the threat of substitutes is high, industry profitability suffers. Substitute products or services limit an industry's profit potential by placing a ceiling on prices. If an industry does not distance itself from substitutes through product performance, marketing, or other means, it will suffer in terms of profitability — and often growth potential."

**Identification challenge.** Porter spends substantial space on the recognition problem: *"Substitutes are always present, but they are easy to overlook because they may appear to be very different from the industry's product."* His Father's Day gift example: neckties and power tools as substitutes. Also: do-without, buy-used, do-it-yourself as substitutes. The framework requires a deliberate identification step before any rating.

**Direct vs indirect substitutes.** Direct substitutes replace the industry's product to the same buyer (videoconferencing for travel). Indirect / downstream substitutes replace a *buyer industry's* product, which then reduces demand for our industry (Porter: lawn-care services threatened when multifamily urban homes substitute for single-family suburban). Both should be identified.

### 4.1 Identification of substitutes

**Industry:** What substitutes — direct, indirect, do-without, used, do-it-yourself — perform the same or a similar function as this industry's product? List them explicitly, named, including substitutes that *appear* different. For each, state the buyer use-case being substituted.
*Answer shape: list of named substitutes (direct and indirect) with brief description of the use-case overlap. No rating at this step — identification first, then assessment in 4.2-4.4.*

**Company:** Are there company-specific substitutes that don't apply to peers — substitutes for a particular product line, geography, or customer segment that the company is over- or under-exposed to?
*Answer shape: list of company-specific substitution exposures, with narrative.*

### 4.2 Price-performance trade-off of substitutes

**Industry:** For each substitute identified, what is the price-performance trade-off relative to the industry's product? Better relative value of the substitute = tighter ceiling on industry profit potential. Porter cites Vonage and Skype eroding traditional long-distance telephony; Netflix and Google YouTube vs video rental.
*Answer shape: rating `low | moderate | high` (substitute price-performance attractiveness — high = strong substitute pressure). For each material substitute, brief comment on the price-performance comparison and its trajectory (improving, stable, deteriorating).*

**Company:** Does this company's offering have a stronger or weaker price-performance position vs the substitute set than the industry typical — through differentiated features, integration, service, or quality?
*Answer shape: rating `low | moderate | high` (relative to industry — high = company more exposed to substitutes than peers), plus narrative.*

### 4.3 Buyer switching cost to substitute

**Industry:** What costs do buyers face in switching from the industry's product to substitutes — re-equipping, retraining, regulatory re-approval, ecosystem re-build, service-relationship loss? Porter notes branded-drug to generic switching is "minimal cost," which is why the shift is rapid and substantial.
*Answer shape: rating `low | moderate | high` (buyer switching cost to substitute — low = high substitute threat), plus narrative on the dominant switching-cost type.*

**Company:** Has this company built switching costs that delay buyer migration to substitutes more than the industry typical — proprietary integration, certification, embedded service, contractual lock-in?
*Answer shape: rating `low | moderate | high` (relative to industry — high = company has higher switch-deterrent than peers), plus list of company-specific switch-deterrent mechanisms.*

### 4.4 Cross-industry substitution dynamics

Porter explicitly: *"Strategists should be particularly alert to changes in other industries that may make them attractive substitutes when they were not before. Improvements in plastic materials, for example, allowed them to substitute for steel in many automobile components."* Substitution risk is dynamic, not static.

**Industry:** Are there adjacent or unrelated industries with rising capability or falling cost that could become a substitute for this industry's product over the forecast horizon? Distinguish current substitutes (4.1-4.3) from emerging substitution risk.
*Answer shape: list of emerging substitution-risk vectors, each with narrative on the underlying technology or capability shift, time horizon, and severity. Cross-reference to `disruption_vectors` in §7.4.*

**Company:** Is this company more or less exposed to emerging cross-industry substitution than peers — through product mix, customer mix, or geographic mix?
*Answer shape: rating `low | moderate | high` (relative to industry), plus narrative.*

### 4.5 Synthesis

After working through 4.1-4.4:

1. **Static vs dynamic.** Distinguish the rating into a current-substitute pressure (4.2 + 4.3) and an emerging-substitution risk (4.4). Both feed the overall force rating, but they have different implications: static substitution caps current pricing; dynamic substitution threatens future revenue and lifecycle stage.
2. **Industry rollup.** Record `five_forces.substitutes.rating` (`low | moderate | high`). One-paragraph `rationale` naming the dominant substitute(s) and whether the rating is driven by static price-performance or by an emerging-substitution risk.
3. **Disruption cross-check.** Per §7.3 / §7.5, substitution is one of the two main mechanisms by which industries get disrupted (the other being new entrants). Substitution-driven disruption signals should appear in §7.4 `disruption_vectors`. Confirm consistency between this section's emerging substitutes (4.4) and the archetype's disruption vectors.
4. **Company-level divergence.** Where the company's position diverges materially from the industry, record:
   (a) in `competitive_position.differentiation_position` (§8.2): differentiation-derived substitute resistance (4.2);
   (b) in `franchise_assets` (§8.2): switching-cost moats vs substitutes (4.3);
   (c) in `innovation_position` (§8.2): R&D and pipeline activity oriented at maintaining position vs substitutes (4.2, 4.4);
   (d) in `risk_exposures.regulatory` and / or new entries to `disruption_vectors`: emerging substitution exposure (4.4).

---

## 5. Competitive Rivalry

**Definition (Porter 2008).** "Rivalry among existing competitors takes many familiar forms, including price discounting, new product introductions, advertising campaigns, and service improvements. High rivalry limits the profitability of an industry. The degree to which rivalry drives down an industry's profit potential depends, first, on the intensity with which companies compete and, second, on the basis on which they compete."

**Two-component framing.** Porter is explicit that rivalry has two distinct dimensions and both must be assessed:

1. **Intensity** — how hard companies compete (covered in 5.1-5.5).
2. **Basis** — what dimensions they compete on, with **price competition the most destructive** because it transfers profits directly from industry to customers (covered in 5.6-5.9).

A high-intensity industry that competes on differentiated, non-price dimensions can sustain profitability; a moderate-intensity industry that gravitates to price competition often cannot.

### Intensity of rivalry — Porter's five factors

#### 5.1 Number and balance of competitors

**Industry:** Are competitors numerous, or roughly equal in size and power? Where rivals are numerous or balanced, no industry leader can enforce industry-wide discipline, and rivals find it hard to avoid poaching one another's business.
*Answer shape: rating `low | moderate | high` (intensity contribution from competitor balance — high = many or balanced rivals), plus quantification (number of meaningful competitors, top-3 share).*

**Company:** Is this company a clear industry leader (with the ability to set industry behaviour) or one of several balanced rivals?
*Answer shape: rating `leader | strong second-tier | balanced rival | challenger | follower`, plus narrative.*

#### 5.2 Industry growth rate

**Industry:** Is industry growth slow? Slow growth precipitates fights for market share because the only way to grow is to take it from rivals. Fast growth allows all participants to grow without conflict.
*Answer shape: rating `low | moderate | high` (intensity contribution from growth — high = slow-growth industry), plus the underlying growth rate (real and nominal where possible).*

**Company:** Does this company face faster or slower growth than the industry typical — through geographic mix, segment mix, or product mix?
*Answer shape: rating `low | moderate | high` (relative to industry), plus narrative.*

#### 5.3 Exit barriers

**Industry:** How high are exit barriers — highly specialised assets, management commitment to the business, regulatory constraints on shutdown, employment obligations? High exit barriers keep companies in the market even at low or negative returns; excess capacity remains in use and the profitability of healthy competitors suffers as the sick ones hang on.
*Answer shape: rating `low | moderate | high` (intensity contribution from exit barriers), plus narrative on the dominant exit-barrier type.*

**Company:** Does this company face higher or lower exit costs than peers — through asset specificity, jurisdictional commitments, brand-portfolio entanglement?
*Answer shape: rating `low | moderate | high` (relative to industry), plus narrative.*

#### 5.4 Strategic stakes and non-economic commitment

**Industry:** Are rivals highly committed to the business with non-economic aspirations — state-owned competitors with employment or prestige goals, units of larger companies competing for image or full-line offering, ego-driven incumbents? Porter notes media and high tech as fields where personality and ego have exaggerated rivalry.
*Answer shape: rating `low | moderate | high` (non-economic strategic stakes), plus narrative naming the relevant rival types.*

**Company:** Does this company face rivals with non-economic motivations specifically targeting its segments — state-owned national champions, conglomerate divisions, founder-led competitors?
*Answer shape: rating `low | moderate | high` (relative to industry), plus list of rivals with non-economic commitment.*

#### 5.5 Signal readability among rivals

**Industry:** Can rivals read one another's strategic signals well, or are they prone to misinterpretation due to lack of familiarity, diverse approaches to competing, or differing goals? Poor signal readability tends to escalate competitive moves into damaging cycles.
*Answer shape: rating `low | moderate | high` (intensity contribution from poor signal readability — high = signals poorly read, escalation risk), plus narrative.*

**Company:** Is this company more or less able to read rivals' signals than peers — through industry tenure, executive networks, intelligence capability — and is it more or less likely to be misread by others?
*Answer shape: rating `low | moderate | high` (relative to industry), plus narrative.*

### Basis of rivalry — what pushes competition toward price

Porter: *"Rivalry is especially destructive to profitability if it gravitates solely to price because price competition transfers profits directly from an industry to its customers."* The four conditions below push competition toward price.

#### 5.6 Product similarity and low switching costs

**Industry:** Are rivals' products or services nearly identical with few switching costs for buyers? Porter cites airline price wars as the canonical example. Identical products + low switching encourage rivals to cut prices to win customers.
*Answer shape: rating `low | moderate | high` (price-rivalry pressure from product similarity), plus narrative on the basis of differentiation if any.*

**Company:** Does this company differentiate sufficiently to insulate it from price-based rivalry, or does it compete on similar terms to peers?
*Answer shape: rating `low | moderate | high` (relative to industry — high = company competes on price more than peers), plus narrative on differentiation strategy.*

#### 5.7 Fixed-cost / marginal-cost structure

**Industry:** Are fixed costs high and marginal costs low? This creates intense pressure for competitors to cut prices below average cost, even close to marginal cost, to keep capacity utilised. Porter cites paper and aluminium (basic materials, especially with non-growing demand) and delivery companies with fixed-route networks.
*Answer shape: rating `low | moderate | high` (price-rivalry pressure from cost structure — high = high fixed / low marginal), plus quantification (typical fixed-cost share of total).*

**Company:** Does this company have a more variable cost structure than peers, insulating it from fill-the-capacity pressure, or is it more fixed-cost than the industry typical?
*Answer shape: rating `low | moderate | high` (relative to industry), plus narrative.*

#### 5.8 Capacity-expansion lumpiness

**Industry:** Must capacity be expanded in large increments to be efficient (Porter's PVC example)? Lumpy capacity additions disrupt the industry's supply-demand balance and create recurring overcapacity / price-cutting cycles.
*Answer shape: rating `low | moderate | high` (price-rivalry pressure from lumpy capacity), plus narrative on the typical scale of efficient capacity addition.*

**Company:** Does this company face the same capacity-lumpiness dynamic as peers, or has it built capacity-flexibility (modular plants, third-party capacity, asset-light models) that buffers it?
*Answer shape: rating `low | moderate | high` (relative to industry), plus narrative.*

#### 5.9 Product perishability

**Industry:** Is the product perishable in any sense? Porter takes a broad definition: tomatoes rot, computer models become obsolete, information becomes outdated, hotel rooms unused tonight cannot be sold tomorrow. Perishability creates strong temptation to cut prices to sell while value remains.
*Answer shape: rating `low | moderate | high` (price-rivalry pressure from perishability), plus narrative on the perishability mechanism.*

**Company:** Does this company face more or less perishability exposure than peers — through inventory mix, product life-cycle, capacity-utilisation profile?
*Answer shape: rating `low | moderate | high` (relative to industry), plus narrative.*

### 5.10 Synthesis

After working through 5.1-5.9:

1. **Two-component intersection.** Porter's framing requires both intensity AND basis to be assessed. A useful aggregation: high intensity x price basis = highly destructive rivalry; high intensity x non-price basis = sustainable competitive activity that may even raise barriers to substitutes / entrants; low intensity x price basis = moderate; low intensity x non-price basis = the most profitable configuration. The overall rating should reflect both axes, not just one.
2. **Convergent vs divergent dimensions.** Porter notes that when "all or many competitors aim to meet the same needs or compete on the same attributes, the result is zero-sum competition." Where rivals compete on different dimensions (different segments, different value propositions), rivalry is less destructive even when intensity is high. Worth a sentence in the rationale.
3. **Industry rollup.** Record `five_forces.rivalry.rating` (`low | moderate | high`). One-paragraph `rationale` naming whether intensity or basis is doing the work, identifying the dominant 2-3 sub-determinants, and stating whether competition is convergent or divergent in dimensions.
4. **Cross-check with §7.5.** A high-rivalry rating should pull `lifecycle_stage` toward `mature` or `declining`, and should compress default driver ranges (margins, pricing power) per the §7.5 link 2 calibration discipline. Confirm consistency.
5. **Company-level divergence.** Where the company's position diverges materially from the industry, record:
   (a) in `competitive_position.differentiation_position` (§8.2): differentiation that insulates from price rivalry (5.6);
   (b) in `competitive_position.cost_position` (§8.2): cost-curve placement that wins price wars without bleeding (5.7);
   (c) in `franchise_assets` (§8.2): customer relationships, channel position, capacity flexibility that reduce direct rivalry exposure (5.6, 5.8);
   (d) in `archetype_specific` (§8.2): for industries where the dominant rivalry dynamic is industry-specific (banks competing on deposit pricing; insurers on combined ratio), capture the company's positioning on that dimension in the archetype-specific block.
