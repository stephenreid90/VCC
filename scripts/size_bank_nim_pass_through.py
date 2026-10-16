"""R16-4 sizing (16 Oct 2026): how much of a cash-rate move reaches WBC's net interest margin.

Porter's bank work (data/industries/australian_major_banks.yaml) names the lever -- rate rises
pass to lending faster than to deposits -- but gives no size. This script measures it from
WBC's own half-year NIM history against the RBA cash rate averaged over the same half, so the
pass-through rests on a stated basis instead of a typed number.

Two readings, both in basis points of NIM per 100bp of cash rate:
  level     NIM regressed on the half-year average cash rate (slope, in bp per 100bp).
  change    half-on-half change in NIM regressed on the change in average cash rate.
The level slope is the one a scenario path would use. The sample is one rate cycle
(1H21 to 1H26, ten halves), so the band matters more than the point.

Writes design/methodology/bank_nim_pass_through_set.yaml; tests/dcf/test_bank_nim_pass_through.py
pins it.  Usage:  PYTHONPATH=src python scripts/size_bank_nim_pass_through.py
"""

from datetime import date, timedelta
from pathlib import Path
import math
import re

import yaml

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "design" / "methodology" / "bank_nim_pass_through_set.yaml"
BPS = 10000.0  # ssot-allow: unit conversion
HALF_RE = re.compile(r"^(1H|2H)(\d\d) \((\w{3}) (\d{4})\)$")


def cash_rate_changes():
    doc = yaml.safe_load((ROOT / "data" / "macro" / "rba_cash_rate.yaml").read_text(encoding="utf-8"))
    return [(c["effective"], float(c["target"])) for c in doc["rba_cash_rate"]["changes"]]


def avg_cash_rate(start: date, end: date, changes) -> float:
    """Day-weighted average target over [start, end]."""
    total, days = 0.0, 0
    d = start
    while d <= end:
        rate = [r for eff, r in changes if eff <= d][-1]
        total += rate
        days += 1
        d += timedelta(days=1)
    return total / days


def half_bounds(label: str):
    """'1H24 (Mar 2024)' -> (2023-10-01, 2024-03-31); '2H24 (Sep 2024)' -> (2024-04-01, 2024-09-30)."""
    m = HALF_RE.match(label)
    h, yy, _, yyyy = m.group(1), m.group(2), m.group(3), int(m.group(4))
    if h == "1H":
        return date(yyyy - 1, 10, 1), date(yyyy, 3, 31)
    return date(yyyy, 4, 1), date(yyyy, 9, 30)


def wbc_half_year_nims():
    doc = yaml.safe_load((ROOT / "data" / "companies" / "wbc.yaml").read_text(encoding="utf-8"))
    bb = doc["company"]["normalised_baseline"]["bank_build"] if "company" in doc else None
    # walk for nim_history_annual wherever it sits
    def find(node, key):
        if isinstance(node, dict):
            if key in node:
                return node[key]
            for v in node.values():
                r = find(v, key)
                if r is not None:
                    return r
        elif isinstance(node, list):
            for v in node:
                r = find(v, key)
                if r is not None:
                    return r
        return None
    hist = find(doc, "nim_history_annual")
    anchors = find(doc, "nim_anchors")
    out = [("1H21 (Mar 2021)", float(anchors["long_term_pre_2022_baseline"]))]
    for fy in hist:
        for label, h in fy["half_year_decomposition"].items():
            out.append((label, float(h["nim"])))
    out.append(("1H26 (Mar 2026)", float(anchors["current_1h26_nim"])))
    return out


def ols(xs, ys):
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    slope = sxy / sxx
    intercept = my - slope * mx
    resid = [y - (intercept + slope * x) for x, y in zip(xs, ys)]
    se = math.sqrt(sum(r * r for r in resid) / (n - 2) / sxx) if n > 2 else float("nan")
    syy = sum((y - my) ** 2 for y in ys)
    r2 = 1 - sum(r * r for r in resid) / syy if syy else float("nan")
    return slope, intercept, se, r2


