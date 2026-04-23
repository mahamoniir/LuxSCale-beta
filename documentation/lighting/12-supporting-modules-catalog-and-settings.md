# Supporting modules: catalog resolution, IES loading, settings, visuals

This document covers **Python modules on the calculation path** that are not the core **`calculate.py` / `uniformity_calculator.py`** formulas but **determine which photometry is used**, **whether the API accepts a height**, **how many solutions are returned**, and **how optional figures are built**.

---

## 1. `luxscale/paths.py`

**Role:** **`project_root()`** returns the repository root directory. All JSON assets (`assets/`, `ies-render/`) and log paths are joined from this anchor.

**Math:** None — filesystem anchor only.

---

## 2. `luxscale/app_settings.py`

### 2.1 Source

**`assets/app_settings.json`** (optional) is **deep-merged** over **`DEFAULT_SETTINGS`**. Cached with **`@lru_cache`** until **`clear_app_settings_cache()`**.

Default **`calc`** block includes:

- **`max_solutions_total`**: **80** (cap on **compliant** rows returned).
- **`interior_height_min_m`**: **3.0**
- **`interior_height_max_m`**: **5.0** — doubles as **threshold** \(H_\text{th}\) between interior/exterior catalog (same key as **`get_interior_height_max_m()`** used in **`determine_zone`** / **`determine_luminaire`**).
- **`exterior_height_min_m`**: present in defaults but **not** read by **`validate_ceiling_height_m`** (exterior lower bound is effectively **`interior_height_max_m`** in validation).
- **`exterior_height_max_m`**: **20.0**
- **`maintenance_factor`**: **0.8** (runtime design MF; clamped)
- **`room_reflectance_preset`**: `"medium"` (indirect fraction estimate for grid illuminance scaling)

### 2.2 Ceiling height validation **`validate_ceiling_height_m(height)`**

Let \(h\) = ceiling height (m), \(H_\text{th} =\) **`get_interior_height_max_m()`**, \(h_\text{min} =\) **`get_interior_height_min_m()`**, \(h_\text{ext,max} =\) **`get_exterior_height_max_m()`**.

| Condition | Accepted? |
|-----------|-----------|
| \(h < h_\text{min}\) (and interior branch) | **No** |
| \(h_\text{min} \le h < H_\text{th}\) | **Yes** (interior catalog zone) |
| \(H_\text{th} \le h \le h_\text{ext,max}\) | **Yes** (exterior catalog zone) |
| \(h > h_\text{ext,max}\) | **No** |

So **interior** is the half-open band **[h_min, H_th)** and **exterior** is **[H_th, h_ext,max]** — consistent with **`determine_zone`**: **`height < H_th`** → interior efficacy and luminaire families.

**Effect on calcs:** If validation fails, **`calculate_lighting`** is never called for that request.

### 2.3 **`get_max_solutions_total()`**

\[
N_\text{cap} = \mathrm{clamp}(\texttt{max\_solutions\_total},\, 1,\, 1000)
\]

The main search stops appending **compliant** rows when **`len(results) ≥ N_cap`**. This **does not change** lux or U₀ formulas — it only **truncates** how many options the user sees.

### 2.4 **`get_ui_config()`**

Exposes UI batch sizes and **`ceiling_height_bounds`** for the front end — no direct change to numerical results.

---

## 3. `luxscale/fixture_catalog.py`

**Role:** Load the active fixture map (`assets/<active_fixture_map_basename()>`) and find a row with **`api_luminaire_name`** and **`power_w`** matching the calculation request.

**`fixture_entry_for_api(name, power_w)`** returns an entry dict (including **`relative_ies_path`**, **`ies_file_exists`**, etc.) or **`None`**.

**Math:** None — **exact match** on name and integer watts.

**Used by:** **`ies_fixture_params.resolve_ies_path`** (first try), then **`fixture_ies_catalog.merged_ies_relative_map`** fallback.

---

## 4. `luxscale/fixture_ies_catalog.py`

