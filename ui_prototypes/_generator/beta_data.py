# -*- coding: utf-8 -*-
"""MOCKED cost-of-capital / beta data contract for the UI beta workbench (Workstream D).
Deterministic synthetic scatter points whose OLS slope matches the stored beta, so the
scatterplot and the beta are mutually consistent. This is a PLACEHOLDER: the real version
must come from Ben's EODHD pipeline (EOD price series per peer + index, plus gearing/tax
for unlevering). Shape here is the spec that pipeline must reproduce."""
import random

def _scatter(beta, n, sigma_i, sigma_e, seed):
    r = random.Random(seed); raw = []
    for _ in range(n):
        xi = r.gauss(0, sigma_i); yi = beta*xi + r.gauss(0, sigma_e)
        raw.append([xi, yi])
    mx = sum(p[0] for p in raw)/n; my = sum(p[1] for p in raw)/n
    cov = sum((p[0]-mx)*(p[1]-my) for p in raw); var = sum((p[0]-mx)**2 for p in raw)
    slope = cov/var
    # rescale y so the OLS slope equals the target beta exactly (keeps scatter, fixes slope)
    k = beta/slope
    pts = [[round(x, 4), round(my + k*(y-my), 4)] for x, y in raw]
    return round(beta, 3), pts

def _comp(name, ticker, why, tax, de, betas, selected, seed, det=None, mfin=None):
    data = {}; s = seed
    for idx, (bw, bm) in betas.items():
        sw, pw = _scatter(bw, 26, 0.020, 0.020, s); s += 1
        sm, pm = _scatter(bm, 40, 0.045, 0.040, s); s += 1
        data[idx] = {"weekly · 2y": {"beta": sw, "points": pw},
                     "monthly · 4y": {"beta": sm, "points": pm}}
    return {"name": name, "ticker": ticker, "why": why, "tax": tax, "gearingDE": de,
            "selected": selected, "data": data, "det": det, "mfin": mfin}

def _cand(name, ticker, why, tax, de, hint):
    return {"name": name, "ticker": ticker, "why": why, "tax": tax, "gearingDE": de,
            "betaHint": hint, "addable": "private" not in ticker.lower()}

