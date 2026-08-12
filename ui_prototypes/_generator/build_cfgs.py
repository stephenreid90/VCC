# -*- coding: utf-8 -*-
import json
# Optional lease-neutral EV/EBITDAR multiples basis (methodology §4.6.5): add a
#   "leaseNeutral": { "capMult": 8, "peer": <ref mult>, "peerNote": str, "note": str,
#                     "subject": { "rent": <annual lease cost>, "leaseLiabInND": <reported lease liab in netDebt> } }
# block INSIDE a company's "multiples" dict, and give each peer mfin a { "rent", "leaseLiab" } pair,
# ONLY for a lease-heavy archetype. It gates the EV/EBITDAR toggle in gen_ui.py (house re-capitalisation:
# strip reported lease liability, add uniform rent x capMult; EBITDAR = EBITDA + rent). DNL/WBC/CSL are
# lease-light and deliberately carry NO leaseNeutral block, so the feature stays dormant for them.

def dtable(rows):
    h='<table style="width:100%; font-size:13px;">'
    for r in rows:
        bold = ('Cost of equity' in r[0]) or ('WACC' in r[0] and '=' in r[0])
        h+='<tr><td style="padding:4px 0; %s">%s</td><td style="text-align:right; padding:4px 8px; %s">%s</td><td style="padding:4px 0;">%s</td></tr>'%(
            'font-weight:500;' if bold else 'color:var(--text2);', r[0], 'font-weight:500;' if bold else '', r[1],
            '<span style="font-size:11px; padding:1px 7px; border-radius:6px; background:var(--%s-bg); color:var(--%s-tx);">%s</span>'%({'disclosed':'success','derived':'info','judgment':'warning'}[r[2]],{'disclosed':'success','derived':'info','judgment':'warning'}[r[2]],r[2]))
    return h+'</table>'

def bridge(rows, intro):
    h='<p>%s</p><table style="width:100%%; font-size:13px;">'%intro
    for r in rows:
        bold = ('per share' in r[0]) or ('Enterprise value' in r[0]) or ('Equity value' in r[0]) or ('equity value' in r[0])
        h+='<tr><td style="padding:3px 0; %s">%s</td><td style="text-align:right; %s">%s</td></tr>'%('font-weight:500;' if bold else 'color:var(--text2);', r[0], 'font-weight:500;' if bold else '', r[1])
    return h+'</table>'

# ---- Shared world-scenario descriptions (from data/scenarios/*.md) ----
WORLD_DESC = {
 "Muddle Through":'<p>Post-2022 friction proves persistent rather than transitional: inflation cools but lands above target (2.5–3.5%) and central banks tacitly accept the overshoot rather than crush demand. Real rates settle structurally higher than the 2010s (~1.0%). The US keeps outperforming on fiscal expansion, AI investment and immigration, but the lift doesn&rsquo;t propagate to Europe or EM. Climate policy stays patchy and AI&rsquo;s productivity transmission is slow, with rents concentrating in platform owners. No crisis, no resolution — a grinding extension of present conditions. Global growth ~2.3%.</p><p><b>Macro picture.</b> Global growth ~2.3% (US ~2.4% leads; advanced-economy aggregate 1.5–2.0%; EM bifurcating by commodity exposure). Headline inflation settles ~3.0% — above target but tacitly accepted rather than fought; real policy rates ~1.0%, materially above the 2010s zero-bound. USD firm but range-bound.</p><p><b>What would move the world elsewhere.</b> Sustained inflation re-anchoring at target → Orderly Convergence; expectations breaking above 3% with second-round wage dynamics → Stagflation Persists; any regime-changing shock in energy, markets, climate or geopolitics → one of the boundary scenarios.</p>',
 "Orderly Convergence":'<p>The conditions for benign resolution stack up at once. Supply-side normalisation plus genuine AI productivity gains absorb wage pressure, so inflation returns to ~2.3% without a demand crush; real rates settle modestly positive. The political reset climate policy needed happens, and geopolitical tensions materially de-escalate. This time US growth propagates — pulling Europe out of stagnation and supporting EM — and AI rents diffuse, re-expanding growth multiples. Global growth recovers to 3.0–3.2%.</p><p><b>Macro picture.</b> Growth recovers to 3.0–3.2% (US 2.5%; Europe out of stagnation to 1.8–2.2%; EM 4–5%). Advanced-economy inflation back to ~2.3% by year 3; real policy rates a modestly positive ~0.8%. The USD softens as the Fed eases and capital flows reglobalise.</p><p><b>What would move the world elsewhere.</b> Sticky inflation despite supply normalisation → Muddle Through; expectations un-anchoring → Stagflation Persists; geopolitical escalation → Fragmentation; a physical-loss or carbon-policy crisis → Disorderly Climate; a persistent enterprise-AI adoption lag → AI Productivity Lag.</p>',
 "Stagflation Persists":'<p>The IMF severe scenario plays out: an energy shock spikes prices and keeps them elevated, inflation expectations break above the 3% credibility threshold, and second-round wage-price dynamics take hold. Central banks lose credibility and hold restrictive policy through the horizon; real rates settle 2–3% with recession inside the scenario. Climate policy backslides as a cost-of-living crisis crushes the transition coalition; growth-stock multiples compress and trade barriers ratchet up. Growth slows to 1.5–2.0%.</p><p><b>Macro picture.</b> Growth slows to 1.5–2.0% with an in-scenario recession (advanced economies contract ~0.5% in year 2). Inflation peaks 5.5–6% then settles 4–5%; nominal cash rates 5–7%, real rates ~2.5%. USD strong on rate-differential and safe-haven flows, with some EM currency crises.</p><p><b>What would move the world elsewhere.</b> The energy spike fading without second-round transmission, or credible central-bank re-anchoring → Muddle Through or Orderly Convergence; a deeper recession with rapid disinflation → a deflationary case outside the current set.</p>',
 "Fragmentation":'<p>The US-China contest hardens and trade-as-weapon (tariffs, sanctions, export controls) becomes routine, extending into industrial and commodity flows. Supply chains regionalise into duplicated US-aligned and China-aligned systems, energy markets bifurcate, and critical-minerals access becomes the new geopolitical front. The duplicated footprint is inflationary (~3.5%) and growth bifurcates — China-aligned economies may outpace the US-aligned bloc, with Europe hit hardest and Australia facing an acute security-vs-supply dilemma. The new equilibrium is structurally inferior.</p><p><b>Macro picture.</b> Growth ~2.0%, below Muddle Through on supply-chain-duplication costs and bifurcated by bloc (China-aligned 3.5–4.0%; US-aligned ~1.8%). Advanced-economy inflation ~3.5%; real rates ~1.5%. USD reserve share erodes gradually but stays dominant; gold prominent as a cross-bloc settlement medium.</p><p><b>What would move the world elsewhere.</b> Major diplomatic breakthroughs — a substantive US-China trade framework, a Russia-Ukraine settlement, an Iran deal revival — would weaken the bloc-formation logic; sustained globalisation gains in low-sensitivity categories would signal barrier-stability rather than ratcheting.</p>',
 "Disorderly Climate":'<p>The already-running disorderly climate path has its crystallisation moment — most likely a confluence of a catastrophic insured-loss event, regulator-forced de-leveraging of carbon-intensive loan books, and a carbon-price spike. Policy snaps from drift to abrupt crisis action: carbon prices to EUR 200+, border-adjustment mechanisms, expanded transition subsidies. Capital reallocates abruptly, so sectoral dispersion widens sharply even as aggregate growth stays near Muddle Through (~2.0–2.2%, inflation 4.5–5% from carbon pass-through). This scenario tests terminal-state convergence hardest — assumed-perpetual moats reveal stranded-asset half-lives inside the horizon.</p><p><b>Macro picture.</b> Aggregate growth 2.0–2.2% (near Muddle Through) but with far wider sectoral dispersion. Inflation peaks 4.5–5% from carbon-cost pass-through before easing to ~3% by year 10; real rates ~1.5% with elevated volatility. The EU ETS carbon price spikes to EUR 200+ and settles ~EUR 200–220; insurance is repriced sharply in physical-risk regions.</p><p><b>What would move the world elsewhere.</b> Continued drift without crystallisation → Muddle Through; a political reset enabling orderly transition → Orderly Convergence; climate-policy backsliding under a macro crisis → Stagflation&rsquo;s climate-stagnant posture.</p>',
 "AI Productivity Lag":'<p>The Solow paradox at AI scale. Capability and capex advance genuinely (deficit-funded, US-led), but economy-wide productivity transformation doesn&rsquo;t arrive on the bull timeline: enterprise adoption is slow, so aggregate TFP grows only ~0.5% versus the 1.5%+ current investment implies. Rents capture is asymmetric — platform owners take the bulk while broad enterprise pays without proportional payback — and market concentration intensifies. The saving grace is the labour-cost channel: AI contains white-collar wage growth even where productivity transmission is weak. Headline numbers resemble Muddle Through, but the underlying story differs.</p><p><b>Macro picture.</b> Growth 1.9–2.0%, modestly below Muddle Through; inflation ~3.0% and real rates ~1.0% — both Muddle-Through-like. Aggregate TFP grows only ~0.5%. The tell: headline numbers resemble Muddle Through while the story underneath is fundamentally different.</p><p><b>What would move the world elsewhere.</b> Enterprise-AI adoption broadening with genuine TFP flow-through → Orderly Convergence; an AI-capex collapse or financial-market unwind → a tech-investment-unwind stress variant outside the set; a major non-AI shock → Stagflation, Fragmentation or Disorderly Climate depending on the shock.</p>',
}

# ---- Global discount-rate theory (jurisdiction-neutral best practice). Per-company "what we did" supplied separately. ----
DR_PROPER = [
 ("rf","Risk-free rate",
  "The theoretically correct rate is a zero-coupon (spot) sovereign yield in the cash-flow currency, matched to the timing of each cash flow — a coupon bond&rsquo;s yield-to-maturity blends reinvestment assumptions across its life and is only an average. In practice the deep, liquid 10-year benchmark is used as a proxy, with longer tenors for very long-life assets; a steeply sloped curve is where that approximation most distorts long-dated NPVs."),
 ("erp","Equity risk premium",
  "The expected excess return of equities over the risk-free asset. It is unobservable, so it is estimated from long-run historical premia, forward-looking/implied models, or surveys — none decisive. Mature-market estimates cluster around 5–6%, but the statistical error is wide, so the figure is best treated as a reasoned convention rather than a measurement."),
 ("beta","Beta",
  "A single-stock regression beta is noisy and shifts with the estimation window and the index chosen, so triangulate from a comparable set: unlever peer equity betas to asset betas and re-lever to the subject&rsquo;s target capital structure, cross-checked against adjusted (mean-reverting) or fundamental betas. Index choice — local versus global — matters most when a company&rsquo;s earnings currency differs from its listing."),
 ("debt","Cost of debt",
  "The risk-free rate plus a credit-spread margin set by the company&rsquo;s (or its comparable set&rsquo;s) target credit rating, referencing traded corporate-bond spreads over sovereigns at matching tenor. Use a through-the-cycle target rating consistent with the assumed gearing, not the current coupon."),
 ("gearing","Gearing / capital-structure weights",
  "Weight equity and debt at market value on a target, through-the-cycle basis — informed by the subject&rsquo;s own structure and the comparable-set average rather than a single spot snapshot, which is volatile and often inconsistent with the betas measured over the same window."),
 ("wacc","WACC vs cost of equity",
  "For an ordinary company, discount ungeared after-tax cash flows (FCFF) at the WACC and bridge enterprise value to equity via net debt. For a bank, funding — deposits and wholesale debt — is an operating input rather than financing, so discount cash flows to equity at the cost of equity directly; a WACC/EV bridge would be wrong."),
]

# ---- Gated optional component: imputation / franking-credit "gamma".
# Narrow relevance (dividend-imputation regimes, e.g. Australia; typically regulated /
# infrastructure assets), so NOT part of the global default. Reintroduced only when a
# company config supplies a gamma "what we did" note: drtheory(<DID>, gamma_did="...")
# appends the row. Mirrors the multiples.leaseNeutral gating; dormant for DNL/WBC/CSL. ----
GAMMA_COMPONENT = ("Imputation / franking credits (gamma)",
  "In classical-tax jurisdictions no adjustment applies. Under a dividend-imputation system (e.g. Australia), company tax already paid can attach to dividends as credits usable by resident shareholders; some valuers capture this via a &lsquo;gamma&rsquo; factor (contested, ~0.25–0.65), most often for regulated or infrastructure assets. Practice is divided, and many decline it in a general business valuation because the credits&rsquo; value differs sharply between domestic and foreign holders.")

