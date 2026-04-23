# Where Room function (“place”) is picked in the code

“Room function” in the product is the string field **`place`** sent to the calculation API. It must match a key in Python’s **`define_places`** (see below).

---

## 1. Main web UI — `index.html`

**HTML (user picks from a dropdown)**

- File: `index.html`
- Section: “Define the function”
- Element: `<select id="place">` with `<option value="…">` values:
  - `Room`, `Office`, `Cafe`, `Factory production line`, `Factory warehouse`

**JavaScript (value read on submit)**

- Same file, inside `<script>`:
  - `document.getElementById("place").value` is used when building the payload for:
    - `getResults()` → JSON field `place`
    - `calculate()` → `data.place` for `submit.php`

These **`value` attributes** must stay aligned with `define_places` keys in `lighting_calc.py`.

---

## 2. New UI — `index2.html`

**HTML**

- File: `index2.html`
- Label: “Room Function”
- Element: `<select id="dimPlace" name="place" required>`
- Options include a placeholder plus the same logical place types (with human-readable labels).

**JavaScript**

- `document.getElementById("dimPlace").value` → passed as `place` into:
  - `getResults(place, sides, height)` (POST body to `/calculate`)
  - `submitData.place` when posting to `submit.php`

---

## 3. Python calculation engine — `lighting_calc.py`

**Authoritative list of allowed `place` values**

- File: `lighting_calc.py`
- Dict: **`define_places`** (keys: `"Room"`, `"Office"`, `"Cafe"`, `"Factory production line"`, `"Factory warehouse"`)
- Each entry supplies **`lux`** and **`uniformity`** used by `calculate_lighting(place, sides, height)`.

**Lookup**

- Function: `calculate_lighting(place, sides, height)`
- Line of interest: `required_lux = define_places[place]["lux"]` (and uniformity from the same dict).

If the frontend sends a `place` string that is **not** a key in `define_places`, Python will raise **`KeyError`**.

---

## 4. Flask API — `app.py`

- Reads `place` from JSON: `data["place"]`
- Passes it to `calculate_lighting(place, sides, height)` from `lighting_calc.py`.

Same contract as above.

---

## 5. Duplicate / legacy copies

- `maha/lighting_calc.py` — duplicate `define_places` + GUI; keep in sync if you still use it.
- `maha/index.html`, `maha/in.html` — separate `<select id="place">` UIs.
- `res.html` — free-text `#place` input (different UX; still sends `place` to API).

---

## 6. Downstream (not selection, but storage/display)

- Results pages read **`request.place`** from API responses (`result.html`, `online-result.html`, etc.) for summaries and PDF text — they do not define the list of room types.

---

## Summary table

| Layer | File | What to change when adding a room type |
|-------|------|----------------------------------------|
| UI options | `index.html`, `index2.html` | `<select>` options (or future datalist) |
| API payload | Same JS | `place` string |
| Engine | `lighting_calc.py` | `define_places` new key + lux/uniformity |

Next: see [02-standards-json-datalist-upgrade.md](02-standards-json-datalist-upgrade.md) for integrating `standards_keywords_upgraded.json` and datalist inputs.
