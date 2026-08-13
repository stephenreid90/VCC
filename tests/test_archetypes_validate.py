"""Thread e: every industry-archetype file validates against the §7.4-v2 schema.

The schema now accepts both the original industrial shape (new_entrants / substitutes,
full lifecycle+concentration+cost-structure+scenario-sensitivity blocks) and the newer
bank / biopharma shape (threat_of_* + rivalry_subforces, archetype_class, bank_archetype,
finer ArchetypeRating gradations), so load_inputs validates all archetypes strictly —
no more raw / tolerant passthrough.
"""

from pathlib import Path

import pytest
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
