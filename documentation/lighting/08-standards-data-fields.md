# Standards data (`standards_cleaned.json`)

## 1. Volume and role

- **`standards/standards_cleaned.json`** holds **74** task rows (structured lighting requirements).
- The UI lets users pick a row (e.g. by **`ref_no`** such as **`6.1.1`**). Labels may be enriched via **`standards/aliases_upgraded.json`**.

---

## 2. Fields (typical row)

| Field | Meaning | Drives Python solver? |
|-------|---------|------------------------|
| **`ref_no`** | Clause-style reference | Selection key |
| **`category`**, **`task_or_activity`**, **`tasks`** | Taxonomy / search | Display |
| **`Em_r_lx`** | Maintained **average** illuminance on the **task area** (lx) | **Yes** — target average (lumen method) |
| **`Em_u_lx`** | Uniformity-related or upper band (lx) in many codes | **Display / PDF** — not recomputed as a separate grid check in **`calculate.py`** |
| **`Uo`** | Minimum **U₀** = **E_min/E_avg** | **Yes** — compared to **U0_calculated** |
| **`Ra`** | Minimum colour rendering index | **Display** — not validated against lamp **CRI** in engine |
| **`RUGL`** | Glare index (Unified Glare Rating style value in dataset) | **Display** — **not** computed |
| **`Ez_lx`** | Vertical / cylindrical illuminance targets (context-dependent in full codes) | **Display** — **not** simulated |
| **`Em_wall_lx`**, **`Em_ceiling_lx`** | Wall / ceiling illuminance | **Display** — **not** simulated |
| **`specific_requirements`** | Free-text notes | **Display** |
| **`category_base`** | Grouping | **Display** |

**Rule of thumb:** Only **Em_r_lx** and **Uo** participate in **automated pass/fail** in **`luxscale/lighting_calc/calculate.py`**. Other numeric fields support **documentation**, **exports**, and **future** extensions.

---

## 3. Egyptian code representation

Requirements are **normalized into JSON** for the app. Official clause numbering appears in **`ref_no`** and text fields; always verify against the **published** code for legal compliance — the tool is an **engineering aid**.

---

## 4. Legacy **`define_places`**

If no **`standard_row`** is passed, **`constants.define_places`** supplies **lux** and **uniformity** for named room types (**Room**, **Office**, **Cafe**, etc.).

---

Next: [09-beam-angle-and-ies-metadata.md](./09-beam-angle-and-ies-metadata.md)
