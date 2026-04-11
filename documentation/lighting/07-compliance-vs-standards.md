# Compliance vs standards (Lux gap, U₀ gap)

## 1. Targets

From **`standards_cleaned.json`** (when **`standard_row`** is passed):

- **Required average illuminance:** **`Em_r_lx`**
- **Required uniformity ratio:** **`Uo`** (stored as a decimal, e.g. **0.4**)

Legacy path: **`define_places[place]`** in **`constants.py`** provides **`lux`** and **`uniformity`**.

---

## 2. Row fields **`_row_with_compliance_metrics`** (`calculate.py`)

Let **`avg`** = **Average Lux** (lumen method).

\[
\text{Lux gap} = \max(0,\, E_{m,r} - \text{avg})
\]

Let **`u0`** = **`U0_calculated`** from the grid (may be missing).

\[
\text{U0 gap} = \max(0,\, U_{0,\text{req}} - u_0)
\]

**`is_compliant`** = (Lux gap ≈ 0) **and** (U0 gap ≈ 0).

So compliance requires **both**:

1. **Lumen-method average** ≥ **Em,r**
2. **Grid U₀** ≥ **Uo**

---

## 3. Over-lighting cap (main sweep)

To avoid listing layouts that are far too bright on average:

\[
\text{avg\_lux} \le 1.35 \times E_{m,r}
\]

If exceeded, the fixture-count loop **breaks** upward for that luminaire/power/efficacy line.

---

## 4. Minimum spacing

If **min(spacing_x, spacing_y) < 0.8 m**, the loop **breaks** — no further density for that line.

---

## 5. Closest non-compliant candidate

If no **(lux OK + U₀ OK)** is found for a combo, the row with best tuple **(U₀ gap, Lux gap, total power, fixtures)** is kept as **`closest_non_compliant_candidate`** for **seeding** the fallback sweep.

---

## 6. Uniformity fallback sweep

When **no** compliant option exists in the main search but **closest** candidates exist:

**`_uniformity_fallback_sweep_rows`** increases **fixture count** (with a **relaxed** average-lux cap **1.65 × Em,r**), still requiring **lumen average ≥ Em,r**, and re-evaluates **U₀**. Purpose: **tighter spacing** often **raises** **U₀** (more overlap). Results are tagged **`Selection: uniformity_fixture_sweep_fallback`**.

**`fast=True`**: smaller caps on fallback span, coarser steps, lower uniformity call budget.

---

## 7. Standard margin columns

- **Standard margin (lux %)** = \((E_{m,r} - \text{avg}) / E_{m,r} \times 100\) — can be **negative** if over target.
- **Standard margin (U0 %)** = \((U_{0,\text{req}} - U_0) / U_{0,\text{req}} \times 100\)

---

Next: [08-standards-data-fields.md](./08-standards-data-fields.md)
