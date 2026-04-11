# API integration and client-side state

## 1. Endpoints the front-end calls

### 1.1 Calculate (required for study creation)

| Property | Value |
|----------|--------|
| **Method** | `POST` |
| **Path** | `/calculate` (full URL from `getCalculateApiUrl()` — e.g. `http://127.0.0.1:5000/calculate` or PythonAnywhere host) |
| **Content-Type** | `application/json` |

**Body variants:**

**A) Room function only (`index2.html`, legacy `index.html`):**

```json
{
  "place": "Office",
  "sides": [w1, l1, w2, l2],
  "height": 3.0,
  "project_info": { "project_name": "...", "name": "...", "company": "...", "phone": "...", "email": "..." }
}
```

**B) Standard row (`index3.html`):**

```json
{
  "sides": [...],
  "height": 3.0,
  "project_info": {
    "project_name": "...",
    "standard_ref_no": "6.27.1",
    "standard_category": "...",
    "standard_task_or_activity": "...",
    "standard_lighting": { ... full row ... }
  },
  "standard_ref_no": "6.27.1",
  "fast": 1
}
```

`fast` is optional; enables faster calc on server.

**Success response (simplified):**

```json
{
  "status": "success",
  "results": [ { "Luminaire": "...", "Power (W)": ..., ... } ],
  "calculation_meta": { "calc_mode": "full|fast", "no_compliant_options": true|false, ... },
  "length": 0,
  "width": 0
}
```

**Errors:** HTTP 400 with `{ "status": "error", "message": "..." }` — e.g. invalid ceiling height, missing fields.

---

### 1.2 UI settings (optional, index2/index3)

| Property | Value |
|----------|--------|
| **Method** | `GET` |
| **Path** | `/api/ui-settings` |

Returns JSON including **`ceiling_height_bounds`** (`interior_min_m`, `interior_max_m`, `exterior_max_m`) plus pagination settings. Used to align client **`validateCeilingHeightM`** with server **`validate_ceiling_height_m`**.

---

### 1.3 Places (optional, index3 standards bootstrap)

| Property | Value |
|----------|--------|
| **Method** | `GET` |
| **Path** | `/places` |

Returns merged **category_keywords**, **standard_categories**, calculator places — enriches **`standards-picker.js`** when the API is reachable.

---

### 1.4 Submit study

| Property | Value |
|----------|--------|
| **Method** | `POST` |
| **Path** | Tried in order: `./api/submit.php`, `/LuxScaleAI/api/submit.php`, `/api/submit.php`, then **`http://127.0.0.1:5000/api/submit`** on localhost |

**Body:** Project metadata + `sides` + `height` + `results` (array) + optional `standard_*` + **`calculation_meta`**.

**Success:** `{ "status": "success", "token": "<hex32>" }` (Flask) or nested under `data` in some PHP variants — client normalizes to `token`.

---

### 1.5 Get study

| Property | Value |
|----------|--------|
| **Method** | `GET` |
| **Path** | `/api/get?token=<hex>` or `api/get.php?token=` |

Returns stored payload for **`result.html`**.

---

## 2. `localStorage` keys

| Key pattern | Set by | Used by |
|-------------|--------|---------|
| `user_token` | index.html / study flows | Legacy |
| `luxscale_result_links` | index2/index3 | “View last result” link list with TTL |
| `luxscale_result_rows_{token}` | index2/index3 after submit | **result.html** — full calc rows if API strips fields |
| `luxscale_result_request_{token}` | index3 | **result.html** — standard metadata if API incomplete |
| `lightingModelData` | result.html | Optional handoff to 3D / CAD |

**Important:** Stashes are **best-effort**; clearing site data breaks merge behavior — token URL still works if server stores full payload.

---

## 3. Cookies

| Name | Set by | Notes |
|------|--------|-------|
| `results` | `getResults` in index2/index3/index | Large JSON in cookie is fragile; prefer server + token |

---

## 4. Query string conventions

| Param | Page | Effect |
|-------|------|--------|
| `token` | `result.html` | Load study |
| `fast` | `index3.html` | Adds `fast: 1` to calculate payload |
| `stored_at` | Generated links | TTL for saved result links |

---

## 5. Error handling patterns (current)

| Scenario | Behavior |
|----------|----------|
| **Network failure** | `fetch` throws; index2/3 `alert("Failed to create study: " + error.message)` |
| **HTTP 400** | Often plain text body; index3 surfaces `errorText` in thrown Error |
| **Missing `results` array** | Explicit `throw new Error(...)` |

**Improvements (roadmap):** parse JSON error bodies, show `message` in a non-blocking banner; `aria-live` for screen readers.

---

Next: [threejs-and-maha.md](./threejs-and-maha.md).
