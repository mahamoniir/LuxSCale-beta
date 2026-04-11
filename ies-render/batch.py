import os, sys, glob, time

IES_DIR = os.path.join("examples", "SC_FIXED")
OUT_DIR = os.path.join(IES_DIR, "results")
LOG     = os.path.join(OUT_DIR, "ALL_RESULTS.txt")

os.makedirs(OUT_DIR, exist_ok=True)

REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from module import IES_Thumbnail_Generator

try:
    from luxscale.ies_fixture_params import approx_beam_angle_deg
except ImportError:
    approx_beam_angle_deg = None


def process_ies(ies_path):
    result = {"file": os.path.basename(ies_path), "path": ies_path}
    t0 = time.time()

    try:
        tb = IES_Thumbnail_Generator(ies_path)
    except Exception as e:
        result["error"] = f"load failed: {e}"
        return result

    d = tb.ies_data
    if not d:
        result["error"] = "ies_data is None"
        return result

    # -- known attributes from IESData --
    result["shape"]      = getattr(d, "shape",         "n/a")
    result["width_m"]    = getattr(d, "width",         "n/a")
    result["length_m"]   = getattr(d, "length",        "n/a")
    result["height_m"]   = getattr(d, "height",        "n/a")
    result["lumens"]     = getattr(d, "lumens_per_lamp","n/a")
    result["num_lamps"]  = getattr(d, "num_lamps",     "n/a")
    result["multiplier"] = getattr(d, "multiplier",    "n/a")
    result["max_value"]  = getattr(d, "max_value",     "n/a")

    v = getattr(d, "vertical_angles",   None)
    h = getattr(d, "horizontal_angles", None)
    result["vert"]  = f"{v[0]}-{v[-1]} deg ({len(v)} values)" if v else "n/a"
    result["horiz"] = f"{h[0]}-{h[-1]} deg ({len(h)} values)" if h else "n/a"

    # candela_values is a dict: {angle_key: [list of floats per vertical angle]}
    cd = getattr(d, "candela_values", None)
    if cd and isinstance(cd, dict):
        all_vals = [val for row in cd.values() for val in row]
        result["peak_cd"] = f"{max(all_vals):.1f} cd"
        result["min_cd"]  = f"{min(all_vals):.1f} cd"
        first_key = list(cd.keys())[0]
        last_key  = list(cd.keys())[-1]
        result["candela_first_row"] = f"angle {first_key}: {cd[first_key][:5]}..."
        result["candela_last_row"]  = f"angle {last_key}: {cd[last_key][:5]}..."
        result["num_horiz_planes"]  = len(cd)
        result["num_vert_per_plane"]= len(cd[first_key])
    else:
        result["peak_cd"] = "n/a"
        result["min_cd"]  = "n/a"

    # beam angle
    if approx_beam_angle_deg:
        try:
            ba = approx_beam_angle_deg(d)
            result["beam_angle"] = f"{ba:.2f} deg" if ba is not None else "n/a"
        except Exception as e:
            result["beam_angle"] = f"error: {e}"
    else:
        result["beam_angle"] = "n/a (luxscale not importable)"

    # render
    img_name = os.path.splitext(os.path.basename(ies_path))[0] + "_render.png"
    img_path = os.path.join(OUT_DIR, img_name)
    try:
        tb.render(size=512, horizontal_angle=0, distance=0.0,
                  blur_radius=0, save=True, out_path=img_path)
        result["render"] = f"OK -> {img_path}"
    except Exception:
        try:
            tb.render(size=512, horizontal_angle=0, distance=0.0,
                      blur_radius=0, save=True)
            result["render"] = "OK (default path)"
        except Exception as e2:
            result["render"] = f"FAILED: {e2}"

    result["elapsed"] = f"{time.time()-t0:.2f}s"
    return result


def fmt(r):
    lines = ["=" * 60,
             f"FILE : {r['file']}",
             f"PATH : {r['path']}",
             "-" * 60]
    if "error" in r:
        lines.append(f"  ERROR: {r['error']}")
    else:
        for k, label in [
            ("shape",             "Shape            "),
            ("width_m",           "Width m          "),
            ("length_m",          "Length m         "),
            ("height_m",          "Height m         "),
            ("vert",              "Vert angles      "),
            ("horiz",             "Horiz angles     "),
            ("num_horiz_planes",  "Horiz planes     "),
            ("num_vert_per_plane","Vert per plane   "),
            ("peak_cd",           "Peak candela     "),
            ("min_cd",            "Min candela      "),
            ("max_value",         "max_value attr   "),
            ("beam_angle",        "Beam angle FWHM  "),
            ("lumens",            "Lumens/lamp      "),
            ("num_lamps",         "Num lamps        "),
            ("multiplier",        "Multiplier       "),
            ("candela_first_row", "Candela[0]       "),
            ("candela_last_row",  "Candela[-1]      "),
            ("render",            "Render           "),
            ("elapsed",           "Time             "),
        ]:
            lines.append(f"  {label}: {r.get(k, 'n/a')}")
    lines.append("")
    return "\n".join(lines)


ies_files = sorted(glob.glob(os.path.join(IES_DIR, "*.IES")) +
                   glob.glob(os.path.join(IES_DIR, "*.ies")))

if not ies_files:
    print(f"No .IES files in {IES_DIR}")
    sys.exit(1)

print(f"Found {len(ies_files)} files.\n")

out = [f"IES Batch Results - {time.strftime('%Y-%m-%d %H:%M:%S')}",
       f"Total files: {len(ies_files)}", ""]

ok = fail = 0
for f in ies_files:
    print(f"  Processing: {os.path.basename(f)}")
    r = process_ies(f)
    block = fmt(r)
    out.append(block)
    if "error" in r:
        fail += 1
    else:
        ok += 1

out.append("=" * 60)
out.append(f"DONE: {ok} OK, {fail} failed")

with open(LOG, "w", encoding="utf-8") as f:
    f.write("\n".join(out))

print(f"\nSaved to: {LOG}")
print(f"Result: {ok} OK, {fail} failed")