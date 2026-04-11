"""
Classify LM-63 photometric angle grids (vertical / horizontal spans).

Many Type C floods ship with horizontal angles only 0°…90° (one quadrant); the rest of the
azimuth is implied by symmetry — this is valid, not a corrupt “half file”. Other files use
only 0°…90° vertical (lower hemisphere) or 90°…180° (upper). This module exposes those cases
for UI and QA without changing rendering math.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional


def _near(a: float, b: float, eps: float = 1.0) -> bool:
    return abs(float(a) - float(b)) < eps


@dataclass(frozen=True)
class PhotometryCoverage:
    """Angle-span summary for one parsed ``IESData``."""

    vertical_deg: tuple[float, float]
    horizontal_deg: tuple[float, float]
    vertical_kind: str
    horizontal_kind: str
    is_vertical_partial_hemisphere: bool
    is_horizontal_partial_azimuth: bool
    summary: str


def describe_photometry_coverage(ies_data: Any) -> Optional[PhotometryCoverage]:
    """
    Inspect ``vertical_angles`` / ``horizontal_angles`` and return a stable classification.

    ``is_vertical_partial_hemisphere`` is True when only 0–90° or only 90–180° vertical
    (half of the 0–180° Type C vertical range), not when V is −90…+90° (full vertical slice).

    ``is_horizontal_partial_azimuth`` is True when horizontal span is well under 360°
    (e.g. 0–90° quadrant photometry).
    """
    if ies_data is None:
        return None
    va = getattr(ies_data, "vertical_angles", None) or []
    ha = getattr(ies_data, "horizontal_angles", None) or []
    if len(va) < 2 or len(ha) < 1:
        return None

    v0, v1 = float(va[0]), float(va[-1])
    h0 = float(ha[0])
    h1 = float(ha[-1]) if len(ha) > 1 else h0
    h_span = h1 - h0

    # --- Vertical classification
    if _near(v0, 0) and _near(v1, 180):
        vk = "V 0..180 deg (both hemispheres along vertical grid)"
        v_partial = False
    elif _near(v0, 0) and _near(v1, 90):
        vk = "V 0..90 deg (lower hemisphere only)"
        v_partial = True
    elif _near(v0, 90) and _near(v1, 180):
        vk = "V 90..180 deg (upper hemisphere only)"
        v_partial = True
    elif _near(v0, -90) and _near(v1, 90):
        vk = "V -90...+90 deg (symmetric vertical grid)"
        v_partial = False
    else:
        vk = f"V {v0:g}..{v1:g} deg (non-standard span)"
        v_partial = not (abs(v1 - v0) >= 170)

    # --- Horizontal classification (Type C azimuth in file)
    if len(ha) < 2:
        hk = f"H single slice ({h0:g} deg)"
        h_partial = True
    elif len(ha) >= 2 and (h_span >= 350 or (_near(h0, -180) and _near(h1, 180))):
        hk = "H full azimuth (~360 deg)"
        h_partial = False
    elif _near(h0, 0) and _near(h1, 180):
        hk = "H 0..180 deg (half azimuth)"
        h_partial = True
    elif _near(h0, 0) and _near(h1, 90):
        hk = "H 0..90 deg (single quadrant)"
        h_partial = True
    elif _near(h0, -90) and _near(h1, 90):
        hk = "H -90..+90 deg"
        h_partial = True
    else:
        hk = f"H {h0:g}..{h1:g} deg"
        h_partial = h_span < 300

    parts = [vk, hk]
    if h_partial:
        parts.append(
            "Partial azimuth in file: common for Type C (mirror symmetry assumed beyond listed angles)."
        )
    if v_partial:
        parts.append(
            "Partial vertical range: intensity exists only in one 90 deg vertical band of the 0-180 deg space."
        )

    summary = " | ".join(parts)
    return PhotometryCoverage(
        vertical_deg=(v0, v1),
        horizontal_deg=(h0, h1),
        vertical_kind=vk,
        horizontal_kind=hk,
        is_vertical_partial_hemisphere=v_partial,
        is_horizontal_partial_azimuth=h_partial,
        summary=summary,
    )


def is_likely_quadrant_horizontal_photometry(ies_data: Any) -> bool:
    """True when horizontal angles are ~0°…90° only (your SC flood case)."""
    c = describe_photometry_coverage(ies_data)
    if c is None:
        return False
    return c.is_horizontal_partial_azimuth and _near(c.horizontal_deg[0], 0) and _near(
        c.horizontal_deg[1], 90
    )
