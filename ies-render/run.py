import logging
import os
import sys

from module import IES_Thumbnail_Generator

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

try:
    from luxscale.ies_fixture_params import approx_beam_angle_deg
except ImportError:
    approx_beam_angle_deg = None  # type: ignore[misc, assignment]


if __name__ == "__main__":
    ies_paths = [
        "examples/vertical_angles.ies",
        "examples/horiz_angles.ies",
        "examples/ies-lights-pack/area-light.ies",
        "examples/SC-ies/SC STREET 50W/SL250SI5KN01_75x150deg_50W.IES"
    ]
    tb = IES_Thumbnail_Generator(ies_paths[2])
    if tb.ies_data and approx_beam_angle_deg:
        ba = approx_beam_angle_deg(tb.ies_data)
        logging.info(
            "Beam angle (FWHM 50%, narrowest across H planes; same as LuxScale / result UI): "
            + (f"{ba:.2f} deg" if ba is not None else "n/a")
        )
    elif tb.ies_data and not approx_beam_angle_deg:
        logging.info(
            "Beam angle: run from repo root so `luxscale` is importable, or use ies.json derived.beam_angle_deg_half_power_vertical_slice."
        )
    # tb.generate(size=1024, horizontal_angle=0, distance=0.3, blur_radius=0.5, save=True)
    tb.render(size=1024, horizontal_angle=0, distance=0.0, blur_radius=0, save=True)
