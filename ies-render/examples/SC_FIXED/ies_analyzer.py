"""
ies_analyzer.py
---------------
Standalone IES file reader and analyzer.
No external dependencies — pure Python standard library only.

Usage:
    # Analyze one file:
    python ies_analyzer.py path/to/file.IES

    # Analyze all IES files in a folder:
    python ies_analyzer.py examples/SC_FIXED/

    # Analyze a folder and save results:
    python ies_analyzer.py examples/SC_FIXED/ --out results.txt

Outputs:
    - Header metadata (manufacturer, lumcat, description, etc.)
    - Photometric geometry (lamp count, lumens, watts, multiplier)
    - Fixture physical dimensions
    - Vertical / horizontal angle grid
    - Candela distribution summary
    - Computed beam angles (FWHM half-power, 10% threshold)
    - Computed total lumens (integrated from candela data)
    - Efficacy (lm/W) if wattage is available
    - Symmetry type
    - Distribution classification (flood, spot, wide, asymmetric, etc.)
"""

import os
import sys
import glob
import math
import argparse
from typing import Optional


# ── IES keyword → photometric type descriptions ───────────────────────────────
PHOTO_TYPE = {
    "1": "Type C (most common — vertical=0 nadir, horizontal=azimuth)",
    "2": "Type B (lateral/rotational — used for adjustable fixtures)",
    "3": "Type A (automotive — rarely used in architectural)",
}

UNIT_TYPE = {
    "1": "feet",
    "2": "meters",
}


def _flatten_tokens(lines):
    tokens = []
    for line in lines:
        tokens.extend(line.split())
    return tokens


