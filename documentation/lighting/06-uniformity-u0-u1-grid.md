# Uniformity U₀ and U₁ on the work-plane grid

## 1. Sample grid

**`work_plane_grid_symmetric(length, width, grid_n)`** places **N×N** points on the floor plan using the **same symmetric rule** as fixtures: coordinates **(i+½)L/N**, **(j+½)W/N** — full room, **half-spacing** inset from each wall (equivalent to centres of **N** equal bays per axis).

**`uniformity_grid_n_for_room`** picks **N** from floor area (smaller **N** on very large floors for CPU cost):

| Area (m²) | N |
|-----------|---|
| &lt; 900 | 10 (default) |
| ≥ 900 | 8 |
| ≥ 1800 | 6 |
| ≥ 3500 | 5 |

---

## 2. Summing contributions

For each work-plane sample **(px, py)**:

\[
E(px,py) = \sum_{\text{fixtures } k} E_k(px,py)
\]

Each **E_k** comes from **`illuminance_at_point_horizontal`** (IES candela + inverse square + cos).

---

## 3. Aggregates

Over all **N²** samples:

\[
E_\text{min} = \min E,\quad
E_\text{max} = \max E,\quad
E_\text{avg} = \frac{1}{N^2}\sum E
\]

---

## 4. Uniformity ratios (as implemented)

\[
U_0 = \frac{E_\text{min}}{E_\text{avg}} \quad (\text{often called uniformity ratio } U_0 \text{ in standards})
\]

\[
U_1 = \frac{E_\text{min}}{E_\text{max}}
\]

**Standards** in this app primarily compare **U₀** to **`Uo`** from the selected row. **U₁** is computed for reporting; it is **not** the primary compliance gate in **`calculate.py`**.

---

## 5. Relation to average lux and height

- **Lumen-method “Average Lux”** = spatial mean from **\(N \cdot \Phi \cdot MF / A\)** — **not** the same number as **E_avg** from the grid unless the distribution is perfectly uniform and scaling matches.
- **Compliance** uses lumen-method average vs **Em,r**; **U₀** uses **grid** **E_min/E_avg**.
- **Ceiling height** enters **only** the **IES** path (distance **\(r\)** and angles). Raising the ceiling **without** changing lumens generally **lowers** illuminance and can **change** **U₀** (wider spacing of “pools” of light).

---

## 6. Text reports

**`format_uniformity_report_txt`** prints **E_min**, **E_avg**, **E_max**, **U₀**, **U₁**, fixture coordinates, optional ASCII plan, and a **row-major** matrix of **E** on the grid.

---

Next: [07-compliance-vs-standards.md](./07-compliance-vs-standards.md)
