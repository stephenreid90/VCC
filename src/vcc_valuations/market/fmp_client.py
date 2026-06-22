"""
Financial Modeling Prep (FMP) API client.

A deliberately thin wrapper over the handful of FMP endpoints needed to
estimate an implied Equity Market Risk Premium (EMRP) for the US market.

Free-tier friendly
------------------
FMP's *index* data (e.g. the ^GSPC quote) sits in a premium dataset, but
the EMRP model is scale-invariant — it depends on the cash *yield* and
growth path, not the absolute price level — so SPY (the S&P 500 ETF, a
normal US-listed ticker available on the free plan) is used as the proxy.

Endpoints used (all on FMP's current "stable" API, free-plan accessible):
  * SPY quote                 -> price proxy for the index level
  * 10-year Treasury rate     -> the risk-free rate
  * SPY dividend history      -> trailing-12m dividend yield

Free plan limits: 250 requests/day, 500 MB / 30 days, US data only. One
EMRP run uses ~3 requests. If a single call is ever blocked on your plan,
the run script lets you supply that number by hand instead (manual
override), so you are never wholly dependent on the API.

What FMP does NOT give at any tier, and is therefore a model assumption:
  * aggregate S&P 500 *buyback* yield
  * bottom-up consensus earnings growth for the index as a whole

The API key is read from the FMP_API_KEY environment variable. Never
hard-code it; put it in a local .env file (already git-ignored). See
.env.example.

Docs: https://site.financialmodelingprep.com/developer/docs
"""

from __future__ import annotations

import os
from datetime import date, timedelta

import requests

_BASE = "https://financialmodelingprep.com/stable"

DEFAULT_TIMEOUT = 15


class FMPError(RuntimeError):
    """Raised when the FMP API returns an error or an unexpected payload."""


class FMPClient:
    """Minimal FMP client. One session, JSON only, explicit errors."""

    def __init__(self, api_key: str | None = None, timeout: int = DEFAULT_TIMEOUT):
        self.api_key = api_key or os.environ.get("FMP_API_KEY")
        if not self.api_key:
            raise FMPError(
                "No FMP API key found. Set the FMP_API_KEY environment "
                "variable (e.g. in a local .env file) or pass api_key=..."
            )
        self.timeout = timeout
        self._session = requests.Session()

    # ------------------------------------------------------------------ #
    # low-level
    # ------------------------------------------------------------------ #
    def _get(self, endpoint: str, params: dict | None = None):
        params = dict(params or {})
        params["apikey"] = self.api_key
        url = f"{_BASE}/{endpoint}"
        try:
            resp = self._session.get(url, params=params, timeout=self.timeout)
        except requests.RequestException as exc:  # network / DNS / timeout
            raise FMPError(f"FMP request failed for {endpoint}: {exc}") from exc
        if resp.status_code == 402 or resp.status_code == 403:
            raise FMPError(
                f"FMP denied {endpoint} (HTTP {resp.status_code}) — this "
                "endpoint likely needs a paid plan. Use a manual override."
            )
        if resp.status_code != 200:
            raise FMPError(
                f"FMP returned HTTP {resp.status_code} for {endpoint}: "
                f"{resp.text[:200]}"
            )
        data = resp.json()
        # FMP signals auth/plan problems as a dict with an 'Error Message'.
        if isinstance(data, dict) and data.get("Error Message"):
            raise FMPError(data["Error Message"])
        return data

    # ------------------------------------------------------------------ #
    # endpoints
    # ------------------------------------------------------------------ #
    def index_level(self, symbol: str = "SPY") -> float:
        """
        Latest price for a ticker. Defaults to SPY as the free-tier S&P 500
        proxy (the model is scale-invariant, so the ETF level is fine).
        """
        data = self._get("quote", {"symbol": symbol})
        if not data:
            raise FMPError(f"No quote returned for {symbol}")
        return float(data[0]["price"])

    def risk_free_rate(self, tenor: str = "year10") -> float:
        """
        Most recent constant-maturity Treasury yield as a decimal.

        `tenor` is an FMP field name, e.g. 'year10', 'year5', 'month3'.
        FMP reports percentages, so 4.25 is returned as 0.0425.
        """
        today = date.today()
        params = {
            "from": (today - timedelta(days=14)).isoformat(),
            "to": today.isoformat(),
        }
        data = self._get("treasury-rates", params)
        if not data:
            raise FMPError("No treasury data returned")
        latest = max(data, key=lambda row: row["date"])
        if tenor not in latest:
            raise FMPError(
                f"Tenor {tenor!r} not in treasury row; "
                f"available: {sorted(latest)}"
            )
        return float(latest[tenor]) / 100.0

    def dividend_yield(self, symbol: str = "SPY") -> float:
        """
        Trailing-12-month dividend yield as a decimal, using SPY as the
        S&P 500 proxy (sum of last 12m cash dividends / current price).
        """
        price = self.index_level(symbol)
        if price <= 0:
            raise FMPError(f"Non-positive price for {symbol}; cannot yield")
        data = self._get("dividends", {"symbol": symbol})
        rows = data if isinstance(data, list) else data.get("historical", [])
        cutoff = date.today() - timedelta(days=365)
        ttm = 0.0
        for row in rows:
            raw = row.get("date")
            if not raw:
                continue
            if date.fromisoformat(raw[:10]) >= cutoff:
                ttm += float(row.get("adjDividend") or row.get("dividend") or 0.0)
        return ttm / price
