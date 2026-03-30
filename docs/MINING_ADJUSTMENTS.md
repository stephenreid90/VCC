# Mining Valuation Adjustments

## Key Differences vs Corporate DCF

Mining companies require adjustments for:
1. **Commodity price cycles** — Blend spot and long-term price
2. **Reserve depletion** — Assets are finite; model reserve life explicitly
3. **FCF conversion** — Capital-intensive, high AISC erodes conversion rates
4. **Jurisdiction risk** — Political/regulatory discount

## Functions in `models/adjustments/mining.py`

### `commodity_price_adjustment()`
Blends spot and long-term price. Typical weight: 70% long-term, 30% spot.

### `reserve_life_adjustment()`
Calculates effective reserve life with depletion risk discount.

### `production_cost_adjustment()`
Projects AISC inflation over explicit period.

### `fcf_conversion_adjustment()`
Applies sector + risk-tier discount to EBITDA → FCF:

| Commodity | Base Conversion | Risk Tiers |
|-----------|----------------|------------|
| Gold | 65% | low +5%, high -8% |
| Copper | 55% | |
| Iron Ore | 60% | |
| Lithium | 50% | (high capex) |

## Recommended Workflow
1. Start with standard DCF in `01_dcf_build.ipynb`
2. Apply `MiningAdjustments.commodity_price_adjustment()` to FCF assumptions
3. Shorten explicit period to match reserve life
4. Apply FCF conversion discount