DNL = {
 "mock": True, "subject": {"name": "Dyno Nobel", "ticker": "DNL.AX", "selectedBeta": 1.10, "tax": 0.275, "de": 0.27, "det": {"ndeb":2.1,"dol":1.7,"cyc":0.65},
   "measuredNote": "Measured β 0.36 (post-demerger, world-index AUD series) — too short and noisy to use."},
 "rf": 4.30, "erp": 5.00, "alpha": 0.0,
 "indices": ["S&P/ASX 200", "MSCI World"], "indexDefault": "S&P/ASX 200",
 "windows": ["weekly · 2y", "monthly · 4y"], "windowDefault": "weekly · 2y",
 "toDiscount": {"mode": "wacc", "wE": 0.79, "kdAfterTax": 4.20, "label": "WACC"},
 "detNote": "Read across the three drivers: <b>Sasol</b> screens high on all of them &mdash; heavy financial and operational leverage plus deep oil-price cyclicality &mdash; which is why its equity beta (1.45) tops the set and why it is excluded as an outlier. <b>Yara</b> carries the most operating leverage (ammonia plants are highly fixed-cost) but steadier fertiliser demand, so a middling asset beta. <b>Orica</b> sits closest to Dyno Nobel on operational leverage and cyclicality. Dyno Nobel&rsquo;s ~78% contracted book dampens its revenue cyclicality versus the mining-services peers, supporting an asset beta a touch below them before regearing to the lower DNL D/E.",
 "comparables": [
   _comp("Orica", "ORI.AX", "Only ASX-listed direct explosives peer; near-identical mining-customer mix and ammonium-nitrate feedstock exposure.", 0.30, 0.45, {"S&P/ASX 200": (1.05, 1.02), "MSCI World": (1.15, 1.10)}, True, 101, det={"ndeb":1.8,"dol":1.9,"cyc":0.75}, mfin={"ccy":"AUD","price":21.00,"shares":480,"netDebt":1800,"ebitda":{"ttm":1400,"fwd":1540},"ebit":{"ttm":915,"fwd":1007},"ni":{"ttm":650,"fwd":715}}),
   _comp("Yara International", "YAR.OL", "Global nitrogen / AN major; shares the ammonia-cost driver, though a broader fertiliser mix dilutes the explosives read.", 0.24, 0.35, {"S&P/ASX 200": (1.20, 1.18), "MSCI World": (1.25, 1.22)}, True, 111, det={"ndeb":1.5,"dol":2.3,"cyc":0.55}, mfin={"ccy":"USD","price":82.00,"shares":258,"netDebt":3500,"ebitda":{"ttm":3800,"fwd":3990},"ebit":{"ttm":2600,"fwd":2730},"ni":{"ttm":1930,"fwd":2027}}),
   _comp("ICL Group", "ICL", "Specialty minerals plus AN; similar cyclical mining-demand beta.", 0.23, 0.40, {"S&P/ASX 200": (1.10, 1.08), "MSCI World": (1.12, 1.10)}, True, 121, det={"ndeb":2.0,"dol":1.8,"cyc":0.60}, mfin={"ccy":"USD","price":5.00,"shares":1290,"netDebt":2200,"ebitda":{"ttm":1150,"fwd":1242},"ebit":{"ttm":750,"fwd":810},"ni":{"ttm":496,"fwd":536}}),
   _comp("Sasol", "SOL.JO", "Explosives via BME but dominated by energy / chemicals and highly geared — excluded as an outlier.", 0.28, 0.80, {"S&P/ASX 200": (1.45, 1.40), "MSCI World": (1.50, 1.45)}, False, 131, det={"ndeb":2.6,"dol":2.8,"cyc":0.85}, mfin={"ccy":"ZAR","price":12.50,"shares":640,"netDebt":6000,"ebitda":{"ttm":3111,"fwd":3204},"ebit":{"ttm":2000,"fwd":2060},"ni":{"ttm":1231,"fwd":1268}}),
 ],
 "candidates": [
   _cand("AECI", "AFE.JO", "African explosives + chemicals; smaller and less liquid, similar mining exposure.", 0.28, 0.55, 1.15),
   _cand("Enaex", "ENAEX.SN", "Chilean explosives pure-play — strong conceptual comp, but thin cross-listing liquidity.", 0.25, 0.50, 1.10),
   _cand("Austin Powder", "(private)", "Direct US explosives peer but privately held — no listed beta available.", 0.30, 0.60, 1.20),
 ],
  "candidates2": [
   _cand("CF Industries", "CF", "US nitrogen / ammonia major — an input-cost proxy rather than an explosives peer, so a weaker read.", 0.24, 0.35, 0.95),
   _cand("Nutrien", "NTR", "Ag-inputs giant with ammonia exposure; diversified well beyond explosives, arguable at best.", 0.25, 0.40, 1.10),
   _cand("Incitec Pivot Fertilisers", "IPF.AX", "The demerged sibling — same heritage, but a fertiliser demand driver, not mining explosives.", 0.28, 0.45, 0.90),
  ],
}