def drtheory(did, gamma_did=None):
    rows = [[lbl, bp, did.get(k, '&mdash;')] for (k, lbl, bp) in DR_PROPER]
    if gamma_did:
        rows.append([GAMMA_COMPONENT[0], GAMMA_COMPONENT[1], gamma_did])
    return rows

DNL_DID = {
 "rf":"10-year Commonwealth Government Securities YTM, <b>4.30%</b> (indicative, May 2026). Single spot 10-year — the pragmatic-benchmark choice, no duration-matching or normalisation.",
 "erp":"<b>5.0%</b> — a Damodaran-style mature-Australia premium, deliberately ~100bps below the 6.0% Australian-expert convention, with a small country premium baked in.",
 "beta":"Peer triangulation, rejecting the measured <b>0.36</b> (unreliable post-demerger): Orica ~1.05 / Yara ~1.20 / ICL ~1.10 cluster (Sasol 1.45 excluded) → selected <b>1.10</b>.",
 "debt":"<b>6.00%</b> pre-tax = an AUD investment-grade BBB-tier spread (~170bps) over the 10-year sovereign; after-tax 6.00% × (1−0.30) = 4.20%.",
 "gearing":"Market-value weights <b>E/V 83.5% / D/V 16.5%</b> (equity = 1,770m shares × AUD 3.61 ≈ 6,390; debt = net debt 1,261 at the 31 Mar 2026 anchor, §5.3). Market-value basis.",
 "wacc":"<b>WACC ≈ 8.88%</b> (Re 9.80% at β 1.10; 83.5% equity + 16.5% debt at 4.20% after-tax). Held constant across scenarios (§3.5).",
}
WBC_DID = {
 "rf":"10-year Commonwealth Government Securities YTM, <b>4.30%</b> (indicative, May 2026). Single spot 10-year — the pragmatic-benchmark choice.",
 "erp":"<b>5.0%</b> — a Damodaran-style mature-Australia premium, ~100bps below the 6.0% Australian-expert convention.",
 "beta":"Peer triangulation: CBA 0.80 / NAB 0.72 / WBC 0.73 cluster → <b>0.75</b>; ANZ 0.57 excluded as an institutional-dilution outlier, MQG 0.88 a different archetype. Measured 0.73 documented alongside.",
 "debt":"Not applicable — a bank is discounted at cost of equity, with deposits and wholesale funding treated as operating inputs, not financing (§15).",
 "gearing":"Not applicable — no WACC / EV bridge for a bank.",
 "wacc":"<b>Cost of equity 8.05%</b> (Rf 4.30% + β 0.75 × ERP 5.0%), held constant across scenarios, no WACC/EV bridge — the bank convention (§15).",
}
CSL_DID = {
 "rf":"10-year US Treasury, <b>4.50%</b> (USD-functional). Single spot 10-year, matching CSL&rsquo;s USD cash-flow currency — the correct-currency point behind rejecting the AUD-index beta below.",
 "erp":"<b>5.0%</b> — a Damodaran-style mature-market premium, ~100bps below the 6.0% Australian-expert convention.",
 "beta":"Peer triangulation: Grifols / Takeda / Sanofi cluster 0.7–0.9 → selected <b>0.85</b>. Measured <b>0.094</b> rejected — it regressed an AUD-listed price against an AUD index for a USD-earning business.",
 "debt":"Not separately built — CSL&rsquo;s DCF discounts FCFF at the cost of equity (8.75%) rather than a blended WACC; see &lsquo;WACC vs cost of equity&rsquo; below.",
 "gearing":"Not applied — the CSL DCF discounts FCFF at Re, so no debt/equity weighting is used.",
 "wacc":"A single <b>cost of equity 8.75%</b> is applied to FCFF rather than a blended WACC — a simplification worth flagging; it slightly understates the discount rate versus a formal WACC.",
}

