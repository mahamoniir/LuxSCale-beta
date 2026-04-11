# Assets, scripts, and data files

## 1. Directory map (`assets/`)

| Path | Type | Role |
|------|------|------|
| **`favicon.svg`** | Image | Tab icon |
| **`logo.svg`**, **`SClogo.svg`** | SVG | Brand marks |
| **`myvideo.mp4`** | Video | Looping full-screen background on marketing pages |
| **`standards-picker.js`** | JS | Standards UI: datalists, category/task filtering, resolve `ref_no` row — see §3 |
| **`standard-display.js`** | JS | Maps `standards_cleaned.json` fields to human labels via **`standards/aliases_upgraded.json`** |
| **`fixture_map.json`** | JSON | API luminaire name → image URLs, IES paths, online product links for **`result.html`** |
| **`fixture_ies_catalog.json`** | JSON | Luminaire × wattage → IES file paths (server/calc use; UI may reference) |
| **`fixtures_online.json`** | JSON | Storefront metadata merged into fixture map |
| **`app_settings.json`** | JSON | Runtime calc/UI settings (merged with code defaults); edited via **admin dashboard** |

Optional/generated assets (not exhaustive): product PNGs, `ies_json/` references under `ies-render/`.

---

## 2. Root-level CSS

| File | Consumers |
|------|-----------|
| **`style.css`** | **`index.html`** — legacy layout (sides grid, hero, form spacing) |

`index2.html`, `index3.html`, `result.html`, `about.html` use **embedded `<style>` blocks** or Bootstrap for self-contained deployment.

---

## 3. `standards-picker.js` (detailed)

**Loaded by:** `index3.html` only.

**Exports:** `initStandardsPicker(options)` (IIFE pattern).

**Typical options:**

| Option | Meaning |
|--------|---------|
| `cleanedRows` | Parsed **`standards_cleaned.json`** array |
| `cleanedUrl` | URL used for debugging / reload |
| `categoryInput`, `taskInput` | Text inputs bound to datalists |
| `categoryDatalist`, `taskDatalist` | `<datalist>` elements |
| `categoryKeywords` | From **`standards_keywords_upgraded.json`** — keyword → ref list |
| `categoryLabels` | Optional ordered list (merged with `/places` when API works) |
| `onRowResolved` | Callback with full row object when category + task match uniquely |

**Data flow:**

1. User types category → filter categories by keyword or substring.
2. User selects task → filter `cleanedRows` where `category` and `task_or_activity` match.
3. On unique row, `onRowResolved(row)` fires → `lastResolvedStandardRow` in `index3.html`.

**Failure modes:** Missing JSON → empty datalists; ambiguous task → row not resolved until disambiguated.

---

## 4. `standard-display.js` (detailed)

**Loaded by:** `result.html`.

**Purpose:** Display **`standard_lighting`** objects with **consistent labels** (e.g. “Reference no.” instead of raw `ref_no`).

**Mechanism:**

- Fetches **`standards/aliases_upgraded.json`** once (cached).
- Maps cleaned keys (`Em_r_lx`, `Uo`, …) through **`CLEANED_TO_ALIAS_PARAM`** to alias keys, then to display strings.
- **`FALLBACK_LABELS`** if alias file missing.

**Extending:** Add keys to `aliases_upgraded.json` **and** optional entries in `FALLBACK_LABELS` for offline resilience.

---

## 5. `standards/` (front-end readable)

| File | Role |
|------|------|
| **`standards_cleaned.json`** | Rows: `ref_no`, `category`, `task_or_activity`, `Em_r_lx`, `Uo`, … — **source of truth** for picker + API |
| **`standards_keywords_upgraded.json`** | Category keywords, metadata |
| **`aliases_upgraded.json`** | Human labels for parameters |

These are **static files**; Flask **`/places`** may mirror or extend categories for the picker when online.

---

## 6. Naming conventions (JS/HTML)

| Pattern | Example |
|---------|---------|
| **DOM ids** | `dimA`–`dimD`, `dimHeight`, `stdCategory`, `stdTask` |
| **localStorage** | `luxscale_result_rows_{token}`, `luxscale_result_request_{token}`, `luxscale_result_links` |
| **API fields** | PascalCase keys in result rows (`Luminaire`, `Spacing X (m)`) with snake_case duplicates for legacy consumers |

---

## 7. Future modularization

Candidates to extract to **`assets/modules/`** (ES modules or IIFE bundles):

| Module | Contents |
|--------|----------|
| `api-config.js` | `getCalculateApiUrl`, `getUiSettingsApiUrl`, `getPlacesApiUrl` — single source for localhost vs production |
| `ceiling-validation.js` | `validateCeilingHeightM` + default bounds (mirror server) |
| `submit-study.js` | Retry loop over PHP/Flask submit endpoints |

---

Next: [api-client-and-state.md](./api-client-and-state.md).
