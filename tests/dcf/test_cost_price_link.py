"""D-104 (ruled 20 Oct 2026): the cost-price link is declared on the archetype, read by the
translator, overridable per company and per call, and leaves a flat-real path alone."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from vcc_valuations.dcf.resource_engine import ResourceEngine
from vcc_valuations.resource_translator import (
    build_resource_inputs_from_data, cost_price_link_params, price_and_cost_paths,
)
from vcc_valuations.translator import load_inputs

ROOT = Path(__file__).resolve().parents[2]


def _resource_companies():
    out = []
    for p in sorted((ROOT / "data" / "companies").glob("*.yaml")):
        d = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
        if (d.get("normalised_baseline") or {}).get("engine") == "resource":
            out.append((p.stem, d["company_position"]["industry_archetype"]))
    return out


@pytest.mark.parametrize("cid,arch", _resource_companies())
def test_archetype_declares_the_link_and_the_translator_reads_it(cid, arch):
    inp = load_inputs(ROOT, "muddle_through", arch, cid)
    params = cost_price_link_params(inp)
    assert params is not None
    assert params["elasticity_per_10pct"] == 1.5 and params["lag_years"] == 1
    assert params["cap_above_base_pct"] == 20.0 and params["symmetric"] is True
    assert cost_price_link_params(inp, {"elasticity_per_10pct": 3.0})["elasticity_per_10pct"] == 3.0
    with pytest.raises(KeyError):
        cost_price_link_params(inp, {"elasticity": 3.0})


@pytest.mark.parametrize("cid,arch", _resource_companies())
def test_company_override_takes_precedence_over_the_archetype(cid, arch):
    inp = load_inputs(ROOT, "muddle_through", arch, cid)
    inp["company_raw"]["normalised_baseline"]["cost_price_link"] = {"lag_years": 2}
    assert cost_price_link_params(inp)["lag_years"] == 2
    assert cost_price_link_params(inp)["elasticity_per_10pct"] == 1.5


@pytest.mark.parametrize("cid,arch", _resource_companies())
def test_flat_real_price_path_carries_no_link(cid, arch):
    inp = load_inputs(ROOT, "fragmentation", arch, cid)
    spot = inp["financials"]["spot_reference"]
    flat = {"gold_usd_oz": spot["gold_usd_oz"], "aud_usd": spot["aud_usd"], "copper_usd_t": 20000.0}
    e = build_resource_inputs_from_data(inp, "fragmentation", flat_real=flat)
    assert all(x == pytest.approx(1.0) for x in e.cost_price_link)
    # whereas the scenario's own path above spot raises costs after the lag
    e2 = build_resource_inputs_from_data(inp, "fragmentation")
    assert max(e2.cost_price_link) > 1.0 and max(e2.cost_price_link) <= 1.20


@pytest.mark.parametrize("cid,arch", _resource_companies())
def test_link_reads_the_primary_real_price_with_the_declared_lag(cid, arch):
    inp = load_inputs(ROOT, "orderly_convergence", arch, cid)
    e = build_resource_inputs_from_data(inp, "orderly_convergence")
    paths = price_and_cost_paths(inp, "orderly_convergence", len(e.cost_price_link))
    real = [p / c for p, c in zip(paths["primary_aud"], paths["cpi_index"])]
    for t in range(1, len(real)):
        expected = min(1.0 + 0.15 * (real[t - 1] / real[0] - 1.0), 1.20)
        assert e.cost_price_link[t] == pytest.approx(expected)
    assert e.cost_price_link[0] == pytest.approx(1.0)


@pytest.mark.parametrize("cid,arch", _resource_companies())
def test_switching_the_link_off_reproduces_the_unlinked_engine(cid, arch):
    inp = load_inputs(ROOT, "stagflation_persists", arch, cid)
    off = build_resource_inputs_from_data(inp, "stagflation_persists", cost_link_override={"elasticity_per_10pct": 0.0})
    assert all(x == pytest.approx(1.0) for x in off.cost_price_link)
    on = build_resource_inputs_from_data(inp, "stagflation_persists")
    r_off, r_on = ResourceEngine().run(off), ResourceEngine().run(on)
    assert r_on.value_per_share < r_off.value_per_share
    assert r_on.revenue == pytest.approx(r_off.revenue)
    assert r_on.royalty == pytest.approx(r_off.royalty)
