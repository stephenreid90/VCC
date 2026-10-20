"""The resource_lifecycle framework is typed, not a free-form mapping (20 Oct 2026)."""

import pytest
import yaml
from pathlib import Path

from vcc_valuations.schemas.frameworks import ComplementaryFramework, ResourceLifecycle

ROOT = Path(__file__).resolve().parents[1]


def test_gold_archetype_details_validate_as_resource_lifecycle():
    doc = yaml.safe_load((ROOT / "data/industries/gold_producers.yaml").read_text(encoding="utf-8"))
    fw = ComplementaryFramework.model_validate(doc["industry_archetype"]["complementary_framework"])
    assert isinstance(fw.details, ResourceLifecycle)


def test_an_untyped_resource_lifecycle_block_is_rejected():
    with pytest.raises(Exception):
        ComplementaryFramework.model_validate({"type": "resource_lifecycle", "details": {"reserve_life": "long"}})
    with pytest.raises(Exception):
        ComplementaryFramework.model_validate({"type": "resource_lifecycle"})
