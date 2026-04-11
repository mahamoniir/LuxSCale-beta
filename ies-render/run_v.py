import os
import subprocess
import sys

# Default `py` may be 3.14 while some deps were installed only for 3.13 (or vice versa).
# IES_Viewer needs qtpy + scipy (+ Pillow via ies_gen).
def _viewer_deps_available() -> bool:
    try:
        import qtpy  # noqa: F401
        import scipy  # noqa: F401
        from PIL import Image  # noqa: F401
    except ModuleNotFoundError:
        return False
    return True


if os.environ.get("LUXSCALE_IES_RENDER_V_SUBPROC") != "1":
    if not _viewer_deps_available():
        if sys.platform == "win32":
            env = os.environ.copy()
            env["LUXSCALE_IES_RENDER_V_SUBPROC"] = "1"
            exe = os.path.abspath(__file__)
            try:
                r = subprocess.run(
                    ["py", "-3.13", exe, *sys.argv[1:]],
                    env=env,
                )
            except FileNotFoundError:
                sys.stderr.write(
                    "Missing dependencies for this Python (need qtpy, scipy, Pillow).\n"
                    "Install for the interpreter you use:\n"
                    "  py -m pip install qtpy PySide6 scipy Pillow\n"
                    "Or run: py -3.13 run_v.py\n"
                )
                raise SystemExit(1) from None
            raise SystemExit(r.returncode)
        import qtpy  # noqa: F401
        import scipy  # noqa: F401
        from PIL import Image  # noqa: F401

from qtpy.QtWidgets import QApplication
from module import IES_Viewer

if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = IES_Viewer()
    viewer.show()
    sys.exit(app.exec_())
