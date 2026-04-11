"""
IES visualization routes — powered by ies_analyzer.py (ieSControl engine).
Register in app.py:
    from luxscale.ies_routes import register_ies_routes
    register_ies_routes(app)
"""
from __future__ import annotations
import io, os, base64, uuid
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from flask import Blueprint, request, jsonify
from luxscale.app_logging import log_step, log_exception

ies_viz_bp = Blueprint("ies_viz", __name__)
_IES_SESSIONS: dict = {}

def register_ies_routes(app):
    app.register_blueprint(ies_viz_bp)

def _fig_to_b64(fig, dpi=130):
    buf = io.BytesIO()
    from luxscale.ies_analyzer import DARK_BG
    fig.savefig(buf, format="png", dpi=dpi, facecolor=DARK_BG, bbox_inches="tight")
    buf.seek(0)
    plt.close(fig)
    return base64.b64encode(buf.read()).decode()

@ies_viz_bp.route("/api/ies/load", methods=["POST"])
def api_ies_load():
    from luxscale.ies_analyzer import parse_ies_file, compute_all_metrics
    data = request.get_json(silent=True) or {}
    ies_path = data.get("ies_path", "").strip()
    if not ies_path and data.get("luminaire_name"):
        try:
            from luxscale.ies_fixture_params import resolve_ies_path
            ies_path = resolve_ies_path(data["luminaire_name"], float(data.get("power_w", 0))) or ""
        except Exception as e:
            return jsonify({"status": "error", "message": f"Could not resolve IES path: {e}"}), 400
    if not ies_path or not os.path.isfile(ies_path):
        return jsonify({"status": "error", "message": "IES file not found"}), 404
    try:
        ies = parse_ies_file(ies_path)
        metrics = compute_all_metrics(ies)
    except Exception as e:
        log_exception("api_ies_load", e)
        return jsonify({"status": "error", "message": str(e)}), 422
    sid = str(uuid.uuid4())[:8]
    _IES_SESSIONS[sid] = {"ies": ies, "metrics": metrics, "path": ies_path, "filename": Path(ies_path).name}
    declared_lm = None
    if ies.lumens_per_lamp > 0 and ies.num_lamps > 0:
        declared_lm = ies.lumens_per_lamp * ies.num_lamps * ies.multiplier
    lor = round(metrics.get("total_lumens", 0) / max(declared_lm or 1, 1) * 100, 1) if declared_lm and declared_lm > 0 else None
    log_step("api_ies_load", "loaded", sid=sid, file=Path(ies_path).name)
    return jsonify({"status": "success", "session_id": sid, "filename": Path(ies_path).name,
        "summary": {"peak_candela": ies.max_value, "beam_angle": metrics.get("beam_angle"),
            "field_angle": metrics.get("field_angle"), "total_lumens": metrics.get("total_lumens"),
            "declared_lumens": declared_lm, "lor_pct": lor, "num_lamps": ies.num_lamps,
            "lumens_per_lamp": ies.lumens_per_lamp, "shape": ies.shape,
            "symmetry": ies.symmetry_label(), "vertical_span": ies.vertical_span_label(),
            "num_vertical": ies.num_vertical, "num_horizontal": ies.num_horizontal,
            "per_h": {str(h): {"peak_cd": v["peak"], "beam": v["beam"], "field": v["field"]}
                      for h, v in metrics["per_h"].items()}}})

@ies_viz_bp.route("/api/ies/polar", methods=["GET"])
def api_ies_polar():
    sid = request.args.get("sid", "")
    if sid not in _IES_SESSIONS:
        return jsonify({"status": "error", "message": "Session not found. Call /api/ies/load first."}), 404
    sess = _IES_SESSIONS[sid]
    from luxscale.ies_analyzer import plot_polar
    h_idx = int(request.args.get("h_idx", 0))
    scale = request.args.get("scale", "linear")
    show_beam = request.args.get("show_beam", "true") == "true"
    try:
        fig = plot_polar(sess["ies"], sess["metrics"], h_idx=h_idx, scale=scale, show_beam=show_beam)
        return jsonify({"status": "success", "image": _fig_to_b64(fig)})
    except Exception as e:
        log_exception("api_ies_polar", e)
        return jsonify({"status": "error", "message": str(e)}), 500

