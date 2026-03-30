"""Mining-specific valuation adjustments."""
from typing import Dict


class MiningAdjustments:
    """Apply mining-sector adjustments to valuation inputs."""

    @staticmethod
    def commodity_price_adjustment(
        commodity: str,
        spot_price: float,
        long_term_price: float,
        weight: float = 0.7,
    ) -> float:
        """Blend spot and long-term price for FCF assumptions."""
        return round(weight * long_term_price + (1 - weight) * spot_price, 4)

    @staticmethod
    def reserve_life_adjustment(
        annual_production: float,
        proven_reserves: float,
        risk_discount: float = 0.05,
    ) -> float:
        """Adjust reserve life for depletion risk."""
        reserve_life_years = proven_reserves / annual_production
        return round(reserve_life_years * (1 - risk_discount), 2)

    @staticmethod
    def production_cost_adjustment(
        current_cost_per_tonne: float,
        inflation_rate: float = 0.02,
        years: int = 5,
    ) -> Dict[int, float]:
        """Project all-in sustaining cost (AISC) over time."""
        return {
            yr: round(current_cost_per_tonne * (1 + inflation_rate) ** yr, 2)
            for yr in range(1, years + 1)
        }

    @staticmethod
    def fcf_conversion_adjustment(
        ebitda: float,
        commodity: str = "generic",
        risk_tier: str = "medium",  # "low", "medium", "high"
    ) -> float:
        """
        Adjust FCF conversion by commodity type and risk tier.

        Risk tiers reflect capital intensity, jurisdiction, and commodity volatility.
        """
        base_conversion = {
            "gold": 0.65,
            "copper": 0.55,
            "iron_ore": 0.60,
            "lithium": 0.50,
            "coal": 0.58,
            "generic": 0.60,
        }.get(commodity.lower(), 0.60)

        risk_adjustments = {"low": 0.05, "medium": 0.0, "high": -0.08}
        adjusted = base_conversion + risk_adjustments.get(risk_tier, 0.0)
        return round(ebitda * max(adjusted, 0.30), 2)