def parse_ies(filepath: str) -> dict:
    """
    Parse a single IES file and return a dict of all extracted data.
    Handles IESNA:LM-63-1986, 1991, 1995, 2002 formats.
    """
    with open(filepath, "r", errors="replace") as f:
        raw = f.read()

    lines = raw.splitlines()
    result = {
        "filepath": filepath,
        "filename": os.path.basename(filepath),
        "filesize_kb": round(os.path.getsize(filepath) / 1024, 1),
        "errors": [],
    }

    # ── 1. Format version line ─────────────────────────────────────────────
    version_line = lines[0].strip() if lines else ""
    if version_line.startswith("IESNA"):
        result["format"] = version_line
    elif version_line.startswith("IES"):
        result["format"] = version_line
    else:
        result["format"] = "Unknown / pre-1986"

    # ── 2. Header keywords ([TEST], [MANUFAC], etc.) ───────────────────────
    keywords = {}
    tilt_idx = None
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.upper().startswith("TILT"):
            tilt_idx = i
            break
        if stripped.startswith("[") and "]" in stripped:
            bracket_end = stripped.index("]")
            key = stripped[1:bracket_end].strip().upper()
            val = stripped[bracket_end + 1:].strip()
            keywords[key] = val

    result["keywords"] = keywords
    result["manufacturer"]  = keywords.get("MANUFAC", keywords.get("MFG", "n/a"))
    result["luminaire"]     = keywords.get("LUMINAIRE", "n/a")
    result["lumcat"]        = keywords.get("LUMCAT", "n/a")
    result["lamp"]          = keywords.get("LAMP", "n/a")
    result["ballast"]       = keywords.get("BALLAST", "n/a")
    result["issuedate"]     = keywords.get("ISSUEDATE", keywords.get("DATE", "n/a"))
    result["test"]          = keywords.get("TEST", "n/a")
    result["more_info"]     = keywords.get("MORE INFO", keywords.get("MOREINFO", "n/a"))

    if tilt_idx is None:
        result["errors"].append("No TILT line found — invalid IES file")
        return result

    # ── 3. TILT ────────────────────────────────────────────────────────────
    tilt_line = lines[tilt_idx].strip()
    result["tilt"] = tilt_line

    data_start = tilt_idx + 1
    # If TILT is not NONE, skip the tilt angle data lines
    if "NONE" not in tilt_line.upper() and "INCLUDE" not in tilt_line.upper():
        # TILT=INCLUDE: next line = lamp-to-luminaire angle, then count, then angles
        try:
            lamp_angle = int(lines[data_start].strip())
            n_tilt = int(lines[data_start + 1].strip())
            data_start += 2 + math.ceil(n_tilt / 10) * 2  # angles + multipliers
        except Exception:
            pass

    # ── 4. Photometric data tokens ─────────────────────────────────────────
    tokens = _flatten_tokens(lines[data_start:])

    try:
        idx = 0

        num_lamps       = int(tokens[idx]);   idx += 1
        lumens_per_lamp = float(tokens[idx]); idx += 1
        cd_multiplier   = float(tokens[idx]); idx += 1
        n_vert          = int(tokens[idx]);   idx += 1
        n_horiz         = int(tokens[idx]);   idx += 1
        photo_type      = tokens[idx];        idx += 1
        units_type      = tokens[idx];        idx += 1
        lum_width       = float(tokens[idx]); idx += 1
        lum_length      = float(tokens[idx]); idx += 1
        lum_height      = float(tokens[idx]); idx += 1
        ballast_factor  = float(tokens[idx]); idx += 1
        future_use      = float(tokens[idx]); idx += 1
        input_watts     = float(tokens[idx]); idx += 1

        result.update({
            "num_lamps":       num_lamps,
            "lumens_per_lamp": lumens_per_lamp,
            "cd_multiplier":   cd_multiplier,
            "n_vert":          n_vert,
            "n_horiz":         n_horiz,
            "photo_type_code": photo_type,
            "photo_type_desc": PHOTO_TYPE.get(photo_type, f"Unknown ({photo_type})"),
            "units_code":      units_type,
            "units":           UNIT_TYPE.get(units_type, f"Unknown ({units_type})"),
            "lum_width":       abs(lum_width),
            "lum_length":      abs(lum_length),
            "lum_height":      abs(lum_height),
            "ballast_factor":  ballast_factor,
            "input_watts":     input_watts,
        })

    except (IndexError, ValueError) as e:
        result["errors"].append(f"Failed parsing photometric header: {e}")
        return result

    # ── 5. Angle arrays ────────────────────────────────────────────────────
    try:
        vert_angles  = [float(tokens[idx + j]) for j in range(n_vert)];  idx += n_vert
        horiz_angles = [float(tokens[idx + j]) for j in range(n_horiz)]; idx += n_horiz
    except (IndexError, ValueError) as e:
        result["errors"].append(f"Failed parsing angle arrays: {e}")
        return result

    result["vert_angles"]  = vert_angles
    result["horiz_angles"] = horiz_angles
    result["vert_min"]     = vert_angles[0]
    result["vert_max"]     = vert_angles[-1]
    result["horiz_min"]    = horiz_angles[0]
    result["horiz_max"]    = horiz_angles[-1]

    # ── 6. Candela matrix ──────────────────────────────────────────────────
    # Stored as: for each horizontal angle, n_vert values
    try:
        candela = []
        for h in range(n_horiz):
            row = [float(tokens[idx + j]) * cd_multiplier for j in range(n_vert)]
            candela.append(row)
            idx += n_vert
    except (IndexError, ValueError) as e:
        result["errors"].append(f"Failed parsing candela matrix: {e}")
        return result

    result["candela"] = candela  # list of lists [horiz][vert]

    # ── 7. Candela statistics ──────────────────────────────────────────────
    all_cd = [v for row in candela for v in row]
    peak_cd = max(all_cd)
    min_cd  = min(all_cd)
    avg_cd  = sum(all_cd) / len(all_cd)

    result["peak_candela"]  = peak_cd
    result["min_candela"]   = min_cd
    result["avg_candela"]   = avg_cd

    # Peak direction
    peak_val = -1
    peak_h_angle = peak_v_angle = 0
    for hi, row in enumerate(candela):
        for vi, val in enumerate(row):
            if val > peak_val:
                peak_val = val
                peak_h_angle = horiz_angles[hi]
                peak_v_angle = vert_angles[vi]
    result["peak_cd_h_angle"] = peak_h_angle
    result["peak_cd_v_angle"] = peak_v_angle

    # ── 8. Beam angles ─────────────────────────────────────────────────────
    # Computed from the first horizontal plane (standard practice for Type C)
    row0 = candela[0]

    def compute_beam_angle(row, angles, threshold_fraction):
        """Find full angle where intensity drops to threshold_fraction of peak."""
        peak = max(row)
        if peak == 0:
            return None
        threshold = peak * threshold_fraction
        # find crossing from peak outward
        for j in range(len(row) - 1):
            if row[j] >= threshold > row[j + 1]:
                frac = (row[j] - threshold) / (row[j] - row[j + 1])
                half_angle = angles[j] + frac * (angles[j + 1] - angles[j])
                return round(half_angle * 2, 2)
        return None

    # For Type C, vertical angles start at 0 (nadir) and go to 90 or 180
    # FWHM = half-power beam angle (50% of peak)
    # Field angle = 10% of peak
    result["beam_angle_fwhm"]  = compute_beam_angle(row0, vert_angles, 0.50)
    result["beam_angle_field"] = compute_beam_angle(row0, vert_angles, 0.10)

    # ── 9. Total lumens (numerical integration) ────────────────────────────
    # Using the zonal cavity method for Type C photometry
    # L = 2π * Σ [ cd(θ) * sin(θ) * Δθ ] integrated over all solid angles
    def compute_total_lumens_typeC(candela_matrix, vert_angs, horiz_angs):
        """
        Numerically integrate the candela distribution to get total lumens.
        Uses the trapezoidal rule over vertical angles, summed across
        horizontal sectors weighted by their azimuthal span.
        """
        total_lm = 0.0
        n_h = len(horiz_angs)
        n_v = len(vert_angs)

        for hi in range(n_h):
            # Azimuthal weight: portion of full circle this plane represents
            if n_h == 1:
                d_phi = 2 * math.pi
            elif hi == 0:
                d_phi = math.radians(horiz_angs[1] - horiz_angs[0]) / 2
                # wrap-around if full circle
                if abs(horiz_angs[-1] - horiz_angs[0]) >= 359:
                    d_phi = math.radians(
                        (horiz_angs[1] - horiz_angs[0]) / 2 +
                        (horiz_angs[0] + 360 - horiz_angs[-1]) / 2
                    )
            elif hi == n_h - 1:
                d_phi = math.radians(horiz_angs[-1] - horiz_angs[-2]) / 2
                if abs(horiz_angs[-1] - horiz_angs[0]) >= 359:
                    d_phi = math.radians(
                        (horiz_angs[-1] - horiz_angs[-2]) / 2 +
                        (horiz_angs[0] + 360 - horiz_angs[-1]) / 2
                    )
            else:
                d_phi = math.radians(
                    (horiz_angs[hi] - horiz_angs[hi - 1]) / 2 +
                    (horiz_angs[hi + 1] - horiz_angs[hi]) / 2
                )

            row = candela_matrix[hi]

            # Trapezoidal integration over vertical angles
            for vi in range(n_v - 1):
                theta1 = math.radians(vert_angs[vi])
                theta2 = math.radians(vert_angs[vi + 1])
                cd1 = row[vi]
                cd2 = row[vi + 1]
                # ∫ cd(θ) sin(θ) dθ ≈ (cd1+cd2)/2 * (sin(θ1)+sin(θ2))/2 * Δθ
                # More accurate: use midpoint sin
                d_theta = theta2 - theta1
                mid_sin = math.sin((theta1 + theta2) / 2)
                mid_cd  = (cd1 + cd2) / 2
                total_lm += mid_cd * mid_sin * d_theta * d_phi

        return round(total_lm, 1)

    computed_lumens = compute_total_lumens_typeC(candela, vert_angles, horiz_angles)
    result["computed_lumens"] = computed_lumens

    # Rated lumens from file header
    if lumens_per_lamp > 0:
        result["rated_lumens"] = round(lumens_per_lamp * num_lamps * ballast_factor, 1)
    else:
        result["rated_lumens"] = None  # -1 means not specified

    # Efficacy
    if input_watts > 0:
        result["efficacy_computed_lm_per_w"] = round(computed_lumens / input_watts, 1)
        if result["rated_lumens"]:
            result["efficacy_rated_lm_per_w"] = round(result["rated_lumens"] / input_watts, 1)
    else:
        result["efficacy_computed_lm_per_w"] = None
        result["efficacy_rated_lm_per_w"]    = None

    # ── 10. Symmetry detection ─────────────────────────────────────────────
    h0 = horiz_angles[0]
    h1 = horiz_angles[-1]
    span = h1 - h0

    if n_horiz == 1:
        symmetry = "Full rotational symmetry (1 plane — axially symmetric)"
    elif abs(span - 360) < 1:
        symmetry = "Full azimuthal (0°–360°)"
    elif abs(span - 180) < 1:
        symmetry = "Half azimuthal (0°–180°, bilateral symmetry assumed)"
    elif abs(span - 90) < 1:
        symmetry = "Quarter azimuthal (0°–90°)"
    elif h0 < 0:
        symmetry = f"Bilateral symmetric ({h0}° to {h1}°)"
    else:
        symmetry = f"Custom ({h0}° to {h1}°, {n_horiz} planes)"
    result["symmetry"] = symmetry

    # ── 11. Distribution classification ────────────────────────────────────
    ba = result["beam_angle_fwhm"]
    if ba is None:
        dist_class = "Undetermined"
    elif ba <= 20:
        dist_class = "Very Narrow Spot (≤20°)"
    elif ba <= 40:
        dist_class = "Narrow Spot (20°–40°)"
    elif ba <= 60:
        dist_class = "Spot (40°–60°)"
    elif ba <= 90:
        dist_class = "Flood (60°–90°)"
    elif ba <= 120:
        dist_class = "Wide Flood (90°–120°)"
    else:
        dist_class = "Very Wide / Diffuse (>120°)"

    # Check if asymmetric (street/area light)
    if n_horiz > 1 and abs(span - 360) < 1:
        # compare 0° plane vs 90° plane
        idx_0   = 0
        idx_90  = None
        for hi, ang in enumerate(horiz_angles):
            if abs(ang - 90) < 1:
                idx_90 = hi
                break
        if idx_90 is not None:
            peak_0  = max(candela[idx_0])
            peak_90 = max(candela[idx_90])
            ratio   = peak_0 / peak_90 if peak_90 > 0 else 999
            if ratio > 1.3 or ratio < 0.77:
                dist_class += " | Asymmetric (street/area light pattern)"

    result["distribution_class"] = dist_class

    return result


