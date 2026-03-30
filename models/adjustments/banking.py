"""Banking-specific valuation adjustments."""
from typing import Dict


class BankingAdjustments:
    """Apply banking-sector adjustments to valuation models."""

    @staticmethod
    def net_interest_margin_adjustment(
        current_nim: float,
        rate_environment: str = "stable",  # "rising", "falling", "stable"
    ) -> float:
        """Adjust NIM based on interest rate environment."""
        adjustments = {"rising": 1.05, "falling": 0.95, "stable": 1.0}
        return round(current_nim * adjustments.get(rate_environment, 1.0), 4)

    @staticmethod
    def loan_loss_reserve_adjustment(
        total_loans: float,
        default_rate: float = 0.01,
        recovery_rate: float = 0.50,
    ) -> float:
        """Calculate expected loan loss provision."""
        return round(total_loans * default_rate * (1 - recovery_rate), 2)

    @staticmethod
    def cet1_ratio_check(
        cet1_ratio: float,
        regulatory_minimum: float = 0.06,
        buffer: float = 0.02,
    ) -> Dict:
        """Check CET1 adequacy and headroom."""
        required = regulatory_minimum + buffer
        headroom = round(cet1_ratio - required, 4)
        return {
            "cet1_ratio": cet1_ratio,
            "required": required,
            "headroom": headroom,
            "adequate": cet1_ratio >= required,
        }

    @staticmethod
    def dividend_capacity(
        net_income: float,
        cet1_ratio: float,
        cet1_target: float = 0.12,
        rwa: float = 0.0,
    ) -> float:
        """Estimate distributable earnings after maintaining CET1 target."""
        if rwa > 0:
            capital_required = max(0, (cet1_target - cet1_ratio) * rwa)
            return round(max(net_income - capital_required, 0), 2)
        return round(net_income * 0.70, 2)  # rough 70% payout if RWA unknown