dnl = {
 "company":"Dyno Nobel Limited (ASX:DNL)","companyShort":"DNL","ccy":"AUD","ccynote":"AUD · WACC-based DCF",
 "dp":2,"market":3.61,"broker":3.61,"scale":4.6,"liveIdx":2,"activeIdx":2,
 "richbook":True,"shares":1884,"netDebt":1512,"netDebtExLeases":1300,"leaseLiab":212,
 "_leaseContract":{"_mock":True,"accountingStandard":"AASB 16 / IFRS 16","totalDebtIncludesLeases":False,"leaseLiability":212,"annualLeaseCost":45,"incrementalBorrowingRate":0.055,"leaseMaturityUndisc":{"y1":48,"y2":44,"y3":40,"y4":34,"y5":28,"beyond5":60},"contractNote":"Shape the real EODHD feed must reproduce (for Ben): (1) whether reported total debt includes AASB 16 lease liabilities; (2) the annual rent / lease-cost line (RoU depreciation + lease interest); (3) the undiscounted lease-maturity table, to re-capitalise peers on a uniform house rule; (4) the accounting standard (AASB 16 / IFRS 16 vs US GAAP ASC 842). MOCK values until the feed returns."},
 "mklab":"vs market (3.61)","brlab":"vs broker target (3.61)","metric4":{"label":"Asymmetry (down/up)","value":"4.05×"},
 "pvsub":"","topnote":"Working prototype — all six scenarios calibrated (v4). Slider responses are an illustrative approximation, not the production DCF engine. Reid Advisory, June 2026.",
 "footnote":"Prototype for discussion. Calibrated central case: DNL Muddle Through AUD 3.48 (market AUD 3.61). Per-scenario figures from dnl_scenarios_comparison_v4.",
 "cp":{"base":3.48,"re0":0.0868,"g0":0.025,"m0":13.5,"tax0":0.275,"wTerm":0.85,"xKey":"gas","x0":100,"xk":-0.0008},
 "sliders":[
   {"k":"re","label":"Discount rate (WACC)","min":7,"max":11,"step":0.25,"def":8.68,"suf":"%","dec":2},
   {"k":"g","label":"Terminal growth","min":1.5,"max":3.5,"step":0.25,"def":2.5,"suf":"%","dec":2},
   {"k":"m","label":"Normalised EBIT margin","min":10,"max":17,"step":0.5,"def":13.5,"suf":"%","dec":1},
   {"k":"tax","label":"Blended tax rate","min":22,"max":32,"step":0.5,"def":27.5,"suf":"%","dec":1},
   {"k":"gas","label":"Gas roll-off drag (cumulative)","min":0,"max":200,"step":25,"def":100,"suf":" bps","dec":0}],
 "scenarios":[
   {"n":"Orderly Convergence","v":4.05,"kind":"up"},
   {"n":"Average broker","v":3.61,"kind":"broker"},
   {"n":"Muddle Through","v":3.48,"kind":"live"},
   {"n":"AI Productivity Lag","v":3.37,"kind":"down"},
   {"n":"Fragmentation","v":2.52,"kind":"down"},
   {"n":"Disorderly Climate","v":1.33,"kind":"down"},
   {"n":"Stagflation Persists","v":1.17,"kind":"down"}],
 "titles":{"world":"World scenario","forces":"Company vs industry — Five Forces","position":"Company position","discount":"Discount rate","assum":"Assumptions & rationale","dcf":"Valuation build-up","multiples":"Multiples","financials":"Summary financials"},
 "snap":{
   "world":'<b id="wsnaptitle">Muddle Through</b> — status-quo extension; gas roll-off offset by peer-gap closure; sits just below market. <span class="more" data-k="world">Learn more →</span>',
   "forces":'<b>DNL vs the industrial-explosives archetype</b>, force by force, with each impact. <span class="more" data-k="forces">See the comparison →</span>',
   "position":'<b>Pure-play explosives</b> — #2 global, Australian duopoly, ~35% coal mix. <span class="more" data-k="position">Learn more →</span>',
   "discount":'<b>WACC ~8.9%</b> = 79% equity (Re 9.80%) + 21% debt. <span class="more" data-k="discount">See the build-up →</span>',
   "assum":'<b>Assumptions</b> — each input tagged and rationalised. <span class="more" data-k="assum">See all →</span>',
   "dcf":'<b>FCFF → per share</b> — single WACC across scenarios; gas roll-off in the margin path. <span class="more" data-k="dcf">Open the build-up →</span>'},
 "narr":{
   "Muddle Through":'<p>Status-quo extension of the post-demerger franchise: mining-customer demand holds, input costs are broadly stable, and the US cost-curve advantage from long-term gas contracts is intact in the near term. The single most consequential firm-specific variable — the <b>US gas-contract roll-off in the 2028–2030 window</b> — is built explicitly into the margin path (−50/−100/−150 bps cumulative Y3/Y4/Y5), and is offset by peer-gap closure toward Orica-level efficiency.</p><p><b>Why AUD 3.48?</b> It sits modestly below market (AUD 3.61, ~4%) — the framework agrees with consensus on the central case. The value-add is not disagreement here, it is the scenario <i>asymmetry</i> around this point.</p><p style="background:var(--secondary); border-radius:8px; padding:10px;"><b>Mental short-cut:</b> a cyclical industrial priced fairly at the centre, but with a downside that bites ~4× harder than the upside lifts.</p>',
   "Orderly Convergence":'<p>Mining capex healthy, transition-mineral demand (copper, lithium, nickel) pulls volumes, and a modest margin lift comes through. The upside is real but capped by the oligopolistic structure — only +AUD 0.57 above Muddle Through.</p>',
   "AI Productivity Lag":'<p>Close to neutral. A modest labour-cost benefit on SG&amp;A from automation, otherwise the macro is broadly status-quo. −3% vs Muddle Through — the least-sensitive scenario.</p>',
   "Fragmentation":'<p>DNL sits ~90% in the US-aligned bloc (USA + Australia), which is the slower-growing bloc; cross-bloc ammonium-nitrate and ammonia flows are regulatorily sensitive and supply chains duplicate. Partially offset by Australia&rsquo;s strategic-mineral position. −27%.</p>',
   "Disorderly Climate":'<p>Coal customers (~35% of the mix) attrit faster than the standard fade assumes; carbon costs flow through ammonia into bulk ANFO; capex rises. A partial offset from transition-mineral mining demand. The moat decays over a shortened fade (§10.6). −60%.</p>',
   "Stagflation Persists":'<p>The binding downside. Sustained input-cost inflation that <b>cannot be passed through</b> — supplier power blocks it while mining customers resist price increases — combined with slowing mining capex. −65% vs Muddle Through; the −AUD 2.31 that sets the 4.05× asymmetry.</p>',
   "_placeholder":'<p>Scenario narrative pending.</p>'},
 "_forces":{
   "intro":"<b>The industry.</b> Industrial explosives is a mature, concentrated oligopoly — the top three (Orica, Dyno Nobel, MAXAM) hold ~65% of global volume and Australia is a duopoly. Scale incumbents earn moderate excess returns from long-term offtake contracts, on-site infrastructure and technology, while marginal players are pushed toward cost-of-capital returns; a profile weighted to high buyer power and high rivalry caps how durable those returns are.</p><p>Below, how Dyno Nobel sits within that archetype, force by force — industry rating is the archetype baseline, the badge is DNL&rsquo;s position, and impact is the growth/margin offset.",
   "rows":[
     ["Buyer power","High","Mining-customer concentration is the binding constraint — top 3–5 global miners drive volume, are highly price-sensitive on bulk ANFO, and hold a real backward-integration threat.","at industry average","0 bps","Same mining-major customer mix as Orica"],
     ["Supplier power","Moderate","Anhydrous ammonia (and upstream natural gas) is the dominant input — contained for producers with long-term gas contracts, significant for spot-gas-exposed players.","more favourable","+200→0 bps","Long-term US gas contracts shield ~70% of US gas through 2028; rolls off by FY31"],
     ["New entrants","Low","Strong barriers — explosives licensing, dangerous-goods and environmental regulation, capital-intensive plants, and incumbents&rsquo; long-term offtake contracts and on-site infrastructure.","more favourable","+15 bps","DNL is itself the new entrant via the DNEL ramp in emerging markets"],
     ["Substitutes","Low","No meaningful substitute for industrial explosives in hard-rock mining; mechanical excavation is niche — coal-volume decline is a demand question, not a substitute one.","at industry average","0 bps","Intra-industry tech substitution affects all players equally"],
     ["Rivalry","High","Concentrated global oligopoly (Orica / Dyno Nobel / MAXAM ~65%); Australia a duopoly. Bulk ANFO competes on price while technology products differentiate.","less favourable","−40 bps","#2 vs Orica #1; more bulk-ANFO, fewer high-margin electronic detonators"]],
   "net":"−25 bps net growth offset (rivalry −30 + product-mix −10 + new-entrants +15). The supplier-power margin edge is transitory — it rolls off with the gas contracts."},
 "_position":'<div class="thytag" style="color:var(--text3); margin:0 0 4px;">Franchise & moat</div><ul style="padding-left:18px;"><li><b>Pure-play post-demerger</b> &ndash; explosives-only after the March 2025 Incitec Pivot split (fertilisers demerged, entity renamed); single reporting segment.</li><li><b>Global #2, Australian duopolist</b> &ndash; #1 in North American industrial explosives (~30% share), #2 to Orica in Australia (~40% share), plus a sub-scale ~5% RoW book slowly gaining.</li><li><b>US cost-curve edge &ndash; transitory</b> &ndash; long-term gas contracts put US ops in the bottom cost-curve quartile (~+200bps margin), rolling off through a 2028&ndash;2030 re-pricing window (6-year average maturity) to nil by FY31.</li><li><b>Switching-cost moat</b> &ndash; 200+ on-site mobile manufacturing units at customer mine sites, multi-decade relationships and 5&ndash;10-year offtake contracts (BHP, Rio Tinto, FMG); ~78% of revenue contracted.</li></ul><div class="thytag" style="color:var(--text3); margin:14px 0 4px;">Geography, product & peers</div><ul style="padding-left:18px;"><li><b>Geography &amp; currency</b> &ndash; ~55% USA, ~35% Australia, ~10% RoW; per-entity functional currency under IAS 21 (parent AUD, Dyno Nobel Americas USD-functional on US revenue, gas and ammonia).</li><li><b>Product &amp; customer mix</b> &ndash; ~50% commodity bulk ANFO, ~18% higher-growth electronic detonators (DigiShot); ~35% coal-exposed, offset by transition-mineral demand. Top 5 customers ~45% of revenue.</li><li><b>Peer-gap to Orica</b> &ndash; Orica is ~30% larger with a technology and diversification lead, driving a net ~25bps company-position growth drag (&minus;30 rivalry, &minus;10 mix, +15 EM ramp).</li></ul><div class="thytag" style="color:var(--text3); margin:14px 0 4px;">Financials & risks</div><ul style="padding-left:18px;"><li><b>Balance sheet</b> &ndash; net debt/EBITDA 2.12x; AUD 647m liquidity; thin FY25 free cash flow (AUD 101m) vs AUD 162m dividends + AUD 289m buybacks; 60&ndash;70% payout target.</li><li><b>Key risks</b> &ndash; gas/ammonia input costs, coal-customer transition, and a weak large-project execution record (Louisiana ammonia overruns 2017&ndash;2020); carbon exposure rated high given ~55% ammonia self-supply.</li></ul>',
 "_discount": '<p>Single WACC, held constant across scenarios (risk is priced in the cash flows, not the rate — §3.5).</p>'+dtable([["Risk-free rate (10y CGS)","4.30%","disclosed"],["Equity risk premium","5.00%","judgment"],["Beta — selected","1.10","judgment"],["= Cost of equity","9.80%","derived"],["Cost of debt (pre-tax)","6.00%","disclosed"],["= WACC (84/16 E/D)","~8.9%","derived"]])+'<p style="margin-top:8px;"><b>Beta — peer triangulation.</b> Orica 1.05 / ICL 1.10 / Yara 1.20 cluster (Sasol 1.45 excluded); DNL placed at 1.10. Measured β 0.36 (world-index, AUD series) rejected as unreliable.</p>',
 "_assum":[
   ["Risk-free rate","4.30%","disclosed","10y Commonwealth Govt bond YTM"],
   ["Equity risk premium","5.00%","judgment","Damodaran-style mature-Australia ERP"],
   ["Beta (selected)","1.10","judgment","Peer cluster Orica/ICL/Yara; measured 0.36 unreliable"],
   ["WACC","~8.9%","derived","83.5% equity × Re 9.80% + 16.5% debt × 6.0%(1−t)"],
   ["Normalised EBIT margin","13.5%","judgment","Through-cycle; corporate already in segment guidance"],
   ["Gas roll-off drag","−50/−100/−150 bps","judgment","Cumulative Y3/Y4/Y5 as US gas contracts roll off (§3.2.1)"],
   ["Terminal growth g","2.5%","judgment","Demographic trajectory pulls toward 2.0% long-run"],
   ["Blended tax rate","27.5%","derived","Jurisdiction-weighted statutory; effective glides to this"],
   ["Net debt","AUD 1,224m","derived","At valuation date: 31 Mar anchor walked over Period A (§7)"],
   ["Shares","1,770m","disclosed","Issued at the 31 Mar 2026 H1 anchor (§5.3)"]],
 "dcf": bridge([["Enterprise value (DCF)","8,064"],["Less: net debt (ex-leases)","(1,300)"],["Less: AASB 16 lease liabilities","(212)"],["Equity value","6,552"],["÷ shares (m)","1,884"],["Value per share AUD","3.48"]],
   "AUD m. Five-year FCFF (stub + FY27–FY31), single WACC ~8.9%, terminal g 2.5%, with the gas roll-off built into the margin path. Per-scenario detail in dnl_scenarios_comparison_v4."),
 "dcfIntro":"AUD m. Click any line to see its make-up. Five-year FCFF (stub + FY27\u2013FY31), single WACC ~8.9%, terminal g 2.5%, gas roll-off in the margin path.",
 "dcfRows":[
   ["Enterprise value (DCF)","8,064","Sum of five years of free cash flow to the firm (stub + FY27\u2013FY31) discounted at WACC ~8.9%, plus a Gordon-growth terminal value at g 2.5%. FCFF is built from a normalised EBIT margin of 13.5% (with the \u221250 / \u2212100 / \u2212150 bps gas roll-off in the margin path), blended tax 27.5%, and steady-state reinvestment. Full per-scenario build in the dnl_scenarios_comparison_v4 workbook."],
   ["Less: net debt (ex-leases)","(1,300)","Interest-bearing borrowings less cash and short-term investments (FY25 liquidity ~AUD 647m = AUD 207m cash + AUD 440m short-term investments), normalised to a steady-state anchor. AASB 16 leases are added on the next line per Approach A."],
   ["Less: AASB 16 lease liabilities","(212)","AASB 16 lease liability treated as debt (Approach A), consistent with the post-AASB 16 EBITDA used above (rent already replaced by right-of-use depreciation and lease interest). Materiality shown in the panel below."],
   ["Equity value","6,552","Enterprise value 8,064 less net debt 1,300 (ex-leases) less AASB 16 leases 212. Post-demerger equity-bridge adjustments (IPF distribution +125, Geelong remediation \u221235, Gibson Island \u221297, transaction costs \u221211, PH contingent +100) broadly net out and are absorbed into the normalised net-debt anchor."],
   ["\u00f7 shares (m)","1,884","Latest reported shares on issue, paired to the net-debt anchor date; no buyback projection is modelled (value-neutral)."],
   ["Value per share AUD","3.48",""]],
 "_financials": {'ccy': 'AUD m', 'fye': '30 Sep', 'years': ['FY21', 'FY22', 'FY23', 'FY24', 'FY25'], 'real': [False, False, False, False, True], 'intro': 'Summary income statement, balance sheet and cash flow. <b>FY25 is real, as-reported</b> (year to 30 Sep 2025, first year as Dyno Nobel post-demerger). <b>FY21–FY24 are illustrative mock placeholders</b> on a continuing-operations basis — not reported figures.', 'note': 'Mock data — FY21–FY24 are placeholders pending Ben’s EODHD DNL/IPL export (feed temporarily down). FY25 is the real reported year from the base-year snapshot.', 'foot': 'FY25 as-reported per the base-year snapshot (EBIT after ~AUD 200m of demerger-related significant items; profit attributable to ordinary holders −AUD 53m after those charges). The cash flow articulates with the other two statements: operating cash flow builds from net profit after tax + D&amp;A + working-capital movements (the working-capital lines tie to the balance-sheet current assets/liabilities), free cash flow = operating cash flow less capex, and cash at end of year equals the balance-sheet cash line each year (FY25 AUD 647m). FY25 working-capital-&amp;-other and financing lines are condensed (they fold in non-cash demerger items, buybacks, net borrowings and short-term-investment movements) so the statement still ties to the reported balance sheet. A small assets-vs-liabilities+equity gap remains from non-controlling interests and rounding to AUD m. FY21–FY24 are mock and internally consistent only for illustration; pre-demerger IPL group results (which included the demerged fertilisers business) are deliberately not shown.', 'pl': [['Revenue', [3180, 3320, 3500, 3600, 3710]], ['Cost of sales', [-2306, -2407, -2538, -2610, -2688]], ['Gross profit', [874, 913, 962, 990, 1022], True], ['Other operating expenses', [-366, -382, -402, -414, -394]], ['EBITDA', [509, 531, 560, 576, 628], True], ['Depreciation & amortisation', [-238, -249, -262, -270, -284]], ['EBIT', [270, 282, 298, 306, 344], True], ['Net interest expense', [-74, -74, -74, -74, -80]], ['Non-operating & significant items', [0, 0, 0, 0, -78]], ['Profit before tax', [196, 208, 224, 232, 186], True], ['Income tax expense', [-53, -56, -60, -63, -38]], ['Net profit after tax', [143, 152, 163, 169, 146], True]], 'bs': [['Cash & short-term investments', [572, 598, 630, 648, 647]], ['Trade & other receivables', [716, 747, 788, 810, 840]], ['Inventory', [445, 465, 490, 504, 519]], ['Other current assets', [80, 83, 88, 90, 116]], ['Total current assets', [1813, 1892, 1995, 2052, 2123], True], ['Property, plant & equipment', [2035, 2125, 2240, 2304, 2366]], ['Goodwill', [1778, 1778, 1778, 1778, 1778]], ['Other intangibles', [763, 797, 840, 864, 848]], ['Investments & other non-current', [413, 432, 455, 468, 531]], ['Total non-current assets', [4990, 5132, 5314, 5414, 5707], True], ['Total assets', [6803, 7024, 7308, 7466, 7830], True], ['Trade & other payables', [636, 664, 700, 720, 734]], ['Short-term debt', [560, 560, 560, 560, 626]], ['Other current liabilities', [191, 199, 210, 216, 231]], ['Total current liabilities', [1387, 1423, 1470, 1496, 1591], True], ['Long-term debt', [1150, 1150, 1150, 1150, 1239]], ['Lease liabilities', [200, 200, 200, 200, 212]], ['Other non-current liabilities', [18, 18, 18, 18, 18]], ['Total non-current liabilities', [1368, 1368, 1368, 1368, 1806], True], ['Total liabilities', [2755, 2791, 2838, 2864, 3397], True], ['Total equity', [4048, 4233, 4470, 4602, 4431], True]], 'cf': [['Net profit after tax', [143, 152, 163, 169, 146]], ['Add: depreciation & amortisation', [238, 249, 262, 270, 284]], ['Add: non-cash significant items', [0, 0, 0, 0, 78]], ['Working capital & other operating items', [-21, -18, -24, -12, 67]], ['Operating cash flow', [360, 383, 401, 427, 575], True], ['Capital expenditure', [-223, -232, -245, -252, -474]], ['Free cash flow', [137, 151, 156, 175, 101], True], ['Dividends paid', [-86, -91, -98, -102, -162]], ['Buybacks, net borrowings & other financing', [-31, -34, -26, -55, 60]], ['Net change in cash', [20, 26, 32, 18, -1], True], ['Cash at beginning of year', [552, 572, 598, 630, 648]], ['Cash at end of year', [572, 598, 630, 648, 647], True]]},
 "dcfDetail": {"reinvest": 25, "leaseMat": {"liab":212,"ev":8064,"shares":1884,"netDebtIncl":1512,"leaseCost":45,"ebitdaRep":628,"ebitdaFwd":772,"threshold":"10-15%","verdict":"Lease-light"}, "netDebt": [["Short-term debt", 626], ["Long-term debt", 1239], ["Gross borrowings", 1865, "sub"], ["Less: cash \u0026 short-term investments", -647], ["Net debt \u2014 reported (narrow, ex-leases)", 1218, "sub"], ["Add: AASB 16 lease liabilities", 212], ["Normalisation to steady-state anchor", 82], ["Net debt used in the bridge (lease-inclusive)", 1512, "tot"]], "netDebtNote": "Approach A (leases = debt): interest-bearing borrowings less cash \u0026 short-term investments; the AUD 212m AASB 16 lease liability is added on its own line per Approach A. Post-demerger equity-bridge items \u2014 IPF distribution +125, Geelong remediation \u221235, Gibson Island \u221297, transaction costs \u221211, PH contingent +100 \u2014 net to ~+82 and are absorbed into the normalised anchor.", "mt": {"years": ["FY27", "FY28", "FY29", "FY30", "FY31"], "revenue": [4139, 4394, 4665, 4953, 5257], "ebit": [608, 699, 728, 748, 768], "taxGlide": [22.5, 23.75, 25.0, 26.25, 27.5], "baseMargin": 14.1, "peerGap": [60, 180, 200, 200, 200], "gasRolloff": [0, 0, -50, -100, -150], "note": "Muddle Through operating build, traceable to the audited workbook (methodology \u00a711: industry baseline + company offset shown explicitly). Only the revenue LEVEL is re-based to the clean post-demerger run-rate — FY26 ~3,905 (TTM to 31 Mar 26), growing at the established ~6% p.a. — replacing the earlier ~3,400 reduced-form base that sat ~13% below the reported baseline. The EBIT margin is UNCHANGED from the established build (14.1% FY26 base + the peer-gap-closure overlay less the US gas-contract roll-off). NOPAT = EBIT \u00d7 (1\u2212tax); FCFF then adds D\u0026A (~7.3% of revenue), deducts capex (~7%) and working-capital investment (D\u0026A \u2248 capex in steady state). Full cash-flow bridge in the workbook. Per-scenario operating lines arrive with the DCF engine; other scenarios use the reduced-form reconstruction above."}},
 "multiples": {"evBridge": True, "baseDefault": "fy26", "metricDefault": "evebitda", "note": "Peer-median multiples are illustrative mock (EODHD feed down). The subject earnings base and the market-implied line are real, computed on the model’s own price / shares / net-debt convention.", "bases": {"fy25u": {"label": "FY25 underlying", "peerKey": "ttm", "ebitda": 768, "ebit": 484, "ni": 322, "note": "Underlying FY25 (year to 30 Sep 25), stripping ~AUD 200m of demerger significant items — operating-income basis (EBIT 484 vs reported 344; EBITDA 768). Trailing, ex one-offs, so the multiple is meaningful."}, "fy26": {"label": "FY26 forward", "peerKey": "fwd", "ebitda": 836, "ebit": 551, "ni": 372, "consensus": {"ebitda": 810, "ebit": 530, "ni": 355}, "note": "FY26 (year to 30 Sep 26) — largely the current year at the May-2026 valuation date. Revenue ~3,905 (TTM to 31 Mar 26, the clean post-demerger run-rate) at the model\u2019s established FY26 base EBIT margin of 14.1% — the existing operating-build assumption, unchanged. Mostly locked in."}, "fy27": {"label": "FY27 forward", "peerKey": "fwd", "peerGrow": 1.055, "ebitda": 910, "ebit": 608, "ni": 409, "consensus": {"ebitda": 880, "ebit": 585, "ni": 393}, "note": "FY27 (year to 30 Sep 27) — first full forward year in the DCF explicit period. Revenue ~4,139 (the established ~6% growth); EBIT margin 14.7% straight from the operating build (14.1% base + peer-gap closure less the US gas-contract roll-off) — the existing assumption, not a new one."}}, "metrics": [{"k": "evebitda", "label": "EV / EBITDA", "kind": "ev", "field": "ebitda", "peer": 8.5, "peerNote": "Orica / Yara / ICL ~8-9.5x"}, {"k": "evebit", "label": "EV / EBIT", "kind": "ev", "field": "ebit", "peer": 12.5, "peerNote": "peer set ~11-14x"}, {"k": "pe", "label": "P / E", "kind": "eq", "field": "ni", "peer": 15.0, "peerNote": "peer set ~13-17x"}]},
 "worldDesc": WORLD_DESC, "_drtheory": drtheory(DNL_DID)
}

