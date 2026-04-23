# Architecture and technology stack

## 1. Application model

LuxScaleAI’s browser UI is a **multi-page application (MPA)**:

| Trait | Detail |
|-------|--------|
| **Navigation** | Full page loads (`index2.html` → `result.html`) or same-origin links with query strings |
| **State** | Mostly **server-backed** (study JSON by token) plus **`localStorage`** for UX enhancement (stashed rows, standard payload) |
| **Bundling** | **None** on the main path: plain `<script>` tags, no Webpack/Vite requirement for core flows |
| **Hosting** | Static files can live on **Apache (XAMPP)**, **nginx**, or CDN; **Flask** (`app.py`) serves API and can serve static files in dev |

This keeps deployment simple for mixed PHP/Python stacks (e.g. XAMPP + Flask on another port).

---

## 2. Logical layers (front-end)

```
┌─────────────────────────────────────────────────────────────┐
│  Presentation: HTML + inline CSS + page-scoped <style>      │
├─────────────────────────────────────────────────────────────┤
│  Behavior: vanilla JS (fetch, DOM, localStorage)            │
├─────────────────────────────────────────────────────────────┤
│  Optional libs: pdf-lib, Bootstrap, Three.js (maha/)        │
├─────────────────────────────────────────────────────────────┤
│  APIs: Flask POST/GET JSON · optional PHP submit/get        │
└─────────────────────────────────────────────────────────────┘
```

There is **no** global SPA router; each HTML file owns its behavior.

---

## 3. Core technologies

| Layer | Technology | Notes |
|-------|------------|--------|
| **Markup** | HTML5 | Forms, semantic regions (`header`, `main`, `footer`), datalists for standards |
| **Styling** | CSS3 | Custom properties (`:root`), flex/grid, `clamp()` for typography, `backdrop-filter` on headers |
| **Script** | ES5–ES6 in browsers | `async/await`, `fetch`, `const`/`let` (assume modern evergreen browsers) |
| **Fonts** | Google Fonts | **Anton** (display headings), **IBM Plex Sans Arabic** (body, RTL-friendly) |
| **Video** | HTML5 `<video>` | Full-screen looped background on several pages (`assets/myvideo.mp4`) |

---

## 4. Third-party libraries (summary)

| Library | Delivery | Role |
|---------|----------|------|
| **pdf-lib** | jsDelivr CDN | Build PDFs on legacy/alternate pages (`results.html`, `spec.html`, `online-result.html`) |
| **Bootstrap 5.3** | jsDelivr CDN | Grid, utilities, modals on report pages |
| **Three.js** | Local `maha/js/three.min.js` | WebGL 3D room/fixture demos |
| **OrbitControls** | Local `maha/js/OrbitControls.js` | Camera orbit (legacy global build) |

Project-owned scripts (not npm in the main tree):

| File | Role |
|------|------|
| `assets/standards-picker.js` | Category/task → `standards_cleaned.json` row |
| `assets/standard-display.js` | Label mapping via `standards/aliases_upgraded.json` |

---

## 5. Back-end coupling

The front-end **does not** implement lighting physics; it sends **room geometry**, **ceiling height**, and either **place** or **standard reference** to the server.

| Service | Typical URL pattern | Protocol |
|---------|---------------------|----------|
| Flask calculate | `http://127.0.0.1:5000/calculate` (dev) | `POST` JSON |
| Flask places | `…/places` | `GET` JSON |
| Flask UI settings | `…/api/ui-settings` | `GET` JSON (ceiling bounds, pagination) |
| Flask submit | `…/api/submit` | `POST` JSON → `{ token }` |
| Flask get study | `…/api/get?token=` | `GET` JSON |
| PHP (optional) | `/LuxScaleAI/api/submit.php`, `get.php` | Same contract where deployed |

See [api-client-and-state.md](./api-client-and-state.md) for payloads and keys.
Current primary `result.html` downloads server-generated PDFs from `/api/report/<token>/...`.

---

## 6. Build, test, and CI

| Topic | Current state | Suggestion |
|-------|---------------|------------|
| **Lint** | No ESLint in repo root for static HTML | Add ESLint + Prettier for `assets/*.js` if team grows |
| **Minification** | Not applied to hand-written pages | Optional for production CDN |
| **E2E** | None documented | Playwright against `index3` + mock API for regression |

---

## 7. Browser support (practical)

Assumptions in code:

- `fetch`, Promises, `async`/`await`
- CSS `backdrop-filter` (progressive enhancement if missing)
- `localStorage` (result page stashing); private mode may throw — some calls are in `try/catch`

**IE11** is not a target.

---

## 8. Security notes (front-end)

| Topic | Practice |
|-------|----------|
| **Tokens** | Study tokens are opaque hex strings; passed in URL — avoid logging in shared environments |
| **XSS** | Prefer `textContent` when injecting user-facing strings; PDF generation paths should escape or sanitize project names |
| **CORS** | Flask `LUXSCALE_CORS_ORIGINS` env for allowed origins when front and API differ |
| **Admin** | `admin/dashboard.html` uses session/API token pattern — see back-end docs |

---

Next: [pages-inventory.md](./pages-inventory.md) for a file-by-file walkthrough of every page.
