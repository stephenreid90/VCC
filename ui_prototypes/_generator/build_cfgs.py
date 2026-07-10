# -*- coding: utf-8 -*-
import json

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
 "Muddle Through":'<p>Post-2022 friction proves persistent rather than transitional: inflation cools but lands above target (2.5–3.5%) and central banks tacitly accept the overshoot rather than crush demand. Real rates settle structurally higher than the 2010s (~1.0%). The US keeps outperforming on fiscal expansion, AI investment and immigration, but the lift doesn&rsquo;t propagate to Europe or EM. Climate policy stays patchy and AI&rsquo;s productivity transmission is slow, with rents concentrating in platform owners. No crisis, no resolution — a grinding extension of present conditions. Global growth ~2.3%.</p>',
 "Orderly Convergence":'<p>The conditions for benign resolution stack up at once. Supply-side normalisation plus genuine AI productivity gains absorb wage pressure, so inflation returns to ~2.3% without a demand crush; real rates settle modestly positive. The political reset climate policy needed happens, and geopolitical tensions materially de-escalate. This time US growth propagates — pulling Europe out of stagnation and supporting EM — and AI rents diffuse, re-expanding growth multiples. Global growth recovers to 3.0–3.2%.</p>',
 "Stagflation Persists":'<p>The IMF severe scenario plays out: an energy shock spikes prices and keeps them elevated, inflation expectations break above the 3% credibility threshold, and second-round wage-price dynamics take hold. Central banks lose credibility and hold restrictive policy through the horizon; real rates settle 2–3% with recession inside the scenario. Climate policy backslides as a cost-of-living crisis crushes the transition coalition; growth-stock multiples compress and trade barriers ratchet up. Growth slows to 1.5–2.0%.</p>',
 "Fragmentation":'<p>The US-China contest hardens and trade-as-weapon (tariffs, sanctions, export controls) becomes routine, extending into industrial and commodity flows. Supply chains regionalise into duplicated US-aligned and China-aligned systems, energy markets bifurcate, and critical-minerals access becomes the new geopolitical front. The duplicated footprint is inflationary (~3.5%) and growth bifurcates — China-aligned economies may outpace the US-aligned bloc, with Europe hit hardest and Australia facing an acute security-vs-supply dilemma. The new equilibrium is structurally inferior.</p>',
 "Disorderly Climate":'<p>The already-running disorderly climate path has its crystallisation moment — most likely a confluence of a catastrophic insured-loss event, regulator-forced de-leveraging of carbon-intensive loan books, and a carbon-price spike. Policy snaps from drift to abrupt crisis action: carbon prices to EUR 200+, border-adjustment mechanisms, expanded transition subsidies. Capital reallocates abruptly, so sectoral dispersion widens sharply even as aggregate growth stays near Muddle Through (~2.0–2.2%, inflation 4.5–5% from carbon pass-through). This scenario tests terminal-state convergence hardest — assumed-perpetual moats reveal stranded-asset half-lives inside the horizon.</p>',
 "AI Productivity Lag":'<p>The Solow paradox at AI scale. Capability and capex advance genuinely (deficit-funded, US-led), but economy-wide productivity transformation doesn&rsquo;t arrive on the bull timeline: enterprise adoption is slow, so aggregate TFP grows only ~0.5% versus the 1.5%+ current investment implies. Rents capture is asymmetric — platform owners take the bulk while broad enterprise pays without proportional payback — and market concentration intensifies. The saving grace is the labour-cost channel: AI contains white-collar wage growth even where productivity transmission is weak. Headline numbers resemble Muddle Through, but the underlying story differs.</p>',
}

