"""
Round-trip validation: load each scenario YAML under data/scenarios/ and
validate it against the ScenarioFile pydantic model.

This catches drift between the architecture spec (section 6.4) and the
content under data/. Any new scenario must validate; any schema change
must be reconciled with the existing scenarios.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml

# Repo root.
ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "src"))

from vcc_valuations.schemas import ScenarioFile  # noqa: E402


SCENARIOS_DIR = ROOT / "data" / "scenarios"


def _scenario_yaml_paths() -> list[Path]:
    return sorted(SCENARIOS_DIR.glob("*.yaml"))


@pytest.fixture(params=_scenario_yaml_paths(), ids=lambda p: p.stem)
def scenario_path(request) -> Path:
    return request.param


def test_scenario_yaml_validates(scenario_path: Path) -> None:
    """Each data/scenarios/<id>.yaml validates against ScenarioFile."""
    with scenario_path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    scenario_file = ScenarioFile.model_validate(data)

    # Trivial sanity checks beyond schema validation.
    assert scenario_file.scenario.id == scenario_path.stem, (
        f"Scenario id {scenario_file.scenario.id!r} does not match filename "
        f"{scenario_path.stem!r}."
    )
    assert scenario_file.scenario.version  # non-empty
    assert scenario_file.scenario.narrative.key_mechanism  # non-empty


def test_six_scenarios_present() -> None:
    """The workshop selected exactly six scenarios (architecture spec section 2)."""
    paths = _scenario_yaml_paths()
    expected = {
        "muddle_through",
        "orderly_convergence",
        "stagflation_persists",
        "fragmentation",
        "disorderly_climate_crystallisation",
        "ai_productivity_lag",
    }
    actual = {p.stem for p in paths}
    assert actual == expected, (
        f"Expected scenarios {expected}; found {actual}."
    )
