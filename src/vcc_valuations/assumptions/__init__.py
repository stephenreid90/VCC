"""
Layer 6 — assumptions translation.

This package turns qualitative driver movements + a base-year snapshot into the
numeric, schema-compliant assumption inputs the DCF / DDM engines consume
(architecture spec section 11). Built out incrementally per the engine
implementation plan:

- ``wacc`` — the single-discipline WACC component build-up (section 3.5).

The full translator (``rules``, ``time_profiles``, ``chain``, ``derivations``,
``consistency``, ``aggregate``, ``build``) lands in milestone M2. Until then the
DCF engine is driven from a resolved ``FcfEngineInputs`` object (see
``vcc_valuations.dcf.fcf_engine``) that mirrors a company's audited-workbook
Assumptions sheet.
"""

from vcc_valuations.assumptions.wacc import WaccBuild

__all__ = ["WaccBuild"]
