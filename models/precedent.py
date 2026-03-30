"""M&A precedent transactions analysis."""
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
import statistics


class PrecedentTransaction(BaseModel):
    name: str
    year: int
    ev: float
    ebitda: Optional[float] = None
    revenue: Optional[float] = None
    control_premium: Optional[float] = None  # % premium to undisturbed price

    model_config = {"extra": "allow"}


class PrecedentResult(BaseModel):
    multiples: List[Dict]
    medians: Dict[str, Optional[float]]
    implied_value: Dict[str, Optional[float]]

    model_config = {"extra": "allow"}


class PrecedentModel:
    def __init__(self, transactions: List[PrecedentTransaction], target_ebitda: Optional[float] = None,
                 target_revenue: Optional[float] = None):
        self.transactions = transactions
        self.target_ebitda = target_ebitda
        self.target_revenue = target_revenue

    def calculate(self) -> PrecedentResult:
        multiples, ev_ebitda_list, ev_rev_list = [], [], []

        for t in self.transactions:
            row = {"name": t.name, "year": t.year}
            if t.ebitda and t.ebitda > 0:
                m = round(t.ev / t.ebitda, 2)
                row["ev_ebitda"] = m
                ev_ebitda_list.append(m)
            if t.revenue and t.revenue > 0:
                m = round(t.ev / t.revenue, 2)
                row["ev_revenue"] = m
                ev_rev_list.append(m)
            if t.control_premium:
                row["control_premium"] = t.control_premium
            multiples.append(row)

        medians = {
            "ev_ebitda": round(statistics.median(ev_ebitda_list), 2) if ev_ebitda_list else None,
            "ev_revenue": round(statistics.median(ev_rev_list), 2) if ev_rev_list else None,
        }

        implied = {}
        if medians["ev_ebitda"] and self.target_ebitda:
            implied["ev_ebitda"] = round(medians["ev_ebitda"] * self.target_ebitda, 2)
        if medians["ev_revenue"] and self.target_revenue:
            implied["ev_revenue"] = round(medians["ev_revenue"] * self.target_revenue, 2)

        return PrecedentResult(multiples=multiples, medians=medians, implied_value=implied)