# ---- Shared discount-rate theory (proper approach + IER evidence). Per-company "what we did" supplied separately. ----
DR_PROPER = [
 ("rf","Risk-free rate",
  "A long-dated government bond yield in the cash-flow currency, ideally matched to the horizon/duration of the cash flows. Practice splits between the deep, liquid 10-year benchmark and a term-matched long bond for very long-life assets; a single YTM is only an average and distorts NPV when the curve is steep. Most take a recent spot rate rather than a normalised one.",
  "In practice, valuers use a recent spot yield on a long government bond in the cash-flow currency — most commonly the 10-year, though some duration-match to 20 or 30-year bonds for very long-life assets. Normalising the rate is debated but usually set aside in favour of a current market yield."),
 ("erp","Equity risk premium",
  "The unobservable expected excess return of equities over the risk-free asset, estimated from long-run historical premia, forward-looking/implied models, or surveys — none theoretically superior. Convention has settled near 6.0%, while acknowledging large statistical error.",
  "Independent experts and practitioners typically adopt a market risk premium around <b>6.0%</b> (a 5–7% range is common), close to updated long-run historical estimates. The estimate carries very wide statistical error — the true premium behind a measured 6% could plausibly sit anywhere in a 2–10% band — and Australian practice usually makes no explicit imputation adjustment inside it."),
 ("beta","Beta",
  "Raw single-stock regression beta is noisy and window-dependent, so triangulate from a comparable set: unlever peer equity betas to asset betas and re-lever to a target structure, and/or use adjusted (mean-reverting) or fundamental betas. Index choice (local vs global) and estimation window materially change the answer.",
  "Standard practice is to triangulate from a comparable set rather than trust a single regression: a subject&rsquo;s measured beta can swing widely across data providers and estimation windows (often anywhere from ~0.8 to ~2.7 for the same company), so experts lean on adjusted / fundamental betas and peer clusters, and treat mechanical unlever / relever with caution."),
 ("debt","Cost of debt / debt margin",
  "Risk-free rate plus a debt margin set by the company&rsquo;s (or comparable-set) credit rating, referencing traded corporate-bond spreads over sovereigns at matching tenor; use a target rating consistent with the assumed gearing, not just the current coupon.",
  "Cost of debt is normally built as the risk-free rate plus a credit-rating-based margin — a BBB issuer&rsquo;s traded spread over the sovereign at matching tenor, using a target rating consistent with the assumed gearing rather than the current coupon. Margins of ~1.5–3% over the risk-free rate are typical for investment-grade names."),
 ("gearing","Gearing / capital-structure weights",
  "Weight equity and debt at market value, using a target/through-cycle structure informed by the subject&rsquo;s own gearing plus the comparable-set average, rather than a single spot snapshot (which is volatile and often inconsistent with the betas measured over the same window).",
  "Weights are taken at <b>market value</b> on a target / through-cycle basis, informed by the comparable-set average rather than a single spot snapshot — commonly 15–25% debt for capital-light industrials, higher for infrastructure-like assets."),
 ("gamma","Gamma / imputation credits",
  "Australia&rsquo;s dividend-imputation system gives resident investors franking credits; some argue these should be captured via a &lsquo;gamma&rsquo; factor (contested, ~0.25–0.65). Regulators such as the AER apply it through the tax line.",
  "Whether to capture franking credits (via a &lsquo;gamma&rsquo; factor, contested at ~0.25–0.65) is heavily debated. Many independent valuers decline to adjust for imputation in a business-valuation context, arguing credit value is effectively binary across the shareholder base (full value to some domestic investors, nil to foreign ones) and not reliably priced by the market."),
 ("wacc","WACC vs cost of equity",
  "For an industrial/miner, discount ungeared after-tax cash flows at a WACC, then bridge enterprise value to equity via net debt. For a bank, debt is raw material (deposits/wholesale funding are operating inputs), so discount cash flows to equity at the cost of equity directly — a WACC/EV bridge is wrong.",
  "Industrials and miners are valued by discounting ungeared after-tax cash flows at a WACC and bridging to equity via net debt; concluded WACCs for mature resource / industrial businesses commonly land around 7–9% (higher in higher-risk jurisdictions). Banks are the exception — deposits and wholesale funding are operating inputs, so bank cash flows are discounted to equity at the cost of equity directly, with no WACC / EV bridge."),
]

def drtheory(did):
    return [[lbl, proper, ier, did.get(k, '&mdash;')] for (k, lbl, proper, ier) in DR_PROPER]

