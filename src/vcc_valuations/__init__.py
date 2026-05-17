"""
VCC Valuations — scenario-based equity valuation module.

Companion to design/architecture.md (v0.1 frozen, tagged architecture-v0.1).

Layers:
  Layer 1 — Scenario library         (schemas.scenario)
  Layer 2 — Industry archetype       (schemas.industry)
  Layer 3 — Company positioning      (schemas.company)
  Layer 4 — Driver taxonomy          (schemas.driver)
  Layer 5 — Linkage / impact matrix  (schemas.linkage)
  Layer 6 — Assumption translation   (schemas.assumption)
  Layer 7 — DCF engine               (deferred)
  Layer 8 — Interactive interface    (deferred; embedded in VCC dashboard)
"""

__version__ = "0.1.0"
