"""CET1 capital diagnostic for the bank engine — warn-only (methodology §15.5).

Open item 8. The §15 fork values a bank by discounting dividends, and the payout
ratio is a flat input in every scenario. Nothing checks whether that payout is
survivable. On WBC's central case book equity compounds at well under the rate
AIEA compounds at, so the implied capital ratio falls in every year of the
explicit period and the model does not notice; under Stagflation, NPAT falls by
more than half with the payout unchanged, which in the real world is the moment a
board stops a buyback and then cuts the dividend.

This module is the first of the two steps that item 8 asks for, and deliberately
only the first. It OBSERVES the trajectory and warns. It does not force a payout
cut, does not feed anything back into the engine, and cannot move a level — book
equity in the §15 build is a pure accumulator (NII comes from AIEA, never from
equity), so the per-period roll-forward this needs sums to exactly the closing
figure the engine already computes. Forcing the payout is a separate change with
its own ruling, and it is the one that will move numbers.

How the ratio is struck, and what that costs
--------------------------------------------
CET1 capital is not book equity: the regulatory measure deducts goodwill,
intangibles and some deferred tax, and the data carries no bridge between the two.
Rather than invent one, the diagnostic **anchors on the bank's own reported CET1
ratio** — an observable, sourced in the company file — and rolls it forward on the
proportional change the model itself implies:

    ratio[t] = ratio[t-1] x (1 + retained[t] / opening_equity[t]) / (rwa[t] / rwa[t-1])

The numerator is the rate at which the model grows equity; the denominator is the
rate at which it grows risk-weighted assets. Their gap is the whole finding, and it
is the part that is genuinely model-implied. Anchoring the level on the reported
ratio means the deduction wedge between book equity and CET1 never has to be
guessed.

Two assumptions are load-bearing and neither is hidden. First, the wedge is held
proportionally constant — true enough over five years for a bank not writing off
goodwill, and wrong in exactly the scenario where it would matter most, a large
impairment. Second, RWA density is held constant unless the caller passes a path,
so RWA grows with AIEA; density drift is a real second-order effect (mix shift
toward mortgages lowers it) and is left to the caller to supply rather than
assumed away silently. Because density appears in both the numerator and
denominator of the RWA growth term, a *constant* density cancels entirely — it
only ever matters when it moves.

The diagnostic is therefore honest about direction and rate of drift, and only
indicative about the level at which a threshold is crossed. That is the right
trade for a warn-only check: the finding is that the ratio falls, and nothing in
the model registers it.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Sequence

# A drift small enough to be rounding rather than a capital problem. Expressed as
# a fraction of RWA, so a quarter of one percentage point over the whole horizon.
_MATERIAL_DRIFT = 0.0025


def _pct(x: float) -> str:
    """Ratio as a percentage string.

    Exists so the percent format spec appears exactly once in this module. The
    SSOT ratchet tokenises every number on a line and is comment-blind, so the
    precision digit inside an inline format spec reads as a bare decimal and
    trips check 3 against whichever register value happens to equal it. Writing
    the spec out even in this docstring trips it, which is why the explanation
    names no digits. One annotated line beats scattering ``ssot-allow`` markers
    through the warning text -- and the marker must sit at the END of its line,
    per the defect of 14 September 2026.
    """
    return f"{x:.2%}"  # ssot-allow: display format, not a domain value


def _bp(x: float) -> str:
    """Drift as a basis-point string."""
    return f"{x:.0f}bp"  # ssot-allow: display format, not a domain value


@dataclass
class Cet1Point:
    """One period of the capital roll-forward."""

    label: str
    opening_book_equity: float
    retained: float
    closing_book_equity: float
    rwa: float
    equity_growth: float
    rwa_growth: float
    cet1_ratio: float


@dataclass
class Cet1Trajectory:
    """The projected CET1 path, the thresholds it was judged against, and warnings."""

    points: List[Cet1Point]
    anchor_ratio: float
    closing_ratio: float
    drift: float                      # closing less anchor, as a fraction of RWA
    floor: float
    operating_target: float
    first_below_target: Optional[str] = None
    first_below_floor: Optional[str] = None
    warnings: List[str] = field(default_factory=list)

    @property
    def drift_bps(self) -> float:
        return self.drift * 10000.0

    @property
    def is_capital_consistent(self) -> bool:
        """True when the payout neither erodes the ratio materially nor breaches."""
        return (
            self.drift >= -_MATERIAL_DRIFT
            and self.first_below_target is None
            and self.first_below_floor is None
        )


def project_cet1(
    *,
    labels: Sequence[str],
    opening_book_equity: float,
    retained_by_period: Sequence[float],
    rwa_by_period: Sequence[float],
    rwa_anchor: float,
    anchor_ratio: float,
    floor: float,
    operating_target: float,
) -> Cet1Trajectory:
    """Roll the reported CET1 ratio forward on the model's own implied growth rates.

    ``rwa_anchor`` is the reported RWA that ``anchor_ratio`` was struck against, so
    the first period's RWA growth is measured from the same balance sheet the ratio
    came from rather than from the first projected period. Getting that wrong would
    silently drop or double-count one period of asset growth, which on these
    magnitudes is worth more than the drift being measured.
    """
    if not (len(labels) == len(retained_by_period) == len(rwa_by_period)):
        raise ValueError(
            "labels, retained_by_period and rwa_by_period must be the same length; got "
            f"{len(labels)}, {len(retained_by_period)}, {len(rwa_by_period)}"
        )
    if rwa_anchor <= 0:
        raise ValueError(f"rwa_anchor must be positive, got {rwa_anchor}")
    if opening_book_equity <= 0:
        raise ValueError(f"opening_book_equity must be positive, got {opening_book_equity}")

    points: List[Cet1Point] = []
    equity = opening_book_equity
    ratio = anchor_ratio
    prev_rwa = rwa_anchor
    first_below_target: Optional[str] = None
    first_below_floor: Optional[str] = None

    for label, retained, rwa in zip(labels, retained_by_period, rwa_by_period):
        opening = equity
        equity_growth = retained / opening
        rwa_growth = (rwa / prev_rwa) - 1.0
        ratio = ratio * (1.0 + equity_growth) / (1.0 + rwa_growth)
        equity = opening + retained

        points.append(Cet1Point(
            label=label,
            opening_book_equity=opening,
            retained=retained,
            closing_book_equity=equity,
            rwa=rwa,
            equity_growth=equity_growth,
            rwa_growth=rwa_growth,
            cet1_ratio=ratio,
        ))

        if ratio < operating_target and first_below_target is None:
            first_below_target = label
        if ratio < floor and first_below_floor is None:
            first_below_floor = label
        prev_rwa = rwa

    closing_ratio = points[-1].cet1_ratio if points else anchor_ratio
    drift = closing_ratio - anchor_ratio

    traj = Cet1Trajectory(
        points=points,
        anchor_ratio=anchor_ratio,
        closing_ratio=closing_ratio,
        drift=drift,
        floor=floor,
        operating_target=operating_target,
        first_below_target=first_below_target,
        first_below_floor=first_below_floor,
    )
    traj.warnings = _warnings_for(traj)
    return traj


def _warnings_for(t: Cet1Trajectory) -> List[str]:
    """Warn on the erosion, then on each threshold, worst last.

    Three separate warnings rather than one, because they are three different
    problems. A ratio that drifts down is a statement about whether the payout is
    consistent with the asset growth in the same model. Crossing the operating
    target is where a board acts. Crossing the regulatory floor is where APRA
    acts, and no board would ever let a projection get there without cutting
    first — so that warning is really saying the payout assumption has stopped
    describing a bank.
    """
    out: List[str] = []

    if t.drift < -_MATERIAL_DRIFT:
        out.append(
            f"CET1 erodes {_bp(abs(t.drift_bps))} over the explicit period, from "
            f"{_pct(t.anchor_ratio)} to {_pct(t.closing_ratio)}: retained earnings are not "
            f"keeping pace with risk-weighted asset growth at the assumed payout. The "
            f"payout is held flat in every period, so nothing in the model responds "
            f"(§15.5, open item 8)."
        )

    if t.first_below_target is not None:
        out.append(
            f"CET1 falls below the {_pct(t.operating_target)} operating target at "
            f"{t.first_below_target}. A board defends its operating target by stopping "
            f"a buyback and then cutting the dividend, which this projection does not "
            f"do — so the dividends being discounted from {t.first_below_target} onward "
            f"are above what the bank would actually pay."
        )

    if t.first_below_floor is not None:
        out.append(
            f"CET1 falls below the {_pct(t.floor)} APRA floor at {t.first_below_floor}. "
            f"A projection that breaches the regulatory minimum while paying an "
            f"unchanged dividend is not describing a bank; the payout assumption has "
            f"stopped being a forecast."
        )

    return out
