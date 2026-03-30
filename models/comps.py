"""Trading comparables analysis — EV/EBITDA, P/E, EV/Revenue."""
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
import statistics


class ComparableCompany(BaseModel):
    name: str
    ev: float = Field(..., description="Enterprise value (USD)")
    ebitda: Optional[float] = None
    net_income: Optional[float] = None
    revenue: Optional[float] = None
    shares_outstanding: Optional[float] = None
    share_price: Optional[float] = None

    model_config = {"extra": "allow"}


class CompsResult(BaseModel):
    multiples: List[Dict]
    medians: Dict[str, Optional[float]]
    implied_value: Dict[str, Optional[float]]

    model_config = {"extra": "allow"}


class CompsModel:
    def __init__(self, peers: List[ComparableCompany], target: ComparableCompany):
        self.peers = peers
        self.target = target

    def calculate(self) -> CompsResult:
        multiples = []
        ev_ebitda_list, pe_list, ev_rev_list = [], [], []

        for c in self.peers:
            row = {"name": c.name}
            if c.ebitda and c.ebitda > 0:
                m = round(c.ev / c.ebitda, 2)
                row["ev_ebitda"] = m
                ev_ebitda_list.append(m)
            if c.net_income and c.shares_outstanding and c.share_price and c.net_income > 0:
                eps = c.net_income / c.shares_outstanding
                m = round(c.share_price / eps, 2)
                row["pe"] = m
                pe_list.append(m)
            if c.revenue and c.revenue > 0:
                m = round(c.ev / c.revenue, 2)
                row["ev_revenue"] = m
                ev_rev_list.append(m)
            multiples.append(row)

        medians = {
            "ev_ebitda": round(statistics.median(ev_ebitda_list), 2) if ev_ebitda_list else None,
            "pe": round(statistics.median(pe_list), 2) if pe_list else None,
            "ev_revenue": round(statistics.median(ev_rev_list), 2) if ev_rev_list else None,
        }

        t = self.target
        implied = {}
        if medians["ev_ebitda"] and t.ebitda:
            implied["ev_ebitda"] = round(medians["ev_ebitda"] * t.ebitda, 2)
        if medians["ev_revenue"] and t.revenue:
            implied["ev_revenue"] = round(medians["ev_revenue"] * t.revenue, 2)

        return CompsResult(multiples=multiples, medians=medians, implied_value=implied)
