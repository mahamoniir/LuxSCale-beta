# Input parameters: room geometry and height

## 1. Floor sides `sides = [a, b, c, d]`

The API accepts **four positive numbers** interpreted as consecutive sides of a **simple quadrilateral** (room outline), in order around the perimeter.

### 1.1 Area (Brahmagupta-style cyclic formula)

**`cyclic_quadrilateral_area(a, b, c, d)`** in **`geometry.py`**:

\[
s = \frac{a+b+c+d}{2}, \quad
A = \sqrt{(s-a)(s-b)(s-c)(s-d)}
\]

This matches a **cyclic** quadrilateral. For a **rectangle** with opposite sides equal, it reduces to **length × width**.

### 1.2 Length and width used elsewhere

\[
\text{length} = \max(a,c), \quad \text{width} = \max(b,d)
\]

(As implemented in **`calculate_lighting`** from tuple **`sides`.)

These define the **axis-aligned** rectangle used for **spacing** and **uniformity** grids (see spacing doc).

---

## 2. Ceiling height `height` (m)

### 2.1 Role in the model

- **Ceiling plane** \(z = H\) where \(H\) = **`ceiling_height_m`** passed to **`compute_uniformity_metrics`**.
- **Work plane** \(z = h_{wp}\) with default **`DEFAULT_WORK_PLANE_HEIGHT_M = 0.75`** m above floor.

Vertical distance **fixture → sample point**:

\[
\Delta z = H - h_{wp}
\]

Used in **`angles_fixture_to_point`** and **`illuminance_at_point_horizontal`**.

### 2.2 Interior vs exterior **catalog** (not a lux formula)

**`determine_zone(height)`** compares **`height`** to **`interior_height_max_m`** (default **5 m** from **`app_settings`**):

| Condition | Zone | Effect |
|-----------|------|--------|
| \(H < H_\text{th}\) | **interior** | Only indoor families (downlight, triproof, backlight) if in catalog |
| \(H \ge H_\text{th}\) | **exterior** | Highbay, flood, street, etc. |

**Height does not appear** in the simple lumen-average formula except indirectly: it does **not** scale average lux in the lumen method in this codebase (average uses **area only**). **Height strongly affects** the **IES grid** via distance \(r\) in the inverse-square law.

### 2.3 Validation bands (app)

**`validate_ceiling_height_m`** enforces plausible bands (interior vs exterior) — see back-end deployment doc — so extreme heights are rejected before calculation.

---

## 3. Summary table

| Parameter | Symbol / name | Used in lumen avg? | Used in IES grid? |
|-----------|---------------|--------------------|------------------|
| Sides | \(a,b,c,d\) | Yes (via area \(A\)) | Yes (room \(L,W\)) |
| Ceiling height | \(H\) | No (directly) | Yes (\(r\), angles) |
| Work plane | \(h_{wp}\) | No | Yes (\(r\), angles) |

---

Next: [03-lumen-method-maintenance-efficacy.md](./03-lumen-method-maintenance-efficacy.md)
