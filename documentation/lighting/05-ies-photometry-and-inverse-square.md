# IES photometry and inverse-square illuminance

## 1. LM-63 Type C data in this tool

**IES** files (LM-63) supply **luminous intensity** \(I\) in **candela (cd)** on a grid of **horizontal** and **vertical** angles. The parser (via **`ies-render/module/ies_parser.py`** or catalog JSON blobs through **`photometry_ies_adapter`**) builds **`IESData`** with:

- **`horizontal_angles`**, **`vertical_angles`**
- **`candela_values`** — intensity table \(I(\gamma_h, \gamma_v)\)

---

## 2. Why IES improves option quality

| Without angular data | With IES |
|---------------------|----------|
| Only **lm/W** and area → one **average** lux | **Real beam shape** → **hot spots**, **walls**, **overlap** |
| Uniformity unknown | **U₀**, **U₁** from a **grid** |
| Beam angle guessed | **Half-power beam** from candela slice (**`approx_beam_angle_deg`**) |

Catalog **IES** ties each **(luminaire name, power)** to a measured or manufacturer file, so comparisons between products use **different distributions**, not a single generic cone.

---

## 3. Angles from fixture to sample point

**`angles_fixture_to_point`** (**`uniformity_calculator.py`**) computes distance **\(r\)** (m), **vertical angle** **\(v\)** (degrees from nadir convention used with the IES vertical axis), and **horizontal angle** **\(h\)** (degrees in plan, `atan2(dy, dx)`).

Ceiling **`ceiling_z`**, work plane **`plane_z`**: \(\Delta z = \text{ceiling} - \text{work plane} > 0\) for downward lighting.

---

## 4. Candela lookup

Current implementation uses **`candela_at_angle_type_c`**:

- Interpolates vertically within each horizontal slice
- Linearly interpolates between adjacent horizontal planes
- Applies azimuth folding for symmetric Type C reductions

`candela_at_angle_simple` remains as a backward-compatible wrapper.

---

## 5. Horizontal illuminance (one source)

For each fixture contribution to a point on the **horizontal** work plane:

\[
E = \frac{I \cdot \cos(i)}{r^{2}}
\]

- **\(I\)** — candela along the direction to the point, scaled by flux (below).
- **\(\cos(i)\)** — factor for **oblique incidence** on the horizontal plane; implementation uses **`(ceiling_z - plane_z) / r`** clipped to **≥ 0** (downward light only).
- **\(r\)** — 3D distance (m); **\(r^{-2}\)** is the **inverse-square** law in metres → lux when **\(I\)** is cd.

**`illuminance_at_point_horizontal`** implements:

```text
I ← candela_at_angle_type_c(...);  if IES lumens: I *= flux_scale / ies_total_lm
return I * cos_i / (r*r)
```

---

## 6. Flux scaling (`flux_scale` / `phi_ies`)

Each grid **slot** receives **`flux_scale = phi_each`** where **`phi_each`** = (total design lumens for the layout) / (number of grid positions). Candela from the file is proportional to **rated** lumens **`phi_ies`** (IES header, or design lumens if header invalid):

\[
I_\text{used} = I_\text{file} \cdot \frac{\phi_\text{each}}{\phi_\text{ies}}
\]

So **absolute** grid lux follows **design lumens per slot**, while **relative** shape follows **IES** — **U₀** ratios are unchanged if **\(I\)** scales uniformly (pure scale cancels in **E_min/E_avg**).

---

## 7. Cached loading

**`_load_ies_data_cached`** (**`ies_fixture_params.py`**) uses **`lru_cache`** and prefers **catalog-backed** blobs when available for faster repeat loads.

---

Next: [06-uniformity-u0-u1-grid.md](./06-uniformity-u0-u1-grid.md)
