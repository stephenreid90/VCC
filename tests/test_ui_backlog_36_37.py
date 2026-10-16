"""Pins for UI backlog items 36 and 37 (16 Oct 2026).

36  Print stylesheet (@media print): controls hidden, cards and tables kept whole,
    build-up panels expanded for printing.
37  Side-by-side scenario comparison: a real toggle button (aria-pressed) renders a
    table from CFG.sliders and each scenario's vals, so no value is typed.
"""

from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GEN = ROOT / "ui_prototypes" / "_generator"
GEN_UI = (GEN / "gen_ui.py").read_text(encoding="utf-8")
KEYS = ("dnl", "wbc", "csl")


def _html(key):
    return (ROOT / "ui_prototypes" / ("%s_scenario_interface.html" % key)).read_text(encoding="utf-8")


def _renderer_body():
    start = GEN_UI.index("function renderCompare(){")
    end = GEN_UI.index("function barColor(k){", start)
    return GEN_UI[start:end]


def test_gen_ui_has_print_stylesheet():
    assert "@media print" in GEN_UI
    assert "break-inside:avoid" in GEN_UI
    assert "beforeprint" in GEN_UI and "afterprint" in GEN_UI


def test_gen_ui_has_compare_toggle_and_renderer():
    assert 'id="cmpbtn"' in GEN_UI
    assert 'aria-pressed="false"' in GEN_UI
    assert "function renderCompare()" in GEN_UI
    assert "renderCompare();" in GEN_UI
    assert "document.getElementById('cmpbtn').addEventListener('click'" in GEN_UI


def test_compare_renderer_reads_cfg_not_typed_values():
    body = _renderer_body()
    assert "CFG.sliders" in body
    assert "s.vals" in body and "hasOwnProperty.call(s.vals" in body
    assert "s.kind!=='broker'" in body
    assert "fmtDelta((s.v/mt.v-1)*100)" in body


def test_compare_table_overflow_wrapper_and_sticky_measure():
    body = _renderer_body()
    assert '<div style="overflow-x:auto; max-width:100%;"><table' in body
    assert "position:sticky; left:0" in body
    assert "inputs that are the same in every scenario are not shown" in body
    assert "hasOwnProperty.call(s.vals" in body and "cols[0].vals[sl.k]" in body
    assert '<div style="min-width:0;"><div class="hd">Outcomes across scenarios' in GEN_UI


def test_generated_pages_carry_print_and_compare():
    for key in KEYS:
        h = _html(key)
        assert "@media print" in h, key
        assert "break-inside" in h, key
        assert 'id="cmpbtn"' in h, key
        assert "function renderCompare()" in h, key
        assert "CFG.sliders" in h, key


def test_node_syntax_of_generated_scripts():
    node = shutil.which("node")
    if not node:
        import pytest
        pytest.skip("node not installed")
    for key in KEYS:
        m = re.search(r"<script>(.*?)</script>", _html(key), re.S)
        assert m, key
        js = ROOT / "ui_prototypes" / "_generator" / ("__check_%s.js" % key)
        js.write_text(m.group(1), encoding="utf-8")
        try:
            res = subprocess.run([node, "--check", str(js)], capture_output=True, text=True)
            assert res.returncode == 0, res.stderr
        finally:
            js.unlink(missing_ok=True)
