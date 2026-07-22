"""
Reproducible regression-oracle extractor (engine implementation plan, section 3).

Runs LibreOffice headless over a reference valuation workbook with
"always recalculate OOXML" forced, then dumps the target cells to a JSON fixture
so the golden numbers are reproducible rather than hand-typed. The committed
fixture ``dnl_mt_v6.json`` is what ``test_e2e_dnl_mt.py`` asserts against; the
test itself does NOT require LibreOffice.

Regenerate:
    python tests/dcf/golden/_recalc.py

Requires ``soffice`` (LibreOffice) and ``openpyxl`` on PATH / in the env.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
WORKBOOK = REPO / "analyses/dnl/valuations/dnl_muddle_through_valuation_v6_2026-06-25.xlsx"
OUT_JSON = Path(__file__).resolve().parent / "dnl_mt_v6.json"

# DCF Worksheet columns: stub=B, Y1..Y5 = C..G
_DCF_COLS = ["B", "C", "D", "E", "F", "G"]
_DCF_ROWS = {
    "revenue": 6, "ebit_margin": 7, "ebit": 8, "applied_tax_rate": 9,
    "tax": 12, "nopat": 13, "da": 14, "capex": 15, "delta_wc": 16, "fcff": 17,
    "mid_times": 21, "discount_factor": 22, "pv_fcff": 23,
}
_SCALARS = {
    "wacc": ("DCF Worksheet", "B20"),
    "terminal_growth": ("DCF Worksheet", "H26"),
    "terminal_fcff": ("DCF Worksheet", "H27"),
    "terminal_value": ("DCF Worksheet", "H28"),
    "terminal_end_time": ("DCF Worksheet", "H29"),
    "terminal_discount_factor": ("DCF Worksheet", "H30"),
    "pv_terminal": ("DCF Worksheet", "H31"),
    "pv_explicit": ("DCF Worksheet", "H34"),
    "enterprise_value": ("DCF Worksheet", "H36"),
    "terminal_share_of_ev": ("DCF Worksheet", "H37"),
    "net_debt_at_valuation": ("Equity Bridge", "C11"),
    "equity_bridge_adjustments_net": ("Equity Bridge", "B24"),
    "lease_liabilities": ("Equity Bridge", "C30"),
    "equity_value": ("Equity Bridge", "C31"),
    "shares_outstanding": ("Equity Bridge", "C32"),
    "value_per_share": ("Equity Bridge", "C33"),
    "market_reference_price": ("Equity Bridge", "C36"),
}


def _recalc_workbook(src: Path, workdir: Path) -> Path:
    """Copy the workbook and force a headless recalc; return the recalced path."""
    prof = workdir / "prof"
    (prof / "user").mkdir(parents=True, exist_ok=True)
    (prof / "user" / "registrymodifications.xcu").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<oor:items xmlns:oor="http://openoffice.org/2001/registry" '
        'xmlns:xs="http://www.w3.org/2001/XMLSchema" '
        'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">\n'
        ' <item oor:path="/org.openoffice.Office.Calc/Formula/Load">'
        '<prop oor:name="OOXMLRecalcMode" oor:op="fuse"><value>0</value></prop></item>\n'
        ' <item oor:path="/org.openoffice.Office.Calc/Formula/Load">'
        '<prop oor:name="ODFRecalcMode" oor:op="fuse"><value>0</value></prop></item>\n'
        "</oor:items>\n"
    )
    local = workdir / src.name
    shutil.copy(src, local)
    subprocess.run(
        [
            "soffice", f"-env:UserInstallation=file://{prof}",
            "--headless", "--calc", "--convert-to", "xlsx",
            "--outdir", str(workdir / "out"), str(local),
        ],
        check=True, capture_output=True,
    )
    return workdir / "out" / src.name


def extract() -> dict:
    import openpyxl

    with tempfile.TemporaryDirectory() as td:
        recalced = _recalc_workbook(WORKBOOK, Path(td))
        wb = openpyxl.load_workbook(recalced, data_only=True)

        dcf = wb["DCF Worksheet"]
        vectors = {
            name: [dcf[f"{col}{row}"].value for col in _DCF_COLS]
            for name, row in _DCF_ROWS.items()
        }
        scalars = {name: wb[sheet][cell].value for name, (sheet, cell) in _SCALARS.items()}

    return {
        "source_workbook": WORKBOOK.name,
        "period_labels": ["Stub", "Y1", "Y2", "Y3", "Y4", "Y5"],
        "vectors": vectors,
        "scalars": scalars,
    }


if __name__ == "__main__":
    data = extract()
    OUT_JSON.write_text(json.dumps(data, indent=2))
    print(f"Wrote {OUT_JSON}")
    print(f"  EV = {data['scalars']['enterprise_value']:.2f}  "
          f"per-share = {data['scalars']['value_per_share']:.4f}  "
          f"terminal-share = {data['scalars']['terminal_share_of_ev']:.4f}")
