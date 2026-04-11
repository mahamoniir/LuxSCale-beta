# Flask API and routes

All routes are defined in **`app.py`** unless noted. Request bodies are **JSON** unless specified.

---

## 1. Core calculator

### `POST /calculate`

**Purpose:** Run `calculate_lighting` with room geometry, height, and either a **standard row** (`standard_ref_no` → `standards_cleaned.json`) or a **legacy `place`** key (`define_places`).

**Validation:**

- `sides`: required (4 numbers).
- `height`: required; **`validate_ceiling_height_m`** (interior/exterior bands).
- Must have **`standard_row` OR `place`** after `_resolve_calculate_inputs`.

**Inputs resolution (`_resolve_calculate_inputs`):**

- Reads `project_info.standard_ref_no` or top-level `standard_ref_no`.
- **`cleaned_row_by_ref(ref)`** scans **`standards/standards_cleaned.json`** for matching `ref_no`.
- If no ref, uses `place` string for legacy lux/uniformity presets.

**Options:**

- **`fast`:** `_want_fast_calculate` — JSON `fast: true/1` or query `?fast=1` → fewer compliant options, coarser fixture steps (see calculation-engine doc).

**Response (success):**

```json
{
  "status": "success",
  "project_info": { ... },
  "results": [ ... ],
  "length": <float>,
  "width": <float>,
  "calculation_trace_file": "<path or null>",
  "calculation_meta": { ... },
  "ui_settings": { ... },
  "standard_row": { ... }
}
```

`standard_row` included when standards-based.

**Tracing:** `CalculationTrace("POST /calculate")` records steps; **`trace.save()`** writes **`calculation_logs/calculation_steps_YYYYMMDD_HHMMSS.txt`**.

**Errors:** 400 with `{ "status": "error", "message": "..." }`.

---

### `POST /pdf`

**Purpose:** Regenerate a simple FPDF report (legacy). Accepts similar body to calculate; uses `calculate_lighting` then builds PDF in memory.

---

## 2. Public read-only

### `GET /`

JSON welcome message.

### `GET /places`

Loads **`standards/standards_keywords_upgraded.json`** and **`standards_cleaned.json`**, merges category lists for the front-end picker. Also exposes **`calculator_places`** from `define_places`.

### `GET /api/ui-settings`

Returns **`get_ui_config()`** from `app_settings`: pagination, compliance field flags, **`ceiling_height_bounds`**.

### `GET /api/public-config`

Returns `{ "api_base": <LUXSCALE_DASHBOARD_API_BASE or default> }` for static admin pages.

---

## 3. Study storage (Flask)

### `POST /api/submit`

- Validates `sides`, `height`, **`results` array** (may be empty).
- **`validate_ceiling_height_m`** on height.
- Generates token, writes **`api/data/studies/<token>.json`** (under Flask `_STUDIES_DIR`).
- Returns `{ "status": "success", "token": "<hex>" }`.

### `GET /api/get?token=<hex32>`

- Loads study JSON, returns payload shape expected by **`result.html`** (see front-end doc).

---

## 4. Admin API (session or bearer)

| Route | Method | Notes |
|-------|--------|--------|
| **`/api/admin/login`** | POST | JSON credentials → session cookie + optional bearer token |
| **`/api/admin/logout`** | POST | Clear session / revoke token |
| **`/api/admin/settings`** | GET, PUT | Read/write **`assets/app_settings.json`** |
| **`/api/admin/fixture-map`** | GET, PUT | Read/write **`assets/fixture_map.json`**, clears fixture cache |

Auth: **`_admin_session_ok()`** — Flask `session["admin"]` **or** **`X-Admin-Token`** header matching in-memory token map (`_ADMIN_TOKENS`).

---

## 5. Standards helper

### `POST /standards/resolve`

Body: `{ "ref_no": "6.27.1" }`  
Returns `{ "status": "success", "row": <full cleaned row> }` or 404.

---

## 6. Static serving

### `GET /assets/<path>`

Serves files from **`assets/`** (favicon, video, JS, JSON) when users open the admin dashboard **via Flask** (same origin).

### `GET /admin/dashboard.html`

Sends **`admin/dashboard.html`** file.

---

## 7. CORS

**`flask-cors`** with `supports_credentials=True`. Origins from **`LUXSCALE_CORS_ORIGINS`** or localhost defaults. Required when the HTML is on **port 80** and API on **5000**.

---

Next: [calculation-engine.md](./calculation-engine.md)
