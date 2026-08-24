"""Single-source-of-truth lint (design/single_source_of_truth.md §5).

Three checks, cheapest first:

1. **No stored derived values in layer 2.** A key that names a computed quantity
   (``computed_wacc``, ``enterprise_value``, ``price_per_share`` ...) must not
   appear in ``data/companies/<id>.yaml``. This is the ``computed_wacc: 0.0882``
   defect: a layer-3 value stored beside its own inputs, silently stale.

2. **No layer-2 block left in layer 1.** ``data/financials/<id>.yaml`` must not
   carry ``normalised_baseline`` — it migrated to ``data/companies/``. Guards
   against the split being quietly undone by a feed refresh or a merge.

3. **Register values are not duplicated in code (ratchet).** Every scalar in the
   register is searched for as a literal across source, scripts and the UI
   generator. Known pre-existing duplicates are recorded in
   ``ssot_lint_baseline.json``; anything *new* fails. As the backfill proceeds
   the baseline must shrink, so a stale entry fails too.

Check 3 is deliberately a ratchet rather than a hard gate: the generator carries
a whole older parameter set that cannot be re-derived by hand until the scenario
engine exists (M2/M3), and hand-patching it would create a fourth inconsistent
set. The ratchet stops the bleeding without demanding the backfill first.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
BASELINE = Path(__file__).parent / "ssot_lint_baseline.json"

DERIVED_KEY = re.compile(
    r"^(computed_|derived_|implied_).*|.*_(wacc|ev)$|^(wacc|enterprise_value|"
    r"equity_value|cost_of_equity|fair_value|price_per_share|value_per_share|"
    r"per_share_value)$"
)

SCAN_GLOBS = ("src/**/*.py", "scripts/**/*.py", "ui_prototypes/_generator/*.py")

# Values too generic to be evidence of duplication (years, counts, small ints,
# common ratios). Matching these would drown the signal.
def _is_scannable(v) -> bool:
    if not isinstance(v, (int, float)) or isinstance(v, bool):
        return False
    a = abs(float(v))
    if a == 0 or a < 0.02 or 1900 <= a <= 2100:
        return False
    return not (float(v).is_integer() and a < 100)


def _walk(node, prefix=""):
    if isinstance(node, dict):
        for k, v in node.items():
            yield from _walk(v, f"{prefix}.{k}" if prefix else str(k))
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from _walk(v, f"{prefix}[{i}]")
    else:
        yield prefix, node


def _company_ids():
    return sorted(p.stem for p in (ROOT / "data" / "companies").glob("*.yaml")
                  if not p.stem.endswith("_documents"))


def _load(p: Path):
    return yaml.safe_load(p.read_text(encoding="utf-8")) or {}


# ----------------------------------------------------------------- check 1
# Observed market snapshots from the feed are layer 1 by definition, even when
# the underlying quantity is derived by whoever published it (EODHD's own EV).
OBSERVED_PREFIXES = ("market_data.", "share_statistics.")

# Pre-existing stored derived values, each to be cleared when that company is
# split per design/single_source_of_truth.md §3. Listed rather than silently
# skipped so the debt stays visible; remove an entry when it is fixed.
KNOWN_STORED_DERIVED: dict[str, str] = {
    # Register empty. CSL's computed_cost_of_equity was cleared in the 25 Jul
    # 2026 CSL split; WBC's cost_of_equity in the 11 Aug 2026 WBC split. No
    # company now stores a computed discount rate.
}


def test_no_stored_derived_values_in_data():
    """Neither layer may store a computed answer.

    Deliberately covers layer 1 as well as layer 2: the defect that motivated
    this check (``computed_wacc: 0.0882``) lived in ``data/financials``, so a
    layer-2-only scan would have missed the very thing it was written for.
    """
    offenders = []
    for cid in _company_ids():
        for rel in (f"data/companies/{cid}.yaml", f"data/financials/{cid}.yaml"):
            p = ROOT / rel
            if not p.exists():
                continue
            for path, _ in _walk(_load(p)):
                leaf = path.split(".")[-1].split("[")[0]
                if path.startswith(OBSERVED_PREFIXES):
                    continue
                if DERIVED_KEY.match(leaf):
                    offenders.append(f"{rel} :: {path}")
    fixed = sorted(set(KNOWN_STORED_DERIVED) - set(offenders))
    assert not fixed, (
        "These stored derived values are gone — remove them from "
        "KNOWN_STORED_DERIVED so the check tightens:\n  " + "\n  ".join(fixed)
    )
    offenders = sorted(set(offenders) - set(KNOWN_STORED_DERIVED))
    assert not offenders, (
        "A computed answer is stored as data. Delete it; the engine computes "
        "these (protocol rule 2):\n  " + "\n  ".join(offenders)
    )


# ----------------------------------------------------------------- check 2
def test_layer_2_block_not_left_in_layer_1():
    offenders = [
        f"data/financials/{p.name}"
        for p in (ROOT / "data" / "financials").glob("*.yaml")
        if "normalised_baseline" in _load(p)
    ]
    # CSL was split on 25 July 2026; no company should carry a layer-2 block in
    # layer 1 now. Kept as an (empty) exemption set for the next unsplit company.
    known_unmigrated: set[str] = set()
    unexpected = sorted(set(offenders) - known_unmigrated)
    assert not unexpected, (
        "Judgement found in a machine-refreshable layer-1 file:\n  "
        + "\n  ".join(unexpected)
        + "\nMove it to data/companies/<id>.yaml (protocol rules 3 and 4)."
    )


# ----------------------------------------------------------------- check 3
def _register_values():
    """{value_as_written: [register paths that hold it]} across both layers."""
    reg: dict[str, set[str]] = {}
    for cid in _company_ids():
        for rel in (f"data/companies/{cid}.yaml", f"data/financials/{cid}.yaml"):
            p = ROOT / rel
            if not p.exists():
                continue
            for path, val in _walk(_load(p)):
                if _is_scannable(val):
                    reg.setdefault(_fmt(val), set()).add(f"{rel}::{path}")
    return reg


def _fmt(v) -> str:
    return f"{float(v):.10g}"


NUMBER = re.compile(r"(?<![\w.])[-+]?(?:\d+\.\d+|\.\d+|\d+)(?![\w.])")


def _find_duplicates():
    """Tokenise each line once and test membership, rather than searching for
    every register value in every line — the naive form is O(lines x values)
    and takes minutes on this repo."""
    reg = _register_values()
    hits: dict[str, list[str]] = {}
    for pattern in SCAN_GLOBS:
        for f in sorted(ROOT.glob(pattern)):
            rel = f.relative_to(ROOT).as_posix()
            for line in f.read_text(encoding="utf-8", errors="ignore").split("\n"):
                if "ssot-allow" in line:
                    continue
                for tok in NUMBER.findall(line):
                    try:
                        key = _fmt(float(tok))
                    except ValueError:
                        continue
                    if key in reg:
                        hits.setdefault(f"{rel}:{key}", sorted(reg[key])[:1])
    return hits


def test_register_values_not_duplicated_in_code():
    if not BASELINE.exists():
        pytest.skip("no baseline recorded yet — run scripts/ssot_lint_baseline.py")
    baseline = set(json.loads(BASELINE.read_text(encoding="utf-8")))
    found = set(_find_duplicates())
    new = sorted(found - baseline)
    assert not new, (
        "New hardcoded copies of register values (protocol rule 1):\n  "
        + "\n  ".join(new)
        + "\nConsume engine output instead, or annotate the line '# ssot-allow'."
    )
    stale = sorted(baseline - found)
    assert not stale, (
        "Baseline entries no longer match. EITHER the duplicate was removed "
        "(good — regenerate the baseline so the ratchet tightens) OR the value "
        "DRIFTED and the copy is now stale (bad — reconcile it first). Check "
        "which before regenerating:\n  " + "\n  ".join(stale)
    )


# Known limitation: the register is keyed by value, not by path, so a value
# stays "live" while any register entry still holds it. Updating `beta` while
# leaving `beta_selected` behind is therefore invisible to check 3. Fixing that
# needs the layer-2 schema (protocol §8, open item 9) to state which key is
# authoritative for each quantity.


# ---------------------------------------------------------------- check 12
def test_valuation_date_ties_the_anchor_walk_and_the_stub():
    """§7.2/§7.5: one date, reachable three ways, and they must agree.

    Batch 3, item 13. The valuation date was implied by ``period_a_days`` and
    recoverable only from a comment. Stating it lets the walk (anchor + Period A)
    and the stub fraction (valuation date -> fiscal year-end) be checked against
    each other, which is the discipline §7.5 asks for and nothing enforced.
    """
    from datetime import date, timedelta

    for cid in _company_ids():
        comp = _load(ROOT / f"data/companies/{cid}.yaml")
        nb = comp.get("normalised_baseline") or {}
        vd = nb.get("valuation_date")
        if vd is None:
            continue
        fin = _load(ROOT / f"data/financials/{cid}.yaml")
        anchor = (fin.get("derived_metrics") or {}).get("net_debt_at")
        days = (nb.get("equity_bridge_run_rates") or {}).get("period_a_days")
        assert anchor and days is not None, f"{cid}: valuation_date needs an anchor and period_a_days"
        assert anchor + timedelta(days=days) == vd, (
            f"{cid}: anchor {anchor} + {days} days = {anchor + timedelta(days=days)}, "
            f"but valuation_date says {vd}"
        )

        # The stub must run from the valuation date to the fiscal year-end.
        fy_end = date(vd.year, 9, 30) if vd <= date(vd.year, 9, 30) else date(vd.year + 1, 9, 30)
        implied = (fy_end - vd).days / 365.0
        assert abs(implied - nb["stub_years"]) < 0.005, (
            f"{cid}: stub_years {nb['stub_years']} implies a different valuation date — "
            f"{vd} to {fy_end} is {implied:.3f} years"
        )


# ---------------------------------------------------------------- check 11
def test_archetype_fallback_must_be_declared_not_inferred():
    """A mistyped archetype id must raise, not degrade to the segment path.

    Batch 3, item 20. ``load_inputs`` used to return ``archetype=None`` whenever
    the file was absent, which is indistinguishable from a typo — and a typo that
    silently changes the valuation path is the worst kind.
    """
    from vcc_valuations.translator import load_inputs

    with pytest.raises(FileNotFoundError, match="segment_level_valuation is not set"):
        load_inputs(ROOT, "muddle_through", "industrial_explosivez", "dnl")

    # CSL declares it, so the segment path still loads with no archetype.
    csl = load_inputs(ROOT, "muddle_through", "biopharmaceuticals", "csl")
    assert csl["archetype"] is None


# ---------------------------------------------------------------- check 10
# Check 3 scans CODE for copies of register values. It is blind to a register
# value duplicated inside its own data file — which is how CSL carried the whole
# normalised_baseline scalar block as a second copy of segment_fcff for months
# (batch 3, item 12). Same defect, opposite direction: one judgement, two homes,
# and nothing to stop them drifting apart.
INTRA_BASELINE = ROOT / "tests" / "ssot_intra_file_baseline.json"

# Paths where the same value legitimately appears more than once.
_INTRA_EXEMPT = (
    ".by_scenario.",          # six scenarios sharing a figure is not duplication
    "_rationale",             # prose
    ".rationale.",
    "beta_peer_dataset",      # peers genuinely share ratios
    ".peers.",
)


def _intra_file_duplicates() -> dict[str, list[str]]:
    """{"file:value": [paths]} for a scannable scalar living at 2+ paths in one file."""
    hits: dict[str, list[str]] = {}
    for cid in _company_ids():
        for rel in (f"data/companies/{cid}.yaml", f"data/financials/{cid}.yaml"):
            path = ROOT / rel
            if not path.exists():
                continue
            seen: dict[str, list[str]] = {}
            for where, value in _walk(_load(path)):
                if not _is_scannable(value):
                    continue
                if any(x in where for x in _INTRA_EXEMPT) or "[" in where:
                    continue
                seen.setdefault(_fmt(float(value)), []).append(where)
            for value, paths in seen.items():
                if len(paths) > 1:
                    hits[f"{rel}:{value}"] = sorted(paths)
    return hits


def test_layer_2_judgements_are_not_stored_twice_in_one_file():
    """One judgement, one home. A second copy is a drift waiting to happen.

    Ratcheted like check 3: a NEW duplicate fails, and a baselined duplicate that
    disappears also fails, so the baseline can only be regenerated deliberately
    and only ever tightens.
    """
    if not INTRA_BASELINE.exists():
        pytest.skip("no baseline recorded yet — run scripts/ssot_lint_baseline.py")
    baseline = set(json.loads(INTRA_BASELINE.read_text(encoding="utf-8")))
    found = _intra_file_duplicates()
    new = sorted(set(found) - baseline)
    assert not new, (
        "A layer-2 judgement now appears at more than one path in its own file:\n  "
        + "\n  ".join(f"{k}  at  {', '.join(found[k])}" for k in new)
        + "\nKeep one copy — the one the engine reads — and move the rationale "
          "prose beside it."
    )
    stale = sorted(baseline - set(found))
    assert not stale, (
        "Baseline entries no longer match. EITHER a duplicate was removed (good "
        "— regenerate so the ratchet tightens) OR a value drifted and the copies "
        "no longer agree, which is the defect this check exists to catch. Read "
        "them before regenerating:\n  " + "\n  ".join(stale)
    )


# --------------------------------------------------------- consumer join
def test_resolve_normalised_baseline_reconstructs_the_wacc_build():
    """The split must be invisible to consumers.

    Layer 2 (data/companies) joined with layer 1 (data/financials) has to hand
    back the pre-migration ``wacc_build`` shape, or every downstream caller
    breaks silently. This is the coverage the migration itself most needed.
    """
    from vcc_valuations.translator import load_inputs, resolve_normalised_baseline

    inputs = load_inputs(
        ROOT,
        scenario_id="muddle_through",
        archetype_id="industrial_explosives",
        company_id="dnl",
    )
    norm = resolve_normalised_baseline(inputs)

    # Layer-2 scalars.
    assert norm["ebit_margin"] == 0.135        # ssot-allow: pinning the join
    assert norm["net_debt"] == 1300.0          # ssot-allow
    assert norm["tax_rate"] == 0.30            # ssot-allow
    assert norm["terminal_growth"] == 0.025    # ssot-allow

    # Rejoined wacc_build spans both layers.
    wb = norm["wacc_build"]
    assert wb["risk_free_rate"] == 0.0430          # ssot-allow: layer 1
    assert wb["equity_market_value"] == 6390.0     # ssot-allow: layer 1 (§5.3 anchor)
    assert wb["debt_market_value"] == 1260.8       # ssot-allow: layer 1 (§5.3 anchor)
    assert wb["equity_risk_premium"] == 0.0500     # ssot-allow: layer 2
    assert wb["beta"] == 1.10                      # ssot-allow: layer 2
    assert wb["cost_of_debt_pretax"] == 0.0600     # ssot-allow: layer 2
    assert "computed_wacc" not in wb, "layer-3 value must not be stored"
    assert "wacc_method" not in norm, "wacc_method is folded into wacc_build"


def test_csl_split_reconstructs_cost_of_equity_build():
    """CSL is split like DNL, but discounts FCFF at the cost of equity.

    So its observed inputs (``coe_observed_inputs``, layer 1) rejoin its
    method/selection block (``coe_method``, layer 2) into ``cost_of_equity_build``
    — the mirror of DNL's ``wacc_build`` — and no ``wacc_build`` is produced.
    """
    from vcc_valuations.translator import resolve_normalised_baseline

    fin = _load(ROOT / "data" / "financials" / "csl.yaml")
    comp = _load(ROOT / "data" / "companies" / "csl.yaml")
    norm = resolve_normalised_baseline({"financials": fin, "company_raw": comp})

    # Layer-2 scalars. These used to be asserted at normalised_baseline top
    # level, where they sat as a second copy of what segment_fcff already held.
    # The mirror was deleted on 23 Aug 2026 (batch 3, item 12), so the assertion
    # moved to the copy the engine actually reads — which is the point: a test
    # that pins a duplicate keeps the duplicate alive.
    mt = norm["segment_fcff"]["by_scenario"]["muddle_through"]
    assert mt["tax_rate"] == 0.19               # ssot-allow: pinning the join
    assert mt["terminal_growth"] == 0.03        # ssot-allow
    assert mt["terminal_ebit_margin"] == 0.30   # ssot-allow

    # Rejoined cost_of_equity_build spans both layers.
    coe = norm["cost_of_equity_build"]
    assert coe["risk_free_rate"] == 0.045       # ssot-allow: layer 1
    assert coe["beta_measured"] == 0.094        # ssot-allow: layer 1
    assert len(coe["beta_peer_dataset"]) == 4   # layer 1
    assert coe["equity_risk_premium"] == 0.05   # ssot-allow: layer 2
    assert coe["beta"] == 0.85                  # ssot-allow: layer 2
    assert "computed_cost_of_equity" not in coe, "layer-3 value must not be stored"
    assert "coe_method" not in norm, "coe_method is folded into cost_of_equity_build"
    assert "wacc_build" not in norm, "CSL has no WACC build"

    # And the split really happened: no normalised_baseline left in layer 1.
    assert "normalised_baseline" not in fin


# Companies whose financials carry no §5.3 anchor dates yet. Listed rather than
# skipped silently: before 23 Aug 2026 the check simply moved on, so two of three
# companies were exempt from the discipline and nothing said so (batch 3, item 13).
NO_ANCHOR_DATES_YET: dict[str, str] = {
    "csl": "Segment-valued off FY25 actuals; anchors sit in segment_fcff.anchors "
           "without dates. Add when the CSL bridge is rebuilt for the WACC move (D-06).",
    "wbc": "Bank bridge is struck off the 1H26 income and balance-sheet anchors; "
           "the §5.3 date discipline has not been applied to the bank archetype yet.",
}


def test_share_and_netdebt_anchor_dates_paired():
    """Methodology §5.4: shares_outstanding_at must equal net_debt_at.

    Any company financials that declare a §5.3 issued-share anchor must pair it
    with a net-debt anchor at the same reported balance-sheet date, and carry a
    §5.3 source note. This is the equity-bridge "don't accidentally mismatch the
    denominator and the leverage" check.
    """
    fin_dir = ROOT / "data" / "financials"
    checked = 0
    for path in sorted(fin_dir.glob("*.yaml")):
        fin = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        ss = fin.get("share_statistics", {}) or {}
        if "shares_outstanding_at" not in ss:
            assert path.stem in NO_ANCHOR_DATES_YET, (
                f"{path.name}: no §5.3 share anchor date and not on the known-gap "
                "list. Add shares_outstanding_at / net_debt_at, or add the company "
                "to NO_ANCHOR_DATES_YET with a reason so the gap stays visible."
            )
            continue
        checked += 1
        dm = fin.get("derived_metrics", {}) or {}
        assert "net_debt_at" in dm, (
            f"{path.name}: §5.4 — share anchor present but derived_metrics.net_debt_at missing"
        )
        assert ss["shares_outstanding_at"] == dm["net_debt_at"], (
            f"{path.name}: §5.4 — shares_outstanding_at {ss['shares_outstanding_at']} "
            f"!= net_debt_at {dm['net_debt_at']}"
        )
        assert ss.get("shares_outstanding_source"), (
            f"{path.name}: §5.3 — shares_outstanding_source required with the anchor"
        )
    assert checked >= 1, "expected at least one company with a §5.3 share anchor (DNL)"


def test_wbc_split_reconstructs_cost_of_equity_build():
    """WBC (bank) is split like CSL: it discounts at the cost of equity.

    Observed inputs (``coe_observed_inputs``, layer 1, ``data/financials/wbc.yaml``)
    rejoin the method/selection block (``coe_method``, layer 2, ``data/companies/
    wbc.yaml``) into ``cost_of_equity_build`` -- the mirror of DNL's ``wacc_build``.
    No stored ``cost_of_equity``; no ``wacc_build`` (a bank has no WACC weighting).
    """
    from vcc_valuations.translator import resolve_normalised_baseline

    fin = _load(ROOT / "data" / "financials" / "wbc.yaml")
    comp = _load(ROOT / "data" / "companies" / "wbc.yaml")
    norm = resolve_normalised_baseline({"financials": fin, "company_raw": comp})

    coe = norm["cost_of_equity_build"]
    assert coe["risk_free_rate"] == 0.0430        # ssot-allow: layer 1
    assert coe["beta_measured"] == 0.73           # ssot-allow: layer 1
    assert len(coe["beta_peer_dataset"]) == 5     # layer 1
    assert coe["equity_risk_premium"] == 0.0500   # ssot-allow: layer 2
    assert coe["beta"] == 0.75                    # ssot-allow: layer 2
    assert "cost_of_equity" not in coe, "layer-3 value must not be stored"
    assert "coe_method" not in norm, "coe_method is folded into cost_of_equity_build"
    assert "wacc_build" not in norm, "WBC (bank) has no WACC build"

    # And the split really happened: no normalised_baseline left in layer 1.
    assert "normalised_baseline" not in fin


def test_csl_segment_assumptions_live_in_layer2_not_layer1():
    """CSL layer-1 circularity fix (11 Aug 2026): per-segment SCENARIO assumptions
    (growth paths, margin uplifts) are layer 2 and must not sit in the observed
    ``data/financials/csl.yaml`` ``segments`` block. Observed FY25 revenue/margin
    stay in layer 1.
    """
    fin = _load(ROOT / "data" / "financials" / "csl.yaml")
    comp = _load(ROOT / "data" / "companies" / "csl.yaml")

    LAYER2 = {"muddle_through_growth_path", "muddle_through_cagr", "growth_shape",
              "growth_rationale", "margin_uplift_cum_fy31", "margin_uplift_rationale"}
    for seg in fin["segments"]:
        leaked = LAYER2 & set(seg)
        assert not leaked, f"layer-2 leak in financials segment {seg.get('segment')}: {leaked}"
        assert "fy25_revenue" in seg and "fy25_or_margin" in seg

    sb = comp["normalised_baseline"]["segment_baseline"]
    assert {s["segment"] for s in sb} == {"csl_behring", "csl_seqirus", "csl_vifor"}
    beh = next(s for s in sb if s["segment"] == "csl_behring")
    assert beh["muddle_through_growth_path"][0] == -0.01   # ssot-allow
    assert beh["margin_uplift_cum_fy31"] == 0.015          # ssot-allow

    assert "normalised_baseline" not in fin
    assert fin["base_year_status"] != "workbook_reverse_engineered"


def test_working_capital_intensity_declared_for_every_non_exempt_company():
    """Working-capital ratchet (working_capital_treatment.md §5 step 5).

    Every company whose archetype is not exempt (bank) must carry both the
    layer-1 ``working_capital_history`` and the layer-2
    ``normalised_baseline.working_capital_intensity.clean_years`` judgement —
    so working_capital_intensity_from_data() can derive an applied figure for
    it. A bank must be exempt BY the ``industry_type: bank`` rule, never by
    silently having neither block (which would look, from the outside,
    identical to an intensity of zero — the exact failure mode the
    terminal-share warning already hit once, see working_capital_treatment.md
    §3).
    """
    from vcc_valuations.translator import load_inputs, working_capital_intensity_from_data

    cases = [
        ("dnl", "muddle_through", "industrial_explosives"),
        ("csl", "muddle_through", "biopharmaceuticals"),
        ("wbc", "muddle_through", "australian_major_banks"),
    ]
    for company_id, scenario_id, archetype_id in cases:
        inp = load_inputs(ROOT, scenario_id, archetype_id, company_id)
        is_bank = inp["company_raw"]["company_position"].get("industry_type") == "bank"
        result = working_capital_intensity_from_data(inp)
        if is_bank:
            assert result is None, f"{company_id}: bank must be exempt (None), not a value"
        else:
            assert result is not None, f"{company_id}: non-exempt company must produce an intensity"
            assert 0.0 <= result.result <= 1.0, f"{company_id}: intensity {result.result} out of range"