**Role:** Build **`(luminaire name, power) → relative path under `ies-render/`** without requiring **`fixture_map.json`**.

- **`merged_ies_relative_map()`**: builds from **`scan_examples_ies_dataset(active_ies_dataset())`** and optional storefront filtering; this is the active runtime merge path.
- **`catalog_luminaire_power_options()`**: distinct wattages per luminaire — feeds **`determine_luminaire`** options in **`geometry.py`**.

**Math:** None — data wiring. **Determines which IES files exist** for the solver’s luminaire list.

---

## 5. `luxscale/ies_fixture_params.py`

Already summarized in [09-beam-angle-and-ies-metadata.md](./09-beam-angle-and-ies-metadata.md). Calculation-relevant points:

### 5.1 **`resolve_ies_path(luminaire_name, power_w)`**

1. **`fixture_catalog.fixture_entry_for_api`** → if **`ies_file_exists`**, return **`normpath(ies-render + relative_ies_path)`** if file exists.
2. Else **`merged_ies_relative_map()[ (name, int(power)) ]`**, normalized via **`normalize_relative_ies_path`**, under **`ies-render/`**.

If no path or missing file → **uniformity skipped** / placeholders for that option.

### 5.2 **`_load_ies_data_cached`**

Delegates to **`try_load_ies_data_via_catalog`** (below); on **`None`**, parses **`.ies`** with **`IES_Parser`**.

### 5.3 **`ies_params_for_file`**

Lumens per lamp, beam angle, etc., for result rows — **does not** replace grid integration.

---

## 6. `luxscale/ies_json_loader.py`

**Role:** Read **`ies-render/ies.json`** index and, per entry, optional **`photometry_json`** blob files under **`ies-render/`** (e.g. **`ies_json/...`**).

**`index_entry_by_relative_path(rel)`** — linear scan matching **`relative_path`**.

**`load_photometry_blob(rel)`** — returns parsed JSON or **`None`**.

**Math:** None — I/O and lookup.

---

## 7. `luxscale/photometry_ies_adapter.py`

**Role:** When the catalog index marks **`status == "ok"`** and a blob exists, build **`IESData`** **without** re-parsing LM-63 text.

### 7.1 Equivalence

**`ies_data_from_index_and_blob`** constructs the same **`IESData`** structure **`IES_Parser`** would: horizontal/vertical angles, **`candela_values`**, **`lumens_per_lamp`**, **`multiplier`**, **`num_lamps`**, opening dimensions, **shape**.

Candela arrays are copied from **`blob["photometry"]`**:

- **`horizontal_angles_deg`**, **`vertical_angles_deg`**
- **`candela_by_horizontal_deg`** — keys match horizontal angle strings; rows are vertical profiles.

**Therefore:** For a given fixture, **illuminance and U₀** from **`uniformity_calculator`** match whether data came from **blob** or **`.ies` parse`**, assuming the blob was generated from the same source file.

### 7.2 Fallback

If index/blob missing or construction fails → **`try_load_ies_data_via_catalog`** returns **`None`** → **`_load_ies_data_cached`** parses the **`.ies`** file directly.

---

## 8. `luxscale/calculation_trace.py`

**Role:** Optional structured step log (e.g. API passes **`CalculationTrace`** into **`calculate_lighting`**). Writes human-readable traces for debugging.

**Math:** None — observability only; results are unchanged if tracing is off.

### 8.1 `luxscale/app_logging.py`

**`log_step`** records calculation milestones (IES parse, fixture sweep, uniformity failures) to the configured log file. **No effect** on numeric outputs.

---

## 9. `luxscale/lighting_calc/plotting.py`

Used by **`draw_heatmap`**, **`draw_lighting_distribution`** (API / PDF / GUI helpers).

### 9.1 **`draw_heatmap(length, width, num_x, num_y)`**

Builds a **100×100** accumulator **`heatmap`**. For each fixture grid cell \((i,j)\) it maps the cell centre to integer indices:

\[
x_\text{idx} = \left\lfloor \frac{(i+\tfrac12)\,L/\texttt{num\_x}}{L} \cdot 100 \right\rfloor,\quad
y_\text{idx} = \left\lfloor \frac{(j+\tfrac12)\,W/\texttt{num\_y}}{W} \cdot 100 \right\rfloor
\]

Then **`heatmap[y_idx, x_idx] += 1`** (overlap adds).

**Important:** This is a **count of fixture centres per coarse cell**, **not** physical **lux** or candela. It is a **qualitative** layout visualization — **not** a substitute for **`compute_uniformity_metrics`**.

### 9.2 **`draw_lighting_distribution`**

Draws **orange rectangles** at fixture centres using **`luminaire_shapes`** sizes from **`constants.py`** — schematic only.

---

## 10. Module dependency chain (calculation)

```
app.py
  validate_ceiling_height_m (app_settings)
  calculate_lighting (lighting_calc/calculate)
      determine_luminaire → catalog_luminaire_power_options (fixture_ies_catalog)
      resolve_ies_path → fixture_catalog | merged_ies_relative_map
      _load_ies_data_cached → photometry_ies_adapter | IES_Parser
      compute_uniformity_metrics (uniformity_calculator)
  draw_heatmap (plotting) — optional; not used inside calculate_lighting
```

---

## 11. Files intentionally not duplicated here

- **`ies_json_builder.py`**, **`fixture_map_builder.py`**, **`regenerate_fixture_catalog.py`**: build-time / admin tooling; they **shape** the catalog but are not invoked on every **`POST /calculate`**.
- **`sc_ies_scan.py`**: filesystem scan feeding `merged_ies_relative_map` (active examples datasets plus legacy helpers) — no per-request photometric formula.

---

Next: [README.md](./README.md) (index)
