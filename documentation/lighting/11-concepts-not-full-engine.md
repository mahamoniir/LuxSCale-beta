# Concepts referenced in standards but not fully modeled

The JSON standards and PDFs often list quantities beyond what **`calculate.py`** simulates. This avoids overstating what the tool proves.

## 1. Glare (UGR / RUGL)

**`RUGL`** in **`standards_cleaned.json`** is **displayed** but **not** computed from fixture positions, luminances, or viewing directions. Full **UGR** needs room dimensions, observer position, and luminaire luminance areas.

---

## 2. Wall and ceiling illuminance

**`Em_wall_lx`**, **`Em_ceiling_lx`** are **targets** for **display** — the engine does **not** integrate illuminance on vertical surfaces or cavity flux.

---

## 3. **`Em_u_lx`** and **`Ez_lx`**

These may represent upper illuminance bands, vertical task illuminance, or cylindrical illuminance depending on the source table. The app **does not** run separate vertical-grid or cylindrical illuminance calculations today.

---

## 4. Colour quality (**Ra**)

**CRI / Ra** is **not** checked against the selected luminaire product data in the solver.

---

## 5. Daylight, furniture, non-rectangular rooms

- **No daylight** contribution.
- **No furniture** occlusion.
- **No full radiosity/light-transport solver**; current implementation can apply a simple inter-reflection estimate factor from room reflectance presets.
- **Floor** is a **rectangle** derived from **`max(a,c)` × `max(b,d)`** for length/width; the **area** may come from the **cyclic quadrilateral** formula — see [02-input-parameters-room-and-height.md](./02-input-parameters-room-and-height.md).

---

## 6. Maintenance

Maintenance is modeled by a single configurable **`maintenance_factor`** (from app settings; default 0.8), not lamp-specific L90 curves or cleaning schedules.

---

## 7. Where to read older design notes

**`uniformity/*.md`** may describe earlier margin rules or grids — **always prefer** **`luxscale/uniformity_calculator.py`** and this **`documentation/lighting/`** set for **current** behavior.

---

Back to [README.md](./README.md)
