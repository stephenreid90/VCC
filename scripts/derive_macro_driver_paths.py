"""D-72: derive every archetype's declared macro-driver paths and write them to the scenario files.

Each industry archetype (``data/industries/<id>.yaml``) lists the macro drivers its
revenue chain reads in ``required_macro_drivers``, and for each one HOW every world
scenario gets its year-anchored path (``derivation``; the methods are the
``DerivationMethod`` enum in ``schemas/industry.py``). This script is the only
place those methods are executed:

* ``scenario_series`` -- the scenario file already carries the series; nothing to do.
* ``spread`` -- a base scenario series plus a FIXED GAP, calibrated so the path's
  mean over the anchor years reproduces the level anchor the declaration points at
  (D-72 decision 2: spread, not multiple).
* ``transition_then_baseline`` -- the scenario's level anchor while the scenario is
  in transition, reverting to the baseline scenario's anchor from the scenario's
  own equilibrium year (``time_profile``) -- D-72 decision 3.

Anchor years are D-37's 1 / 3 / 5 / 7 / 10, linearly interpolated between.

Standing rule 4: the series live in ``data/scenarios/<id>.yaml`` as ordinary
``macro_variables`` (so SSOT check 14 reads them), this script writes them between
``BEGIN/END derived paths`` markers (one block per archetype), and
``tests/test_macro_driver_paths.py`` asserts the committed series equal what the
declarations produce. The insertion is textual so the scenario files keep their
comments. Nothing in here names a company or a driver.

    PYTHONPATH=src python scripts/derive_macro_driver_paths.py --write
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from vcc_valuations.schemas.industry import (  # noqa: E402
    DerivationMethod, IndustryArchetypeFile, RequiredMacroDriver,
)

ANCHOR_YEARS = (1, 3, 5, 7, 10)
PERCENT = 100.0  # ssot-allow
SCENARIOS = ["muddle_through", "orderly_convergence", "ai_productivity_lag",
             "fragmentation", "disorderly_climate_crystallisation", "stagflation_persists"]


# ----------------------------------------------------------------- data access
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


_company_cache: dict = {}
_UNIT_TO_PERCENT = {"decimal": 100.0, "percent": 1.0, "bps": 0.01}  # ssot-allow
_INDEX_RE = re.compile(r"^(.*)\[(-?\d+)\]$")


def _walk(node, dotted):
    for key in dotted.split("."):
        m = _INDEX_RE.match(key)
        if m:
            node = node[m.group(1)][int(m.group(2))]
        else:
            node = node[key]
    return node


def level_anchor(anchor, scenario_id) -> float:
    """Resolve a ``LevelAnchor`` for one scenario: its terms summed, returned in PERCENT."""
    if anchor.company not in _company_cache:
        _company_cache[anchor.company] = yaml.safe_load(
            (ROOT / "data" / "companies" / f"{anchor.company}.yaml").read_text(encoding="utf-8"))
    doc = _company_cache[anchor.company]
    return sum(float(_walk(doc, t.path.format(scenario=scenario_id))) * _UNIT_TO_PERCENT[t.units]
               for t in anchor.terms)


def archetypes():
    out = []
    for path in sorted((ROOT / "data" / "industries").glob("*.yaml")):
        out.append(IndustryArchetypeFile.model_validate(
            yaml.safe_load(path.read_text(encoding="utf-8"))).industry_archetype)
    return out


# -------------------------------------------------------------------- methods
def base_series_at(scenario_id: str, series_names, year: float) -> float:
    """The SPREAD base at ``year``: the named scenario series summed (percent)."""
    doc = _scenario_doc(scenario_id)
    return sum(interpolate(_series(doc, name), year) for name in series_names)


def _spread(driver: RequiredMacroDriver, scenario_id: str):
    d = driver.derivation
    base_at = [base_series_at(scenario_id, d.series, y) for y in ANCHOR_YEARS]
    gap = level_anchor(d.anchor, scenario_id) - sum(base_at) / len(base_at)
    return [(y, round(b + gap, 2)) for y, b in zip(ANCHOR_YEARS, base_at)], \
        f"{' + '.join(d.series)} plus a fixed gap of {gap:+.2f}pp (spread, not multiple)"


def _transition_then_baseline(driver: RequiredMacroDriver, scenario_id: str):
    d = driver.derivation
    eq = equilibrium_year(_scenario_doc(scenario_id))
    transition = level_anchor(d.anchor, scenario_id)
    baseline = level_anchor(d.anchor, d.baseline_scenario)
    return [(y, round(transition if y < eq else baseline, 2)) for y in ANCHOR_YEARS], \
        f"the scenario's anchor until its equilibrium year ({eq}), then {d.baseline_scenario}'s"


METHODS = {
    DerivationMethod.SPREAD: _spread,
    DerivationMethod.TRANSITION_THEN_BASELINE: _transition_then_baseline,
}


def derive(archetype, scenario_id):
    """``{variable: ([(year, value_pct), ...], note)}`` for the archetype's DERIVED drivers."""
    out = {}
    for driver in archetype.required_macro_drivers:
        if not driver.is_derived:
            continue
        out[driver.variable] = METHODS[driver.derivation.method](driver, scenario_id)
    return out


