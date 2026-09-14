"""D-43a: a moat source declares what it actually does.

A contract confers a RENT — a cash advantage with an end date, carried in the
explicit period. A BARRIER is what stops a rival taking the business, and it is
what the terminal excess-return decay horizon measures. The first draft of D-43
conflated them and said a contractual expiry sets the horizon, which produced a
standing contradiction on Denali: the impact matrix declared a ten-to-fifteen
year horizon while the gas contracts underwriting one leg of the moat expire six
years from the valuation date.

This test is a ratchet in the shape of check 13. A moat block that declares roles
must declare one for every source — the schema enforces that. A block that does
not declare them at all must be named in the baseline, so the rule tightens as
blocks are filled in and can never quietly loosen.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterator, List, Tuple

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
COMPANIES = sorted((ROOT / "data" / "companies").glob("*.yaml"))
BASELINE = ROOT / "tests" / "moat_role_baseline.json"

VALID_ROLES = {"rent", "barrier", "both"}


def _walk(node: Any, path: str = "") -> Iterator[Tuple[str, Dict[str, Any]]]:
    """Yield every moat block in a document, with a readable path to it."""
    if isinstance(node, dict):
        for k, v in node.items():
            here = f"{path}.{k}" if path else str(k)
            if k == "moat" and isinstance(v, dict) and "sources" in v:
                yield here, v
            else:
                yield from _walk(v, here)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from _walk(v, f"{path}[{i}]")


def _blocks() -> List[Tuple[str, Dict[str, Any]]]:
    out: List[Tuple[str, Dict[str, Any]]] = []
    for f in COMPANIES:
        doc = yaml.safe_load(f.read_text(encoding="utf-8"))
        for path, block in _walk(doc):
            out.append((f"{f.stem}:{path}", block))
    return out


def _baseline() -> set:
    if not BASELINE.exists():
        return set()
    return set(json.loads(BASELINE.read_text(encoding="utf-8"))["undeclared"])


def test_there_are_moat_blocks_to_check() -> None:
    assert _blocks(), "no moat blocks found — the company files have moved"


@pytest.mark.parametrize("key,block", _blocks(), ids=lambda x: x if isinstance(x, str) else "")
def test_a_block_either_declares_its_roles_or_is_baselined(key: str, block: dict) -> None:
    roles = block.get("source_roles")
    if roles is None:
        assert key in _baseline(), (
            f"{key} declares moat sources but no roles. D-43a needs each source "
            f"marked rent, barrier or both. Add them, or add {key!r} to "
            f"{BASELINE.name} with a reason if the judgement is not yet made."
        )
        return

    assert key not in _baseline(), (
        f"{key} now declares roles but is still in {BASELINE.name}. "
        f"Regenerate the baseline so it only ever tightens."
    )
    assert set(roles) == set(block["sources"]), (
        f"{key}: roles must cover every source exactly"
    )
    for source, role in roles.items():
        assert role in VALID_ROLES, f"{key}: {source} has role {role!r}"


def test_a_rent_bearing_source_does_not_set_the_horizon_alone(
) -> None:
    """The Denali case the rule was written for.

    If every declared source were rent-bearing there would be no barrier to set
    a horizon from, and the original D-43 reading would apply — the expiry would
    set it directly. That is a legitimate configuration, but it should be
    visible rather than arrived at by accident, so assert it is not the case
    anywhere today.
    """
    for key, block in _blocks():
        roles = block.get("source_roles")
        if not roles:
            continue
        if all(r == "rent" for r in roles.values()):
            pytest.fail(
                f"{key}: every source is rent-bearing, so the moat has no "
                f"barrier and the decay horizon collapses to the earliest "
                f"expiry. Intended? Say so in the block's evidence."
            )