wbc = {
 "company":"Westpac Banking Corporation (ASX:WBC)","companyShort":"WBC","ccy":"AUD","ccynote":"AUD · cost-of-equity (bank §15)",
 "dp":2,"market":35.32,"broker":33.45,"scale":40.0,"liveIdx":2,"activeIdx":2,
 "mklab":"vs market (35.32)","brlab":"vs broker target (33.45)","metric4":{"label":"Asymmetry (down/up)","value":"1.90×"},
 "pvsub":"","topnote":"Working prototype — all six scenarios calibrated (v3). Slider responses are an illustrative approximation, not the production engine. Bank fork (methodology §15). Reid Advisory, June 2026.",
 "footnote":"Prototype for discussion. Calibrated central case: WBC Muddle Through AUD 30.15 (market AUD 35.32). Per-scenario figures from wbc_scenarios_comparison_v2.",
 "cp":{"base":30.15,"re0":0.0805,"g0":0.025,"m0":11.5,"tax0":0.30,"wTerm":0.95,"xKey":"credit","x0":18,"xk":-0.004},
 "sliders":[
   {"k":"re","label":"Discount rate (cost of equity)","min":7,"max":10,"step":0.25,"def":8.05,"suf":"%","dec":2},
   {"k":"g","label":"Terminal growth","min":1.5,"max":3.5,"step":0.25,"def":2.5,"suf":"%","dec":2},
   {"k":"m","label":"Terminal ROE","min":9,"max":14,"step":0.25,"def":11.5,"suf":"%","dec":2},
   {"k":"tax","label":"Effective tax rate","min":25,"max":32,"step":0.5,"def":30,"suf":"%","dec":1},
   {"k":"credit","label":"Through-cycle credit loss","min":5,"max":60,"step":5,"def":18,"suf":" bps","dec":0}],
 "scenarios":[
   {"n":"Orderly Convergence","v":35.46,"kind":"up"},
   {"n":"Average broker","v":33.45,"kind":"broker"},
   {"n":"Muddle Through","v":30.15,"kind":"live"},
   {"n":"AI Productivity Lag","v":29.75,"kind":"down"},
   {"n":"Fragmentation","v":27.29,"kind":"down"},
   {"n":"Disorderly Climate","v":23.11,"kind":"down"},
   {"n":"Stagflation Persists","v":20.09,"kind":"down"}],
 "titles":{"world":"World scenario","forces":"Company vs industry — Five Forces","position":"Company position","discount":"Discount rate","assum":"Assumptions & rationale","dcf":"Valuation build-up"},
 "snap":{
   "world":'<b id="wsnaptitle">Muddle Through</b> — status-quo NIM at anchor; UNITE cost-to-income glide; through-cycle credit losses. <span class="more" data-k="world">Learn more →</span>',
   "forces":'<b>WBC vs the major-banks archetype</b>, force by force, with each impact. <span class="more" data-k="forces">See the comparison →</span>',
   "position":'<b>#2 mortgage book</b> (~20% system); the question is whether UNITE closes the peer gap. <span class="more" data-k="position">Learn more →</span>',
   "discount":'<b>Cost of equity 8.05%</b> = Rf 4.30% + β 0.75 × ERP 5.0% (no WACC bridge). <span class="more" data-k="discount">See the build-up →</span>',
   "assum":'<b>Assumptions</b> — each input tagged and rationalised. <span class="more" data-k="assum">See all →</span>',
   "dcf":'<b>Bank build-up</b> — NIM, credit, cost-to-income, CET1-bound payout, ROE fade. <span class="more" data-k="dcf">Open the build-up →</span>'},
 "narr":{
   "Muddle Through":'<p>Status-quo extension: NIM held at the through-cycle 1.94% anchor, the UNITE cost-to-income glide delivers part of the peer-gap closure, and credit losses run at the 18 bps through-cycle anchor. CET1 (12.42%) sits comfortably above target, supporting the buyback.</p><p><b>Why AUD 30.15, ~15% below market?</b> The market (AUD 35.32) is implicitly trading WBC at a <i>successful-transformation</i> outcome — essentially the Orderly Convergence scenario (AUD 35.46) — not at this status-quo base. To converge to market on a Muddle Through path, terminal ROE has to be 12.1% (CBA-like), not the archetype mid-point.</p><p style="background:var(--secondary); border-radius:8px; padding:10px;"><b>Mental short-cut:</b> the market is paying for the transformation; Muddle Through is what you get if it only half-lands.</p>',
   "Orderly Convergence":'<p>Healthy loan growth, a benign credit cycle and modest NIM uplift; UNITE closes most of the cost-to-income gap. At AUD 35.46 it sits essentially at market — the framework&rsquo;s read on what current pricing implies. +17.6% vs Muddle Through.</p>',
   "AI Productivity Lag":'<p>Close to neutral. A modest cost benefit from automation, offset by weaker macro loan demand. −1.3% vs Muddle Through.</p>',
   "Fragmentation":'<p>Hits non-interest income (markets / institutional) more than net interest income, with modest credit losses on the business book. −9.5%.</p>',
   "Disorderly Climate":'<p>APRA climate-adjusted RWA models lift capital intensity for vulnerable zones; WBC&rsquo;s #2 mortgage book carries more absolute climate-vulnerable exposure than NAB or ANZ. Transmission is mainly via terminal-ROE compression (−1.5pp). −23%.</p>',
   "Stagflation Persists":'<p>The binding downside. NIM compresses −20 bps (deposit competition + slow front-book repricing), credit losses lift to peak-cycle (+50 bps), and cost growth runs ahead of the glide. CET1 forces payout from 75% down to ~50% to rebuild capital. NPAT Y5 AUD 3.7bn vs MT AUD 8.9bn. −33%.</p>',
   "_placeholder":'<p>Scenario narrative pending.</p>'},
 "_forces":{
   "intro":"<b>The industry.</b> The Australian majors are a durable, APRA-protected oligopoly — four-pillars policy, D-SIB capital floors and deep deposit franchises keep the Big Four insulated on a 5–10 year view. Roughly 55% of the pool is Australian housing, where the tension between competitive front-book pricing and sticky back-book margin is the single most important profitability dynamic; returns are structurally solid but rate- and credit-cycle sensitive.</p><p>Below, how Westpac sits within that archetype, force by force — industry rating is the archetype baseline, the badge is WBC&rsquo;s position, and impact is the NIM/growth offset.",
   "rows":[
     ["Buyer power","Low–moderate","Retail customers have low switching propensity (relationship inertia, bundling, discharge friction); the binding constraint sits in the marginal front-book mortgage-refinancing cohort.","at industry average","0 bps","Switching costs + oligopoly; standard across the Big Four"],
     ["Supplier power","Moderate","Deposit-holders and wholesale-debt investors are the funding &lsquo;suppliers&rsquo; with real switching options, but the Big Four are price-takers within a narrow oligopolistic funding-cost range.","more favourable","+8 bps NIM","AUD 149bn non-interest-bearing transaction deposits — a funding-cost floor"],
     ["New entrants","Low","APRA licensing, D-SIB capital floors (~11.5% CET1), distribution scale, and incumbent deposit-franchise funding advantage; neo-bank waves produced no material disruption.","at industry average","0 bps","Four-pillars policy + capital and licensing barriers"],
     ["Substitutes","Low–moderate","Non-bank lenders take share when serviceability binds, super substitutes for term deposits, fintech erodes some transaction revenue — gradual margin erosion, not existential displacement.","at industry average","0 bps","Fintech / neobank nibble; not displacement-scale"],
     ["Rivalry","Moderate","Oligopolistic (CBA ~25%, WBC ~20%, NAB/ANZ ~14% mortgage share); pricing discipline holds in benign periods but breaks under share-loss pressure (2022–24 cashback discounting compressed NIM).","less favourable","−10 bps","~10pp cost-to-income gap to CBA (51.7% vs ~42%); mid-tier ROE"]],
   "net":"+8 bps NIM (deposit franchise) less ~−10 bps revenue growth (cost-to-income gap to peers)."},
 "_position":'<div class="thytag" style="color:var(--text3); margin:0 0 4px;">Franchise & moat</div><ul style="padding-left:18px;"><li><b>#2 Big Four franchise</b> &ndash; second-largest by total assets, anchored on a AUD 517.7bn Australian mortgage book (~20% system share, #2 to CBA&rsquo;s ~25%) plus an AUD 18.5bn RAMS book in run-off.</li><li><b>Deposit-funded edge</b> &ndash; #2 household deposits (AUD 615bn retail base), including AUD 149bn non-interest-bearing transaction balances giving a structural +8bps NIM funding-cost advantage over wholesale-funded peers.</li><li><b>Segment mix</b> &ndash; consumer ~37% of earnings, business &amp; wealth ~28% (AUD 238bn loans, #3, rebuilding), institutional (WIB) ~17%, Westpac NZ ~12% (NZD-functional, ~18% NZ mortgage share).</li></ul><div class="thytag" style="color:var(--text3); margin:14px 0 4px;">Transformation & rivalry</div><ul style="padding-left:18px;"><li><b>The transformation thesis</b> &ndash; does the multi-year UNITE program (FY26&ndash;FY28) close the ~10pp cost-to-income gap to CBA (51.7% vs ~42%, NAB ~43%) and the ~4pp ROE gap (9.8% TTM vs a 10.5% through-cycle anchor)?</li><li><b>Rivalry drag</b> &ndash; the cost-to-income gap is ~150bps of ROE drag vs the leaders; treated as a management-committed glide toward ~45% by FY29, leaving ~&minus;10bps residual growth drag plus ~&minus;5bps from the business-banking rebuild.</li></ul><div class="thytag" style="color:var(--text3); margin:14px 0 4px;">Capital, funding & risks</div><ul style="padding-left:18px;"><li><b>Capital</b> &ndash; Level 2 CET1 12.42% (Level 1 12.75%), 92bps above the 11.0&ndash;11.5% target &ndash; binds payout under stress; Total Capital 21.5%, AT1 AUD 8.5bn, total RWA AUD 458bn, mortgage RWA density 22.6%.</li><li><b>Funding &amp; loan book</b> &ndash; gross loans AUD 890bn, customer deposits AUD 745bn; through-cycle credit-loss anchor 18bps (low end of Big Four) vs benign 1H26 actual ~10bps.</li><li><b>Capital return</b> &ndash; 70&ndash;75% payout target (77% actual, 100% franked), forward dividend AUD 1.54 (~4.4% yield); AUD 1.5bn buyback active, AUD 581m executed FY25.</li><li><b>Key risks</b> &ndash; high rate/credit-cycle sensitivity (peak-cycle losses ~75bps); UNITE re-platforming is the single largest execution risk; indirect climate exposure via vulnerable mortgage geographies.</li></ul>',
 "_discount": '<p>Cost of equity only — no WACC / EV bridge for a bank (methodology §15).</p>'+dtable([["Risk-free rate (10y CGS)","4.30%","disclosed"],["Equity risk premium","5.00%","judgment"],["Beta — selected","0.75","judgment"],["= Cost of equity Re","8.05%","derived"]])+'<p style="margin-top:8px;"><b>Beta — peer triangulation.</b> CBA 0.80 / NAB 0.72 / WBC 0.73 cluster → 0.75; ANZ excluded as an institutional-dilution outlier. Measured β 0.73 documented alongside.</p>',
 "_assum":[
   ["Risk-free rate","4.30%","disclosed","10y Commonwealth Govt bond YTM"],
   ["Equity risk premium","5.00%","judgment","Damodaran-style mature-Australia ERP"],
   ["Beta (selected)","0.75","judgment","CBA/NAB/WBC cluster; ANZ excluded; measured 0.73"],
   ["Cost of equity Re","8.05%","derived","Rf + β × ERP (no WACC — bank)"],
   ["Through-cycle NIM","1.94%","derived","FY22–FY25 disclosed range midpoint"],
   ["Through-cycle credit loss","18 bps","judgment","Low end of Big Four 15–25 bps; mortgage-heavy book"],
   ["Cost-to-income (1H26)","51.7%","disclosed","vs CBA ~42% / NAB ~43%"],
   ["CET1 (Level 2)","12.42%","disclosed","92 bps above 11.0–11.5% target"],
   ["Terminal ROE","fade to Ke","judgment","§15.8; market-implied 12.1% to hit current price"],
   ["Shares","3,414.9m","disclosed","EODHD-verified"],
   ["AT1 hybrids","AUD 8,522m","disclosed","Deducted from ordinary equity"]],
 "dcf": bridge([["Through-cycle NIM","1.94%"],["Through-cycle credit loss","18 bps"],["Cost-to-income","51.7%"],["Terminal ROE → Ke","fade to 8.05%"],["Ordinary equity value (post-AT1)","~102,960"],["÷ shares (m)","3,414.9"],["Value per share AUD","30.15"]],
   "AUD m. Bank valuation (methodology §15): cost of equity 8.05%, ROE fade to Ke for terminal — no WACC / EV bridge. CET1 binds payout under stress. Per-scenario detail in wbc_scenarios_comparison_v2."),
 "dcfIntro":"AUD m. Click any line to see its make-up. Bank valuation (methodology \u00a715): cost of equity 8.05%, ROE fade to Ke for terminal \u2014 no WACC / EV bridge; CET1 binds payout under stress.",
 "dcfRows":[
   ["Through-cycle NIM","1.94%","FY22\u2013FY25 disclosed NIM range midpoint, decomposed as industry AIEA NIM 1.86% + WBC deposit-franchise supplier-power offset +8 bps (AUD 149bn non-interest-bearing transaction deposits act as a funding-cost floor)."],
   ["Through-cycle credit loss","18 bps","Low end of the Big Four 15\u201325 bps range given the mortgage-heavy book. Benign 1H26 actual is ~10 bps; the peak-cycle (Stagflation) assumption is ~75 bps."],
   ["Cost-to-income","51.7%","1H26 actual, ~10pp above CBA (~42%) and NAB (~43%). The UNITE glide is assumed to close about half the gap, toward ~45% by FY29."],
   ["Terminal ROE \u2192 Ke","fade to 8.05%","Return on equity fades to the cost of equity for terminal value (\u00a715.8). A market-implied terminal ROE of ~12.1% would be required to justify the current share price."],
   ["Ordinary equity value (post-AT1)","~102,960","Equity cash flows discounted at Ke 8.05% with CET1-binding payout under stress; AT1 hybrids of AUD 8,522m are deducted from ordinary equity."],
   ["\u00f7 shares (m)","3,414.9","EODHD-verified shares on issue."],
   ["Value per share AUD","30.15",""]],
 "worldDesc": WORLD_DESC, "_drtheory": drtheory(WBC_DID)
}

