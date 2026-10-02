"""D-72: derive the two industry macro-driver paths each scenario carries, and write them.

Decisions 2 and 3 of ``design/methodology/driver_path_translation_proposal.md``
(Stephen, 2 Oct 2026):

* ``global_mining_real_growth`` = the scenario's ``real_gdp_growth_world`` path
  plus a FIXED GAP, the gap calibrated so the path's average over the anchor
  years reproduces the level anchor DNL already carries
  (``revenue_growth_chain.by_scenario.<s>.macro.global_mining_real_growth``).
* ``gas_price_growth`` = DNL's level anchor while the scenario is in transition,
  reverting to the baseline scenario's value from the scenario's own
  equilibrium year (``time_profile``). Elevated price GROWTH through a transition
  leaves a higher price LEVEL in equilibrium with normal growth thereafter.

Anchor years are D-37's 1 / 3 / 5 / 7 / 10, linearly interpolated between.

Standing rule 4: the series live in ``data/scenarios/<id>.yaml`` as ordinary
``macro_variables`` (so SSOT check 14 reads them), this script writes them, and
``tests/test_macro_driver_paths.py`` asserts the committed series equal what
this derivation produces. Run with ``--write`` to (re)insert them; the insertion
is textual so the scenario files keep their comments.

    PYTHONPATH=src python scripts/derive_macro_driver_paths.py --write
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
ANCHOR_YEARS = (1, 3, 5, 7, 10)
PERCENT = 100.0  # ssot-allow
BASELINE_SCENARIO = "muddle_through"
SCENARIOS = ["muddle_through", "orderly_convergence", "ai_productivity_lag",
             "fragmentation", "disorderly_climate_crystallisation", "stagflation_persists"]
DERIVED = ("global_mining_real_growth", "gas_price_growth")


def interpolate(points, year):
    pts = sorted((p["year"], p["value"]) for p in points)
    if year <= pts[0][0]:
        return pts[0][1]
    if year >= pts[-1][0]:
        return pts[-1][1]
    for (y0, v0), (y1, v1) in zip(pts, pts[1:]):
        if y0 <= year <= y1:
            return v0 + (v1 - v0) * (year - y0) / (y1 - y0)
    raise AssertionError


def _scenario_doc(scenario_id):
    return yaml.safe_load((ROOT / "data" / "scenarios" / f"{scenario_id}.yaml").read_text(encoding="utf-8"))["scenario"]


def _series(doc, variable):
    for mv in doc["macro_variables"]:
        if mv["variable"] == variable and mv.get("time_series"):
            return mv["time_series"]
    raise KeyError(variable)


def equilibrium_year(doc):
    return max(p["year_start"] for p in doc["time_profile"])


def level_anchors():
    raw = yaml.safe_load((ROOT / "data" / "companies" / "dnl.yaml").read_text(encoding="utf-8"))
    by = raw["normalised_baseline"]["revenue_growth_chain"]["by_scenario"]
    return {s: by[s]["macro"] for s in SCENARIOS}


def derive(scenario_id, anchors=None):
    """Return ``{variable: [(year, value_pct), ...]}`` for the two derived drivers."""
    anchors = anchors or level_anchors()
    doc = _scenario_doc(scenario_id)
    gdp = _series(doc, "real_gdp_growth_world")
    gdp_at = [interpolate(gdp, y) for y in ANCHOR_YEARS]
    mining_level = anchors[scenario_id]["global_mining_real_growth"] * PERCENT
    gap = mining_level - sum(gdp_at) / len(gdp_at)
    mining = [(y, round(g + gap, 2)) for y, g in zip(ANCHOR_YEARS, gdp_at)]

    eq = equilibrium_year(doc)
    transition = anchors[scenario_id]["gas_price_growth"] * PERCENT
    baseline = anchors[BASELINE_SCENARIO]["gas_price_growth"] * PERCENT
    gas = [(y, round(transition if y < eq else baseline, 2)) for y in ANCHOR_YEARS]
    return {"global_mining_real_growth": mining, "gas_price_growth": gas, "_gap": round(gap, 2), "_eq": eq}


def render(scenario_id, d):
    gap, eq = d["_gap"], d["_eq"]
    out = [
        "    # D-72 derived paths (2 Oct 2026) -- written by scripts/derive_macro_driver_paths.py,",
        "    # asserted by tests/test_macro_driver_paths.py. Not hand-typed; edit the level",
        "    # anchors in data/companies/dnl.yaml or the series they derive from, then rerun.",
        "    - variable: global_mining_real_growth",
        "      units: percent_yoy",
        "      type: time_series",
        f"      # real_gdp_growth_world plus a fixed gap of {gap:+.2f}pp (decision 2: spread, not multiple)",
        "      time_series:",
    ]
    out += [f"        - {{year: {y}, value: {v}}}" for y, v in d["global_mining_real_growth"]]
    out += [
        "    - variable: gas_price_growth",
        "      units: percent_yoy",
        "      type: time_series",
        f"      # DNL's transition-phase anchor until the equilibrium year ({eq}), then the baseline (decision 3)",
        "      time_series:",
    ]
    out += [f"        - {{year: {y}, value: {v}}}" for y, v in d["gas_price_growth"]]
    return "\n".join(out) + "\n"


_BLOCK_RE = re.compile(
    r"    # D-72 derived paths.*?(?=\n    - variable: (?!global_mining_real_growth|gas_price_growth)|\n\n|\Z)",
    re.S,
)


def write(scenario_id, d):
    path = ROOT / "data" / "scenarios" / f"{scenario_id}.yaml"
    text = path.read_text(encoding="utf-8")
    text = _BLOCK_RE.sub("", text, count=1)
    marker = "  macro_variables:\n"
    assert text.count(marker) == 1, scenario_id
    text = text.replace(marker, marker + render(scenario_id, d), 1)
    path.write_text(text, encoding="utf-8")


def main(argv):
    do_write = "--write" in argv
    anchors = level_anchors()
    for s in SCENARIOS:
        d = derive(s, anchors)
        print(f"{s:36s} gap={d['_gap']:+.2f} eq={d['_eq']:2d} "
              f"mining={[v for _, v in d['global_mining_real_growth']]} "
              f"gas={[v for _, v in d['gas_price_growth']]}")
        if do_write:
            write(s, d)
    if do_write:
        print("written")


if __name__ == "__main__":
    main(sys.argv[1:])
