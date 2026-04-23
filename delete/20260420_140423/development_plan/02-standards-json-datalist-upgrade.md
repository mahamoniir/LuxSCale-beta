# Upgrade path: `standards_keywords_upgraded.json` + two datalist inputs

This document explains how **`standards/standards_keywords_upgraded.json`** relates to **Room function**, and how you can replace the **`<select>`** with **two text inputs** backed by **`<datalist>`** suggestions.

---

## 1. What the JSON file contains

File: `standards/standards_keywords_upgraded.json`

Rough structure (see the file for full content):

| Section | Role |
|---------|------|
| `metadata` | Version, description |
| `common_mappings` | Maps a **keyword phrase** (e.g. `"office"`, `"warehouse"`) → array of **standard reference IDs** (e.g. `"6.26.2"`) |
| `category_keywords` | Groups keywords by category for broader navigation |
| `keyword_to_refs` | Additional keyword → standard refs |
| `usage_guide` | Suggested lookup flow |

**Important:** This file is a **standards keyword / clause reference** index. It is **not** the same structure as Python’s **`define_places`**, which maps a small set of **room-type labels** to **lux** and **uniformity** for the calculator.

So an integration layer is required: **either**

- map chosen keywords / refs → one of the existing `define_places` keys (`"Office"`, `"Room"`, …), **or**
- extend `define_places` (and possibly the calculation) to use lux values derived from `standards_cleaned.json` or another source.

---

## 2. Where to plug the JSON in the frontend

**Primary targets (same as [01-room-function-code-locations.md](01-room-function-code-locations.md)):**

1. **`index2.html`** — replace the block around `<select id="dimPlace">` (Room Function).
2. **`index.html`** — replace `<select id="place">` under “Define the function”.

**How to load the JSON in the browser**

- **Option A — Static fetch:**  
  `fetch('standards/standards_keywords_upgraded.json')`  
  (Ensure the web server serves `standards/` with correct MIME type; local XAMPP usually fine.)

- **Option B — Build step:**  
  Import or copy a trimmed JSON into your bundle if you use a bundler later.

- **Option C — Server endpoint:**  
  Expose a PHP route that returns the JSON (if you need access control or caching).

After `JSON.parse` / `response.json()`, build in-memory structures:

- List **A**: all keys from `common_mappings` (or a curated subset) for datalist 1.
- List **B**: categories from `category_keywords` **or** flattened standard refs for datalist 2 — depending on product design (see section 3).

---

## 3. Two inputs + datalist (recommended pattern)

**Goal:** Two `<input type="text" list="…">` fields with suggestions, instead of one `<select>`.

Example semantics (you can rename labels):

| Input | Purpose | Datalist source (from JSON) |
|-------|---------|-----------------------------|
| **1 — Space / activity keyword** | User picks or types a phrase like “open office”, “warehouse” | Keys from `common_mappings` (and/or `keyword_to_refs`) |
| **2 — Category or standard ref** | Narrow down: category label **or** show suggested `6.xx.x` refs | Keys from `category_keywords`, **or** union of ref strings returned for input 1 |

**HTML pattern**

```html
<label for="roomKeyword">Space / activity</label>
<input id="roomKeyword" name="room_keyword" list="dl-keywords" autocomplete="off" />

<label for="roomRefOrCategory">Category or standard ref</label>
<input id="roomRefOrCategory" name="room_ref" list="dl-refs-or-cats" autocomplete="off" />

<datalist id="dl-keywords"></datalist>
<datalist id="dl-refs-or-cats"></datalist>
```

**JavaScript outline**

1. On page load, `fetch` the JSON, then:
   - Fill `dl-keywords` with `<option value="…">` for each keyword key you want to expose.
   - Fill `dl-refs-or-cats` from `category_keywords` keys **or** from the refs array for the selected keyword (update when input 1 changes).
2. On submit (where you currently read `dimPlace` / `place`):
   - Derive a **single string** `place` for the API:
     - **Minimum viable:** map `(keyword → closest define_places key)` via a small JS map, e.g. `"warehouse"` → `"Factory warehouse"`, `"office"` → `"Office"`.
     - **Stronger:** store both raw keyword + ref in `project_info` and still send a valid `place` for the calculator.

---

## 4. Keeping the Python API happy

The `/calculate` body still needs:

```json
"place": "<must be a key of define_places in lighting_calc.py>"
```

So the upgrade must include one of:

1. **Mapping table in JS** — keyword/ref → `"Office"` | `"Room"` | …  
2. **Expand `define_places`** in `lighting_calc.py` with new keys and lux/uniformity (and update all UIs accordingly).  
3. **Change the API** — accept `place_free_text` + optional `standard_refs[]` and resolve lux inside Python (larger change; best if lux comes from `standards_cleaned.json`).

---

## 5. Files to touch for a full upgrade

| Area | Files |
|------|--------|
| UI | `index2.html`, `index.html` (and optionally `maha/index.html`, `maha/in.html`) |
| JSON load + datalist JS | Inline `<script>` in those pages, or a new `assets/room-standards-ui.js` |
| Data | `standards/standards_keywords_upgraded.json` (read-only), optionally `standards/standards_cleaned.json` for lux tables later |
| Engine | `lighting_calc.py` → `define_places` and/or new resolution logic |
| API | `app.py` if request shape changes |

---

## 6. Safety and “don’t break production”

- Develop against **local** Flask + local HTML; keep **`place`** mapping tested against `define_places` keys.
- Add **validation**: if no mapping exists, show an error instead of sending an invalid `place`.
- Consider **feature flag**: e.g. `?standards_ui=1` or a localStorage toggle to switch old `<select>` vs new datalist until stable.

---

## 7. Quick reference: current `define_places` keys

From `lighting_calc.py`:

- `Room`
- `Office`
- `Cafe`
- `Factory production line`
- `Factory warehouse`

Any new UX must resolve to these strings (unless you extend the Python dict).
