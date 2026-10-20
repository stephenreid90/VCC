"""Shared fixtures for valuation tests."""
import os
import subprocess
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[1]
_GEN = _ROOT / "ui_prototypes" / "_generator"
_PAGES = [_ROOT / "ui_prototypes" / ("%s_scenario_interface.html" % k) for k in ("dnl", "wbc", "csl", "evn")]


@pytest.fixture(scope="session", autouse=True)
def generated_ui_pages():
    """Build the prototype pages when any is absent.

    The pages are gitignored build output (reproducible from ui_prototypes/_generator),
    so a fresh checkout such as the GitHub Actions runner has none. Five UI tests read
    them; from 16 October 2026 they failed every CI run for that reason alone. Building
    takes about ten seconds. If the build fails the tests that need the pages fail with
    the build's own error rather than a missing-file error.
    """
    if all(p.exists() for p in _PAGES):
        return
    env = dict(os.environ, PYTHONPATH=os.pathsep.join(filter(None, [str(_ROOT / "src"), os.environ.get("PYTHONPATH", "")])))
    for script in ("build_cfgs.py", "gen_ui.py"):
        res = subprocess.run([sys.executable, script], cwd=str(_GEN), capture_output=True, text=True, env=env)
        if res.returncode != 0:
            raise RuntimeError("%s failed building the prototype pages:\n%s" % (script, res.stderr[-2000:]))
from models.dcf import DCFAssumptions
from models.three_statement import ThreeStatementAssumptions
from models.comps import ComparableCompany


@pytest.fixture
def apple_dcf():
    return DCFAssumptions(
        fcf_base=110e9,
        fcf_growth_rate=5.0,
        wacc=7.65,
        terminal_growth=2.5,
        explicit_periods=5,
        net_debt=-50e9,
        shares_outstanding=15.5e9,  # absolute share count
    )


@pytest.fixture
def corp_3s():
    return ThreeStatementAssumptions(
        revenue_base=1_000e6,
        revenue_growth=8.0,
        ebitda_margin=25.0,
        da_pct_revenue=4.0,
        tax_rate=30.0,
        capex_pct_revenue=5.0,
        nwc_pct_revenue=2.0,
        explicit_periods=5,
    )


@pytest.fixture
def peer_companies():
    return [
        ComparableCompany(name="PeerA", ev=50e9, ebitda=5e9, revenue=20e9,
                          net_income=2e9, shares_outstanding=1000, share_price=50),
        ComparableCompany(name="PeerB", ev=80e9, ebitda=8e9, revenue=30e9,
                          net_income=3e9, shares_outstanding=1500, share_price=60),
        ComparableCompany(name="PeerC", ev=40e9, ebitda=4e9, revenue=15e9,
                          net_income=1.5e9, shares_outstanding=800, share_price=45),
    ]