def format_report(d: dict) -> str:
    """Format the parsed IES data into a readable report."""
    sep  = "=" * 70
    sep2 = "-" * 70
    lines = []

    def row(label, value, unit=""):
        lines.append(f"  {label:<35} {value} {unit}".rstrip())

    lines.append(sep)
    lines.append(f"  FILE : {d['filename']}")
    lines.append(f"  PATH : {d['filepath']}")
    lines.append(f"  SIZE : {d['filesize_kb']} KB")
    lines.append(sep2)

    # Errors
    if d.get("errors"):
        for e in d["errors"]:
            lines.append(f"  !! ERROR: {e}")
        lines.append(sep)
        return "\n".join(lines)

    # Format version & header
    lines.append("  HEADER / METADATA")
    lines.append(sep2)
    row("IES Format Version",      d.get("format", "n/a"))
    row("Manufacturer",            d.get("manufacturer", "n/a"))
    row("Luminaire description",   d.get("luminaire", "n/a"))
    row("Luminaire catalog No.",   d.get("lumcat", "n/a"))
    row("Lamp description",        d.get("lamp", "n/a"))
    row("Ballast description",     d.get("ballast", "n/a"))
    row("Issue date",              d.get("issuedate", "n/a"))
    row("Test report",             d.get("test", "n/a"))
    row("TILT",                    d.get("tilt", "n/a"))

    # Other keywords
    skip = {"MANUFAC","MFG","LUMINAIRE","LUMCAT","LAMP","BALLAST",
            "ISSUEDATE","DATE","TEST","MORE INFO","MOREINFO"}
    for k, v in d.get("keywords", {}).items():
        if k not in skip and v:
            row(f"[{k}]", v)

    lines.append("")
    lines.append("  PHOTOMETRIC GEOMETRY")
    lines.append(sep2)
    row("Photometric type",        d.get("photo_type_desc", "n/a"))
    row("Measurement units",       d.get("units", "n/a"))
    row("Number of lamps",         d.get("num_lamps", "n/a"))
    row("Lumens/lamp (rated)",     d.get("lumens_per_lamp", "n/a"),
        "(−1 = not specified)")
    row("Candela multiplier",      d.get("cd_multiplier", "n/a"))
    row("Ballast factor",          d.get("ballast_factor", "n/a"))
    row("Input watts",             d.get("input_watts", "n/a"), "W")
    row("Symmetry",                d.get("symmetry", "n/a"))

    lines.append("")
    lines.append("  FIXTURE PHYSICAL DIMENSIONS")
    lines.append(sep2)
    row("Width",   d.get("lum_width",  "n/a"), d.get("units", ""))
    row("Length",  d.get("lum_length", "n/a"), d.get("units", ""))
    row("Height",  d.get("lum_height", "n/a"), d.get("units", ""))

    lines.append("")
    lines.append("  ANGLE GRID")
    lines.append(sep2)
    va = d.get("vert_angles", [])
    ha = d.get("horiz_angles", [])
    row("Vertical angles",
        f"{d['vert_min']}° – {d['vert_max']}°  ({d['n_vert']} values)")
    if len(va) <= 20:
        row("  Values", str(va))
    else:
        row("  First 5", str(va[:5]))
        row("  Last 5",  str(va[-5:]))
    row("Horizontal angles",
        f"{d['horiz_min']}° – {d['horiz_max']}°  ({d['n_horiz']} planes)")
    if len(ha) <= 20:
        row("  Values", str(ha))
    else:
        row("  First 5", str(ha[:5]))
        row("  Last 5",  str(ha[-5:]))

    lines.append("")
    lines.append("  CANDELA DISTRIBUTION")
    lines.append(sep2)
    row("Peak candela",    f"{d['peak_candela']:.2f}", "cd")
    row("Min candela",     f"{d['min_candela']:.2f}",  "cd")
    row("Avg candela",     f"{d['avg_candela']:.2f}",  "cd")
    row("Peak direction",
        f"H={d['peak_cd_h_angle']}°  V={d['peak_cd_v_angle']}°")

    # First horizontal plane preview
    cd = d.get("candela", [])
    if cd:
        row("Plane H=0° (first 8 values)",
            str([round(v, 1) for v in cd[0][:8]]) + "...")
        if len(cd) > 1:
            row("Plane H=last (first 8)",
                str([round(v, 1) for v in cd[-1][:8]]) + "...")

    lines.append("")
    lines.append("  COMPUTED BEAM ANGLES  (from first horizontal plane)")
    lines.append(sep2)
    ba_fwhm  = d.get("beam_angle_fwhm")
    ba_field = d.get("beam_angle_field")
    row("Beam angle — FWHM (50% peak)",
        f"{ba_fwhm}°" if ba_fwhm else "n/a")
    row("Field angle (10% peak)",
        f"{ba_field}°" if ba_field else "n/a")
    row("Distribution classification",  d.get("distribution_class", "n/a"))

    lines.append("")
    lines.append("  LUMEN OUTPUT & EFFICACY")
    lines.append(sep2)
    row("Computed total lumens",
        f"{d['computed_lumens']:.0f}", "lm  (integrated from candela data)")
    rated = d.get("rated_lumens")
    row("Rated total lumens (header)",
        f"{rated:.0f}" if rated else "not specified in file", "lm")
    eff_c = d.get("efficacy_computed_lm_per_w")
    eff_r = d.get("efficacy_rated_lm_per_w")
    row("Efficacy (computed lumens)",
        f"{eff_c}" if eff_c else "n/a", "lm/W")
    row("Efficacy (rated lumens)",
        f"{eff_r}" if eff_r else "n/a", "lm/W")

    lines.append(sep)
    lines.append("")
    return "\n".join(lines)


