# Overview and tool scope

## 1. What LuxScaleAI’s lighting engine does

The backend answers: **“Which luminaires (from the catalog) can illuminate this room to meet a target average illuminance and a minimum uniformity ratio, given ceiling height and floor shape?”**

It combines:

1. **Lumen method** — fast **spatial average** illuminance on the floor (no angular distribution except via rated lm/W).
2. **IES-based point-by-point grid** — **Type C candela** from each fixture, **inverse-square** to a horizontal work plane, then **U₀ = E_min/E_avg** (and U₁).

**Compliance** in the shipped solver primarily checks:

- **Average lux** (lumen method) ≥ **Em,r** from the selected standard row (or legacy `define_places`).
- **U₀** from the grid ≥ **Uo** from the same row.

Other fields in **`standards_cleaned.json`** (UGR, E_z, wall/ceiling illuminance, CRI) are **stored and shown in the UI/PDF** but are **not** recomputed by the Python engine as separate physics simulations.

---

## 2. Standards data volume

- **`standards/standards_cleaned.json`** contains **74** task rows (each with `ref_no`, category, tasks, photometric parameters).
- The **Egyptian lighting code** is represented as this structured JSON (labels may follow **`standards/aliases_upgraded.json`** in the UI).

Selecting a row by **`ref_no`** (e.g. `6.27.1`) loads **Em_r_lx**, **Uo**, and other fields for display; **solver targets** use **Em_r_lx** and **Uo** for the checks above.

---

## 3. Main Python modules

| Module | Role |
|--------|------|
| **`luxscale/lighting_calc/calculate.py`** | Orchestrates lumen method, fixture sweep, calls uniformity, compliance rows |
| **`luxscale/lighting_calc/geometry.py`** | Area, zone, luminaire list, **`calculate_spacing`** |
| **`luxscale/lighting_calc/constants.py`** | **`maintenance_factor`**, **`led_efficacy`**, **`define_places`**, nominal **`beam_angle`** |
| **`luxscale/uniformity_calculator.py`** | Grid illuminance, **U₀**, **U₁**, report text |
| **`luxscale/ies_fixture_params.py`** | Load IES → candela, **beam angle** helper, **`ies_params_for_file`** |

---

## 4. What is *not* in scope

- **Glare (UGR)** — not computed from luminaires in 3D; standard value is **informational**.
- **Vertical illuminance / cylindrical illuminance** — not a separate ray-tracing pass.
- **Daylight** — indoor-only artificial lighting.
- **Obstacles / furniture** — empty rectangular room.

---

Next: [02-input-parameters-room-and-height.md](./02-input-parameters-room-and-height.md)
