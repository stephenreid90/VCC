"""Thread e: every industry-archetype file validates against the §7.4-v2 schema.

The schema now accepts both the original industrial shape (new_entrants / substitutes,
full lifecycle+concentration+cost-structure+scenario-sensitivity blocks) and the newer
bank / biopharma shape (threat_of_* + rivalry_subforces, archetype_class, bank_archetype,
finer ArchetypeRating gradations), so load_inputs validates all archetypes strictly —
no more raw / tolerant passthrough.
"""

from pathlib import Path

import pytest
from pydantic import ValidationError
import yaml

from vcc_valuations.schemas.industry import IndustryArchetypeFile

ROOT = Path(__file__).resolve().parents[1]
ARCHETYPES = sorted(p.stem for p in (ROOT / "data" / "industries").glob("*.yaml"))


@pytest.mark.parametrize("archetype_id", ARCHETYPES)
def test_archetype_file_validates(archetype_id):
    raw = yaml.safe_load(open(ROOT / "data" / "industries" / f"{archetype_id}.yaml"))
    IndustryArchetypeFile.model_validate(raw)  # raises on any error


def test_both_five_forces_generations_accepted():
    ind = IndustryArchetypeFile.model_validate(
        yaml.safe_load(open(ROOT / "data" / "industries" / "industrial_explosives.yaml"))
    ).industry_archetype
    bank = IndustryArchetypeFile.model_validate(
        yaml.safe_load(open(ROOT / "data" / "industries" / "australian_major_banks.yaml"))
    ).industry_archetype
    # industrial uses the original naming; bank uses the v2 naming + archetype_class
    assert ind.five_forces.new_entrants is not None
    assert ind.archetype_class is None
    assert bank.five_forces.threat_of_new_entrants is not None
    assert bank.archetype_class == "bank"
    assert bank.bank_archetype is not None


# ------------------------------------------------- five-forces completeness
# Batch 3, item 19. The validator that stops a five-forces block from carrying
# three forces, or one force under two names with different ratings.
def _forces_payload(**overrides):
    force = {"rating": "moderate", "rationale": "x"}
    base = {
        "buyer_power": force, "supplier_power": force, "rivalry": force,
        "new_entrants": force, "substitutes": force,
    }
    base.update(overrides)
    return {k: v for k, v in base.items() if v is not None}


def test_five_forces_rejects_a_missing_force():
    from vcc_valuations.schemas.industry import FiveForces

    with pytest.raises(ValidationError, match="missing the new entrants force"):
        FiveForces.model_validate(_forces_payload(new_entrants=None))
    with pytest.raises(ValidationError, match="missing the substitutes force"):
        FiveForces.model_validate(_forces_payload(substitutes=None))


def test_five_forces_rejects_both_naming_generations():
    from vcc_valuations.schemas.industry import FiveForces

    same = {"rating": "moderate", "rationale": "x"}
    with pytest.raises(ValidationError, match="two names for one force"):
        FiveForces.model_validate(_forces_payload(threat_of_new_entrants=same))

    conflicting = {"rating": "high", "rationale": "x"}
    with pytest.raises(ValidationError, match="CONTRADICTORY"):
        FiveForces.model_validate(_forces_payload(threat_of_substitutes=conflicting))


def test_five_forces_accepts_either_generation_alone():
    from vcc_valuations.schemas.industry import FiveForces

    force = {"rating": "moderate", "rationale": "x"}
    FiveForces.model_validate(_forces_payload())
    FiveForces.model_validate(_forces_payload(
        new_entrants=None, substitutes=None,
        threat_of_new_entrants=force, threat_of_substitutes=force,
    ))
