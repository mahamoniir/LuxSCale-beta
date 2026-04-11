# `standards_cleaned.json`: category → task_or_activity with two datalists

## Data shape (verified)

File: `standards/standards_cleaned.json`

- Root: **JSON array** of row objects (one row per standard line item).
- Each row includes at least:
  - **`ref_no`** — clause reference (e.g. `"6.1.1"`).
  - **`category`** — full category label used for grouping (often includes sub-area after ` – `, e.g. `"Traffic zones inside buildings"` or `"General areas inside buildings – Rest, sanitation and first aid rooms"`).
  - **`task_or_activity`** — short description of the task/activity for that row.
  - **`tasks`** — optional array of finer-grained task strings (not always 1:1 with `task_or_activity`).
  - Illuminance fields: **`Em_r_lx`**, **`Em_u_lx`**, **`Uo`**, etc.
  - Optional: **`category_base`**, **`category_sub`** for hierarchy display.

**Important:** `category` values are **long strings**. The set of **unique `category` values** is your **first datalist** (category picker).

For a chosen **`category`**, filter rows where `row.category === selectedCategory` (exact string match after user picks from datalist). The **unique `task_or_activity`** values (and optionally `tasks` expanded) form the **second datalist**.

If two rows share the same **`category`** + **`task_or_activity`** but different **`ref_no`**, disambiguate in the UI (e.g. show `task_or_activity (ref_no)` in the datalist `value`, or keep a hidden `ref_no` when user selects).

---

## UI pattern you asked for

1. **Input 1 — Category**  
   - `<input type="text" list="dl-categories" id="stdCategory" autocomplete="off">`  
   - `<datalist id="dl-categories">` filled with **unique** `category` strings from the JSON (sorted).

2. **Input 2 — Task / activity**  
   - `<input type="text" list="dl-tasks" id="stdTask" autocomplete="off">`  
   - `<datalist id="dl-tasks">` filled when category changes: all **`task_or_activity`** values for rows matching that category (unique, stable order).

3. **Events**  
   - On **`change`** or **`input`** of category (debounced optional): rebuild `dl-tasks`.  
   - Clear task field when category changes if it no longer applies.

---

## Wiring to LuxScale `place` (calculator)

The Python calculator today expects **`place`** ∈ `define_places` keys (`Room`, `Office`, …).  
**`category` / `task_or_activity` from `standards_cleaned.json` are not the same field.**

You can:

| Approach | Description |
|----------|-------------|
| **A — Mapping** | After user picks category+task, map to nearest `place` string (JS lookup table) for `/calculate`. |
| **B — Lux from standards** | Use selected row’s **`Em_r_lx`** (or `Em_u_lx`) as target illuminance and extend Python to accept **`required_lux`** instead of only `place` (larger change). |
| **C — Store only for report** | Send `place` from mapping (A) and add `category`, `task_or_activity`, `ref_no` inside **`project_info`** for PDF/display only. |

---

## Implementation in this repo

- **Helper script:** `assets/standards-picker.js`  
  - Loads `standards/standards_cleaned.json`  
  - Builds category list + filtered task list  
  - Call `initStandardsPicker({ ... })` from your page after DOM ready  

- **Integration:** Replace or supplement the Room function `<select>` in `index2.html` / `index.html` with the two inputs + datalists, then connect `getResults` / submit payload to your chosen approach (A/B/C above).

---

## Fetch path note

From `http://localhost/LuxScaleAI/index2.html`, the JSON URL should be:

`standards/standards_cleaned.json` (relative to site root) or  
`/LuxScaleAI/standards/standards_cleaned.json` depending on deployment.

Use the same origin as the HTML page to avoid CORS issues.