csl = {
 "company":"CSL Limited (ASX:CSL)","companyShort":"CSL","ccy":"AUD","ccynote":"USD functional · AUD at 0.66 · cost-of-equity DCF",
 "dp":2,"market":105.53,"broker":136.0,"scale":260.0,"liveIdx":1,"activeIdx":1,
 "mklab":"vs market (105.53)","brlab":"vs average broker (136)","metric4":{"label":"Terminal % of value","value":"75%"},
 "pvsub":"AUD (USD-functional model, at 0.66)",
 "topnote":"Working prototype — all six scenarios calibrated (v4 / comparison v2). Slider responses are an illustrative approximation, not the production DCF engine. USD-functional; per-share shown in AUD at 0.66. Reid Advisory, June 2026.",
 "footnote":"Prototype for discussion. Calibrated central case: CSL Muddle Through USD 134.52 / AUD 203.83 (market AUD 105.53). The framework sits ~93% above market — a §16 &lsquo;cause for curiosity&rsquo;, not a calibration error; β held at 0.85 for a repeatable framework. Per-scenario figures from csl_scenarios_comparison_v2 and _muddle_through_v4.",
 "cp":{"base":203.83,"re0":0.0875,"g0":0.03,"m0":30.0,"tax0":0.19,"wTerm":0.752,"xKey":"uplift","x0":150,"xk":0.0004},
 "sliders":[
   {"k":"re","label":"Discount rate (cost of equity)","min":7,"max":11,"step":0.25,"def":8.75,"suf":"%","dec":2},
   {"k":"g","label":"Terminal growth","min":2,"max":4,"step":0.25,"def":3.0,"suf":"%","dec":2},
   {"k":"m","label":"Terminal EBIT margin","min":26,"max":34,"step":0.5,"def":30.0,"suf":"%","dec":1},
   {"k":"tax","label":"Effective tax rate","min":15,"max":25,"step":0.5,"def":19.0,"suf":"%","dec":1},
   {"k":"uplift","label":"Peer-gap margin uplift (Behring)","min":0,"max":300,"step":25,"def":150,"suf":" bps","dec":0}],
 "scenarios":[
   {"n":"Orderly Convergence","v":237.29,"kind":"up"},
   {"n":"Muddle Through","v":203.83,"kind":"live"},
   {"n":"AI Productivity Lag","v":198.53,"kind":"down"},
   {"n":"Average broker","v":136.0,"kind":"broker"},
   {"n":"Disorderly Climate","v":174.79,"kind":"down"},
   {"n":"Fragmentation","v":168.23,"kind":"down"},
   {"n":"Stagflation Persists","v":159.90,"kind":"down"}],
 "titles":{"world":"World scenario","forces":"Company vs industry — Five Forces","position":"Company position","discount":"Discount rate","assum":"Assumptions & rationale","dcf":"Valuation build-up"},
 "snap":{
   "world":'<b id="wsnaptitle">Muddle Through</b> — plasma franchise resumes its 5–7% secular path after the near-term Behring trough; margin, not volume, is the channel. <span class="more" data-k="world">Learn more →</span>',
   "forces":'<b>CSL vs the plasma / vaccines / specialty archetypes</b>, force by force, with each impact. <span class="more" data-k="forces">See the comparison →</span>',
   "position":'<b>Three businesses</b> — Behring (plasma ~72%), Seqirus (vaccines), Vifor (specialty). <span class="more" data-k="position">Learn more →</span>',
   "discount":'<b>Cost of equity 8.75%</b> = Rf 4.50% + β 0.85 × ERP 5.0% (applied to FCFF). <span class="more" data-k="discount">See the build-up →</span>',
   "assum":'<b>Assumptions</b> — each input tagged and rationalised. <span class="more" data-k="assum">See all →</span>',
   "dcf":'<b>FCFF → per share</b> — terminal 30% margin, g 3%, terminal capex = D&amp;A. <span class="more" data-k="dcf">Open the build-up →</span>'},
 "narr":{
   "Muddle Through":'<p>Post-2022 friction persists without crushing demand. The plasma franchise resumes its secular 5–7% Ig path once the near-term Behring trough (Medicare Part D redesign + China access soft patch) annualises across FY26–27. Vertical integration and fractionation scale hold the margin edge; peer-gap closure delivers <b>+150 bps</b> to Behring by FY31 (full +250 reserved for the upside). Terminal margin 30%, g 3%.</p><p><b>Why ~93% above market?</b> Not because the cash-flow path is heroic — the near-term lines sit on top of consensus — but because the terminal capitalises a high-quality compounder at ~22× forward earnings while the market trades CSL at ~11×. The entire gap is a disagreement about the <i>terminal</i>, not the next two years. Per §16 this premium is a <b>cause for curiosity, not a calibration error</b>: the §3.5.7 reverse-DCF shows no single lever reconciles to market (it would need β ≈ 1.7, or a terminal margin ~half FY25&rsquo;s, or perpetual −4% contraction), so β is deliberately held at 0.85 to keep the framework rules-based and the gap visible.</p><p style="background:var(--secondary); border-radius:8px; padding:10px;"><b>Mental short-cut:</b> CSL is a margin story, not a volume story — in every scenario the plasma keeps flowing, so watch the gap between what CSL pays US donors and what Medicare lets it charge. The framework prices the recovery; the market prices the trough.</p>',
   "Orderly Convergence":'<p>Inflation re-anchors, real rates normalise, and a productivity surprise eases costs. That buys CSL a faster Behring-trough exit and genuine donor-wage relief, making the <b>full +250 bps</b> peer-gap closure credible. Terminal margin 31.5%, g 3.25%. Instructive that the upside is only +16% — a defensive staple has no operating-leverage explosion; the upside is quiet compounding in a kind world.</p>',
   "AI Productivity Lag":'<p>Foundation models advance and gains concentrate in platform owners, showing up as white-collar wage containment — a mild tailwind on CSL&rsquo;s ~USD 1bn G&amp;A and USD 1.4bn R&amp;D. But softer macro pulls terminal g to 2.875%. The two roughly offset — the tech axis barely touches a plasma franchise. −2.6% vs Muddle Through.</p>',
   "Disorderly Climate":'<p>Disorderly transition; carbon-cost pass-through runs inflation 3–5%. CSL is exposed through cost, not demand: fractionation is energy-intensive and distribution is cold-chain dependent, so margins compress. The one genuine portfolio offset sits here — <b>Seqirus pandemic / health-disruption optionality</b> lifts vaccine demand — which is why this lands <i>better</i> than Fragmentation despite the larger cost shock. Terminal margin 28%. −14.2%.</p>',
   "Fragmentation":'<p>Trade barriers harden, supply chains localise, and China access becomes a geopolitical instrument. CSL&rsquo;s collect-in-US / fractionate / distribute-globally model is structurally awkward when blocs fragment, and Behring&rsquo;s China Ig access is the most exposed line. Peer-gap closure stalls to zero and tax drifts to 20%. With no offsetting segment (unlike the Seqirus climate cushion), the channels compound. −17.4% — the second-worst.</p>',
   "Stagflation Persists":'<p>The downside boundary and the clearest illustration of the thesis: plasma demand still holds, so the entire stress arrives as <b>margin</b> — US donor-collection wages surge (supplier-power channel at full stretch), payors press hard on price, and peer-gap closure <i>reverses</i> (Behring margin 150 bps below the FY25 base). Terminal margin 26.5%. Revenue is near-indistinguishable from Muddle Through; the whole 21% fall is the donor-vs-payor squeeze. Even here the number sits +52% above market — the puzzle §16 turns to.</p>',
   "_placeholder":'<p>Scenario narrative pending.</p>'},
 "_forces":{
   "intro":"<b>The industry.</b> Plasma-derived therapies is a near-unenterable oligopoly — CSL, Grifols, Takeda, Octapharma and Kedrion compete on supply reliability and yield rather than price, behind 5–10 year regulatory approvals and multi-billion-dollar fractionation capex. Secular immunoglobulin demand keeps the pool growing; the main constraint on industry profitability is payer-side price pressure as buyers consolidate. CSL spans three archetypes (plasma ~72%, vaccines, specialty pharma), so the rating is summarised across them.</p><p>Below, how CSL sits within that archetype, force by force — the company offsets are the Behring decomposition; Seqirus and Vifor sit at industry average.",
   "rows":[
     ["Buyer power","Moderate","Payers (Medicare, EU health systems, hospitals) hold the purse, but the products are life-sustaining so volume is inelastic — the pressure is on price, with US Medicare Part D redesign the live front.","at industry average","0 bps","Same payer mix as peers; no CSL-specific pricing edge"],
     ["Supplier power","Low–moderate","Plasma is collected from paid US donors; supplier power is generally low but donor-collection labour is a real, cyclical cost lever exposed to US frontline wages.","more favourable","+5 bps","Owns the largest plasma-donor collection network — vertical integration lowers input dependence"],
     ["New entrants","Very low","5–10yr FDA/EMA/TGA approval plus multi-billion fractionation capex make plasma near-unenterable; vaccines and specialty are low–moderate.","at industry average","0 bps","No CSL edge beyond the shared industry moat"],
     ["Substitutes","Low","No recombinant immunoglobulin at scale and biosimilar plasma is very hard; mRNA and gene therapy are a long-tail, industry-wide risk, not a near-term substitute.","at industry average","0 bps","Long-tail risk affects all fractionators equally"],
     ["Rivalry","Moderate","A rational oligopoly (CSL / Grifols / Takeda / Octapharma / Kedrion) competing on supply reliability and yield rather than price; capacity is added deliberately.","more favourable","+10 bps","Scale leader → lower marginal cost via fractionation efficiency"]],
   "net":"+15 bps margin (supplier +5, rivalry-scale +10), 0 bps revenue growth. CSL captures the industry&rsquo;s secular growth (Ig demand, indication expansion) plus a modest structural margin edge — but transmits macro stress through margin, not volume."},
 "_position":'<div class="thytag" style="color:var(--text3); margin:0 0 4px;">Businesses & moat</div><ul style="padding-left:18px;"><li><b>Three businesses on one balance sheet:</b> CSL Behring (plasma-derived therapies, ~72% of revenue, ~42% margin), CSL Seqirus (influenza vaccines, ~14%, ~47% margin — <b>demerger announced FY26</b>), CSL Vifor (iron-deficiency / renal specialty pharma, ~14%, ~49% margin, acquired Aug 2022).</li><li><b>Franchise edge:</b> the world&rsquo;s largest plasma-collection network + fractionation scale + FDA/EMA/TGA barriers — a manufacturing / scale moat, not a patent moat (patent-cliff exposure very low).</li></ul><div class="thytag" style="color:var(--text3); margin:14px 0 4px;">Geography & demand</div><ul style="padding-left:18px;"><li><b>Geography / currency:</b> global USD-functional group, ASX-listed AUD parent; US is ~55% of the plasma market. First worked example where the parent itself is USD-functional.</li><li><b>Demand character:</b> price-inelastic in volume (life-sustaining Ig) — scenarios transmit through <b>margin and policy, not volume</b>.</li></ul><div class="thytag" style="color:var(--text3); margin:14px 0 4px;">Risks & capital</div><ul style="padding-left:18px;"><li><b>Key risk:</b> US Medicare Part D redesign (~USD 100m Ig hit in 1H26) and China Ig/albumin access; donor-collection wage inflation is the other margin channel.</li><li><b>Capital:</b> net debt ~1.8× EBITDA and de-levering; USD 750m buyback; Strategic Transformation targeting &gt;USD 500m pre-tax savings by FY28.</li></ul>',
 "_discount": '<p>Cost of equity applied directly to FCFF — CSL&rsquo;s workbook discounts at Re rather than a blended WACC (a simplification; see the theory panels below).</p>'+dtable([["Risk-free rate (10y UST)","4.50%","disclosed"],["Equity risk premium","5.00%","judgment"],["Beta — selected","0.85","judgment"],["= Cost of equity Re","8.75%","derived"]])+'<p style="margin-top:8px;"><b>Beta — peer triangulation.</b> Grifols / Takeda / Sanofi cluster 0.7–0.9 → 0.85. Measured β <b>0.094</b> rejected — an AUD-listed price regressed against an AUD index for a USD-earning business (the correct-currency point). The §3.5.7 reverse-DCF implies the market is pricing β ≈ 1.7.</p>',
 "_assum":[
   ["Risk-free rate","4.50%","disclosed","10y US Treasury, mid-2026 (USD-functional)"],
   ["Equity risk premium","5.00%","judgment","Damodaran-style mature-market ERP"],
   ["Beta (selected)","0.85","judgment","Peers Grifols/Takeda/Sanofi 0.7–0.9; measured 0.094 unreliable"],
   ["Cost of equity Re","8.75%","derived","Rf + β × ERP, applied to FCFF (no WACC)"],
   ["Behring growth (J-curve)","−1% → 5.5%","judgment","FY26 trough (Part D + China) recovering to archetype 5–7% by FY29"],
   ["Peer-gap margin uplift","+150 bps","judgment","Behring, cumulative by FY31; full +250 reserved for Orderly Convergence"],
   ["Terminal EBIT margin","30.0%","judgment","Binding — capitalises 30%, not the FY31 peak"],
   ["Terminal growth g","3.0%","judgment","US nominal-GDP-adjacent"],
   ["Terminal capex","= D&A (6.0%)","judgment","Reinvestment consistency; explicit capex stays 4.5%"],
   ["Blended effective tax","19%","disclosed","FY26 guidance 18–20%"],
   ["Net debt (1H26)","USD 9,100m","disclosed","~1.8× EBITDA"],
   ["Restructuring PV","USD 507m","derived","FY26 425 + FY27 100, PV at Re; §4.4(b)"],
   ["Shares","478.9m","disclosed","EODHD, 15 Jun 2026"]],
 "dcf": bridge([["Sum PV explicit FCFF (FY27–FY31)","18,390"],["PV of terminal value","55,640"],["Enterprise value","74,029"],["Less: net debt","(9,100)"],["Less: restructuring PV","(507)"],["Equity value","64,422"],["÷ shares (m)","478.9"],["Value per share USD","134.52"],["Value per share AUD (×1.5152)","203.83"]],
   "USD m. Five-year FCFF (FY27–FY31) plus terminal, discounted at the 8.75% cost of equity with mid-period discounting. Terminal binds to a 30% EBIT margin with terminal capex = D&amp;A (75% of value). Per-scenario detail in csl_scenarios_comparison_v2."),
 "dcfIntro":"USD m. Click any line to see its make-up. Five-year FCFF (FY27\u2013FY31) + terminal, discounted at the 8.75% cost of equity with mid-period discounting; terminal binds to a 30% EBIT margin with terminal capex = D&amp;A.",
 "dcfRows":[
   ["Sum PV explicit FCFF (FY27\u2013FY31)","18,390","Five years of FCFF discounted at the 8.75% cost of equity with mid-period discounting. FCFF derives from group EBIT rising 4,346 \u2192 6,295 (USD m), less tax at 19% and reinvestment, with the Behring J-curve (\u22121% \u2192 5.5%) and +150 bps peer-gap margin uplift."],
   ["PV of terminal value","55,640","Gordon-growth terminal at g 3%, terminal EBIT margin 30% (binding, not the FY31 peak), terminal capex = D&amp;A; discounted at 8.75%. This is ~75% of enterprise value."],
   ["Enterprise value","74,029","PV of explicit FCFF 18,390 + PV of terminal value 55,640."],
   ["Less: net debt","(9,100)","1H26 net debt of ~USD 9,100m (~1.8x EBITDA), de-levering."],
   ["Less: restructuring PV","(507)","Present value of Strategic Transformation cash costs (FY26 425 + FY27 100) discounted at Re; the \u00a74.4(b) cost-of-closure consistency deduction."],
   ["Equity value","64,422","Enterprise value 74,029 less net debt 9,100 less restructuring PV 507."],
   ["\u00f7 shares (m)","478.9","EODHD, 15 Jun 2026."],
   ["Value per share USD","134.52",""],
   ["Value per share AUD (\u00d71.5152)","203.83","USD 134.52 \u00d7 1.5152 (AUD per USD; = 0.66 USD per AUD)."]],
 "worldDesc": WORLD_DESC, "_drtheory": drtheory(CSL_DID)
}

