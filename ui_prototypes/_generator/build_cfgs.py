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

dnl = {
 "company":"Dyno Nobel Limited (ASX:DNL)","companyShort":"DNL","ccy":"AUD","ccynote":"AUD · WACC-based DCF",
 "dp":2,"market":3.61,"broker":3.61,"scale":4.6,"liveIdx":2,"activeIdx":2,
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
     ["Buyer power","high (binding)","at industry average","0 bps","Same mining-major customer mix as Orica"],
     ["Supplier power","moderate","more favourable","+200→0 bps","Long-term US gas contracts shield ~70% of US gas through 2028; rolls off by FY31"],
     ["New entrants","low","more favourable","+15 bps","DNL is itself the new entrant via the DNEL ramp in emerging markets"],
     ["Substitutes","low","at industry average","0 bps","Intra-industry tech substitution affects all players equally"],
     ["Rivalry","moderate","less favourable","−40 bps","#2 vs Orica #1; more bulk-ANFO, fewer high-margin electronic detonators"]],
   "net":"−25 bps net growth offset (rivalry −30 + product-mix −10 + new-entrants +15). The supplier-power margin edge is transitory — it rolls off with the gas contracts."},
 "_position":'<ul style="padding-left:18px;"><li><b>Pure-play industrial explosives</b> post-demerger — global co-leader (#2 behind Orica), Australian duopolist.</li><li><b>Geography</b> ~55% USA, ~35% Australia, ~10% RoW; per-entity functional currency (parent AUD, US subsidiary USD per IAS 21).</li><li><b>Customer mix</b> ~35% coal (structurally declining), offset by transition-mineral mining demand.</li><li><b>Edge</b> US cost-curve advantage from long-term gas contracts — transitory, rolling off 2028–2030.</li></ul>',
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
   "AUD m. Five-year FCFF (stub + FY27–FY31), single WACC ~8.7%, terminal g 2.5%, with the gas roll-off built into the margin path. Per-scenario detail in dnl_scenarios_comparison_v4.")
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
     ["Buyer power","moderate","at industry average","0 bps","Switching costs + oligopoly; standard across the Big Four"],
     ["Supplier power","moderate","more favourable","+8 bps NIM","AUD 149bn non-interest-bearing transaction deposits — a funding-cost floor"],
     ["New entrants","low","at industry average","0 bps","Four-pillars policy + capital and licensing barriers"],
     ["Substitutes","low–moderate","at industry average","0 bps","Fintech / neobank nibble; not displacement-scale"],
     ["Rivalry","moderate","less favourable","−10 bps","~10pp cost-to-income gap to CBA (51.7% vs ~42%); mid-tier ROE"]],
   "net":"+8 bps NIM (deposit franchise) less ~−10 bps revenue growth (cost-to-income gap to peers)."},
 "_position":'<ul style="padding-left:18px;"><li><b>#2 Australian mortgage book</b> (~20% system housing share) and #2 household deposits (AUD 615bn retail base).</li><li><b>The question</b>: does UNITE close the ~10pp cost-to-income gap to CBA (51.7% vs ~42%) and ~4pp ROE gap (9.8% vs 13.6%)?</li><li><b>Capital</b> CET1 12.42%, 92 bps above the 11.0–11.5% target — binds payout under stress (§15.5).</li></ul>',
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
   "AUD m. Bank valuation (methodology §15): cost of equity 8.05%, ROE fade to Ke for terminal — no WACC / EV bridge. CET1 binds payout under stress. Per-scenario detail in wbc_scenarios_comparison_v2.")
}

json.dump({"dnl":dnl,"wbc":wbc}, open('/tmp/cfgs.json','w'), ensure_ascii=False)
print("cfgs.json written")