def analyze_file(path: str) -> tuple:
    """Parse and format one IES file. Returns (data_dict, report_string)."""
    data   = parse_ies(path)
    report = format_report(data)
    return data, report


def main():
    parser = argparse.ArgumentParser(
        description="IES file analyzer — reads and reports full photometric data"
    )
    parser.add_argument("path",
        help="Path to a single .IES file, or a folder to batch-process")
    parser.add_argument("--out", default=None,
        help="Save full report to this .txt file")
    parser.add_argument("--quiet", action="store_true",
        help="Suppress console output (useful when --out is set)")
    args = parser.parse_args()

    target = args.path

    # Collect files
    if os.path.isfile(target):
        ies_files = [target]
    elif os.path.isdir(target):
        ies_files = sorted(
            glob.glob(os.path.join(target, "*.IES")) +
            glob.glob(os.path.join(target, "*.ies"))
        )
        if not ies_files:
            print(f"No .IES files found in: {target}")
            sys.exit(1)
    else:
        print(f"Path not found: {target}")
        sys.exit(1)

    all_reports = []
    summary_rows = []

    for fp in ies_files:
        data, report = analyze_file(fp)
        all_reports.append(report)

        if not args.quiet:
            print(report)

        # Summary row
        summary_rows.append({
            "file":       data["filename"],
            "watts":      data.get("input_watts", "?"),
            "peak_cd":    f"{data['peak_candela']:.0f}" if "peak_candela" in data else "?",
            "lm":         f"{data['computed_lumens']:.0f}" if "computed_lumens" in data else "?",
            "lm_per_w":   f"{data['efficacy_computed_lm_per_w']}" if data.get("efficacy_computed_lm_per_w") else "?",
            "beam_fwhm":  f"{data['beam_angle_fwhm']}°" if data.get("beam_angle_fwhm") else "?",
            "class":      data.get("distribution_class", "?"),
        })

    # Summary table
    summary_lines = [
        "",
        "=" * 70,
        "  SUMMARY TABLE",
        "=" * 70,
        f"  {'FILE':<45} {'W':>5} {'Lm':>7} {'lm/W':>6} {'PeakCd':>8} {'Beam':>7}",
        "-" * 70,
    ]
    for r in summary_rows:
        fname = r["file"][:44]
        summary_lines.append(
            f"  {fname:<45} {str(r['watts']):>5} {r['lm']:>7} "
            f"{r['lm_per_w']:>6} {r['peak_cd']:>8} {r['beam_fwhm']:>7}"
        )
    summary_lines.append("=" * 70)
    summary_lines.append(f"  Total files: {len(ies_files)}")
    summary = "\n".join(summary_lines)

    if not args.quiet:
        print(summary)

    # Save output
    if args.out:
        full_output = "\n".join(all_reports) + "\n" + summary + "\n"
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(full_output)
        print(f"\nSaved to: {args.out}")


if __name__ == "__main__":
    main()