# OUTSTANDING (pending Ben's EODHD / broker feed): the WBC and CSL comparables below carry
# det=None and mfin=None, so the Comparability-metrics sheet and the peer-multiples grid are NOT
# built for them (only for DNL). WBC needs a BANK set — det {business-mix, credit-cyclicality,
# CET1 buffer} and mfin {price, shares, ni ttm/fwd, book_equity, dividend} -> P/E, P/B, yield (no
# EV/EBITDA). CSL needs the DNL shape — det {ndeb, dol, cyc} and mfin {price, shares, netDebt,
# ebitda/ebit/ni ttm+fwd}. See WORKING_NOTES.md "OUTSTANDING — blocked on peer data".
WBC = {
 "mock": True, "subject": {"name": "Westpac", "ticker": "WBC.AX", "selectedBeta": 0.75, "tax": 0.30, "de": 0.0,
   "measuredNote": "Measured β 0.73 (documented alongside; used as a cross-check, not mechanically)."},
 "rf": 4.30, "erp": 5.00, "alpha": 0.0,
 "indices": ["S&P/ASX 200", "MSCI World"], "indexDefault": "S&P/ASX 200",
 "windows": ["weekly · 2y", "monthly · 4y"], "windowDefault": "weekly · 2y",
 "toDiscount": {"mode": "coe", "label": "cost of equity"},
 "bank": True,
 "comparables": [
   _comp("CommBank", "CBA.AX", "Largest Australian major; same four-pillars oligopoly, premium franchise and funding.", 0.30, 0.0, {"S&P/ASX 200": (0.80, 0.82), "MSCI World": (0.85, 0.86)}, True, 201),
   _comp("NAB", "NAB.AX", "Business-bank-tilted major; closest ROE and balance-sheet-mix comparator to WBC.", 0.30, 0.0, {"S&P/ASX 200": (0.72, 0.74), "MSCI World": (0.78, 0.79)}, True, 211),
   _comp("ANZ", "ANZ.AX", "Institutional / international revenue dilution lowers systematic risk — excluded as an outlier.", 0.30, 0.0, {"S&P/ASX 200": (0.57, 0.60), "MSCI World": (0.62, 0.64)}, False, 221),
   _comp("Macquarie", "MQG.AX", "Different archetype (capital markets / asset management) — informative, not comparable.", 0.30, 0.0, {"S&P/ASX 200": (0.88, 0.90), "MSCI World": (0.95, 0.96)}, False, 231),
 ],
 "candidates": [
   _cand("Bendigo & Adelaide", "BEN.AX", "Regional; smaller, different funding mix and cost base.", 0.30, 0.0, 0.70),
   _cand("Bank of Queensland", "BOQ.AX", "Regional outlier; higher funding cost, structurally lower ROE.", 0.30, 0.0, 0.68),
 ],
  "candidates2": [
   _cand("Suncorp Group", "SUN.AX", "Bank + general insurance; post-bank-sale mix muddies the read, but a listed Australian financial.", 0.30, 0.0, 0.85),
   _cand("Judo Bank", "JDO.AX", "SME-focused challenger; higher growth and risk profile, weakly comparable.", 0.30, 0.0, 1.10),
   _cand("Virgin Money UK", "VMUK", "UK mid-tier bank; different market and rate cycle, adjacent-only.", 0.25, 0.0, 1.20),
  ],
}

CSL = {
 "mock": True, "subject": {"name": "CSL", "ticker": "CSL.AX", "selectedBeta": 0.85, "tax": 0.19, "de": 0.35,
   "measuredNote": "Measured β 0.094 — an AUD-listed price regressed against an AUD index for a USD-earning business. Switch the index to S&P 500 / MSCI World to see the correct-currency calculation."},
 "rf": 4.50, "erp": 5.00, "alpha": 0.0,
 "indices": ["S&P 500", "MSCI World"], "indexDefault": "S&P 500",
 "windows": ["weekly · 2y", "monthly · 4y"], "windowDefault": "weekly · 2y",
 "toDiscount": {"mode": "coe", "label": "cost of equity"},
 "comparables": [
   _comp("Grifols", "GRF", "Closest plasma pure-play; same donor-collection + fractionation model and end markets.", 0.22, 0.90, {"S&P 500": (0.85, 0.88), "MSCI World": (0.80, 0.82)}, True, 301),
   _comp("Takeda", "4502.T", "Plasma via Baxalta plus broad pharma; a partial but relevant comp.", 0.20, 0.50, {"S&P 500": (0.75, 0.78), "MSCI World": (0.72, 0.74)}, True, 311),
   _comp("Sanofi", "SAN.PA", "Large-cap pharma with immunology overlap; a defensive-beta anchor.", 0.21, 0.30, {"S&P 500": (0.80, 0.82), "MSCI World": (0.78, 0.80)}, True, 321),
 ],
 "candidates": [
   _cand("GSK", "GSK.L", "Vaccines overlap with Seqirus; broader pharma portfolio.", 0.21, 0.40, 0.75),
   _cand("Roche", "ROG.SW", "Diagnostics + pharma; defensive, high-quality comparator.", 0.19, 0.25, 0.70),
   _cand("Octapharma", "(private)", "Direct plasma peer but privately held — no listed beta.", 0.22, 0.60, 0.80),
 ],
  "candidates2": [
   _cand("argenx", "ARGX", "Immunology / autoimmune biotech; overlaps CSL Behring&rsquo;s therapeutic areas but pre-scale and higher beta.", 0.15, 0.10, 0.95),
   _cand("AstraZeneca", "AZN.L", "Large-cap pharma incl. rare-disease (Alexion); defensive but very diversified.", 0.18, 0.25, 0.70),
   _cand("Biotest", "BIO3.DE", "European plasma small-cap; direct model overlap but thin liquidity.", 0.28, 0.55, 0.80),
  ],
}

BETA = {"dnl": DNL, "wbc": WBC, "csl": CSL}
