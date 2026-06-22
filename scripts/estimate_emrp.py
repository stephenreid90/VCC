"""
Estimate the implied US Equity Market Risk Premium (EMRP) for the S&P 500.

Free-tier friendly: uses SPY (the S&P 500 ETF, available on FMP's free
plan) as the index proxy, since the model is scale-invariant. Pulls three
live inputs from Financial Modeling Prep (FMP):
    * SPY price              (proxy for the index level)
    * 10-year Treasury yield (risk-free rate)
    * SPY trailing dividend yield

and combines them with analyst-supplied assumptions you set below:
    * net buyback yield      (added to dividend yield -> total cash yield)
    * CONSENSUS_GROWTH        (per-year growth, for as long as consensus runs)

then solves for the IRR that equates the proxy price to the PV of that
cash-flow stream. Implied EMRP = IRR - risk-free rate.

Any single live input can be pinned by hand (see the MANUAL_* overrides) so
the run still works if an endpoint is blocked on your plan.

Usage:
    # put FMP_API_KEY in a local .env (see .env.example) or export it
    PYTHONPATH=src python scripts/estimate_emrp.py
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from vcc_valuations.market.fmp_client import FMPClient, FMPError  # noqa: E402
from vcc_valuations.market.implied_emrp import estimate_emrp  # noqa: E402

# --------------------------------------------------------------------------- #
# Analyst assumptions — edit these.
# --------------------------------------------------------------------------- #
# Index proxy. SPY is free-tier; the model is scale-invariant so the ETF
# level gives the same implied return as the raw index.
SYMBOL = "SPY"

# Net buyback yield: cash returned via repurchases as a % of index, on top of
# dividends. FMP has no aggregate buyback feed at any tier, so set it from your
# own source (S&P DJI buyback reports have run ~1.5-2.5% in recent years).
BUYBACK_YIELD = 0.018

# Consensus growth path for cash flows to shareholders, one rate per year, for
# as many years as consensus runs. After the last entry the terminal rate
# applies in perpetuity. Replace with your consensus EPS-growth series.
CONSENSUS_GROWTH = [0.11, 0.09, 0.08, 0.07, 0.06]

# Terminal growth: conventionally the risk-free rate (set below from FMP).
# Set to None to use the live risk-free rate, or pin a number, e.g. 0.04.
TERMINAL_GROWTH: float | None = None

# --------------------------------------------------------------------------- #
# Manual overrides — leave as None to pull live from FMP. Set a number to skip
# that API call (useful if an endpoint is blocked on your plan, or for offline
# what-if runs). Values are decimals: 0.043 = 4.3%.
# --------------------------------------------------------------------------- #
MANUAL_PRICE: float | None = None           # e.g. 600.0 (SPY) or 5500.0 (index)
MANUAL_RISK_FREE: float | None = None        # e.g. 0.043
MANUAL_DIVIDEND_YIELD: float | None = None   # e.g. 0.013


def _load_dotenv(path: Path) -> None:
    """Minimal .env loader (no extra dependency); ignores if absent."""
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip().strip("'\""))


def main() -> int:
    _load_dotenv(ROOT / ".env")

    # Only build a client if we actually need to hit the API.
    need_live = (
        MANUAL_PRICE is None
        or MANUAL_RISK_FREE is None
        or MANUAL_DIVIDEND_YIELD is None
    )
    client = None
    if need_live:
        try:
            client = FMPClient()
        except FMPError as exc:
            print(f"FMP error: {exc}", file=sys.stderr)
            return 1

    try:
        index_level = (
            MANUAL_PRICE if MANUAL_PRICE is not None
            else client.index_level(SYMBOL)
        )
        risk_free = (
            MANUAL_RISK_FREE if MANUAL_RISK_FREE is not None
            else client.risk_free_rate("year10")
        )
        dividend_yield = (
            MANUAL_DIVIDEND_YIELD if MANUAL_DIVIDEND_YIELD is not None
            else client.dividend_yield(SYMBOL)
        )
    except FMPError as exc:
        print(
            f"FMP error: {exc}\n"
            "Tip: pin the affected value via a MANUAL_* override at the top "
            "of this script and re-run.",
            file=sys.stderr,
        )
        return 1

    terminal_growth = risk_free if TERMINAL_GROWTH is None else TERMINAL_GROWTH
    cash_yield = dividend_yield + BUYBACK_YIELD
    base_cash_flow = cash_yield * index_level

    result = estimate_emrp(
        index_level=index_level,
        base_cash_flow=base_cash_flow,
        consensus_growth=CONSENSUS_GROWTH,
        terminal_growth=terminal_growth,
        risk_free_rate=risk_free,
    )

    src = lambda manual: "manual" if manual is not None else "FMP"
    print(f"Implied US EMRP — S&P 500 via {SYMBOL}\n" + "-" * 42)
    print(f"Price proxy         : {index_level:,.2f}  ({src(MANUAL_PRICE)})")
    print(
        f"Dividend yield      : {dividend_yield:6.2%}  "
        f"({src(MANUAL_DIVIDEND_YIELD)})"
    )
    print(f"Buyback yield       : {BUYBACK_YIELD:6.2%}  (assumption)")
    print(f"Total cash yield    : {cash_yield:6.2%}")
    print(f"Consensus growth    : {[f'{g:.1%}' for g in CONSENSUS_GROWTH]}")
    print("-" * 42)
    print(result.summary())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