DNL_DID = {
 "rf":"10-year Commonwealth Government Securities YTM, <b>4.30%</b> (indicative, May 2026). Single spot 10-year — the pragmatic-benchmark choice, no duration-matching or normalisation.",
 "erp":"<b>5.0%</b> — a Damodaran-style mature-Australia premium, deliberately ~100bps below the 6.0% Australian-expert convention, with a small country premium baked in.",
 "beta":"Peer triangulation, rejecting the measured <b>0.36</b> (unreliable post-demerger): Orica ~1.05 / Yara ~1.20 / ICL ~1.10 cluster (Sasol 1.45 excluded) → selected <b>1.10</b>.",
 "debt":"<b>6.00%</b> pre-tax = an AUD investment-grade BBB-tier spread (~170bps) over the 10-year sovereign; after-tax 6.00% × (1−0.30) = 4.20%.",
 "gearing":"Market-value weights <b>E/V 79% / D/V 21%</b> (equity = 1,884m shares × AUD 3.61; debt = reported net debt). Market-value basis using reported net debt.",
 "gamma":"Not applied — consistent with the standard business-valuation view, and with our ERP making no explicit imputation allowance.",
 "wacc":"<b>WACC ≈ 8.68%</b> (Re 9.80% at β 1.10; 79% equity + 21% debt at 4.20% after-tax). Held constant across scenarios (§3.5).",
}
WBC_DID = {
 "rf":"10-year Commonwealth Government Securities YTM, <b>4.30%</b> (indicative, May 2026). Single spot 10-year — the pragmatic-benchmark choice.",
 "erp":"<b>5.0%</b> — a Damodaran-style mature-Australia premium, ~100bps below the 6.0% Australian-expert convention.",
 "beta":"Peer triangulation: CBA 0.80 / NAB 0.72 / WBC 0.73 cluster → <b>0.75</b>; ANZ 0.57 excluded as an institutional-dilution outlier, MQG 0.88 a different archetype. Measured 0.73 documented alongside.",
 "debt":"Not applicable — a bank is discounted at cost of equity, with deposits and wholesale funding treated as operating inputs, not financing (§15).",
 "gearing":"Not applicable — no WACC / EV bridge for a bank.",
 "gamma":"Not applied — consistent with the standard business-valuation view and our imputation-neutral ERP.",
 "wacc":"<b>Cost of equity 8.05%</b> (Rf 4.30% + β 0.75 × ERP 5.0%), held constant across scenarios, no WACC/EV bridge — the bank convention (§15).",
}
CSL_DID = {
 "rf":"10-year US Treasury, <b>4.50%</b> (USD-functional). Single spot 10-year, matching CSL&rsquo;s USD cash-flow currency — the correct-currency point behind rejecting the AUD-index beta below.",
 "erp":"<b>5.0%</b> — a Damodaran-style mature-market premium, ~100bps below the 6.0% Australian-expert convention.",
 "beta":"Peer triangulation: Grifols / Takeda / Sanofi cluster 0.7–0.9 → selected <b>0.85</b>. Measured <b>0.094</b> rejected — it regressed an AUD-listed price against an AUD index for a USD-earning business.",
 "debt":"Not separately built — CSL&rsquo;s DCF discounts FCFF at the cost of equity (8.75%) rather than a blended WACC; see &lsquo;WACC vs cost of equity&rsquo; below.",
 "gearing":"Not applied — the CSL DCF discounts FCFF at Re, so no debt/equity weighting is used.",
 "gamma":"Not applied — CSL is USD-functional, so Australian imputation is moot in any case.",
 "wacc":"A single <b>cost of equity 8.75%</b> is applied to FCFF rather than a blended WACC — a simplification worth flagging; it slightly understates the discount rate versus a formal WACC.",
}