@ies_viz_bp.route("/api/ies/panorama", methods=["GET"])
def api_ies_panorama():
    import numpy as _np, math as _math
    from PIL import Image as _PILImage
    sid = request.args.get("sid", "")
    if sid not in _IES_SESSIONS:
        return jsonify({"status": "error", "message": "Session not found. Call /api/ies/load first."}), 404
    ies = _IES_SESSIONS[sid]["ies"]
    W=min(int(request.args.get("w",1024)),2048); PH=min(int(request.args.get("h",512)),1024)
    room_h=float(request.args.get("room_h",3.0)); room_sz=float(request.args.get("room_sz",6.0))
    intensity=float(request.args.get("intensity",1.0)); ct=request.args.get("ct","warm")
    try:
        va=_np.array(ies.vertical_angles,dtype=_np.float64); ha=_np.array(ies.horizontal_angles,dtype=_np.float64)
        mat=_np.array([ies.candela_values[h] for h in ies.horizontal_angles],dtype=_np.float64)
        nH,nV=mat.shape; max_ha=float(ha[-1])
        def lookup(v_flat,h_flat):
            v=_np.clip(v_flat.ravel(),va[0],va[-1])
            h=(_np.fmod(_np.fmod(h_flat.ravel(),360.0)+360.0,360.0))
            if max_ha<=90.5:
                h=_np.where(h>270.0,360.0-h,h); h=_np.where(h>180.0,h-180.0,h); h=_np.where(h>90.0,180.0-h,h)
            elif max_ha<=180.5: h=_np.where(h>180.0,360.0-h,h)
            h=_np.zeros_like(h) if nH==1 else _np.clip(h,ha[0],ha[-1])
            with _np.errstate(divide='ignore',invalid='ignore'):
                hi=_np.clip(_np.searchsorted(ha,h,'right')-1,0,nH-2); dha=_np.where(ha[hi+1]>ha[hi],ha[hi+1]-ha[hi],1.0)
                ht=_np.clip((h-ha[hi])/dha,0.0,1.0); vi=_np.clip(_np.searchsorted(va,v,'right')-1,0,nV-2)
                dva=_np.where(va[vi+1]>va[vi],va[vi+1]-va[vi],1.0); vt=_np.clip((v-va[vi])/dva,0.0,1.0)
            hi1=_np.minimum(hi+1,nH-1); vi1=_np.minimum(vi+1,nV-1)
            return ((mat[hi,vi]*(1-vt)+mat[hi,vi1]*vt)*(1-ht)+(mat[hi1,vi]*(1-vt)+mat[hi1,vi1]*vt)*ht)*intensity
        cam_y=1.2; fix_y=float(room_h); ceil_y=fix_y+0.5; s=float(room_sz); INF=1e30
        lon=(_np.arange(W,dtype=_np.float64)/W-0.5)*2.0*_math.pi
        lat=(0.5-_np.arange(PH,dtype=_np.float64)/PH)*_math.pi
        LON,LAT=_np.meshgrid(lon,lat)
        RX=_np.cos(LAT)*_np.sin(LON); RY=_np.sin(LAT); RZ=_np.cos(LAT)*_np.cos(LON)
        t_hit=_np.full((PH,W),INF,dtype=_np.float64)
        NX=_np.zeros((PH,W),dtype=_np.float64); NY=_np.zeros((PH,W),dtype=_np.float64); NZ=_np.zeros((PH,W),dtype=_np.float64)
        def hit_plane(Rcomp,O_val,p_val,nx,ny,nz,bounds_fn):
            with _np.errstate(divide='ignore',invalid='ignore'):
                t=_np.where(_np.abs(Rcomp)>1e-9,(p_val-O_val)/Rcomp,INF)
            t=_np.where(t>1e-4,t,INF); hx=RX*t; hy=cam_y+RY*t; hz=RZ*t; t=_np.where(bounds_fn(hx,hy,hz),t,INF)
            upd=t<t_hit; _np.copyto(t_hit,t,where=upd); _np.copyto(NX,nx,where=upd); _np.copyto(NY,ny,where=upd); _np.copyto(NZ,nz,where=upd)
        hit_plane(RY,cam_y,0.0,0,1,0,lambda hx,hy,hz:(_np.abs(hx)<=s)&(_np.abs(hz)<=s))
        hit_plane(RY,cam_y,ceil_y,0,-1,0,lambda hx,hy,hz:(_np.abs(hx)<=s)&(_np.abs(hz)<=s))
        hit_plane(RX,0.0,-s,1,0,0,lambda hx,hy,hz:(hy>=0)&(hy<=ceil_y)&(_np.abs(hz)<=s))
        hit_plane(RX,0.0,s,-1,0,0,lambda hx,hy,hz:(hy>=0)&(hy<=ceil_y)&(_np.abs(hz)<=s))
        hit_plane(RZ,0.0,-s,0,0,1,lambda hx,hy,hz:(hy>=0)&(hy<=ceil_y)&(_np.abs(hx)<=s))
        hit_plane(RZ,0.0,s,0,0,-1,lambda hx,hy,hz:(hy>=0)&(hy<=ceil_y)&(_np.abs(hx)<=s))
        missed=t_hit>=INF*0.5; t_safe=_np.where(missed,1.0,t_hit)
        HX=RX*t_safe; HY=cam_y+RY*t_safe; HZ=RZ*t_safe
        DX=HX; DY=HY-fix_y; DZ=HZ; D2=DX*DX+DY*DY+DZ*DZ; D=_np.sqrt(D2)+1e-6
        V_ANG=_np.degrees(_np.arccos(_np.clip(-DY/D,-1.0,1.0))); H_ANG=(_np.degrees(_np.arctan2(DZ,DX))+360.0)%360.0
        CD=lookup(V_ANG,H_ANG).reshape(PH,W); COS=_np.maximum(0.0,-(DX*NX+DY*NY+DZ*NZ)/D)
        LUX=CD*COS/(D2+1e-9); REFL=_np.where(NY>0.5,0.40,_np.where(NY<-0.5,0.85,0.72))
        RAD=_np.where(missed,0.0,LUX*REFL)
        valid=RAD[~missed]; p99=float(_np.percentile(valid,99)) if valid.size>0 else 1.0; p99=max(p99,1e-4)
        T=_np.log1p(RAD/p99*10.0)/_math.log1p(10.0); T=_np.clip(T**0.68,0.0,1.0)
        CT={"warm":(1.00,0.84,0.54),"neutral":(1.00,0.96,0.82),"cool":(0.82,0.92,1.00)}
        r,g,b=CT.get(ct,CT["warm"])
        img8=(_np.stack([_np.clip(T*r+0.012,0,1),_np.clip(T*g+0.012,0,1),_np.clip(T*b+0.012,0,1)],axis=-1)*255).astype(_np.uint8)
        pil=_PILImage.fromarray(img8,"RGB"); buf=io.BytesIO(); pil.save(buf,"PNG",optimize=True); buf.seek(0)
        return jsonify({"status":"success","image":base64.b64encode(buf.read()).decode(),"width":W,"height":PH})
    except Exception as e:
        log_exception("api_ies_panorama",e)
        return jsonify({"status":"error","message":str(e)}),500

@ies_viz_bp.route("/api/ies/plots/all", methods=["GET"])
def api_ies_all_plots():
    sid = request.args.get("sid","")
    if sid not in _IES_SESSIONS:
        return jsonify({"status":"error","message":"Session not found"}),404
    sess=_IES_SESSIONS[sid]
    from luxscale.ies_analyzer import plot_polar,plot_candela_profile,plot_heatmap,plot_beam_bar,plot_flux_curve
    ies=sess["ies"]; m=sess["metrics"]
    try:
        return jsonify({"status":"success",
            "polar":   _fig_to_b64(plot_polar(ies,m,scale="linear")),
            "candela": _fig_to_b64(plot_candela_profile(ies,m)),
            "heatmap": _fig_to_b64(plot_heatmap(ies)),
            "beam_bar":_fig_to_b64(plot_beam_bar(ies,m)),
            "flux":    _fig_to_b64(plot_flux_curve(ies))})
    except Exception as e:
        log_exception("api_ies_all_plots",e)
        return jsonify({"status":"error","message":str(e)}),500