def main():
    changes = cash_rate_changes()
    rows = []
    for label, nim in wbc_half_year_nims():
        s, e = half_bounds(label)
        rows.append({"half": label, "nim_bps": round(nim * BPS, 1), "avg_cash_rate_pct": round(avg_cash_rate(s, e, changes), 3)})
    xs = [r["avg_cash_rate_pct"] for r in rows]
    ys = [r["nim_bps"] for r in rows]
    lvl_slope, lvl_int, lvl_se, lvl_r2 = ols(xs, ys)
    dx = [b - a for a, b in zip(xs, xs[1:])]
    dy = [b - a for a, b in zip(ys, ys[1:])]
    chg_slope, _, chg_se, chg_r2 = ols(dx, dy)
    ex_slope, _, ex_se, ex_r2 = ols(xs[1:], ys[1:])  # without the pre-cycle 1H21 point
    cycle_rate = max(xs) - min(xs)
    cycle_nim = ys[xs.index(max(xs))] - ys[0]
    out = {
        "bank_nim_pass_through_set": {
            "generated": "16 Oct 2026 by scripts/size_bank_nim_pass_through.py (R16-4)",
            "what": "bp of WBC group NIM per 100bp of RBA cash rate, measured over 1H21-1H26",
            "sample_halves": len(rows),
            "observations": rows,
            "level_regression": {
                "pass_through_bp_per_100bp": round(lvl_slope, 2), "std_error": round(lvl_se, 2),
                "r_squared": round(lvl_r2, 3), "intercept_nim_bps": round(lvl_int, 1),
                "band_1se_bp_per_100bp": [round(lvl_slope - lvl_se, 2), round(lvl_slope + lvl_se, 2)],
            },
            "level_regression_excluding_1h21": {
                "pass_through_bp_per_100bp": round(ex_slope, 2), "std_error": round(ex_se, 2),
                "r_squared": round(ex_r2, 3),
                "why": "1H21 (206bp) predates the cycle and the FY22 register; shown so the slope is not read off one point",
            },
            "change_regression": {
                "pass_through_bp_per_100bp": round(chg_slope, 2), "std_error": round(chg_se, 2),
                "r_squared": round(chg_r2, 3),
            },
            "cycle_check": {
                "cash_rate_rise_pct_points": round(cycle_rate, 2),
                "nim_change_at_peak_rate_bps": round(cycle_nim, 1),
                "implied_bp_per_100bp": round(cycle_nim / cycle_rate, 2),
            },
            "reading": (
                "The sample is one hiking-and-easing cycle, ten half-years. Group NIM stayed in a "
                "188-197bp band while the cash rate rose 425bp, so the measured pass-through is small "
                "and not statistically distinct from zero. A one-for-one path (100bp per 100bp) is "
                "ruled out by the data; the typed per-scenario shift is of the same order as the "
                "measurement. Deposit repricing and front-book mortgage competition offset the lending-side "
                "benefit the Porter's work names."
            ),
        }
    }
    OUT.write_text(yaml.safe_dump(out, sort_keys=False, allow_unicode=True, width=110), encoding="utf-8")
    for r in rows:
        print(f"{r['half']:18s} NIM {r['nim_bps']:6.1f}bp  cash {r['avg_cash_rate_pct']:5.3f}%")
    print(f"level:  {lvl_slope:+.2f} bp/100bp (se {lvl_se:.2f}, R2 {lvl_r2:.3f})")
    print(f"ex1H21: {ex_slope:+.2f} bp/100bp (se {ex_se:.2f}, R2 {ex_r2:.3f})")
    print(f"change: {chg_slope:+.2f} bp/100bp (se {chg_se:.2f}, R2 {chg_r2:.3f})")
    print(f"cycle:  +{cycle_rate:.2f}pp cash -> {cycle_nim:+.1f}bp NIM  = {cycle_nim / cycle_rate:+.2f} bp/100bp")
    print(f"wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