def derived_variables(archetype):
    return [d.variable for d in archetype.required_macro_drivers if d.is_derived]


# ---------------------------------------------------------------- writing
def _begin(archetype_id):
    return f"    # BEGIN derived paths ({archetype_id})"


END = "    # END derived paths"


def render(archetype, scenario_id, d):
    out = [
        _begin(archetype.id),
        "    # Written by scripts/derive_macro_driver_paths.py from the derivations declared in",
        f"    # data/industries/{archetype.id}.yaml; asserted by tests/test_macro_driver_paths.py.",
        "    # Not hand-typed: edit the declaration, the anchors or the base series, then rerun.",
    ]
    for variable, (series, note) in d.items():
        units = next(x.derivation.units for x in archetype.required_macro_drivers if x.variable == variable)
        out += [
            f"    - variable: {variable}",
            f"      units: {units}",
            "      type: time_series",
            f"      # {note}",
            "      time_series:",
        ]
        out += [f"        - {{year: {y}, value: {v}}}" for y, v in series]
    out.append(END)
    return "\n".join(out) + "\n"


# The pre-14-Oct block had no END marker; its header is matched so a first run
# replaces it cleanly. Afterwards only the BEGIN..END form exists.
_LEGACY_RE = re.compile(
    r"    # D-72 derived paths.*?(?=\n    - variable: (?!global_mining_real_growth|gas_price_growth)|\n\n|\Z)",
    re.S,
)


def write(archetype, scenario_id, d):
    path = ROOT / "data" / "scenarios" / f"{scenario_id}.yaml"
    text = path.read_text(encoding="utf-8")
    block_re = re.compile(re.escape(_begin(archetype.id)) + r".*?" + re.escape(END) + r"\n", re.S)
    text = block_re.sub("", text, count=1)
    text = _LEGACY_RE.sub("", text, count=1)
    text = text.replace("  macro_variables:\n\n", "  macro_variables:\n", 1)
    if not d:
        path.write_text(text, encoding="utf-8")
        return
    marker = "  macro_variables:\n"
    assert text.count(marker) == 1, scenario_id
    text = text.replace(marker, marker + render(archetype, scenario_id, d), 1)
    path.write_text(text, encoding="utf-8")


def main(argv):
    do_write = "--write" in argv
    for archetype in archetypes():
        if not derived_variables(archetype):
            continue
        print(f"== {archetype.id}: {', '.join(derived_variables(archetype))}")
        for s in SCENARIOS:
            d = derive(archetype, s)
            print(f"  {s:36s} " + "  ".join(f"{v}={[x for _, x in ser]}" for v, (ser, _) in d.items()))
            if do_write:
                write(archetype, s, d)
    if do_write:
        print("written")


if __name__ == "__main__":
    main(sys.argv[1:])
