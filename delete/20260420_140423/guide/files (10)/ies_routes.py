"""
ies_routes.py  ·  LuxScale IES integration
==========================================
Drop this file into your luxscale/ folder (next to app.py / main.py).
Register with:
    from ies_routes import ies_bp
    app.register_blueprint(ies_bp)

Depends on ies_analyzer.py being in the same folder.
Requires: Flask, numpy, matplotlib, scipy, Pillow
"""

import io
import base64
import uuid
import math as _math
import os
from pathlib import Path
from flask import Blueprint, request, jsonify, abort

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as _np
from PIL import Image as _PILImage

from ies_analyzer import (
    parse_ies, parse_ies_file, compute_all_metrics,
    compute_beam_angle, plot_polar, plot_3d_surface,
    DARK_BG, DEMO_IES,
)

ies_bp = Blueprint("ies", __name__, url_prefix="/ies")

# ── In-memory session store keyed by session_id ───────────────────────────────
_sessions: dict = {}

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _fig_to_b64(fig, dpi=130) -> str:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=dpi, facecolor=DARK_BG, bbox_inches="tight")
    buf.seek(0)
    plt.close(fig)
    return base64.b64encode(buf.read()).decode()


def _sess(sid: str) -> dict:
    if sid not in _sessions:
        abort(404, description="IES session not found. Please upload a file first.")
    return _sessions[sid]


