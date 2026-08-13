"""CSL-1: the segment-level company file loads through the pipeline.

Locks the schema fix that lets CSL (multi-segment biopharma, segment-FCFF / M3) parse:
- ``CompanyPositionFile`` accepts CSL's per-segment archetype map + consolidated id, the
  ``segment_level_valuation`` flag, ``operating_result_share`` on segments (in place of
  ``ebit_share``), and the company-level method overlays.
- ``load_inputs`` tolerates the absent consolidated archetype / matrix (CSL resolves
  archetypes per segment); the industrial and bank paths are unaffected.

This is the foundation for wiring CSL to a segment-FCFF engine; it does not yet value CSL.
"""

from pathlib import Path

from vcc_valuations.schemas.company import CompanyPositionFile
from vcc_valuations.translator import load_inputs

ROOT = Path(__file__).resolve().parents[1]


def test_csl_company_file_validates():
    import yaml

    raw = yaml.safe_load(open(ROOT / "data" / "companies" / "csl.yaml"))
    cp = CompanyPositionFile.model_validate(raw).company_position
    assert cp.id == "csl"
    assert cp.segment_level_valuation is True
    assert len(cp.segments) == 3
    # segments disclose operating_result_share (not ebit_share)
    assert cp.segments[0].operating_result_share is not None
    assert cp.industry_archetype_consolidated == "biopharmaceuticals"


def test_csl_loads_through_pipeline():
    inp = load_inputs(ROOT, "muddle_through", "biopharmaceuticals", "csl")
    assert inp["company"].id == "csl"
    # no consolidated archetype / matrix file -> tolerant None (resolved per segment)
    assert inp["archetype"] is None
    assert inp["matrix"] is None


def test_dnl_and_wbc_paths_unaffected():
    dnl = load_inputs(ROOT, "muddle_through", "industrial_explosives", "dnl")
    assert dnl["archetype"] is not None and dnl["matrix"] is not None
    from vcc_valuations.schemas.industry import IndustryArchetype

    wbc = load_inputs(ROOT, "muddle_through", "australian_major_banks", "wbc")
    assert isinstance(wbc["archetype"], IndustryArchetype) and wbc["matrix"] is not None
