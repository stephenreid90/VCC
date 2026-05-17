"""
Export JSON Schemas for the top-level pydantic models to design/schemas/.

The JSON Schemas are the contract for non-Python consumers (Ben's data
workstream, the eventual VCC dashboard renderer). They're regenerated from
the pydantic models; never edit the .schema.json files by hand.

Usage:
    python scripts/export_json_schemas.py

Writes one .schema.json file per top-level model under design/schemas/.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Make sure src/ is on the path when running as a script.
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from vcc_valuations.schemas import (  # noqa: E402
    AssumptionSet,
    CompanyPositionFile,
    DriverFile,
    DriverMovementSet,
    ImpactMatrix,
    IndustryArchetypeFile,
    ScenarioFile,
)
from vcc_valuations.schemas.linkage import CompanyOverride  # noqa: E402


# Top-level models to export. Map model class -> output filename.
EXPORTS = {
    ScenarioFile: "scenario.schema.json",
    IndustryArchetypeFile: "industry_archetype.schema.json",
    CompanyPositionFile: "company_position.schema.json",
    DriverFile: "driver_catalogue.schema.json",
    ImpactMatrix: "impact_matrix.schema.json",
    CompanyOverride: "company_override.schema.json",
    DriverMovementSet: "driver_movement_set.schema.json",
    AssumptionSet: "assumption_set.schema.json",
}


def main() -> None:
    out_dir = ROOT / "design" / "schemas"
    out_dir.mkdir(parents=True, exist_ok=True)

    for model_cls, filename in EXPORTS.items():
        schema = model_cls.model_json_schema()
        out_path = out_dir / filename
        with out_path.open("w", encoding="utf-8") as f:
            json.dump(schema, f, indent=2, sort_keys=False)
            f.write("\n")
        print(f"Wrote {out_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
