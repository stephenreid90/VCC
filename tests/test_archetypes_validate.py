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


# ---------------------------------------------- typed bank archetype (item 19)
def test_bank_archetype_is_typed_not_a_free_dict():
    """The block was ``Dict[str, Any]``: any key could be missing or misspelt."""
    from vcc_valuations.schemas.industry import BankArchetype

    bank = IndustryArchetypeFile.model_validate(
        yaml.safe_load(open(ROOT / "data" / "industries" / "australian_major_banks.yaml"))
    ).industry_archetype
    assert isinstance(bank.bank_archetype, BankArchetype)
    assert bank.bank_archetype.regulator == "APRA"
    assert len(bank.bank_archetype.cost_of_equity_anchor.peer_beta_dataset_2026_06_15) == 5


def _cet1(**overrides):
    base = {
        "regulatory_minimum": 0.08, "capital_conservation_buffer": 0.025,
        "countercyclical_buffer": 0.01, "d_sib_surcharge": 0.01,
        "total_floor": 0.115,
        "components_in_total": ["regulatory_minimum", "capital_conservation_buffer",
                                "d_sib_surcharge"],
        "rationale": "x",
    }
    base.update(overrides)
    return base


def test_cet1_floor_total_must_match_its_declared_components():
    from vcc_valuations.schemas.industry import Cet1Floor

    Cet1Floor.model_validate(_cet1())
    with pytest.raises(ValidationError, match="does not equal the sum"):
        Cet1Floor.model_validate(_cet1(total_floor=0.125))
    with pytest.raises(ValidationError, match="unknown components"):
        Cet1Floor.model_validate(_cet1(components_in_total=["regulatory_minimum", "typo"]))


def test_credit_cycle_anchor_must_be_ordered():
    from vcc_valuations.schemas.industry import CreditCycleAnchor

    ok = {"through_cycle_loss_rate_bps": 20, "peak_cycle_loss_rate_bps": 80,
          "benign_cycle_loss_rate_bps": 5, "rationale": "x"}
    CreditCycleAnchor.model_validate(ok)
    with pytest.raises(ValidationError, match="benign <= through-cycle <= peak"):
        CreditCycleAnchor.model_validate({**ok, "peak_cycle_loss_rate_bps": 10})


def test_cost_of_equity_ranges_must_be_low_then_high():
    from vcc_valuations.schemas.industry import BankCostOfEquityAnchor

    bank = IndustryArchetypeFile.model_validate(
        yaml.safe_load(open(ROOT / "data" / "industries" / "australian_major_banks.yaml"))
    ).industry_archetype
    payload = bank.bank_archetype.cost_of_equity_anchor.model_dump()
    payload["beta_range_measured"] = [0.88, 0.57]
    with pytest.raises(ValidationError, match=r"beta_range_measured must be \[low, high\]"):
        BankCostOfEquityAnchor.model_validate(payload)


def test_rivalry_subforces_are_typed():
    """A sub-force with no rating used to validate as a free dict."""
    from vcc_valuations.schemas.industry import RivalrySubforce

    bank = IndustryArchetypeFile.model_validate(
        yaml.safe_load(open(ROOT / "data" / "industries" / "australian_major_banks.yaml"))
    ).industry_archetype
    subs = bank.five_forces.rivalry_subforces
    assert subs and all(isinstance(x, RivalrySubforce) for x in subs)
    with pytest.raises(ValidationError):
        RivalrySubforce.model_validate({"sub_dimension": "x", "rationale": "y"})
