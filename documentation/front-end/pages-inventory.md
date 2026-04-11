# Page-by-page inventory

Paths are relative to the **repository root** unless noted. Each subsection lists **purpose**, **major UI blocks**, **JavaScript responsibilities**, and **dependencies**.

---

## Root — primary LuxScale flows

### `index.html`

| Aspect | Detail |
|--------|--------|
| **Purpose** | Original marketing + calculator landing: video hero, quadrilateral room input, room “place” selection, Short Circuit branding. |
| **Styles** | `style.css` (external). Inline styles for dark input blocks. |
| **Key DOM** | Inputs `a`–`d` (sides), `height`, `place` `<select>`, hero copy. |
| **Behavior** | `getCalculateApiUrl()` switches localhost vs remote; `getResults()` POSTs JSON to `/calculate` with `place`, `sides`, `height`, `project_info`; validates width/length pairs match; stores `document.cookie` with results; submit posts to **`http://localhost/sc-luxscaleai/api/submit.php`** (hardcoded in snippet — adjust per deployment). |
| **Output** | On success with token → redirects to **`results.html?token=`** (not `result.html`). |
| **Notes** | Disables right-click/select via inline script (UX choice). |

---

### `index2.html` — “Next design” (room function only)

| Aspect | Detail |
|--------|--------|
| **Purpose** | LedEXPO-style flow **without** JSON standards picker: user picks **room function** from fixed list matching `define_places` (Room, Office, Cafe, Factory…). |
| **Visual** | Full-screen video, dark glass overlay, Anton/IBM Plex, hero + stat cards, collapsible **study form**. |
| **Form fields** | `dimA`–`dimD` (rectangle sides), `dimHeight`, `dimPlace`; hint text for ceiling **3–5 m interior / 5–20 m exterior**. |
| **Validation** | Width1 = Width2, Length1 = Length2; positive dimensions; **`validateCeilingHeightM()`** (client); loads bounds from **`/api/ui-settings`** when Flask available. |
| **API** | `getCalculateApiUrl()` → `POST /calculate` with `{ place, sides, height, project_info }` (no `standard_ref_no`). |
| **Submit** | `submitStudy()` tries multiple endpoints (PHP + Flask `/api/submit`); expects `{ token }`; stores **`user_token`**, **`luxscale_result_rows_{token}`** in `localStorage`; redirects to **`result.html?token=`** via `createStoredResultLink`. |
| **Other** | `RESULT_LINKS_KEY`, TTL for “View Last Result”; `openStudyForm` / `cancelStudyForm` toggle `#studyFormSection`. |

---

### `index3.html` — standards-based study (Egyptian code rows)

| Aspect | Detail |
|--------|--------|
| **Purpose** | Same shell as index2 but **category + task** resolve a row in **`standards/standards_cleaned.json`** (`ref_no`, `Em_r_lx`, `Uo`, …). |
| **Scripts** | **`assets/standards-picker.js`** (must load before inline script); **`initStandardsPicker`** with `cleanedRows`, datalists `#dl-std-categories`, `#dl-std-tasks`, `onRowResolved` → `lastResolvedStandardRow`. |
| **Standards loading** | `fetchStandardsJsonOk("standards/standards_cleaned.json")` with fallbacks for XAMPP path prefixes; optional merge from **`/places`** for category list. |
| **Calculate payload** | `POST /calculate` with `sides`, `height`, `project_info` including **`standard_ref_no`**, `standard_lighting`, category/task strings; optional **`fast: 1`** from URL `?fast=1`. |
| **Submit payload** | Adds `standard_ref_no`, `standard_category`, `standard_task_or_activity`, **`standard_lighting`** (full row clone); stashes **`luxscale_result_request_{token}`** (standard metadata) and **`luxscale_result_rows_{token}`**. |
| **Datalists** | Placed **outside** hidden panel (comment in file: some browsers skip suggestions when list is under `display:none`). |

---

### `result.html` — main results viewer

| Aspect | Detail |
|--------|--------|
| **Purpose** | Loads a saved study by **`?token=`**, merges API payload with **localStorage** stashes, renders tables/cards, compliance, PDF export, optional standard block. |
| **Libraries** | **Bootstrap 5** CSS/JS, **pdf-lib**; **`assets/standard-display.js`** for aliased labels (`aliases_upgraded.json`). |
| **Data flow** | `fetchResultsPayload(token)` tries Flask `/api/get` and PHP `get.php` candidates; **`mergeWithStashedStandard`** / **`mergeWithStashedResults`** reconcile incomplete API responses with what index2/3 saved. |
| **Storage keys** | `luxscale_result_request_{token}`, `luxscale_result_rows_{token}`, `luxscale_result_links`, `lightingModelData` (3D-related handoff). |
| **Features** | Fixture images from **`assets/fixture_map.json`** patterns; calculation meta (`calc_mode`, `no_compliant_options`, etc.); analysis text when zero solutions. |

---

### `about.html`

| Aspect | Detail |
|--------|--------|
| **Purpose** | Company/product information; same visual language as index2 (video, overlay, header/footer). |
| **Behavior** | Mostly static; navigation links to home and contact. |

---

### `results.html`, `spec.html`, `online-result.html`

| File | Purpose |
|------|---------|
| **`results.html`** | Alternate PDF-centric report page (pdf-lib + Bootstrap); used by **legacy `index.html`** redirect (`?token=`). |
| **`spec.html`** | Specification-style PDF helper. |
| **`online-result.html`** | Variant using **`cad.js`** + pdf-lib + Bootstrap for online-specific layout. |

Keep behavior aligned with **`result.html`** when changing submit/get contracts.

---

### `res.html`

| Aspect | Detail |
|--------|--------|
| **Purpose** | Minimal form: project fields + place + sides + height → posts to backend (compact demo). |

---

## Admin

### `admin/dashboard.html`

| Aspect | Detail |
|--------|--------|
| **Purpose** | Authenticated UI to edit **`assets/app_settings.json`** (max solutions, interior/exterior height bounds, UI batch sizes). |
| **API** | Uses dashboard API base from **`.env`** / `LUXSCALE_DASHBOARD_API_BASE` for load/save settings. |
| **Security** | Login flow; not intended for public internet without TLS and strong secrets. |

---

## Experimental / demos — `maha/`

| File | Description |
|------|-------------|
| **`maha/3d_model.html`** | Rich Three.js room: extruded door wall, high-bay-style fixtures, beams, grid outline, arrows, sprites. |
| **`maha/test.html`** | Room + downlight-style fixtures; `THREE.sRGBEncoding` on renderer; spacing lines. |
| **`maha/solid.html`** | Simpler room + emissive fixture groups; yellow outline. |
| **`maha/3d_view.html`** | Parameterized viewer (`GridHelper`, high-bay assembly). |
| **`maha/view.html`** | Entry/wrapper for viewer (see file for query usage). |
| **`maha/index.html`**, **`maha/in.html`** | Canvas **2D** lux distribution + fetch to calculator API; older UX. |
| **`maha/test-ex.html`** | Minimal test page. |

Shared assets: **`maha/js/three.min.js`**, **`maha/js/OrbitControls.js`**.

---

## Flow comparison table

| Entry | Standard row | Calculate identity | Result page |
|-------|--------------|--------------------|-------------|
| `index.html` | Via `place` presets only | `place` + sides + height | `results.html` |
| `index2.html` | No | `place` + sides + height | `result.html` |
| `index3.html` | Yes (`standard_ref_no`) | + `project_info.standard_*` | `result.html` |

---

Next: [assets-and-modules.md](./assets-and-modules.md).
