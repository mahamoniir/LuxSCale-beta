# Spacing, layout, and fixture count

## 1. Grid factorization `calculate_spacing(length, width, count)`

**`luxscale/lighting_calc/geometry.py`** chooses integers **`best_x`**, **`best_y`** such that:

\[
\text{best\_x} \times \text{best\_y} = \text{count}
\]

(exact divisor pair of **`count`**) and **minimizes** \(|\text{spacing\_x} - \text{spacing\_y}|\) where:

\[
\text{spacing\_x} = \frac{L}{\text{best\_x}}, \quad
\text{spacing\_y} = \frac{W}{\text{best\_y}}
\]

**Why exact:** Using **`x*y ≥ count`** (old behaviour) often picked the **same** grid for different fixture counts (e.g. 5×4 for 16, 18, and 20). Flux was then spread across **too many** virtual positions, so **every** grid illuminance scaled together with **N** and **U₀ = E_min/E_avg did not change** when adding fixtures — a modelling error.

So the layout tends toward **similar row and column spacing** among **valid factorizations** of **`count`** (e.g. 16 → 4×4, 18 → 6×3, 20 → 5×4 on a 9×8 m room).

**Solver:** **`spacing_factor_pairs`** lists every valid `(bx, by)` that also satisfies the **minimum spacing** rule. The main search and fallback **evaluate IES uniformity for each** pair at a given fixture count and keep the layout with the **smallest (U₀ gap, Lux gap)** (or the first fully compliant). Different pairs (e.g. 20 luminaires on 9×9 m: 4×5 vs 5×4 vs 2×10 vs 10×2) can yield **different U₀** — transposed or elongated grids change overlap and min/average illuminance.

---

## 2. Symmetric fixture positions

**`fixture_positions_symmetric_grid`** in **`uniformity_calculator.py`** places fixtures at:

\[
x_i = \left(i + \tfrac{1}{2}\right) \frac{L}{n_x}, \quad
y_j = \left(j + \tfrac{1}{2}\right) \frac{W}{n_y}
\]

- **Centre-to-centre** spacing: \(L/n_x\), \(W/n_y\).
- **Wall to nearest fixture row** (half-bay): half of that spacing on each axis.

---

## 3. Grid size vs fixture count

The solver passes **`best_x`**, **`best_y`** from **`calculate_spacing(length, width, num_fixtures)`** into **`compute_uniformity_metrics`**.

With **exact** factorization, **`n_grid = best_x × best_y = num_fixtures`**. Each of the **`n_grid`** positions carries one luminaire’s share of flux:

- **`phi_total = num_fixtures × lumens_per_fixture`**
- **`phi_each = phi_total / n_grid = lumens_per_fixture`** per position (one fixture per grid cell).

---

## 4. Minimum spacing cap (main search and fallback)

**`calculate.py`** enforces a **logical minimum centre-to-centre spacing** on the **tighter** axis:

\[
\min(\text{spacing\_x}, \text{spacing\_y}) \ge 0.8\ \text{m}
\]

If adding fixtures would violate this, the inner loop **breaks** (no denser layouts for that luminaire/power line).

**Note:** **`get_spacing_constraints(zone)`** in **`geometry.py`** returns legacy **(min, max)** tuples per axis for interior vs exterior; the **current** lighting solver does **not** call it — it uses the **0.8 m** floor only.

---

## 5. What appears in results

Each row exposes **Spacing X (m)** and **Spacing Y (m)** as **`length/best_x`** and **`width/best_y`** — the **centre-to-centre** distances used for reporting and the uniformity layout.

---

Next: [05-ies-photometry-and-inverse-square.md](./05-ies-photometry-and-inverse-square.md)
