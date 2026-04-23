# IES (LM-63) file mathematics and tool-derived quantities

Sources: **`ies-render/module/ies_parser.py`** (`IES_Parser`, **`IESData`**), **`luxscale/ies_fixture_params.py`**, **`luxscale/photometry_ies_adapter.py`**, **`luxscale/uniformity_calculator.py`**.

---

## 1. File structure (after `TILT=NONE`)

The parser reads **13 header numbers** (`light_data[0..12]`):

| Index | Field | Role |
|-------|-------|------|
| 0 | **`num_lamps`** | Integer lamp count |
| 1 | **`lumens_per_lamp`** | Rated lumens per lamp (from file) |
| 2 | **`multiplier`** | Photometric multiplier |
| 3 | **`num_vertical_angles`** | \(N_v\) |
| 4 | **`num_horizontal_angles`** | \(N_h\) |
| 6 | **unit** | 1 = feet, 2 = metres (opening dimensions) |
| 7–9 | width, length, height | Opening box (converted to **metres** if feet) |

Then: **vertical angles** (\(N_v\) values), **horizontal angles** (\(N_h\) values), **candela** flat list of length \(N_v \times N_h\).

The flat list is reshaped into **`candela_values[horizontal_angle] → list of length \(N_v\)** (vertical profile at that azimuth).

\[
I_{\max} = \max \text{ over all tabulated candela.}
\]

---

## 2. Total luminous flux from the IES header (as used in the tool)

**Rated output** used for scaling context:

\[
\Phi_\mathrm{IES,header} = (\text{lumens\_per\_lamp}) \times (\text{multiplier}) \times (\text{num\_lamps}).
\]

**`ies_params_for_file`** exposes:

\[
\texttt{lumens\_per\_lamp key value} = (\text{lumens\_per\_lamp}) \times (\text{multiplier})
\]

(**without** multiplying by **`num_lamps`** in that dict — naming follows “per lamp group” in header; **`num_lamps`** is separate).

**Uniformity calculator** uses:

\[
\phi_\mathrm{file} = (\text{lumens\_per\_lamp}) \times (\text{multiplier}) \times n_\mathrm{lamps}
\]

as **`phi_ies_file`** for **`ies_rated_lm_file`**. If \(\phi_\mathrm{file} \le 0\), **design** lumens \(P\cdot\eta\) substitute **`phi_ies`** for normalization (**`ies_scale_note`**).

---

## 3. Candela scaling at each fixture (uniformity)

For each **grid slot** on the layout:

\[
\phi_\mathrm{total,design} = N \cdot (P \cdot \eta), \quad
n_\mathrm{slots} = n_x n_y, \quad
\phi_\mathrm{each} = \frac{\phi_\mathrm{total,design}}{n_\mathrm{slots}}.
\]

Candela used in \(E = I \cos i / R^2\):

\[
I_\mathrm{used} = I_\mathrm{table} \cdot \frac{\phi_\mathrm{each}}{\phi_\mathrm{IES}},
\quad
\phi_\mathrm{IES} = \max(\phi_\mathrm{file},\, \text{design fallback}).
\]

So **absolute** lx follow **installed design lumens**; **shape** follows **IES** candela distribution.

---

## 4. Beam/field angle metrics

Current result metadata comes from `ies_params_for_file(...)` via analyzer metrics (`compute_all_metrics`), which expose:

- `beam_angle_deg`
- `field_angle_deg`
- optional asymmetry spans (`beam_angle_min/max`, `field_angle_min/max`)

The solver/report path normalizes beam outputs to non-negative display values and falls back to nominal `beam_angle` when IES metadata is unavailable.

---

## 5. Opening dimensions and shape

**`IESData`** carries **`width`**, **`length`**, **`height`** (m, non-negative from **`fabs`** in parser), **`shape`** string (rectangular, point, etc.). These describe the **luminaire opening** in LM-63 — **not** the room. They appear in **`ies_params_for_file`** for display.

---

## 6. JSON blob vs direct parse

**`try_load_ies_data_via_catalog`** rebuilds **identical numeric arrays** to **`IES_Parser`** when **`ies.json`** + **`photometry_json`** blob exist — **same** \(I(\gamma_h,\gamma_v)\) for illuminance math.

---

## 7. Summary table (tool outputs from IES)

| Quantity | Formula / source |
|----------|-------------------|
| **Candela table** | LM-63 photometric web |
| **max_candela** | \(\max\) of table |
| **Beam angle (°)** | Analyzer-derived beam metric from `ies_params_for_file` (normalized for display) |
| **Lumens (header product)** | lumens_per_lamp × multiplier (× num_lamps for total rated flux) |
| **Grid E, U₀, U₁** | Inverse square + superposition + min/mean/max ratios |

---

Back to [README.md](./README.md)
