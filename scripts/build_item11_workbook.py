"""Build a standalone workbook showing the maths of each item 11 position.

Item 11 asks what the explicit period is allowed to do to Denali's capital intensity.
The four candidate answers differ in one block of rows -- the capex derivation -- and
in nothing else, so a workbook that lays all four out side by side with live formulas
is the shortest honest way to put the choice to a reader who wants to check it rather
than take it on trust.

Every input is read from the live data files through the translator, and the six-
scenario levels come from ``run_item_11`` rather than being typed in, so this file
cannot drift away from the harness. Standing rule 4.
"""
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from pathlib import Path

CHARS_PER_LINE = 10 * 10
LINE_HEIGHT = 14

ROOT = Path(__file__).resolve().parents[1]

from scripts.size_horizon_variants import (
    _chain_rate, build_plan, engine_inputs, load_sets, run_item_11,
)

CFG = load_sets()
SPEC = CFG["sets"][
    [n for n, s in CFG["sets"].items() if s.get("status") == "current"][0]
]
CENTRAL = "muddle_through"
IC_OPEN = CFG["invested_capital_opening"]
H = SPEC["horizon_years"]


def _scenario_inputs(scenario_id):
    inp = engine_inputs(CFG, scenario_id)
    plan = build_plan(CFG, SPEC, scenario_id)
    return {
        "base_revenue": inp.base_year_revenue,
        "stub_years": inp.stub_years,
        "base_margin": inp.base_ebit_margin,
        "stub_tax": inp.stub_tax_rate,
        "tax_glide": list(plan.tax_rate_glide),
        "da": inp.da_pct_revenue,
        "capex_stub": inp.capex_pct_stub,
        "wc": inp.working_capital_intensity,
        "g": inp.terminal_growth,
        "wacc": inp.wacc_scalar,
        "chain_growth": inp.revenue_growth,
        "growth_path": list(plan.growth_path),
        "margin_delta": list(plan.margin_delta),
        "capex_pct": list(plan.capex_pct),
        "net_debt": inp.equity_bridge.net_debt_at_valuation,
        "adj": inp.equity_bridge.equity_bridge_adjustments_net,
        "leases": inp.equity_bridge.lease_liabilities,
        "shares": inp.equity_bridge.shares_outstanding,
        "volume": _chain_rate(CFG, scenario_id, "B25"),
        "pricing": _chain_rate(CFG, scenario_id, "B29"),
    }


MT = _scenario_inputs(CENTRAL)

FONT = "Arial"
BLUE = Font(name=FONT, size=10, color="0000FF")
BLACK = Font(name=FONT, size=10)
GREEN = Font(name=FONT, size=10, color="008000")
BOLD = Font(name=FONT, size=10, bold=True)
HEAD = Font(name=FONT, size=11, bold=True)
TITLE = Font(name=FONT, size=14, bold=True)
SUB = Font(name=FONT, size=10, italic=True, color="595959")
YELLOW = PatternFill("solid", fgColor="FFFF00")
BAND = PatternFill("solid", fgColor="F2F2F2")
RULE = Border(top=Side(style="thin", color="808080"))

MONEY = '$#,##0.0;($#,##0.0);-'
PCT = '0.00%'
PCT1 = '0.0%'
RATE = '0.000%'
PS = '$#,##0.0000'
X = '0.00x'

POSITIONS = [
    ("1 Ruled build", "ruled",
     "Capex follows the declared path: 7.86% in Y1 converging to 7.3% by Y5 (D-38). "
     "7.3% is also D&A, so from Y5 the fixed asset base stops growing in nominal terms."),
    ("2 Hold intensity", "hold",
     "Capex is whatever restores the opening ratio of fixed capital to revenue, every year. "
     "The asset base grows exactly as fast as revenue."),
    ("3 Volume + inflation", "vol_fade",
     "Capital grows at the volume half of each year's revenue growth, inflated at asset "
     "inflation. Pricing growth needs no new capacity; volume and replacement cost do."),
    ("4 Volume, held flat", "vol_flat",
     "The same basis with the chain's volume rate held for all ten years instead of fading "
     "with revenue. This is how the 25 August handover struck it."),
]


def col(i):
    return get_column_letter(i)


def write_row(ws, r, label, values=None, *, font=BLACK, fmt=None, indent=0, band=False):
    c = ws.cell(row=r, column=1, value=label)
    c.font = font
    c.alignment = Alignment(indent=indent)
    if band:
        c.fill = BAND
    if values:
        for i, v in enumerate(values):
            cell = ws.cell(row=r, column=3 + i, value=v)
            cell.font = font
            if fmt:
                cell.number_format = fmt
            if band:
                cell.fill = BAND
    return r + 1


