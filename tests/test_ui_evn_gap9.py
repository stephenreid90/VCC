"""Gap 9 (20 Oct 2026): a resource-engine company in the main scenario-interface prototype.

The page for a company whose engine is ``resource`` is built by
``ui_prototypes/_generator/resource_cfg.py`` from the production engine at generation
time. These tests hold: the six headline levels tie to the pinned set in
``resource_valuation_sets.yaml``; the browser-side form is the engine grid (no second
model); the going-concern terminal disclosures are replaced by the run-off disclosures
(paper section 6 gap 7); every page states the risk-free dates (gap 8); and the page
carries no workbook download it cannot honour.
"""
from __future__ import annotations

import contextlib
import io
import json
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
GEN = ROOT / "ui_prototypes" / "_generator"
sys.path.insert(0, str(GEN))
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

GEN_UI = (GEN / "gen_ui.py").read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def cfgs():
    with contextlib.redirect_stdout(io.StringIO()):
        import build_cfgs  # noqa: F401  (writes cfgs_gen.json)
    return json.loads((GEN / "cfgs_gen.json").read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def sets():
    return yaml.safe_load((ROOT / "design" / "methodology" / "resource_valuation_sets.yaml").read_text(encoding="utf-8"))["sets"]


def _resource_ids():
    from size_resource_valuation import resource_companies
    return [cid for cid, _ in resource_companies()]


def test_every_resource_company_has_a_page_config(cfgs):
    ids = _resource_ids()
    assert ids, "no resource company in data/companies"
    for cid in ids:
        assert cid in cfgs, cid
        assert cfgs[cid]["cp"]["form"] == "engine_grid"


def test_headline_levels_tie_to_the_pinned_set(cfgs, sets):
    names = {"orderly_convergence": "Orderly Convergence", "muddle_through": "Muddle Through",
             "ai_productivity_lag": "AI Productivity Lag", "fragmentation": "Fragmentation",
             "disorderly_climate_crystallisation": "Disorderly Climate", "stagflation_persists": "Stagflation Persists"}
    for cid in _resource_ids():
        cfg, st = cfgs[cid], sets[cid]
        assert st["status"] == "current"
        bars = {b["n"]: b["v"] for b in cfg["scenarios"] if b["kind"] != "broker"}
        for sid, lvl in st["levels"].items():
            assert abs(bars[names[sid]] - lvl) < 5e-4, (sid, bars[names[sid]], lvl)
        assert abs(cfg["cp"]["base"] - st["levels"]["muddle_through"]) < 5e-4
        assert abs(cfg["cp"]["reEngine"] - st["wacc"]) < 1e-6


def test_grid_defaults_reproduce_the_engine_exactly(cfgs, sets):
    """At the slider defaults the interpolation hits a grid point, so every bar is the engine value."""
    for cid in _resource_ids():
        cfg = cfgs[cid]
        g = cfg["cp"]["grid"]
        basis = g["bases"][g["basisDefault"]]
        k = g["goldScales"].index(1.0)
        for b in cfg["scenarios"]:
            if b["kind"] == "broker":
                continue
            s = g["byScen"][b["n"]]
            assert abs(s["gold"][basis][k] - b["v"]) < 5e-4, b["n"]
            assert s["wacc"]["y"][s["wacc"]["x"].index(round(cfg["cp"]["reEngine"] * 100.0, 4))] == 1.0
            assert s["link"]["y"][s["link"]["x"].index(cfg["sliders"][3]["def"])] == 1.0
        # the inventory bases match the pinned sensitivities at the gold-path default
        sens = sets[cid]["sensitivities"]
        mt = g["byScen"]["Muddle Through"]["gold"]
        assert abs(mt["reserves"][k] - sens["inventory_reserves"]["muddle_through"]) < 5e-4
        assert abs(mt["life_extension"][k] - sens["inventory_life_extension"]["muddle_through"]) < 5e-4


def test_sliders_are_engine_dimensions_not_a_going_concern_form(cfgs):
    for cid in _resource_ids():
        keys = [s["k"] for s in cfgs[cid]["sliders"]]
        assert keys == ["re", "gold", "basis", "link"]
        assert cfgs[cid]["sliders"][2]["labels"], "inventory basis slider must carry labels"
        for bad in ("g", "m", "tax"):
            assert bad not in keys


def test_runoff_disclosures_replace_the_terminal_block(cfgs):
    for cid in _resource_ids():
        d = cfgs[cid]["_discount"]
        assert 'id="runoff"' in d
        assert "run-off after year 10" in d and "life" in d and "value per share by inventory basis" in d
        assert "11.4.2" not in d, "the going-concern terminal-share block does not apply to a depleting asset"
        assert "Terminal share of value" not in d


def test_every_page_states_the_risk_free_dates(cfgs):
    for key in ("dnl", "wbc", "csl", *_resource_ids()):
        d = cfgs[key]["_discount"]
        assert 'id="rfdates"' in d, key
        assert "gap 8" in d
        for co in ("DNL", "WBC", "CSL", "EVN"):
            assert co in d


def test_no_workbook_download_is_offered_without_a_workbook(cfgs):
    for cid in _resource_ids():
        cfg = cfgs[cid]
        assert "xlsxB64" not in cfg
        assert cfg.get("workbookNote"), "page must say why no workbook is embedded"
    assert "CFG.workbookNote" in GEN_UI


def test_no_beta_workbench_is_invented(cfgs):
    for cid in _resource_ids():
        assert "beta" not in cfgs[cid]
        assert "not observed" in cfgs[cid]["_discount"]
    assert "if(k==='discount' && BW)" in GEN_UI


def test_narratives_cover_every_world(cfgs):
    for cid in _resource_ids():
        narr = cfgs[cid]["narr"]
        for b in cfgs[cid]["scenarios"]:
            if b["kind"] == "broker":
                continue
            assert b["n"] in narr and "Why A$" in narr[b["n"]], b["n"]
        assert "Mental short-cut" in narr["Muddle Through"]


def test_page_is_generated():
    for cid in _resource_ids():
        html = ROOT / "ui_prototypes" / ("%s_scenario_interface.html" % cid)
        assert html.exists(), html
        t = html.read_text(encoding="utf-8")
        assert 'engine_grid' in t and 'rfdates' in t and 'runoff' in t
