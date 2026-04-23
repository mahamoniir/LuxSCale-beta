# Calculation engine (`calculate_lighting`)

Primary implementation: **`luxscale/lighting_calc/calculate.py`**, invoked from **`app.py`** via **`from luxscale.lighting_calc import calculate_lighting`**.

---

## 1. Function signature and return value

```python
calculate_lighting(place, sides, height, standard_row=None, trace=None, fast=False)
```

**Returns:** `(results: list, length: float, width: float, meta: dict)`

- **`sides`:** four numbers `(a,b,c,d)` — cyclic quadrilateral; **area** from **`cyclic_quadrilateral_area`**, **length** = `max(a,c)`, **width** = `max(b,d)` (see `geometry.py`).
- **`standard_row`:** If present, **`Em_r_lx`** → required average lux, **`Uo`** → required uniformity (as float). Otherwise **`define_places[place]`** supplies lux + uniformity.

---

## 2. Zone and luminaire **option picking**

### 2.1 `determine_zone(height)`

From **`luxscale/lighting_calc/geometry.py`**:

- Reads **`interior_height_max_m`** from **`app_settings`** (default **5 m**).
- **`height < threshold`** → **`"interior"`** LED efficacy zone.
- **`height >= threshold`** → **`"exterior"`**.

### 2.2 `determine_luminaire(height)`

Returns ordered list of **`(luminaire_name, [wattages])`** from **`catalog_luminaire_power_options()`**:

- **Interior:** `SC downlight`, `SC triproof`, `SC backlight` (if present in merged catalog).
- **Exterior:** `SC highbay`, `SC flood light exterior`, `SV flood`, `SC street`, `eco highbay`.

**Option picking** = nested loops: **each luminaire** × **each power** × **each efficacy** (interior: single `led_efficacy["interior"]`; exterior: list `[145,160,200]`).

---

## 3. Lumen method (average illuminance)

Runtime values come from defaults + app settings:

- **`maintenance_factor`** from **`luxscale/app_settings.get_maintenance_factor()`** (default **0.8**, clamped)
- **`led_efficacy`** per zone
- **`beam_angle`** nominal when IES missing

For each candidate:

\[
\text{lumens per fixture} = \text{power (W)} \times \text{efficacy (lm/W)}
\]

\[
\text{Average lux} = \frac{N \times \text{lumens} \times \text{MF}}{\text{area (m}^2\text{)}}
\]

**Minimum fixture count:**

```text
total_lumens_needed = (required_lux * area) / maintenance_factor
min_fixtures = int(total_lumens_needed / lumens) + 1
```

(`maintenance_factor` there is the runtime value loaded via app settings.)

Search **`num_fixtures`** from **`min_fixtures`** upward in steps (**`fixture_step`**: 1 full, 2 in `fast` mode), up to **`max_fixtures`** (min + span).

---

## 4. Spacing (`spacing_factor_pairs` + `calculate_spacing`)

`geometry.py` exposes:

- `spacing_factor_pairs(...)` for solver sweeps, requiring **`best_x × best_y == num_fixtures`**
- `calculate_spacing(...)` as a single best-pair helper used in fallback/report paths

Spacing uses:

- `spacing_x = length / best_x`
- `spacing_y = width / best_y`

**Sweep behavior:**

- If no factor pairs satisfy **`min_spacing_m`** (default **0.8 m**), that fixture count is skipped.
- **`avg_lux > max_avg_lux`** where **`max_avg_lux = required_lux * 1.35`** → break (over-lighting cap).

---

## 5. IES metadata row enrichment

If **`resolve_ies_path(luminaire, power)`** finds a file and **`ies_params_for_file`** succeeds:

- **`lumens_per_lamp`** from file (else rated lm).
- **`beam_angle_deg`** from `ies_params_for_file(...)` metadata (normalized non-negative in output rows).

If IES lumens ≤ 0, code falls back to rated efficacy.

---

## 6. Uniformity call

For each **`num_fixtures`** candidate with valid IES path:

- **`compute_uniformity_metrics(ies_path, length, width, height, num_fixtures, lumens, best_x, best_y, grid_n)`**

Populates **`U0_calculated`**, **`E_min_grid_lx`**, etc. on the row (see uniformity doc).

---

## 7. `fast` mode

When **`fast=True`**:

- **`max_solutions_cap`** capped (via **`get_max_solutions_total`** and min with 3).
- **`fixture_step = 2`**.
- Uniformity fallback uses coarser steps and lower call budget (`_uniformity_fallback_sweep_rows`).

---

## 8. Heatmaps

**`draw_heatmap`** (imported in `app.py`) — Matplotlib-based; used where referenced from API (not central to `/calculate` JSON). It accumulates **fixture-count** stamps on a 100×100 grid, **not** physical lux — see section **9** in [../lighting/12-supporting-modules-catalog-and-settings.md](../lighting/12-supporting-modules-catalog-and-settings.md) (`plotting.draw_heatmap`).

---

## 9. OpenAI

**`requirements.txt`** lists **`openai`** — optional / future; core lighting path does not require it for compliance.

---

**See also:** [../lighting/12-supporting-modules-catalog-and-settings.md](../lighting/12-supporting-modules-catalog-and-settings.md) (`app_settings` ceiling bounds, `max_solutions_total`, catalog resolution).

---

Next: [compliance-and-standards.md](./compliance-and-standards.md)