dnl = {
 "company":"Dyno Nobel Limited (ASX:DNL)","companyShort":"DNL","ccy":"AUD","ccynote":"AUD · WACC-based DCF",
 "dp":2,"market":3.61,"broker":3.61,"scale":4.6,"liveIdx":2,"activeIdx":2,
 "richbook":True,"shares":1884,"netDebt":1300,
 "mklab":"vs market (3.61)","brlab":"vs broker target (3.61)","metric4":{"label":"Asymmetry (down/up)","value":"4.05×"},
 "pvsub":"","topnote":"Working prototype — all six scenarios calibrated (v4). Slider responses are an illustrative approximation, not the production DCF engine. Reid Advisory, June 2026.",
 "footnote":"Prototype for discussion. Calibrated central case: DNL Muddle Through AUD 3.59 (market AUD 3.61). Per-scenario figures from dnl_scenarios_comparison_v4.",
 "cp":{"base":3.59,"re0":0.0868,"g0":0.025,"m0":13.5,"tax0":0.275,"wTerm":0.85,"xKey":"gas","x0":100,"xk":-0.0008},
 "sliders":[
   {"k":"re","label":"Discount rate (WACC)","min":7,"max":11,"step":0.25,"def":8.68,"suf":"%","dec":2},
   {"k":"g","label":"Terminal growth","min":1.5,"max":3.5,"step":0.25,"def":2.5,"suf":"%","dec":2},
   {"k":"m","label":"Normalised EBIT margin","min":10,"max":17,"step":0.5,"def":13.5,"suf":"%","dec":1},
   {"k":"tax","label":"Blended tax rate","min":22,"max":32,"step":0.5,"def":27.5,"suf":"%","dec":1},
   {"k":"gas","label":"Gas roll-off drag (cumulative)","min":0,"max":200,"step":25,"def":100,"suf":" bps","dec":0}],
 "scenarios":[
   {"n":"Orderly Convergence","v":4.16,"kind":"up"},
   {"n":"Average broker","v":3.61,"kind":"broker"},
   {"n":"Muddle Through","v":3.59,"kind":"live"},
   {"n":"AI Productivity Lag","v":3.48,"kind":"down"},
   {"n":"Fragmentation","v":2.63,"kind":"down"},
   {"n":"Disorderly Climate","v":1.44,"kind":"down"},
   {"n":"Stagflation Persists","v":1.28,"kind":"down"}],
 "titles":{"world":"World scenario","forces":"Company vs industry — Five Forces","position":"Company position","discount":"Discount rate","assum":"Assumptions & rationale","dcf":"Valuation build-up"},
 "snap":{
   "world":'<b id="wsnaptitle">Muddle Through</b> — status-quo extension; gas roll-off offset by peer-gap closure; sits essentially at market. <span class="more" data-k="world">Learn more →</span>',
   "forces":'<b>DNL vs the industrial-explosives archetype</b>, force by force, with each impact. <span class="more" data-k="forces">See the comparison →</span>',
   "position":'<b>Pure-play explosives</b> — #2 global, Australian duopoly, ~35% coal mix. <span class="more" data-k="position">Learn more →</span>',
   "discount":'<b>WACC ~8.7%</b> = 79% equity (Re 9.80%) + 21% debt. <span class="more" data-k="discount">See the build-up →</span>',
   "assum":'<b>Assumptions</b> — each input tagged and rationalised. <span class="more" data-k="assum">See all →</span>',
   "dcf":'<b>FCFF → per share</b> — single WACC across scenarios; gas roll-off in the margin path. <span class="more" data-k="dcf">Open the build-up →</span>'},
 "narr":{
   "Muddle Through":'<p>Status-quo extension of the post-demerger franchise: mining-customer demand holds, input costs are broadly stable, and the US cost-curve advantage from long-term gas contracts is intact in the near term. The single most consequential firm-specific variable — the <b>US gas-contract roll-off in the 2028–2030 window</b> — is built explicitly into the margin path (−50/−100/−150 bps cumulative Y3/Y4/Y5), and is offset by peer-gap closure toward Orica-level efficiency.</p><p><b>Why AUD 3.59?</b> It sits essentially at market (AUD 3.61) — the framework agrees with consensus on the central case. The value-add is not disagreement here, it is the scenario <i>asymmetry</i> around this point.</p><p style="background:var(--secondary); border-radius:8px; padding:10px;"><b>Mental short-cut:</b> a cyclical industrial priced fairly at the centre, but with a downside that bites ~4× harder than the upside lifts.</p>',
   "Orderly Convergence":'<p>Mining capex healthy, transition-mineral demand (copper, lithium, nickel) pulls volumes, and a modest margin lift comes through. The upside is real but capped by the oligopolistic structure — only +AUD 0.57 above Muddle Through.</p>',
   "AI Productivity Lag":'<p>Close to neutral. A modest labour-cost benefit on SG&amp;A from automation, otherwise the macro is broadly status-quo. −3% vs Muddle Through — the least-sensitive scenario.</p>',
   "Fragmentation":'<p>DNL sits ~90% in the US-aligned bloc (USA + Australia), which is the slower-growing bloc; cross-bloc ammonium-nitrate and ammonia flows are regulatorily sensitive and supply chains duplicate. Partially offset by Australia&rsquo;s strategic-mineral position. −27%.</p>',
   "Disorderly Climate":'<p>Coal customers (~35% of the mix) attrit faster than the standard fade assumes; carbon costs flow through ammonia into bulk ANFO; capex rises. A partial offset from transition-mineral mining demand. The moat decays over a shortened fade (§10.6). −60%.</p>',
   "Stagflation Persists":'<p>The binding downside. Sustained input-cost inflation that <b>cannot be passed through</b> — supplier power blocks it while mining customers resist price increases — combined with slowing mining capex. −65% vs Muddle Through; the −AUD 2.31 that sets the 4.05× asymmetry.</p>',
   "_placeholder":'<p>Scenario narrative pending.</p>'},
 "_forces":{
   "intro":"How Dyno Nobel sits relative to the industrial-explosives archetype, force by force. Industry rating is the archetype baseline; the badge is DNL's position; impact is the growth/margin offset.",
   "rows":[
     ["Buyer power","High","Mining-customer concentration is the binding constraint — top 3–5 global miners drive volume, are highly price-sensitive on bulk ANFO, and hold a real backward-integration threat.","at industry average","0 bps","Same mining-major customer mix as Orica"],
     ["Supplier power","Moderate","Anhydrous ammonia (and upstream natural gas) is the dominant input — contained for producers with long-term gas contracts, significant for spot-gas-exposed players.","more favourable","+200→0 bps","Long-term US gas contracts shield ~70% of US gas through 2028; rolls off by FY31"],
     ["New entrants","Low","Strong barriers — explosives licensing, dangerous-goods and environmental regulation, capital-intensive plants, and incumbents&rsquo; long-term offtake contracts and on-site infrastructure.","more favourable","+15 bps","DNL is itself the new entrant via the DNEL ramp in emerging markets"],
     ["Substitutes","Low","No meaningful substitute for industrial explosives in hard-rock mining; mechanical excavation is niche — coal-volume decline is a demand question, not a substitute one.","at industry average","0 bps","Intra-industry tech substitution affects all players equally"],
     ["Rivalry","High","Concentrated global oligopoly (Orica / Dyno Nobel / MAXAM ~65%); Australia a duopoly. Bulk ANFO competes on price while technology products differentiate.","less favourable","−40 bps","#2 vs Orica #1; more bulk-ANFO, fewer high-margin electronic detonators"]],
   "net":"−25 bps net growth offset (rivalry −30 + product-mix −10 + new-entrants +15). The supplier-power margin edge is transitory — it rolls off with the gas contracts."},
 "_position":'<ul style="padding-left:18px;"><li><b>Pure-play post-demerger</b> &ndash; explosives-only after the March 2025 Incitec Pivot split (fertilisers demerged, entity renamed); single reporting segment.</li><li><b>Global #2, Australian duopolist</b> &ndash; #1 in North American industrial explosives (~30% share), #2 to Orica in Australia (~40% share), plus a sub-scale ~5% RoW book slowly gaining.</li><li><b>Geography &amp; currency</b> &ndash; ~55% USA, ~35% Australia, ~10% RoW; per-entity functional currency under IAS 21 (parent AUD, Dyno Nobel Americas USD-functional on US revenue, gas and ammonia).</li><li><b>US cost-curve edge &ndash; transitory</b> &ndash; long-term gas contracts put US ops in the bottom cost-curve quartile (~+200bps margin), rolling off through a 2028&ndash;2030 re-pricing window (6-year average maturity) to nil by FY31.</li><li><b>Switching-cost moat</b> &ndash; 200+ on-site mobile manufacturing units at customer mine sites, multi-decade relationships and 5&ndash;10-year offtake contracts (BHP, Rio Tinto, FMG); ~78% of revenue contracted.</li><li><b>Product &amp; customer mix</b> &ndash; ~50% commodity bulk ANFO, ~18% higher-growth electronic detonators (DigiShot); ~35% coal-exposed, offset by transition-mineral demand. Top 5 customers ~45% of revenue.</li><li><b>Peer-gap to Orica</b> &ndash; Orica is ~30% larger with a technology and diversification lead, driving a net ~25bps company-position growth drag (&minus;30 rivalry, &minus;10 mix, +15 EM ramp).</li><li><b>Key risks</b> &ndash; gas/ammonia input costs, coal-customer transition, and a weak large-project execution record (Louisiana ammonia overruns 2017&ndash;2020); carbon exposure rated high given ~55% ammonia self-supply.</li><li><b>Balance sheet</b> &ndash; net debt/EBITDA 2.12x; AUD 647m liquidity; thin FY25 free cash flow (AUD 101m) vs AUD 162m dividends + AUD 289m buybacks; 60&ndash;70% payout target.</li></ul>',
 "_discount": '<p>Single WACC, held constant across scenarios (risk is priced in the cash flows, not the rate — §3.5).</p>'+dtable([["Risk-free rate (10y CGS)","4.30%","disclosed"],["Equity risk premium","5.00%","judgment"],["Beta — selected","1.10","judgment"],["= Cost of equity","9.80%","derived"],["Cost of debt (pre-tax)","6.00%","disclosed"],["= WACC (79/21 E/D)","~8.7%","derived"]])+'<p style="margin-top:8px;"><b>Beta — peer triangulation.</b> Orica 1.05 / ICL 1.10 / Yara 1.20 cluster (Sasol 1.45 excluded); DNL placed at 1.10. Measured β 0.36 (world-index, AUD series) rejected as unreliable.</p>',
 "_assum":[
   ["Risk-free rate","4.30%","disclosed","10y Commonwealth Govt bond YTM"],
   ["Equity risk premium","5.00%","judgment","Damodaran-style mature-Australia ERP"],
   ["Beta (selected)","1.10","judgment","Peer cluster Orica/ICL/Yara; measured 0.36 unreliable"],
   ["WACC","~8.7%","derived","79% equity × Re 9.80% + 21% debt × 6.0%(1−t)"],
   ["Normalised EBIT margin","13.5%","judgment","Through-cycle; corporate already in segment guidance"],
   ["Gas roll-off drag","−50/−100/−150 bps","judgment","Cumulative Y3/Y4/Y5 as US gas contracts roll off (§3.2.1)"],
   ["Terminal growth g","2.5%","judgment","Demographic trajectory pulls toward 2.0% long-run"],
   ["Blended tax rate","27.5%","derived","Jurisdiction-weighted statutory; effective glides to this"],
   ["Net debt","AUD 1,300m","disclosed","Normalised steady-state"],
   ["Shares","1,884m","disclosed","Latest reported, paired to net-debt anchor"]],
 "dcf": bridge([["Enterprise value (DCF)","8,064"],["Less: net debt","(1,300)"],["Equity value","6,764"],["÷ shares (m)","1,884"],["Value per share AUD","3.59"]],
   "AUD m. Five-year FCFF (stub + FY27–FY31), single WACC ~8.7%, terminal g 2.5%, with the gas roll-off built into the margin path. Per-scenario detail in dnl_scenarios_comparison_v4."),
 "dcfIntro":"AUD m. Click any line to see its make-up. Five-year FCFF (stub + FY27\u2013FY31), single WACC ~8.7%, terminal g 2.5%, gas roll-off in the margin path.",
 "dcfRows":[
   ["Enterprise value (DCF)","8,064","Sum of five years of free cash flow to the firm (stub + FY27\u2013FY31) discounted at WACC ~8.7%, plus a Gordon-growth terminal value at g 2.5%. FCFF is built from a normalised EBIT margin of 13.5% (with the \u221250 / \u2212100 / \u2212150 bps gas roll-off in the margin path), blended tax 27.5%, and steady-state reinvestment. Full per-scenario build in the dnl_scenarios_comparison_v4 workbook."],
   ["Less: net debt","(1,300)","Narrow, normalised steady-state net debt: gross borrowings less cash and short-term investments (FY25 liquidity ~AUD 647m = AUD 207m cash + AUD 440m short-term investments). Excludes leases per the narrow definition, and is paired to the latest reported share count."],
   ["Equity value","6,764","Enterprise value 8,064 less net debt 1,300. Post-demerger equity-bridge adjustments (IPF distribution +125, Geelong remediation \u221235, Gibson Island \u221297, transaction costs \u221211, PH contingent +100) broadly net out and are absorbed into the normalised net-debt anchor."],
   ["\u00f7 shares (m)","1,884","Latest reported shares on issue, paired to the net-debt anchor date; no buyback projection is modelled (value-neutral)."],
   ["Value per share AUD","3.59",""]],
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
   "intro":"How Westpac sits relative to the Australian major-banks archetype, force by force. Industry rating is the archetype baseline; the badge is WBC's position; impact is the NIM/growth offset.",
   "rows":[
     ["Buyer power","Low–moderate","Retail customers have low switching propensity (relationship inertia, bundling, discharge friction); the binding constraint sits in the marginal front-book mortgage-refinancing cohort.","at industry average","0 bps","Switching costs + oligopoly; standard across the Big Four"],
     ["Supplier power","Moderate","Deposit-holders and wholesale-debt investors are the funding &lsquo;suppliers&rsquo; with real switching options, but the Big Four are price-takers within a narrow oligopolistic funding-cost range.","more favourable","+8 bps NIM","AUD 149bn non-interest-bearing transaction deposits — a funding-cost floor"],
     ["New entrants","Low","APRA licensing, D-SIB capital floors (~11.5% CET1), distribution scale, and incumbent deposit-franchise funding advantage; neo-bank waves produced no material disruption.","at industry average","0 bps","Four-pillars policy + capital and licensing barriers"],
     ["Substitutes","Low–moderate","Non-bank lenders take share when serviceability binds, super substitutes for term deposits, fintech erodes some transaction revenue — gradual margin erosion, not existential displacement.","at industry average","0 bps","Fintech / neobank nibble; not displacement-scale"],
     ["Rivalry","Moderate","Oligopolistic (CBA ~25%, WBC ~20%, NAB/ANZ ~14% mortgage share); pricing discipline holds in benign periods but breaks under share-loss pressure (2022–24 cashback discounting compressed NIM).","less favourable","−10 bps","~10pp cost-to-income gap to CBA (51.7% vs ~42%); mid-tier ROE"]],
   "net":"+8 bps NIM (deposit franchise) less ~−10 bps revenue growth (cost-to-income gap to peers)."},
 "_position":'<ul style="padding-left:18px;"><li><b>#2 Big Four franchise</b> &ndash; second-largest by total assets, anchored on a AUD 517.7bn Australian mortgage book (~20% system share, #2 to CBA&rsquo;s ~25%) plus an AUD 18.5bn RAMS book in run-off.</li><li><b>Deposit-funded edge</b> &ndash; #2 household deposits (AUD 615bn retail base), including AUD 149bn non-interest-bearing transaction balances giving a structural +8bps NIM funding-cost advantage over wholesale-funded peers.</li><li><b>Segment mix</b> &ndash; consumer ~37% of earnings, business &amp; wealth ~28% (AUD 238bn loans, #3, rebuilding), institutional (WIB) ~17%, Westpac NZ ~12% (NZD-functional, ~18% NZ mortgage share).</li><li><b>The transformation thesis</b> &ndash; does the multi-year UNITE program (FY26&ndash;FY28) close the ~10pp cost-to-income gap to CBA (51.7% vs ~42%, NAB ~43%) and the ~4pp ROE gap (9.8% TTM vs a 10.5% through-cycle anchor)?</li><li><b>Rivalry drag</b> &ndash; the cost-to-income gap is ~150bps of ROE drag vs the leaders; treated as a management-committed glide toward ~45% by FY29, leaving ~&minus;10bps residual growth drag plus ~&minus;5bps from the business-banking rebuild.</li><li><b>Capital</b> &ndash; Level 2 CET1 12.42% (Level 1 12.75%), 92bps above the 11.0&ndash;11.5% target &ndash; binds payout under stress; Total Capital 21.5%, AT1 AUD 8.5bn, total RWA AUD 458bn, mortgage RWA density 22.6%.</li><li><b>Funding &amp; loan book</b> &ndash; gross loans AUD 890bn, customer deposits AUD 745bn; through-cycle credit-loss anchor 18bps (low end of Big Four) vs benign 1H26 actual ~10bps.</li><li><b>Capital return</b> &ndash; 70&ndash;75% payout target (77% actual, 100% franked), forward dividend AUD 1.54 (~4.4% yield); AUD 1.5bn buyback active, AUD 581m executed FY25.</li><li><b>Key risks</b> &ndash; high rate/credit-cycle sensitivity (peak-cycle losses ~75bps); UNITE re-platforming is the single largest execution risk; indirect climate exposure via vulnerable mortgage geographies.</li></ul>',
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
   "intro":"CSL spans three archetypes (plasma-derived therapies ~72%, vaccines, specialty pharma), so the industry rating is summarised across them. The company offsets are the Behring decomposition — Seqirus and Vifor sit at industry average.",
   "rows":[
     ["Buyer power","Moderate","Payers (Medicare, EU health systems, hospitals) hold the purse, but the products are life-sustaining so volume is inelastic — the pressure is on price, with US Medicare Part D redesign the live front.","at industry average","0 bps","Same payer mix as peers; no CSL-specific pricing edge"],
     ["Supplier power","Low–moderate","Plasma is collected from paid US donors; supplier power is generally low but donor-collection labour is a real, cyclical cost lever exposed to US frontline wages.","more favourable","+5 bps","Owns the largest plasma-donor collection network — vertical integration lowers input dependence"],
     ["New entrants","Very low","5–10yr FDA/EMA/TGA approval plus multi-billion fractionation capex make plasma near-unenterable; vaccines and specialty are low–moderate.","at industry average","0 bps","No CSL edge beyond the shared industry moat"],
     ["Substitutes","Low","No recombinant immunoglobulin at scale and biosimilar plasma is very hard; mRNA and gene therapy are a long-tail, industry-wide risk, not a near-term substitute.","at industry average","0 bps","Long-tail risk affects all fractionators equally"],
     ["Rivalry","Moderate","A rational oligopoly (CSL / Grifols / Takeda / Octapharma / Kedrion) competing on supply reliability and yield rather than price; capacity is added deliberately.","more favourable","+10 bps","Scale leader → lower marginal cost via fractionation efficiency"]],
   "net":"+15 bps margin (supplier +5, rivalry-scale +10), 0 bps revenue growth. CSL captures the industry&rsquo;s secular growth (Ig demand, indication expansion) plus a modest structural margin edge — but transmits macro stress through margin, not volume."},
 "_position":'<ul style="padding-left:18px;"><li><b>Three businesses on one balance sheet:</b> CSL Behring (plasma-derived therapies, ~72% of revenue, ~42% margin), CSL Seqirus (influenza vaccines, ~14%, ~47% margin — <b>demerger announced FY26</b>), CSL Vifor (iron-deficiency / renal specialty pharma, ~14%, ~49% margin, acquired Aug 2022).</li><li><b>Franchise edge:</b> the world&rsquo;s largest plasma-collection network + fractionation scale + FDA/EMA/TGA barriers — a manufacturing / scale moat, not a patent moat (patent-cliff exposure very low).</li><li><b>Geography / currency:</b> global USD-functional group, ASX-listed AUD parent; US is ~55% of the plasma market. First worked example where the parent itself is USD-functional.</li><li><b>Demand character:</b> price-inelastic in volume (life-sustaining Ig) — scenarios transmit through <b>margin and policy, not volume</b>.</li><li><b>Key risk:</b> US Medicare Part D redesign (~USD 100m Ig hit in 1H26) and China Ig/albumin access; donor-collection wage inflation is the other margin channel.</li><li><b>Capital:</b> net debt ~1.8× EBITDA and de-levering; USD 750m buyback; Strategic Transformation targeting &gt;USD 500m pre-tax savings by FY28.</li></ul>',
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
json.dump({"dnl":dnl,"wbc":wbc,"csl":csl}, open(_CFGP,'w'), ensure_ascii=False)
print("cfgs.json written")