import beta_data
dnl["beta"]=beta_data.DNL; wbc["beta"]=beta_data.WBC; csl["beta"]=beta_data.CSL

import os as _os
_CFGP=_os.path.join(_os.path.dirname(_os.path.abspath(__file__)),'cfgs_gen.json')

# ---- Workstream B: Five-Forces -> driver routing (generic by driver key). ----
# Each impact names the reduced-form driver it moves; a transitory force carries a
# FY27-FY31 path (PV-collapsed for the reduced-form, fed natively to the engine at M2).
# Sign convention: +bps = value-accretive; compute applies each driver's own scale/sign.
dnl["_forces"]["impacts"] = [
  {"drv":"", "bps":0},
  {"drv":"gas", "path":[200,200,150,100,50], "note":"US gas-contract cost edge; transitory, routed to the gas driver; path = 200 + gasRolloff overlay, eroding as contracts roll off through FY31."},
  {"drv":"g", "bps":15},
  {"drv":"", "bps":0},
  {"drv":"g", "bps":-40},
]
wbc["_forces"]["impacts"] = [
  {"drv":"", "bps":0},
  {"drv":"m", "bps":8, "note":"deposit-franchise NIM edge; flows through the terminal-ROE driver."},
  {"drv":"", "bps":0},
  {"drv":"", "bps":0},
  {"drv":"g", "bps":-10},
]
csl["_forces"]["impacts"] = [
  {"drv":"", "bps":0},
  {"drv":"m", "bps":5},
  {"drv":"", "bps":0},
  {"drv":"", "bps":0},
  {"drv":"m", "bps":10},
]


