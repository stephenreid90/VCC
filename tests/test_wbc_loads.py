"""WBC-1: the bank company file loads through the full pipeline.

Locks the schema fix that lets the bank archetype (methodology §15) parse:
- ``CompanyPositionFile`` accepts WBC's bank balance sheet (CET1/tier-1/leverage
  ratios), the ``prudentially_strong`` leverage posture, the company-level bank
  extension blocks, and abbreviated divisional segments.
- ``load_inputs`` keeps the bank *industry archetype* as raw (its §15 spec is not
  the industrial ``IndustryArchetypeFile``) while the industrial path stays typed.
- ``ImpactMatrix`` tolerates the bank matrix's ``archetype_class`` / ``version``.

This is the foundation for wiring WBC to a bank valuation engine; it does not yet
value WBC.
"""

from pathlib import Path

from vcc_valuations.schemas.company import CompanyPositionFile
from vcc_valuations.schemas.industry import IndustryArchetype
from vcc_valuations.translator import load_inputs

ROOT = Path(__file__).resolve().parents[1]


def test_wbc_company_file_validates():
    import yaml

    raw = yaml.safe_load(open(ROOT / "data" / "companies" / "wbc.yaml"))
    cp = CompanyPositionFile.model_validate(raw).company_position
    assert cp.id == "wbc"
    # bank capital ratios parse on the balance sheet
    assert cp.balance_sheet.cet1_ratio is not None
    assert cp.balance_sheet.leverage_posture.value == "prudentially_strong"
    # bank extension blocks are carried
    assert cp.bank_specifics is not None


def test_wbc_loads_through_pipeline():
    inp = load_inputs(ROOT, "muddle_through", "australian_major_banks", "wbc")
    assert inp["company"].id == "wbc"
    # bank archetype kept raw (its §15 schema is not yet formalised)
    assert isinstance(inp["archetype"], dict)
    assert inp["archetype"]["archetype_class"] == "bank"
    assert inp["matrix"].industry == "australian_major_banks"


def test_dnl_industrial_archetype_still_typed():
    # non-bank path is unaffected: the industrial archetype still validates to a model
    inp = load_inputs(ROOT, "muddle_through", "industrial_explosives", "dnl")
    assert isinstance(inp["archetype"], IndustryArchetype)