# ---------------------------------------------------------------- Read me
wb = Workbook()
ws = wb.active
ws.title = "Read me"
ws.column_dimensions["A"].width = 3
ws.column_dimensions["B"].width = 104
ws["B2"] = "DNL — item 11: what the explicit period does to capital intensity"
ws["B2"].font = TITLE
lines = [
    ("", ""),
    ("What this is", "h"),
    ("Four ways of deciding how much capital Denali has to put back into the business over the "
     "ten-year explicit period, each carried all the way through to a value per share. Every "
     "sheet is live: change an input on 'Inputs' and all four rebuild.", "p"),
    ("The four sheets differ in exactly one block of rows — the capex derivation. Everything "
     "above and below it is identical, so the difference in the answer is attributable to that "
     "block and to nothing else.", "p"),
    ("", ""),
    ("Why it matters", "h"),
    ("Capex converging to 7.3% of revenue matters because D&A is also 7.3%. A business "
     "reinvesting exactly what it depreciates adds no net fixed capital. Denali's revenue "
     "compounds about 50% over the ten years, so its invested capital falls from 108% of "
     "revenue to 73%. That thinning, not a competitive moat, is what produces the high "
     "terminal return the framework then capitalises forever.", "p"),
    ("", ""),
    ("The four positions", "h"),
]
r = 3
for text, kind in lines:
    if not text:
        r += 1
        continue
    c = ws.cell(row=r, column=2, value=text)
    c.font = HEAD if kind == "h" else Font(name=FONT, size=10)
    c.alignment = Alignment(wrap_text=(kind == "p"), vertical="top")
    if kind == "p":
        ws.row_dimensions[r].height = LINE_HEIGHT * (len(text) // CHARS_PER_LINE + 1)
    r += 1
for name, _key, blurb in POSITIONS:
    c = ws.cell(row=r, column=2, value=name)
    c.font = BOLD
    r += 1
    c = ws.cell(row=r, column=2, value=blurb)
    c.font = Font(name=FONT, size=10)
    c.alignment = Alignment(wrap_text=True, vertical="top")
    ws.row_dimensions[r].height = LINE_HEIGHT * (len(blurb) // CHARS_PER_LINE + 1)
    r += 2

for text, kind in [
    ("Colour convention", "h"),
    ("Blue text is a hardcoded input you can change. Black is a formula. Green is a link to "
     "another sheet. Yellow fill marks the assumption each position turns on.", "p"),
    ("", ""),
    ("Scope", "h"),
    ("Muddle Through only — the central case, and the one the decision is argued on. "
     "'Six scenarios' carries the levels for all six under each position, computed in the "
     "repository harness rather than in this workbook.", "p"),
    ("", ""),
    ("Source", "h"),
    ("Inputs are the live DNL data files as at the 25 May 2026 valuation date, read through "
     "the translator. Invested capital of 3,681.1m is D-44: net PP&E plus intangibles plus "
     "non-cash working capital, goodwill excluded. Generated 26 August 2026.", "p"),
]:
    if not text:
        r += 1
        continue
    c = ws.cell(row=r, column=2, value=text)
    c.font = HEAD if kind == "h" else Font(name=FONT, size=10)
    c.alignment = Alignment(wrap_text=(kind == "p"), vertical="top")
    if kind == "p":
        ws.row_dimensions[r].height = LINE_HEIGHT * (len(text) // CHARS_PER_LINE + 1)
    r += 1

# ---------------------------------------------------------------- Inputs
inp = wb.create_sheet("Inputs")
inp.column_dimensions["A"].width = 46
inp.column_dimensions["B"].width = 14
inp.column_dimensions["C"].width = 46
inp["A1"] = "DNL — Muddle Through, inputs"
inp["A1"].font = TITLE
inp["A2"] = "Blue cells are inputs. Change one and every position sheet rebuilds."
inp["A2"].font = SUB

rows = [
    ("Scalar assumptions", None, None, "h"),
    ("Base year revenue ($mm)", MT["base_revenue"], "FY2026 normalised revenue", MONEY),
    ("Stub period (years)", MT["stub_years"], "25 May 2026 to 30 September 2026", '0.000'),
    ("Base EBIT margin", MT["base_margin"], "Normalised, before scenario overlays", PCT),
    ("D&A, % of revenue", MT["da"], "Held flat across the horizon", PCT),
    ("Capex in the stub, % of revenue", MT["capex_stub"], "Declared separately from Y1", PCT),
    ("Working capital intensity", MT["wc"], "Applied to the change in the revenue run-rate (D-29)", PCT),
    ("Tax rate, stub", MT["stub_tax"], "Glides per year below", PCT),
    ("WACC", MT["wacc"], "Scalar, per the live build", PCT),
    ("Terminal growth (g)", MT["g"], "Declared basis pending D-45", PCT),
    ("Invested capital at valuation date ($mm)", IC_OPEN, "D-44: net PP&E + intangibles + NCWC, goodwill excluded", MONEY),
    ("", None, None, None),
    ("Growth chain (the split that decides positions 3 and 4)", None, None, "h"),
    ("Chain nominal growth (B42)", MT["chain_growth"], "What the explicit period grows at before the fade", RATE),
    ("Industry volume growth (B25)", MT["volume"], "Needs capacity", RATE),
    ("Industry pricing growth (B29)", MT["pricing"], "Does not need capacity", RATE),
    ("Asset inflation used", MT["g"], "Set equal to terminal growth; change here to test it", RATE),
    ("", None, None, None),
    ("Equity bridge ($mm)", None, None, "h"),
    ("Net debt at valuation date", MT["net_debt"], None, MONEY),
    ("Other bridge adjustments, net", MT["adj"], None, MONEY),
    ("Lease liabilities", MT["leases"], None, MONEY),
    ("Shares outstanding (m)", MT["shares"], None, '#,##0.0'),
]
r = 4
KEY = {}
for label, val, note, fmt in rows:
    if fmt == "h":
        c = inp.cell(row=r, column=1, value=label)
        c.font = HEAD
        r += 1
        continue
    if label == "":
        r += 1
        continue
    inp.cell(row=r, column=1, value=label).font = BLACK
    c = inp.cell(row=r, column=2, value=val)
    c.font = BLUE
    c.number_format = fmt
    if "volume" in label.lower() or "pricing" in label.lower():
        c.fill = YELLOW
    if note:
        n = inp.cell(row=r, column=3, value=note)
        n.font = SUB
    KEY[label] = f"Inputs!$B${r}"
    r += 1

# per-year inputs
r += 1
inp.cell(row=r, column=1, value="Per-year inputs").font = HEAD
r += 1
hdr_row = r
inp.cell(row=r, column=1, value="Year").font = BOLD
for k in range(1, H + 1):
    c = inp.cell(row=r, column=2 + k, value=f"Y{k}")
    c.font = BOLD
    c.alignment = Alignment(horizontal="center")
r += 1
peryear = {}
for label, vals, fmt, note in [
    ("Revenue growth (faded)", MT["growth_path"], RATE,
     "Chain rate for five years, then a linear glide onto g in Y10 (D-36)"),
    ("Margin overlay vs base (pp)", MT["margin_delta"], RATE,
     "Transformation plus the re-phased gas roll-off (D-40)"),
    ("Tax rate", MT["tax_glide"], PCT, None),
    ("Capex, % of revenue — position 1 only", MT["capex_pct"], PCT,
     "Converges to 7.3% by Y5 (D-38). Positions 2-4 derive their own."),
]:
    inp.cell(row=r, column=1, value=label).font = BLACK
    for k, v in enumerate(vals):
        c = inp.cell(row=r, column=3 + k, value=v)
        c.font = BLUE
        c.number_format = fmt
    if note:
        inp.cell(row=r, column=15, value=note).font = SUB
    peryear[label] = r
    r += 1

GROWTH_ROW = peryear["Revenue growth (faded)"]
MARGIN_ROW = peryear["Margin overlay vs base (pp)"]
TAX_ROW = peryear["Tax rate"]
CAPEX_ROW = peryear["Capex, % of revenue — position 1 only"]

I_BASEREV = KEY["Base year revenue ($mm)"]
I_STUB = KEY["Stub period (years)"]
I_MARGIN = KEY["Base EBIT margin"]
I_DA = KEY["D&A, % of revenue"]
I_CAPEXSTUB = KEY["Capex in the stub, % of revenue"]
I_WC = KEY["Working capital intensity"]
I_STUBTAX = KEY["Tax rate, stub"]
I_WACC = KEY["WACC"]
I_G = KEY["Terminal growth (g)"]
I_IC = KEY["Invested capital at valuation date ($mm)"]
I_VOL = KEY["Industry volume growth (B25)"]
I_PRICE = KEY["Industry pricing growth (B29)"]
I_INFL = KEY["Asset inflation used"]
I_ND = KEY["Net debt at valuation date"]
I_ADJ = KEY["Other bridge adjustments, net"]
I_LEASE = KEY["Lease liabilities"]
I_SHARES = KEY["Shares outstanding (m)"]


# ---------------------------------------------------------------- position sheets
def build_position(name, key, blurb):
    s = wb.create_sheet(name)
    s.column_dimensions["A"].width = 44
    s.column_dimensions["B"].width = 11
    for k in range(H + 1):
        s.column_dimensions[col(3 + k)].width = 11
    s["A1"] = f"{name} — Muddle Through"
    s["A1"].font = TITLE
    s["A2"] = blurb
    s["A2"].font = SUB
    s["A2"].alignment = Alignment(wrap_text=True, vertical="top")
    s.row_dimensions[2].height = 28

    r = 4
    s.cell(row=r, column=1, value="Period").font = BOLD
    s.cell(row=r, column=3, value="Stub").font = BOLD
    s.cell(row=r, column=3).alignment = Alignment(horizontal="center")
    for k in range(1, H + 1):
        c = s.cell(row=r, column=3 + k, value=f"Y{k}")
        c.font = BOLD
        c.alignment = Alignment(horizontal="center")
    for cix in range(1, 4 + H):
        s.cell(row=r, column=cix).border = RULE
    r += 1

    # revenue
    rev_r = r
    s.cell(row=r, column=1, value="Revenue ($mm)").font = BLACK
    s.cell(row=r, column=3, value=f"={I_BASEREV}*{I_STUB}").font = BLACK
    for k in range(1, H + 1):
        prev = f"{col(3+k-1)}{r}" if k > 1 else I_BASEREV
        g = f"Inputs!{col(3+k-1)}${GROWTH_ROW}"
        f = (f"={I_BASEREV}*(1+{g})" if k == 1
             else f"={col(3+k-1)}{r}*(1+{g})")
        s.cell(row=r, column=3 + k, value=f).font = BLACK
    for k in range(H + 1):
        s.cell(row=r, column=3 + k).number_format = MONEY
    r += 1

    runrate_r = r
    s.cell(row=r, column=1, value="Revenue run-rate at period end ($mm)").font = BLACK
    s.cell(row=r, column=3,
           value=f"={I_BASEREV}*(1+Inputs!$C${GROWTH_ROW})^{I_STUB}").font = BLACK
    for k in range(1, H + 1):
        s.cell(row=r, column=3 + k, value=f"={col(3+k)}{rev_r}").font = BLACK
    for k in range(H + 1):
        s.cell(row=r, column=3 + k).number_format = MONEY
    r += 1

    margin_r = r
    s.cell(row=r, column=1, value="EBIT margin").font = BLACK
    s.cell(row=r, column=3, value=f"={I_MARGIN}").font = BLACK
    for k in range(1, H + 1):
        s.cell(row=r, column=3 + k,
               value=f"={I_MARGIN}+Inputs!{col(3+k-1)}${MARGIN_ROW}").font = BLACK
    for k in range(H + 1):
        s.cell(row=r, column=3 + k).number_format = PCT
    r += 1

    ebit_r = r
    s.cell(row=r, column=1, value="EBIT ($mm)").font = BLACK
    for k in range(H + 1):
        s.cell(row=r, column=3 + k,
               value=f"={col(3+k)}{rev_r}*{col(3+k)}{margin_r}").font = BLACK
        s.cell(row=r, column=3 + k).number_format = MONEY
    r += 1

    tax_r = r
    s.cell(row=r, column=1, value="Tax rate").font = BLACK
    s.cell(row=r, column=3, value=f"={I_STUBTAX}").font = BLACK
    for k in range(1, H + 1):
        s.cell(row=r, column=3 + k, value=f"=Inputs!{col(3+k-1)}${TAX_ROW}").font = BLACK
    for k in range(H + 1):
        s.cell(row=r, column=3 + k).number_format = PCT
    r += 1

    nopat_r = r
    s.cell(row=r, column=1, value="NOPAT ($mm)").font = BOLD
    for k in range(H + 1):
        s.cell(row=r, column=3 + k,
               value=f"={col(3+k)}{ebit_r}*(1-{col(3+k)}{tax_r})").font = BOLD
        s.cell(row=r, column=3 + k).number_format = MONEY
    r += 1

    da_r = r
    s.cell(row=r, column=1, value="D&A ($mm)").font = BLACK
    for k in range(H + 1):
        s.cell(row=r, column=3 + k, value=f"={col(3+k)}{rev_r}*{I_DA}").font = BLACK
        s.cell(row=r, column=3 + k).number_format = MONEY
    r += 1

    # ---- the block that differs
    r += 1
    hdr = s.cell(row=r, column=1, value="The capex derivation — the only block that differs")
    hdr.font = HEAD
    hdr.fill = YELLOW
    for cix in range(2, 4 + H):
        s.cell(row=r, column=cix).fill = YELLOW
    r += 1

    fixed_open_r = capgrowth_r = ratio_r = None
    if key == "ruled":
        capexpct_r = r
        s.cell(row=r, column=1, value="Capex, % of revenue (declared path)").font = GREEN
        s.cell(row=r, column=3, value=f"={I_CAPEXSTUB}").font = GREEN
        for k in range(1, H + 1):
            s.cell(row=r, column=3 + k,
                   value=f"=Inputs!{col(3+k-1)}${CAPEX_ROW}").font = GREEN
        for k in range(H + 1):
            s.cell(row=r, column=3 + k).number_format = PCT
        r += 1
        s.cell(row=r, column=1, value="Capex less D&A, % of revenue").font = BLACK
        for k in range(H + 1):
            s.cell(row=r, column=3 + k,
                   value=f"={col(3+k)}{capexpct_r}-{I_DA}").font = BLACK
            s.cell(row=r, column=3 + k).number_format = PCT
        s.cell(row=r, column=15,
               value="Zero from Y5: no net fixed capital is added.").font = SUB
        r += 1
        capex_r = r
        s.cell(row=r, column=1, value="Capex ($mm)").font = BLACK
        for k in range(H + 1):
            s.cell(row=r, column=3 + k,
                   value=f"={col(3+k)}{rev_r}*{col(3+k)}{capexpct_r}").font = BLACK
            s.cell(row=r, column=3 + k).number_format = MONEY
        r += 1
    else:
        # opening fixed capital and the growth basis
        s.cell(row=r, column=1, value="Fixed capital at valuation date ($mm)").font = BLACK
        s.cell(row=r, column=2,
               value=f"={I_IC}-{I_WC}*{I_BASEREV}").font = BLACK
        s.cell(row=r, column=2).number_format = MONEY
        s.cell(row=r, column=3,
               value="Invested capital less the working-capital stock").font = SUB
        fixed_open_r = r
        r += 1

        if key == "hold":
            s.cell(row=r, column=1, value="Opening fixed capital ÷ revenue").font = BLACK
            s.cell(row=r, column=2, value=f"=$B${fixed_open_r}/{I_BASEREV}").font = BLACK
            s.cell(row=r, column=2).number_format = PCT1
            ratio_r = r
            s.cell(row=r, column=3, value="Held constant in every year below").font = SUB
            r += 1

        capgrowth_r = r
        if key == "hold":
            s.cell(row=r, column=1, value="Fixed capital growth (= revenue growth)").font = BLACK
        elif key == "vol_fade":
            s.cell(row=r, column=1, value="Fixed capital growth (volume + inflation)").font = BLACK
        else:
            s.cell(row=r, column=1, value="Fixed capital growth (chain volume + inflation)").font = BLACK
        for k in range(1, H + 1):
            gcell = f"Inputs!{col(3+k-1)}${GROWTH_ROW}"
            if key == "hold":
                f = f"={gcell}"
            elif key == "vol_fade":
                f = f"=(1+{gcell})*(1+{I_INFL})/(1+{I_PRICE})-1"
            else:
                f = f"=(1+{I_VOL})*(1+{I_INFL})-1"
            c = s.cell(row=r, column=3 + k, value=f)
            c.font = BLACK
            c.number_format = RATE
        if key == "vol_fade":
            s.cell(row=r, column=15,
                   value="Strip the pricing rate out of the year's growth, "
                         "leaving volume; inflate that.").font = SUB
        r += 1

        fixed_r = r
        s.cell(row=r, column=1, value="Fixed capital, closing ($mm)").font = BLACK
        s.cell(row=r, column=3,
               value=f"=$B${fixed_open_r}+{col(3)}{rev_r}*({I_CAPEXSTUB}-{I_DA})").font = BLACK
        for k in range(1, H + 1):
            if key == "hold":
                f = f"=$B${ratio_r}*{col(3+k)}{rev_r}"
            else:
                f = f"={col(3+k-1)}{fixed_r}*(1+{col(3+k)}{capgrowth_r})"
            s.cell(row=r, column=3 + k, value=f).font = BLACK
        for k in range(H + 1):
            s.cell(row=r, column=3 + k).number_format = MONEY
        r += 1

        capex_r = r
        s.cell(row=r, column=1, value="Capex ($mm)").font = BLACK
        s.cell(row=r, column=3,
               value=f"={col(3)}{rev_r}*{I_CAPEXSTUB}").font = BLACK
        for k in range(1, H + 1):
            s.cell(row=r, column=3 + k,
                   value=f"={col(3+k)}{fixed_r}-{col(3+k-1)}{fixed_r}"
                         f"+{col(3+k)}{rev_r}*{I_DA}").font = BLACK
        for k in range(H + 1):
            s.cell(row=r, column=3 + k).number_format = MONEY
        s.cell(row=r, column=15,
               value="Growth in the asset base, plus replacement of what depreciated.").font = SUB
        r += 1

        capexpct_r = r
        s.cell(row=r, column=1, value="Capex, % of revenue (implied)").font = BLACK
        for k in range(H + 1):
            s.cell(row=r, column=3 + k,
                   value=f"={col(3+k)}{capex_r}/{col(3+k)}{rev_r}").font = BLACK
            s.cell(row=r, column=3 + k).number_format = PCT
        r += 1

    r += 1
    dwc_r = r
    s.cell(row=r, column=1, value="Increase in working capital ($mm)").font = BLACK
    s.cell(row=r, column=3,
           value=f"={I_WC}*({col(3)}{runrate_r}-{I_BASEREV})").font = BLACK
    s.cell(row=r, column=4,
           value=f"={I_WC}*({col(4)}{rev_r}-{col(3)}{runrate_r})").font = BLACK
    for k in range(2, H + 1):
        s.cell(row=r, column=3 + k,
               value=f"={I_WC}*({col(3+k)}{rev_r}-{col(3+k-1)}{rev_r})").font = BLACK
    for k in range(H + 1):
        s.cell(row=r, column=3 + k).number_format = MONEY
    r += 1

    fcff_r = r
    s.cell(row=r, column=1, value="Free cash flow to the firm ($mm)").font = BOLD
    for k in range(H + 1):
        s.cell(row=r, column=3 + k,
               value=f"={col(3+k)}{nopat_r}+{col(3+k)}{da_r}"
                     f"-{col(3+k)}{capex_r}-{col(3+k)}{dwc_r}").font = BOLD
        s.cell(row=r, column=3 + k).number_format = MONEY
        s.cell(row=r, column=3 + k).border = RULE
    s.cell(row=r, column=1).border = RULE
    s.cell(row=r, column=2).border = RULE
    r += 1

    t_r = r
    s.cell(row=r, column=1, value="Discounting time (mid-year, years)").font = BLACK
    s.cell(row=r, column=3, value=f"={I_STUB}/2").font = BLACK
    for k in range(1, H + 1):
        s.cell(row=r, column=3 + k, value=f"={I_STUB}+{k}-0.5").font = BLACK
    for k in range(H + 1):
        s.cell(row=r, column=3 + k).number_format = '0.000'
    r += 1

    pv_r = r
    s.cell(row=r, column=1, value="Present value of FCFF ($mm)").font = BLACK
    for k in range(H + 1):
        s.cell(row=r, column=3 + k,
               value=f"={col(3+k)}{fcff_r}/(1+{I_WACC})^{col(3+k)}{t_r}").font = BLACK
        s.cell(row=r, column=3 + k).number_format = MONEY
    r += 1

    # capital roll-forward
    r += 1
    s.cell(row=r, column=1, value="Invested capital, rolled forward").font = HEAD
    r += 1
    ic_r = r
    s.cell(row=r, column=1, value="Invested capital, closing ($mm)").font = BLACK
    s.cell(row=r, column=2, value=f"={I_IC}").font = GREEN
    s.cell(row=r, column=2).number_format = MONEY
    for k in range(H + 1):
        prev = f"$B${r}" if k == 0 else f"{col(3+k-1)}{r}"
        s.cell(row=r, column=3 + k,
               value=f"={prev}+{col(3+k)}{capex_r}-{col(3+k)}{da_r}"
                     f"+{col(3+k)}{dwc_r}").font = BLACK
        s.cell(row=r, column=3 + k).number_format = MONEY
    r += 1
    icrev_r = r
    s.cell(row=r, column=1, value="Invested capital ÷ revenue").font = BLACK
    s.cell(row=r, column=2, value=f"=$B${ic_r}/{I_BASEREV}").font = BLACK
    s.cell(row=r, column=2).number_format = PCT1
    for k in range(1, H + 1):
        s.cell(row=r, column=3 + k,
               value=f"={col(3+k)}{ic_r}/{col(3+k)}{rev_r}").font = BLACK
        s.cell(row=r, column=3 + k).number_format = PCT1
    s.cell(row=r, column=15,
           value="Opening against Y10 is the whole of item 11.").font = SUB
    r += 1

    # terminal
    r += 1
    s.cell(row=r, column=1, value="The terminal").font = HEAD
    r += 1
    lab = lambda t: s.cell(row=r, column=1, value=t)
    y10 = col(3 + H)

    lab("Terminal revenue ($mm)").font = BLACK
    trev_r = r
    s.cell(row=r, column=2, value=f"={y10}{rev_r}*(1+{I_G})").font = BLACK
    s.cell(row=r, column=2).number_format = MONEY
    r += 1

    lab("Fixed capital at the end of Y10 ($mm)").font = BLACK
    tfixed_r = r
    s.cell(row=r, column=2,
           value=f"={y10}{ic_r}-{I_WC}*{y10}{rev_r}").font = BLACK
    s.cell(row=r, column=2).number_format = MONEY
    r += 1

    lab("Terminal capex, % of revenue").font = BLACK
    tcapex_r = r
    c = s.cell(row=r, column=2, value=f"={I_DA}+{I_G}*$B${tfixed_r}/{y10}{rev_r}")
    c.font = BLACK
    c.number_format = PCT
    c.fill = YELLOW
    s.cell(row=r, column=3,
           value="The rate that grows the fixed base at g forever "
                 "(D&A plus g times the base).").font = SUB
    r += 1

    lab("Terminal FCFF ($mm)").font = BLACK
    tfcff_r = r
    s.cell(row=r, column=2,
           value=f"=$B${trev_r}*({y10}{margin_r}*(1-{y10}{tax_r})+{I_DA}"
                 f"-$B${tcapex_r}-{I_G}*{I_WC})").font = BLACK
    s.cell(row=r, column=2).number_format = MONEY
    r += 1

    lab("Terminal value ($mm)").font = BLACK
    tv_r = r
    s.cell(row=r, column=2, value=f"=$B${tfcff_r}/({I_WACC}-{I_G})").font = BLACK
    s.cell(row=r, column=2).number_format = MONEY
    r += 1

    lab("Present value of the terminal ($mm)").font = BLACK
    ptv_r = r
    s.cell(row=r, column=2,
           value=f"=$B${tv_r}/(1+{I_WACC})^({I_STUB}+{H})").font = BLACK
    s.cell(row=r, column=2).number_format = MONEY
    r += 1

    lab("Terminal NOPAT ($mm)").font = BLACK
    tnopat_r = r
    s.cell(row=r, column=2,
           value=f"=$B${trev_r}*{y10}{margin_r}*(1-{y10}{tax_r})").font = BLACK
    s.cell(row=r, column=2).number_format = MONEY
    r += 1

    lab("Terminal return on invested capital").font = BOLD
    troic_r = r
    c = s.cell(row=r, column=2, value=f"=$B${tnopat_r}/{y10}{ic_r}")
    c.font = BOLD
    c.number_format = PCT
    r += 1

    lab("Terminal ROIC ÷ WACC").font = BOLD
    txw_r = r
    c = s.cell(row=r, column=2, value=f"=$B${troic_r}/{I_WACC}")
    c.font = BOLD
    c.number_format = X
    s.cell(row=r, column=3,
           value="Above 1.0x is an excess return the build has to defend.").font = SUB
    r += 1

    # value
    r += 1
    s.cell(row=r, column=1, value="Value").font = HEAD
    r += 1
    lab("Present value of the explicit period ($mm)").font = BLACK
    pvex_r = r
    s.cell(row=r, column=2,
           value=f"=SUM({col(3)}{pv_r}:{y10}{pv_r})").font = BLACK
    s.cell(row=r, column=2).number_format = MONEY
    r += 1
    lab("Enterprise value ($mm)").font = BLACK
    ev_r = r
    s.cell(row=r, column=2, value=f"=$B${pvex_r}+$B${ptv_r}").font = BLACK
    s.cell(row=r, column=2).number_format = MONEY
    r += 1
    lab("Terminal share of enterprise value").font = BLACK
    tvsh_r = r
    s.cell(row=r, column=2, value=f"=$B${ptv_r}/$B${ev_r}").font = BLACK
    s.cell(row=r, column=2).number_format = PCT1
    s.cell(row=r, column=3, value="Above 70% triggers the §11.4.2 sensitivity obligation.").font = SUB
    r += 1
    for text, formula in [
        ("Less net debt ($mm)", f"=-{I_ND}"),
        ("Less other bridge adjustments ($mm)", f"=-{I_ADJ}"),
        ("Less lease liabilities ($mm)", f"=-{I_LEASE}"),
    ]:
        lab(text).font = BLACK
        s.cell(row=r, column=2, value=formula).font = BLACK
        s.cell(row=r, column=2).number_format = MONEY
        r += 1
        lab = lambda t, _r=r: s.cell(row=_r, column=1, value=t)
    eq_r = r
    s.cell(row=r, column=1, value="Equity value ($mm)").font = BOLD
    s.cell(row=r, column=2, value=f"=$B${ev_r}+SUM($B${ev_r+2}:$B${r-1})").font = BOLD
    s.cell(row=r, column=2).number_format = MONEY
    r += 1
    vps_r = r
    c1 = s.cell(row=r, column=1, value="Value per share ($)")
    c1.font = HEAD
    c = s.cell(row=r, column=2, value=f"=$B${eq_r}/{I_SHARES}")
    c.font = HEAD
    c.number_format = PS
    c.fill = YELLOW
    return {"vps": vps_r, "roic": troic_r, "xw": txw_r, "tv": tvsh_r,
            "icrev": icrev_r, "y10": col(3 + H), "tcapex": tcapex_r, "sheet": name}


refs = {}
for name, key, blurb in POSITIONS:
    refs[key] = build_position(name, key, blurb)

# ---------------------------------------------------------------- comparison
cmp = wb.create_sheet("Comparison")
cmp.column_dimensions["A"].width = 44
for i in range(4):
    cmp.column_dimensions[col(2 + i)].width = 20
cmp["A1"] = "The four positions, side by side"
cmp["A1"].font = TITLE
cmp["A2"] = "Muddle Through. Every figure is a live link to the sheet named above it."
cmp["A2"].font = SUB

r = 4
cmp.cell(row=r, column=1, value="").font = BOLD
for i, (name, key, _b) in enumerate(POSITIONS):
    c = cmp.cell(row=r, column=2 + i, value=name)
    c.font = BOLD
    c.alignment = Alignment(horizontal="center", wrap_text=True)
    c.border = RULE
cmp.cell(row=r, column=1).border = RULE
r += 1

for label, fld, fmt, note in [
    ("Value per share ($)", "vps", PS, None),
    ("", None, None, None),
    ("Invested capital ÷ revenue, Y10", "icrev", PCT1, "Opens at 108.3% in every position"),
    ("Terminal capex, % of revenue", "tcapex", PCT, None),
    ("Terminal return on invested capital", "roic", PCT, "WACC is 8.88%"),
    ("Terminal ROIC ÷ WACC", "xw", X, "Above 1.0x needs a defence"),
    ("Terminal share of enterprise value", "tv", PCT1, "Above 70% triggers §11.4.2"),
]:
    if not label:
        r += 1
        continue
    cmp.cell(row=r, column=1, value=label).font = BLACK
    for i, (_n, key, _b) in enumerate(POSITIONS):
        ref = refs[key]
        cell_ref = (f"'{ref['sheet']}'!{ref['y10']}{ref[fld]}" if fld == "icrev"
                    else f"'{ref['sheet']}'!$B${ref[fld]}")
        c = cmp.cell(row=r, column=2 + i, value=f"={cell_ref}")
        c.font = GREEN
        c.number_format = fmt
        c.alignment = Alignment(horizontal="center")
        if fld == "vps":
            c.font = Font(name=FONT, size=12, bold=True, color="008000")
    if note:
        cmp.cell(row=r, column=7, value=note).font = SUB
    r += 1

r += 1
cmp.cell(row=r, column=1, value="Against the current published level of $2.6956").font = BLACK
for i, (_n, key, _b) in enumerate(POSITIONS):
    ref = refs[key]
    c = cmp.cell(row=r, column=2 + i,
                 value=f"='{ref['sheet']}'!$B${ref['vps']}/"
                       f"'{POSITIONS[0][0]}'!$B${refs['ruled']['vps']}-1")
    c.font = BLACK
    c.number_format = '+0.0%;-0.0%;-'
    c.alignment = Alignment(horizontal="center")

# ---------------------------------------------------------------- six scenarios
six = wb.create_sheet("Six scenarios")
six.column_dimensions["A"].width = 34
for i in range(4):
    six.column_dimensions[col(2 + i)].width = 20
six["A1"] = "All six scenarios, each position"
six["A1"].font = TITLE
six["A2"] = ("Computed in the repository harness (scripts/size_horizon_variants.py), not in "
             "this workbook. Only Muddle Through is built out cell by cell here.")
six["A2"].font = SUB

_HARNESS = run_item_11(CFG)
_POSITION_KEYS = {
    "ruled": "ruled_build",
    "hold": "hold_intensity_flat",
    "vol_fade": "volume_plus_asset_inflation",
    "vol_flat": "volume_plus_asset_inflation_held_flat",
}
LEVELS = {
    key: [_HARNESS[name][sid] for sid in CFG["scenarios"]]
    for key, name in _POSITION_KEYS.items()
}
NAMES = [sid.replace("_crystallisation", "").replace("_", " ").title()
         for sid in CFG["scenarios"]]
r = 4
six.cell(row=r, column=1, value="Scenario").font = BOLD
for i, (name, _k, _b) in enumerate(POSITIONS):
    c = six.cell(row=r, column=2 + i, value=name)
    c.font = BOLD
    c.alignment = Alignment(horizontal="center", wrap_text=True)
    c.border = RULE
six.cell(row=r, column=1).border = RULE
r += 1
for j, sname in enumerate(NAMES):
    c = six.cell(row=r, column=1, value=sname)
    c.font = BOLD if sname == "Muddle Through" else BLACK
    for i, (_n, key, _b) in enumerate(POSITIONS):
        c2 = six.cell(row=r, column=2 + i, value=LEVELS[key][j])
        c2.font = BOLD if sname == "Muddle Through" else BLUE
        c2.number_format = PS
        c2.alignment = Alignment(horizontal="center")
    r += 1
r += 1
six.cell(row=r, column=1,
         value="Disorderly Climate is the exception: its capex arc, not the convergence "
               "rule, sets its path, so the positions collapse together there.").font = SUB

def main() -> None:
    out = ROOT / "analyses" / "dnl_item11_capital_intensity.xlsx"
    wb.save(out)
    print(out)


if __name__ == "__main__":
    main()