# ===== SSOT: headline valuation wired to the production engine (replicable) =====
# The displayed base, scenario bars, asymmetry, discount-to-market and the
# narrative's numeric claims are computed by the production engine at generation
# time, so the UI shows one source of truth. engine_pack() is company-agnostic;
# WBC/CSL call it the same way once their scenarios resolve.
import sys as _sys
from pathlib import Path as _Path
_ROOT = _Path(__file__).resolve().parents[2]
_sys.path.insert(0, str(_ROOT / "src"))
from vcc_valuations.translator import load_inputs as _li, build_engine_inputs_from_data as _bi
from vcc_valuations.dcf.fcf_engine import FcfEngine as _Eng

def engine_pack(company_id, archetype_id, scen, broker_price):
    """Run the engine across `scen` [(scenario_id, display_name, kind)]; the
    central case is kind=='live'. Returns the UI display pack, engine-sourced."""
    res = {sid: _Eng().run(_bi(_li(_ROOT, sid, archetype_id, company_id), sid))
           for sid, _nm, _kind in scen}
    live = [t for t in scen if t[2] == "live"][0]
    r0 = res[live[0]]
    base = round(r0.value_per_share, 3)
    vals = {nm: round(res[sid].value_per_share, 3) for sid, nm, _k in scen}
    bars = []
    for sid, nm, kind in scen:
        bars.append({"n": nm, "v": vals[nm], "kind": kind})
        if kind == "up":                      # broker bar sits after the upside
            bars.append({"n": "Average broker", "v": broker_price, "kind": "broker"})
    ups = [v - base for v in vals.values() if v > base]
    downs = [base - v for v in vals.values() if v < base]
    asym = (max(downs) / max(ups)) if (ups and downs) else None
    return {"base": base, "wacc": r0.wacc, "discount_to_market": r0.discount_to_market,
            "vals": vals, "bars": bars, "asym": asym, "live_name": live[1]}

from vcc_valuations.translator import build_bank_inputs_from_data as _bbi
from vcc_valuations.dcf.bank_engine import BankEngine as _BankEng

def bank_pack(company_id, archetype_id, scen, broker_price, market_price):
    """Bank (Ke / DDM, methodology §15) analogue of engine_pack. Runs the bank
    engine across `scen`; central case is kind=='live'. Returns the UI display pack."""
    res = {sid: _BankEng().run(_bbi(_li(_ROOT, sid, archetype_id, company_id), sid))
           for sid, _nm, _kind in scen}
    live = [t for t in scen if t[2] == "live"][0]
    r0 = res[live[0]]
    base = round(r0.value_per_share, 2)
    vals = {nm: round(res[sid].value_per_share, 2) for sid, nm, _k in scen}
    bars = []
    for sid, nm, kind in scen:
        bars.append({"n": nm, "v": vals[nm], "kind": kind})
        if kind == "up":
            bars.append({"n": "Average broker", "v": broker_price, "kind": "broker"})
    ups = [v - base for v in vals.values() if v > base]
    downs = [base - v for v in vals.values() if v < base]
    asym = (max(downs) / max(ups)) if (ups and downs) else None
    return {"base": base, "ke": r0.cost_of_equity, "discount_to_market": base / market_price - 1.0,
            "vals": vals, "bars": bars, "asym": asym,
            "ordinary_equity": {nm: res[sid].ordinary_equity_value for sid, nm, _k in scen},
            "npat_y5": {nm: res[sid].cash_npat[5] for sid, nm, _k in scen}}

from vcc_valuations.translator import build_segment_inputs_from_data as _sgi
from vcc_valuations.dcf.segment_engine import SegmentEngine as _SegEng

def segment_pack(company_id, archetype_id, scen, broker_price, market_price):
    """Segment-FCFF (M3) analogue of engine_pack. Central case is kind=='live'."""
    inps = {sid: _sgi(_li(_ROOT, sid, archetype_id, company_id), sid) for sid, _nm, _kind in scen}
    res = {sid: _SegEng().run(inps[sid]) for sid, _nm, _kind in scen}
    live = [t for t in scen if t[2] == "live"][0]
    r0 = res[live[0]]; _ke = inps[live[0]].cost_of_equity
    base = round(r0.value_per_share_aud, 2)
    vals = {nm: round(res[sid].value_per_share_aud, 2) for sid, nm, _k in scen}
    bars = []
    for sid, nm, kind in scen:
        bars.append({"n": nm, "v": vals[nm], "kind": kind})
        if kind == "up":
            bars.append({"n": "Average broker", "v": broker_price, "kind": "broker"})
    ups = [v - base for v in vals.values() if v > base]
    downs = [base - v for v in vals.values() if v < base]
    asym = (max(downs) / max(ups)) if (ups and downs) else None
    return {"base": base, "ke": _ke, "discount_to_market": base / market_price - 1.0,
            "vals": vals, "bars": bars, "asym": asym, "terminal_share": r0.terminal_share_of_ev,
            "usd": {nm: res[sid].value_per_share_usd for sid, nm, _k in scen},
            "ev": {nm: res[sid].enterprise_value for sid, nm, _k in scen},
            "pv_explicit": {nm: res[sid].pv_explicit for sid, nm, _k in scen},
            "pv_terminal": {nm: res[sid].pv_terminal for sid, nm, _k in scen},
            "equity": {nm: res[sid].equity_value for sid, nm, _k in scen}}

_DNL_SCEN = [
    ("orderly_convergence", "Orderly Convergence", "up"),
    ("muddle_through", "Muddle Through", "live"),
    ("ai_productivity_lag", "AI Productivity Lag", "down"),
    ("fragmentation", "Fragmentation", "down"),
    ("disorderly_climate_crystallisation", "Disorderly Climate", "down"),
    ("stagflation_persists", "Stagflation Persists", "down"),
]
_pk = engine_pack("dnl", "industrial_explosives", _DNL_SCEN, 3.61)
_base = _pk["base"]; _wacc = _pk["wacc"]; _vals = _pk["vals"]; _asym = _pk["asym"]
_dmpct = abs(_pk["discount_to_market"]) * 100.0
_up = _vals["Orderly Convergence"] - _base
_dn = _base - _vals["Stagflation Persists"]
def _pct(nm): return (_vals[nm] / _base - 1.0) * 100.0

dnl["cp"]["base"] = _base
dnl["cp"]["re0"] = round(_wacc, 6)
dnl["scenarios"] = _pk["bars"]
dnl["metric4"] = {"label": "Asymmetry (down/up)", "value": ("%.1f×" % _asym)}
for _s in dnl["sliders"]:
    if _s["k"] == "re":
        _s["def"] = round(_wacc * 100.0, 2)

# narrative numeric claims, engine-sourced (Direction 2: measured central-case framing)
_M = "−"
_n = dnl["narr"]
_n["Muddle Through"] = (_n["Muddle Through"]
    .replace("Why AUD 3.48?", "Why AUD %.2f?" % _base)
    .replace("It sits modestly below market (AUD 3.61, ~4%) — the framework agrees with consensus on the central case. The value-add is not disagreement here, it is the scenario <i>asymmetry</i> around this point.",
             "It sits below market (AUD 3.61, ~%.0f%%) — on a Muddle Through path the framework reads consensus as somewhat rich at the centre, but the emphasis is the scenario <i>asymmetry</i> around this point rather than the central level." % _dmpct)
    .replace("~4× harder", "~%.1f× harder" % _asym))
_n["Orderly Convergence"] = _n["Orderly Convergence"].replace(
    "only +AUD 0.57 above Muddle Through.", "+AUD %.2f above Muddle Through." % _up)
_n["AI Productivity Lag"] = _n["AI Productivity Lag"].replace(
    "−3% vs Muddle Through", "%s%.0f%% vs Muddle Through" % (_M, abs(_pct("AI Productivity Lag"))))
_n["Fragmentation"] = _n["Fragmentation"].replace(
    "−27%.", "%s%.0f%%." % (_M, abs(_pct("Fragmentation"))))
_n["Disorderly Climate"] = _n["Disorderly Climate"].replace(
    "−60%.", "%s%.0f%%." % (_M, abs(_pct("Disorderly Climate"))))
_n["Stagflation Persists"] = _n["Stagflation Persists"].replace(
    "−65% vs Muddle Through; the −AUD 2.31 that sets the 4.05× asymmetry.",
    "%s%.0f%% vs Muddle Through; the %sAUD %.2f that sets the %.1f× asymmetry." % (_M, abs(_pct("Stagflation Persists")), _M, _dn, _asym))
dnl["footnote"] = dnl["footnote"].replace(
    "Calibrated central case: DNL Muddle Through AUD 3.48 (market AUD 3.61)",
    "Engine-computed central case: DNL Muddle Through AUD %.2f (market AUD 3.61)" % _base)
dnl["topnote"] = dnl["topnote"].replace(
    "all six scenarios calibrated (v4)", "all six scenarios computed by the production engine")

# --- build-up bridge + operating build, wired to the engine (central case) ---
from vcc_valuations.translator import equity_bridge_from_data as _ebd
_cs = "muddle_through"
_cinp = _li(_ROOT, _cs, "industrial_explosives", "dnl")
_cbuilt = _bi(_cinp, _cs)
_cr = _Eng().run(_cbuilt)
_eb = _ebd(_cinp, _cs)
def _cm(v): return "{:,.0f}".format(round(v))
def _pr(v): return "(%s)" % _cm(abs(v))     # parenthesised negative
_EV = _eb["B27"].value; _NDv = _eb["B28"].value; _ADJ = _eb["B29"].value
_LEAS = _eb["B30"].value; _EQ = _eb["B31"].value; _SH = _cr.shares_outstanding
_ANCH = _eb["B6"].value; _OCF = _eb["B7"].value; _CPX = _eb["B8"].value; _NDval = _eb["B11"].value
_NDincl = _NDval + (-_LEAS)
_vps = "%.2f" % _cr.value_per_share

dnl["dcf"] = bridge([
    ["Enterprise value (DCF)", _cm(_EV)],
    ["Less: net debt at valuation date", _pr(_NDv)],
    ["Less: equity-bridge adjustments (net)", _pr(_ADJ)],
    ["Less: AASB 16 lease liabilities", _pr(_LEAS)],
    ["Equity value", _cm(_EQ)],
    ["÷ shares (m)", _cm(_SH)],
    ["Value per share AUD", _vps]],
    "AUD m. Five-year FCFF (stub + FY27–FY31) from the production engine, single WACC %.2f%%, terminal g 2.5%%; the gas roll-off is in the margin path. Per-scenario detail across all six worlds." % (_cr.wacc * 100))

dnl["dcfIntro"] = ("AUD m. Click any line to see its make-up. Stub + five explicit years of FCFF "
    "(FY27–FY31) from the production engine, single WACC %.2f%%, terminal g 2.5%%; gas roll-off in the margin path." % (_cr.wacc * 100))

dnl["dcfRows"] = [
    ["Enterprise value (DCF)", _cm(_EV), "Stub + five explicit years of FCFF discounted at the single WACC %.2f%%, plus a Gordon-growth terminal at g 2.5%% (terminal ~%.0f%% of EV). Straight from the production engine — the same number the headline uses." % (_cr.wacc * 100, _cr.terminal_share_of_ev * 100)],
    ["Less: net debt at valuation date", _pr(_NDv), "Net debt at the 31 Mar 2026 anchor (%s) walked to the 25 May 2026 valuation date over Period A — less operating cash flow generated, plus capex paid (methodology §7). Ex-leases; leases are the next line." % _cm(_ANCH)],
    ["Less: equity-bridge adjustments (net)", _pr(_ADJ), "Fertilisers-separation one-offs sitting outside net debt (methodology §4.2): declared dividend, Phosphate Hill ARO/inventory, Geelong and Gibson Island remediation, transaction costs — less the probability-weighted receivables (Perdaman, IPF, PH contingent). Net %s. Previously folded into the net-debt anchor; now shown explicitly." % _cm(_ADJ)],
    ["Less: AASB 16 lease liabilities", _pr(_LEAS), "AASB 16 lease liability treated as debt (Approach A), consistent with the post-AASB 16 EBITDA used above."],
    ["Equity value", _cm(_EQ), "Enterprise value %s less net debt %s, adjustments %s and leases %s." % (_cm(_EV), _cm(_NDv), _cm(_ADJ), _cm(_LEAS))],
    ["÷ shares (m)", _cm(_SH), "Issued shares at the 31 Mar 2026 H1 anchor (§5.3), paired to the net-debt anchor date; no buyback projection is modelled (value-neutral)."],
    ["Value per share AUD", _vps, ""]]