def _customer_summary(ies, metrics: dict) -> dict:
    """
    Returns ONLY the values a customer / installer needs.
    No internal photometry jargon — plain labels, rounded values.
    """
    beam  = metrics.get("beam_angle")
    field = metrics.get("field_angle")
    lm    = metrics.get("total_lumens")

    # Declared output from IES header
    declared_lm = None
    if ies.lumens_per_lamp > 0 and ies.num_lamps > 0:
        declared_lm = ies.lumens_per_lamp * ies.num_lamps * ies.multiplier

    # Pick the "best" lumen value to show the customer:
    # prefer the integrated (measured) value; fall back to declared.
    display_lm = lm if (lm and lm > 0) else declared_lm

    return {
        # ── What customers care about ─────────────────────────────────
        "total_lumens":   round(display_lm)  if display_lm  else None,
        "beam_angle_deg": round(beam, 1)      if beam        else None,
        "field_angle_deg":round(field, 1)     if field       else None,
        "peak_candela":   round(ies.max_value) if ies.max_value else None,

        # ── Extra context (shown in collapsed "Tech" section) ─────────
        "declared_lumens": round(declared_lm) if declared_lm else None,
        "lor_pct": round(
            min(lm / max(declared_lm, 1) * 100, 999), 1
        ) if (lm and declared_lm and declared_lm > 0) else None,
        "symmetry":  ies.symmetry_label(),
        "shape":     ies.shape,

        # ── Passed back so JS can pre-fill the panorama sliders ───────
        "fixture_width_m":  round(ies.width,  4),
        "fixture_length_m": round(ies.length, 4),
        "fixture_height_m": round(ies.height, 4),

        # ── Raw for the polar / 3-D tab ───────────────────────────────
        "horizontal_angles": ies.horizontal_angles,
        "num_vertical":  ies.num_vertical,
        "num_horizontal": ies.num_horizontal,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Upload
# ─────────────────────────────────────────────────────────────────────────────

@ies_bp.route("/upload", methods=["POST"])
def upload():
    """
    POST multipart/form-data  with field "file" (IES file)
    OR   form field "demo"=1  to load the built-in demo.

    Returns JSON:
        { session_id, filename, customer: {...}, ies_data: {...} }
    """
    if "demo" in request.form:
        sid  = str(uuid.uuid4())[:8]
        path = os.path.join(UPLOAD_DIR, f"{sid}_demo.ies")
        with open(path, "w") as f:
            f.write(DEMO_IES)
        ies     = parse_ies(DEMO_IES)
        metrics = compute_all_metrics(ies)
        _sessions[sid] = {"ies": ies, "metrics": metrics,
                          "path": path, "filename": "demo.ies"}
        return jsonify(_response(sid, "demo.ies", ies, metrics))

    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    f = request.files["file"]
    if not f.filename.lower().endswith(".ies"):
        return jsonify({"error": "Only .ies files are accepted"}), 400

    sid       = str(uuid.uuid4())[:8]
    safe_name = f"{sid}_{Path(f.filename).name}"
    path      = os.path.join(UPLOAD_DIR, safe_name)
    f.save(path)

    try:
        ies = parse_ies_file(path)
    except Exception as e:
        os.remove(path)
        return jsonify({"error": str(e)}), 422

    metrics = compute_all_metrics(ies)
    _sessions[sid] = {"ies": ies, "metrics": metrics,
                      "path": path, "filename": f.filename}
    return jsonify(_response(sid, f.filename, ies, metrics))


def _response(sid, filename, ies, metrics):
    return {
        "session_id": sid,
        "filename":   filename,
        "customer":   _customer_summary(ies, metrics),
        "ies_data": {
            "vertical_angles":   ies.vertical_angles,
            "horizontal_angles": ies.horizontal_angles,
            "candela_matrix":    [ies.candela_values[h] for h in ies.horizontal_angles],
            "max_value":         ies.max_value,
            "symmetry":          ies.symmetry_label(),
            "beam_angle":        metrics.get("beam_angle"),
            "field_angle":       metrics.get("field_angle"),
        },
    }


# ─────────────────────────────────────────────────────────────────────────────
# Polar plot  (used for the "Polar Curve" button in the product modal)
# ─────────────────────────────────────────────────────────────────────────────

@ies_bp.route("/plot/polar")
def plot_polar_endpoint():
    """
    GET /ies/plot/polar?sid=<id>&h_idx=0&scale=linear&show_beam=true
    Returns { image: "<base64 PNG>" }
    """
    sid      = request.args.get("sid", "")
    sess     = _sess(sid)
    h_idx    = int(request.args.get("h_idx", 0))
    scale    = request.args.get("scale", "linear")
    show_beam = request.args.get("show_beam", "true") == "true"

    fig = plot_polar(sess["ies"], sess["metrics"],
                     h_idx=h_idx, scale=scale, show_beam=show_beam)
    return jsonify({"image": _fig_to_b64(fig)})


# ─────────────────────────────────────────────────────────────────────────────
# 3-D candela surface  (Three.js raw data endpoint)
# ─────────────────────────────────────────────────────────────────────────────

@ies_bp.route("/ies_data")
def ies_data():
    """
    GET /ies/ies_data?sid=<id>
    Returns full candela matrix for the Three.js 3-D viewer.
    """
    sid     = request.args.get("sid", "")
    sess    = _sess(sid)
    ies     = sess["ies"]
    metrics = sess["metrics"]
    return jsonify({
        "vertical_angles":   ies.vertical_angles,
        "horizontal_angles": ies.horizontal_angles,
        "candela_matrix":    [ies.candela_values[h] for h in ies.horizontal_angles],
        "max_value":         ies.max_value,
        "beam_angle":        metrics.get("beam_angle"),
        "field_angle":       metrics.get("field_angle"),
        "peak_candela":      ies.max_value,
        "symmetry":          ies.symmetry_label(),
    })


# ─────────────────────────────────────────────────────────────────────────────
# Panorama  (360° light simulation — uses place dimensions from POST body)
# ─────────────────────────────────────────────────────────────────────────────

@ies_bp.route("/panorama", methods=["GET", "POST"])
def panorama():
    """
    GET  /ies/panorama?sid=<id>&room_w=<m>&room_l=<m>&room_h=<m>&...
    POST /ies/panorama  { sid, room_w, room_l, room_h, ... }

    room_w, room_l, room_h  → come from the place/project data in LuxScale
    fixture_h               → mounting height of the luminaire
    intensity               → 0.0–2.0  (default 1.0)
    ct                      → warm | neutral | cool
    w, h                    → panorama resolution (default 1024×512)

    Returns { image: "<base64 PNG>", width, height }
    """
    if request.method == "POST":
        args = request.get_json(force=True) or {}
        g = args.get
    else:
        g = request.args.get

    sid       = g("sid", "")
    sess      = _sess(sid)
    ies       = sess["ies"]

    # ── Room / space dimensions from LuxScale place data ─────────────────────
    #    LuxScale passes: room_w (width m), room_l (length m), room_h (ceiling m)
    #    We also accept the legacy single "room_sz" for square rooms.
    room_w    = float(g("room_w",    g("room_sz", 6.0)))
    room_l    = float(g("room_l",    g("room_sz", 6.0)))
    room_h    = float(g("room_h",    3.0))

    # ── Luminaire mounting height (defaults to 80 % of ceiling height) ────────
    fixture_h = float(g("fixture_h", room_h * 0.80))
    fixture_h = min(fixture_h, room_h - 0.05)   # never above ceiling

    intensity = float(g("intensity", 1.0))
    ct        = g("ct", "warm")
    W         = int(g("w",  1024))
    PH        = int(g("h",  512))

    # ── Build candela lookup arrays ───────────────────────────────────────────
    va  = _np.array(ies.vertical_angles,   dtype=_np.float64)
    ha  = _np.array(ies.horizontal_angles, dtype=_np.float64)
    mat = _np.array([ies.candela_values[h] for h in ies.horizontal_angles],
                    dtype=_np.float64)   # (nH, nV)
    nH, nV = mat.shape
    max_ha = float(ha[-1])

    def lookup(v_flat, h_flat):
        v = _np.clip(v_flat.ravel(), va[0], va[-1])
        h = (_np.fmod(_np.fmod(h_flat.ravel(), 360.0) + 360.0, 360.0))
        if max_ha <= 90.5:
            h = _np.where(h > 270.0, 360.0 - h, h)
            h = _np.where(h > 180.0, h - 180.0,  h)
            h = _np.where(h >  90.0, 180.0 - h,  h)
        elif max_ha <= 180.5:
            h = _np.where(h > 180.0, 360.0 - h, h)
        h = _np.zeros_like(h) if nH == 1 else _np.clip(h, ha[0], ha[-1])
        with _np.errstate(divide="ignore", invalid="ignore"):
            hi  = _np.clip(_np.searchsorted(ha, h, "right") - 1, 0, nH - 2)
            dha = _np.where(ha[hi+1] > ha[hi], ha[hi+1] - ha[hi], 1.0)
            ht  = _np.clip((h - ha[hi]) / dha, 0.0, 1.0)
            vi  = _np.clip(_np.searchsorted(va, v, "right") - 1, 0, nV - 2)
            dva = _np.where(va[vi+1] > va[vi], va[vi+1] - va[vi], 1.0)
            vt  = _np.clip((v - va[vi]) / dva, 0.0, 1.0)
        hi1 = _np.minimum(hi + 1, nH - 1)
        vi1 = _np.minimum(vi + 1, nV - 1)
        c   = (  mat[hi,  vi ] * (1-vt) + mat[hi,  vi1] * vt) * (1-ht) \
            + (  mat[hi1, vi ] * (1-vt) + mat[hi1, vi1] * vt) * ht
        return c * intensity

    # ── Ray grid  (equirectangular) ───────────────────────────────────────────
    cam_y  = 1.2                    # eye level (m)
    ceil_y = room_h
    sx     = room_w / 2.0           # half-width  (X axis)
    sz     = room_l / 2.0           # half-length (Z axis)
    INF    = 1e30

    lon = (_np.arange(W,  dtype=_np.float64) / W  - 0.5) * 2.0 * _math.pi
    lat = (0.5 - _np.arange(PH, dtype=_np.float64) / PH) * _math.pi
    LON, LAT = _np.meshgrid(lon, lat)
    RX = _np.cos(LAT) * _np.sin(LON)
    RY = _np.sin(LAT)
    RZ = _np.cos(LAT) * _np.cos(LON)

    # ── Ray → box intersection ────────────────────────────────────────────────
    t_hit = _np.full((PH, W), INF, dtype=_np.float64)
    NX    = _np.zeros((PH, W), dtype=_np.float64)
    NY    = _np.zeros((PH, W), dtype=_np.float64)
    NZ    = _np.zeros((PH, W), dtype=_np.float64)

    def hit_plane(Rcomp, O_val, p_val, nx, ny, nz, bounds_fn):
        with _np.errstate(divide="ignore", invalid="ignore"):
            t = _np.where(_np.abs(Rcomp) > 1e-9, (p_val - O_val) / Rcomp, INF)
        t = _np.where(t > 1e-4, t, INF)
        hx = RX * t
        hy = cam_y + RY * t
        hz = RZ * t
        t  = _np.where(bounds_fn(hx, hy, hz), t, INF)
        upd = t < t_hit
        _np.copyto(t_hit, t,  where=upd)
        _np.copyto(NX,    nx, where=upd)
        _np.copyto(NY,    ny, where=upd)
        _np.copyto(NZ,    nz, where=upd)

    hit_plane(RY, cam_y, 0.0,   0,  1, 0,
              lambda hx,hy,hz: (_np.abs(hx)<=sx) & (_np.abs(hz)<=sz))   # floor
    hit_plane(RY, cam_y, ceil_y, 0, -1, 0,
              lambda hx,hy,hz: (_np.abs(hx)<=sx) & (_np.abs(hz)<=sz))   # ceiling
    hit_plane(RX, 0.0, -sx,  1, 0, 0,
              lambda hx,hy,hz: (hy>=0)&(hy<=ceil_y)&(_np.abs(hz)<=sz))  # wall -X
    hit_plane(RX, 0.0,  sx, -1, 0, 0,
              lambda hx,hy,hz: (hy>=0)&(hy<=ceil_y)&(_np.abs(hz)<=sz))  # wall +X
    hit_plane(RZ, 0.0, -sz,  0, 0,  1,
              lambda hx,hy,hz: (hy>=0)&(hy<=ceil_y)&(_np.abs(hx)<=sx))  # wall -Z
    hit_plane(RZ, 0.0,  sz,  0, 0, -1,
              lambda hx,hy,hz: (hy>=0)&(hy<=ceil_y)&(_np.abs(hx)<=sx))  # wall +Z

    # ── Illuminance ───────────────────────────────────────────────────────────
    missed = t_hit >= INF * 0.5
    t_safe = _np.where(missed, 1.0, t_hit)
    HX  = RX * t_safe
    HY  = cam_y + RY * t_safe
    HZ  = RZ * t_safe
    DX  = HX
    DY  = HY - fixture_h
    DZ  = HZ
    D2  = DX*DX + DY*DY + DZ*DZ
    D   = _np.sqrt(D2) + 1e-6
    V_ANG = _np.degrees(_np.arccos(_np.clip(-DY / D, -1.0, 1.0)))
    H_ANG = (_np.degrees(_np.arctan2(DZ, DX)) + 360.0) % 360.0
    CD  = lookup(V_ANG, H_ANG).reshape(PH, W)
    COS = _np.maximum(0.0, -(DX*NX + DY*NY + DZ*NZ) / D)
    LUX = CD * COS / (D2 + 1e-9)
    REFL = _np.where(NY > 0.5, 0.40,
           _np.where(NY < -0.5, 0.85, 0.72))
    RAD  = LUX * REFL
    RAD  = _np.where(missed, 0.0, RAD)

    # ── Tone mapping ──────────────────────────────────────────────────────────
    valid = RAD[~missed]
    p99   = float(_np.percentile(valid, 99)) if valid.size > 0 else 1.0
    p99   = max(p99, 1e-4)
    T     = _np.log1p(RAD / p99 * 10.0) / _math.log1p(10.0)
    T     = _np.clip(T ** 0.68, 0.0, 1.0)

    CT = {"warm":    (1.00, 0.84, 0.54),
          "neutral": (1.00, 0.96, 0.82),
          "cool":    (0.82, 0.92, 1.00)}
    r, g, b = CT.get(ct, CT["warm"])

    img8 = (_np.stack([
        _np.clip(T * r + 0.012, 0, 1),
        _np.clip(T * g + 0.012, 0, 1),
        _np.clip(T * b + 0.012, 0, 1),
    ], axis=-1) * 255).astype(_np.uint8)

    pil = _PILImage.fromarray(img8, "RGB")
    buf = io.BytesIO()
    pil.save(buf, "PNG", optimize=True)
    buf.seek(0)
    return jsonify({
        "image":  base64.b64encode(buf.read()).decode(),
        "width":  W,
        "height": PH,
    })
