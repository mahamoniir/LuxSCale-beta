# LuxScaleAI lighting calculation — steps and timing

This document describes the **logical pipeline** used when the client calls **`POST /calculate`** (Flask `app.py` → `luxscale.lighting_calc.calculate_lighting`).  
Each successful or failed run can also produce a **timestamped trace file** under `calculation_logs/calculation_steps_YYYYMMDD_HHMMSS.txt` with **wall-clock seconds** per step (`delta_s` = time since the previous step, `sum_s` = time since trace start).

---

## 1. HTTP layer (`app.py`)

| Step | What happens |
|------|----------------|
| Parse JSON | Request body must be a JSON object with `sides`, `height`, and either a valid `standard_ref_no` (from `standards/standards_cleaned.json`) or a `place` key matching `define_places`. |
| Resolve standard | If `standard_ref_no` is present, `cleaned_row_by_ref()` loads the row; targets **Em,r (lx)** and **Uo** come from that row. |
| Trace start | A `CalculationTrace` is created and the step `api_00_ready` is recorded. |

---

## 2. Geometry and targets (`calculate_lighting`)

| Step | What happens |
|------|----------------|
| Sides → room | `length = max(a,c)`, `width = max(b,d)` from quadrilateral sides `a,b,c,d`. |
| Area | `cyclic_quadrilateral_area(a,b,c,d)` (Brahmagupta-style formula for a cyclic quadrilateral). |
| Zone | `determine_zone(height)`: **interior** if height &lt; 5 m, else **exterior** (affects luminaire catalog and LED efficacy list). |
| Targets | **Standard row**: `required_lux = Em_r_lx`, `required_uniformity = Uo`. **Place preset**: values from `define_places[place]`. |
| Trace | Steps `cl_01_calculate_lighting_enter`, `cl_02_geometry_and_targets`. |

---

## 3. Luminaire catalog and IES

| Step | What happens |
|------|----------------|
| Options | `determine_luminaire(height)` returns `(luminaire_name, [wattages])` (e.g. SC highbay at 100/150/200 W by height band). |
| Work-plane grid | `uniformity_grid_n_for_room(length, width)` picks a **coarser** N×N sample grid on very large floors to keep runtime manageable (see `uniformity_calculator.py`). |
| IES path | `resolve_ies_path(luminaire, power)` maps to an **LM-63** `.ies` file (or catalog JSON blob via `photometry_ies_adapter`). |
| IES parameters | `ies_params_for_file()` reads lumens, optional **half-power beam** estimate, etc. |
| Trace | `cl_03_options_and_uniformity_grid`, `cl_04_ies_resolve`. |

---

## 4. Lumen method and fixture-count search

For each **(luminaire, power, efficacy)**:

| Step | What happens |
|------|----------------|
| Lumens per fixture | `lumens = power × efficacy` (efficacy from `led_efficacy[zone]`, possibly a list → multiple passes). |
| Minimum fixtures | `total_lumens_needed = (required_lux × area) / maintenance_factor`, `min_fixtures = floor(total_lumens_needed / lumens) + 1`. |
| Search range | Sweeps `num_fixtures` from `min_fixtures` to `min_fixtures + search_span` (span capped for large `min_fixtures`). |
| Spacing | `calculate_spacing(length, width, num_fixtures, margin)` finds a **best_x × best_y** grid; spacing along length/width derived from that grid and margins. |
| Average illuminance | `avg_lux = (num_fixtures × lumens × maintenance_factor) / area` — compared to `required_lux` and an upper cap to avoid useless over-lit options. |
| Early exit | Stops increasing fixtures when spacing would fall below a floor or average lux exceeds the cap. |

---

## 5. IES-based uniformity (slowest part)

For each candidate `num_fixtures` (when an IES file exists):

| Step | What happens |
|------|----------------|
| Grid uniformity | `compute_uniformity_metrics()` places fixtures on a **best_x × best_y** layout, samples the **work plane** at **N×N** points (wall margin, work-plane height from defaults in `uniformity_calculator.py`). |
| Illuminance | For each sample point, sums **horizontal illuminance** from each fixture using **Type C candela** from the IES, distance **R**, and **cos θ** to the plane (inverse-square with photometric solid). |
| Metrics | **U0 = E_min / E_avg**, **U1 = E_min / E_max** on that grid; also grid E_min / E_avg / E_max in lx (scaled vs design lumens vs IES-rated lumens as documented in code). |
| Compliance | `Lux gap` and `U0 gap` vs standard; search seeks **least fixture count** that meets **both** lux and U0, else keeps **closest non-compliant** candidates for ranking. |

**Why it can be slow:** cost scales roughly with **(number of fixture-count steps) × (uniformity grid points) × (fixtures in layout)** × (efficacy variants). Large floors need many fixtures and many uniformity evaluations.

Trace step **`cl_05_lumen_search_and_uniformity`** records **`uniformity_evaluations`** (how many `compute_uniformity_metrics` calls) and **`uniformity_seconds`** (sum of their wall time).

---

## 6. Outputs and side files

| Output | Description |
|--------|-------------|
| JSON response | `results` rows with lumen-method fields, optional **U0_calculated**, **IES file**, gaps, **Selection** tag, etc. |
| Optional | `uniformity_reports/uniformity_calc_*.txt` when a compliant option produces a formatted chunk (see `write_uniformity_session_txt`). |
| **Per request** | `calculation_logs/calculation_steps_*.txt` — step names with **delta_s** / **sum_s**; path also returned as **`calculation_trace_file`** in the JSON (and on many errors). |

---

## 7. Constants (reference)

- **`maintenance_factor`**, **`led_efficacy`**, **`beam_angle`**, **`define_places`**: `luxscale/lighting_calc/constants.py`
- **Default uniformity grid / margins**: `luxscale/uniformity_calculator.py` (`DEFAULT_GRID_N`, etc.)

---

## 8. Trace file column meanings

- **delta_s**: Seconds since the **previous** step (not including work done *inside* the previous line’s label—each line is measured when that step *ends*).
- **sum_s**: Seconds since **trace start** (first step after `CalculationTrace` creation in `api_calculate`).
- **TOTAL (wall)**: Total elapsed when the file was written.

Step names prefixed with **`api_`** come from Flask; **`cl_`** from `calculate_lighting`.