_dd = dnl["dcfDetail"]
_dd["leaseMat"]["ev"] = round(_EV); _dd["leaseMat"]["shares"] = round(_SH)
_dd["leaseMat"]["liab"] = round(-_LEAS); _dd["leaseMat"]["netDebtIncl"] = round(_NDincl)
_dd["netDebt"] = [
    ["Net debt at 31 Mar 2026 anchor (ex-leases)", round(_ANCH)],
    ["less: operating cash flow in Period A", round(_OCF)],
    ["plus: capex paid in Period A", round(_CPX)],
    ["Net debt at valuation date (ex-leases)", round(_NDval), "sub"],
    ["Add: AASB 16 lease liabilities", round(-_LEAS)],
    ["Net debt used in the bridge (lease-inclusive)", round(_NDincl), "tot"]]
_dd["netDebtNote"] = ("Approach A (leases = debt). Net debt is anchored at the 31 Mar 2026 H1 balance-sheet "
    "date and walked to the 25 May 2026 valuation date over Period A (methodology §7): less operating "
    "cash flow generated, plus capex paid. The AUD %s AASB 16 lease liability is added on its own line. "
    "The Fertilisers-separation one-offs are NOT in net debt — they sit on their own equity-bridge line "
    "(methodology §4.2)." % _cm(-_LEAS))
_dd["mt"]["years"] = ["FY27", "FY28", "FY29", "FY30", "FY31"]
_dd["mt"]["revenue"] = [round(x) for x in _cr.revenue[1:]]
_dd["mt"]["ebit"] = [round(x) for x in _cr.ebit[1:]]
_dd["mt"]["taxGlide"] = [round(x * 100, 2) for x in _cr.applied_tax_rate[1:]]
_dd["mt"]["baseMargin"] = round(_cbuilt.base_ebit_margin * 100, 1)
_dd["mt"]["peerGap"] = [round(x * 10000) for x in _cbuilt.margin_transformation]
_dd["mt"]["gasRolloff"] = [round(x * 10000) for x in _cbuilt.margin_gas_rolloff]
_dd["mt"]["note"] = ("Muddle Through operating build, straight from the production engine (methodology §11: "
    "industry baseline + company offset shown explicitly). Revenue is on the ratified FY26 continuing-ops "
    "base of AUD 3,400m (excludes the discontinued Phosphate Hill revenue in the reported ~3,905 TTM; "
    "methodology §5), growing at the chain-derived ~6.2%% p.a. EBIT margin is the 14.1%% FY26 base plus the "
    "peer-gap-closure overlay less the US gas-contract roll-off. NOPAT = EBIT × (1−applied tax); FCFF adds "
    "D&A (~7.3%% of revenue), deducts capex (~7–8%%) and working-capital investment. Every line is the "
    "engine's own output — the same build behind the headline 3.07.")

# balance-sheet figures used by the multiples EV bridge (engine-anchored)
dnl["shares"] = round(_SH); dnl["netDebt"] = round(_NDincl)
dnl["netDebtExLeases"] = round(_NDval); dnl["leaseLiab"] = round(-_LEAS)
dnl["_leaseContract"]["leaseLiability"] = round(-_LEAS)
# ---- full audited workbook (engine-sourced), base64-embedded for the standalone download ----
# The static HTML cannot call the Python engine at runtime, so we pre-generate the full
# formula workbook here and embed it; the download button serves these bytes (feature #2).
import base64 as _b64
from engine_workbook import build_dnl_workbook_bytes as _wbk
dnl["xlsxB64"] = _b64.b64encode(_wbk(dnl)).decode("ascii")
dnl["xlsxName"] = "DNL_full_valuation_workbook.xlsx"
# ===== end SSOT block =====

# ===== SSOT: WBC bank headline + build-up wired to the production bank engine =====
_WBC_SCEN = [
    ("orderly_convergence", "Orderly Convergence", "up"),
    ("muddle_through", "Muddle Through", "live"),
    ("ai_productivity_lag", "AI Productivity Lag", "down"),
    ("fragmentation", "Fragmentation", "down"),
    ("disorderly_climate_crystallisation", "Disorderly Climate", "down"),
    ("stagflation_persists", "Stagflation Persists", "down"),
]
_wp = bank_pack("wbc", "australian_major_banks", _WBC_SCEN, wbc["broker"], wbc["market"])
_wbase = _wp["base"]; _wke = _wp["ke"]; _wvals = _wp["vals"]; _wasym = _wp["asym"]
_wdm = abs(_wp["discount_to_market"]) * 100.0
_WM = "\u2212"
def _wpct(nm): return (_wvals[nm] / _wbase - 1.0) * 100.0
def _wapct(nm): return abs(_wpct(nm))
_woc = _wvals["Orderly Convergence"]

wbc["cp"]["base"] = _wbase
wbc["cp"]["re0"] = round(_wke, 6)
wbc["scenarios"] = _wp["bars"]
wbc["metric4"] = {"label": "Asymmetry (down/up)", "value": ("%.2f\u00d7" % _wasym)}
for _s in wbc["sliders"]:
    if _s["k"] == "re":
        _s["def"] = round(_wke * 100.0, 2)

# narrative numeric claims, engine-sourced
_wn = wbc["narr"]
_wn["Muddle Through"] = (_wn["Muddle Through"]
    .replace("Why AUD 30.15, ~15% below market?", "Why AUD %.2f, ~%.0f%% below market?" % (_wbase, _wdm))
    .replace("essentially the Orderly Convergence scenario (AUD 35.46)", "essentially the Orderly Convergence scenario (AUD %.2f)" % _woc))
_wn["Orderly Convergence"] = (_wn["Orderly Convergence"]
    .replace("At AUD 35.46 it sits essentially at market", "At AUD %.2f it sits essentially at market" % _woc)
    .replace("+17.6% vs Muddle Through.", "+%.1f%% vs Muddle Through." % _wpct("Orderly Convergence")))
_wn["AI Productivity Lag"] = _wn["AI Productivity Lag"].replace(
    "\u22121.3% vs Muddle Through", "%s%.1f%% vs Muddle Through" % (_WM, _wapct("AI Productivity Lag")))
_wn["Fragmentation"] = _wn["Fragmentation"].replace(
    "\u22129.5%.", "%s%.1f%%." % (_WM, _wapct("Fragmentation")))
_wn["Disorderly Climate"] = _wn["Disorderly Climate"].replace(
    "\u221223%.", "%s%.0f%%." % (_WM, _wapct("Disorderly Climate")))
_wn["Stagflation Persists"] = _wn["Stagflation Persists"].replace(
    "NPAT Y5 AUD 3.7bn vs MT AUD 8.9bn. \u221233%.",
    "NPAT Y5 AUD %.1fbn vs MT AUD %.1fbn. %s%.0f%%." % (
        _wp["npat_y5"]["Stagflation Persists"] / 1000.0, _wp["npat_y5"]["Muddle Through"] / 1000.0,
        _WM, _wapct("Stagflation Persists")))

# build-up: ordinary equity + per-share -> engine (build-up is already §15-shaped)
_word_s = "{:,.0f}".format(round(_wp["ordinary_equity"]["Muddle Through"]))
def _wfix(x):
    return x.replace("102,960", _word_s).replace("30.15", "%.2f" % _wbase) if isinstance(x, str) else x
wbc["dcf"] = _wfix(wbc["dcf"])
wbc["dcfIntro"] = _wfix(wbc["dcfIntro"])
wbc["dcfRows"] = [[_wfix(c) for c in row] for row in wbc["dcfRows"]]
wbc["footnote"] = wbc["footnote"].replace(
    "Calibrated central case: WBC Muddle Through AUD 30.15",
    "Engine-computed central case: WBC Muddle Through AUD %.2f" % _wbase)
wbc["topnote"] = wbc["topnote"].replace(
    "all six scenarios calibrated (v3)", "all six scenarios computed by the production bank engine (\u00a715)")
# full audited WBC bank workbook (engine-sourced), base64-embedded for the standalone download
from engine_workbook import build_wbc_workbook_bytes as _wwbk
wbc["xlsxB64"] = _b64.b64encode(_wwbk(wbc)).decode("ascii")
wbc["xlsxName"] = "WBC_full_valuation_workbook.xlsx"
# ===== end WBC SSOT block =====
# ===== SSOT: CSL segment-FCFF headline + build-up wired to the production engine =====
_CSL_SCEN = [
    ("orderly_convergence", "Orderly Convergence", "up"),
    ("muddle_through", "Muddle Through", "live"),
    ("ai_productivity_lag", "AI Productivity Lag", "down"),
    ("disorderly_climate_crystallisation", "Disorderly Climate", "down"),
    ("fragmentation", "Fragmentation", "down"),
    ("stagflation_persists", "Stagflation Persists", "down"),
]
_sp = segment_pack("csl", "biopharmaceuticals", _CSL_SCEN, csl["broker"], csl["market"])
_sbase = _sp["base"]; _ske = _sp["ke"]; _svals = _sp["vals"]
_sdm = abs(_sp["discount_to_market"]) * 100.0
def _sm(v): return "{:,.0f}".format(round(v))
csl["cp"]["base"] = _sbase
csl["cp"]["re0"] = round(_ske, 6)
csl["scenarios"] = _sp["bars"]
csl["metric4"] = {"label": "Terminal % of value", "value": ("%.0f%%" % (_sp["terminal_share"] * 100))}
for _s in csl["sliders"]:
    if _s["k"] == "re":
        _s["def"] = round(_ske * 100.0, 2)

# build-up bridge + rows -> engine (already FCFF-shaped; source the numbers)
_cmt = "Muddle Through"
_eUSD = _sp["usd"][_cmt]; _eEV = _sp["ev"][_cmt]; _ePVx = _sp["pv_explicit"][_cmt]
_ePVt = _sp["pv_terminal"][_cmt]; _eEq = _sp["equity"][_cmt]
csl["dcf"] = bridge([
    ["Sum PV explicit FCFF (FY27\u2013FY31)", _sm(_ePVx)],
    ["PV of terminal value", _sm(_ePVt)],
    ["Enterprise value", _sm(_eEV)],
    ["Less: net debt", "(9,100)"],
    ["Less: restructuring PV", "(507)"],
    ["Equity value", _sm(_eEq)],
    ["\u00f7 shares (m)", "478.9"],
    ["Value per share USD", "%.2f" % _eUSD],
    ["Value per share AUD", "%.2f" % _sbase]],
    "USD m. Five-year FCFF (FY27\u2013FY31) plus terminal, discounted at the %.2f%% cost of equity with mid-period discounting. Terminal binds to a 30%% EBIT margin with terminal capex = D&amp;A (%.0f%% of value). Engine-computed; per-scenario detail in csl_scenarios_comparison_v2." % (_ske * 100, _sp["terminal_share"] * 100))

csl["footnote"] = csl["footnote"].replace(
    "Calibrated central case: CSL Muddle Through USD 134.52 / AUD 203.83",
    "Engine-computed central case: CSL Muddle Through USD %.2f / AUD %.2f" % (_eUSD, _sbase))
csl["topnote"] = csl["topnote"].replace(
    "all six scenarios calibrated (v4 / comparison v2)",
    "all six scenarios computed by the production segment-FCFF engine (M3)")
# ===== end CSL SSOT block =====
json.dump({"dnl":dnl,"wbc":wbc,"csl":csl}, open(_CFGP,'w'), ensure_ascii=False)
print("cfgs.json written")
