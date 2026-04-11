# Roadmap, React evaluation, and phased delivery

## 1. Strategic goals (front-end)

| Goal | Metric / outcome |
|------|------------------|
| **Reliability** | Fewer failed studies due to endpoint mismatch; clear error messages |
| **Consistency** | One API base resolver; one validation source for ceiling height |
| **Trust** | Results page always shows IES-backed fields when API returns them |
| **Visualization** | Optional 3D preview aligned with calculated grid |
| **Maintainability** | Easier onboarding for developers (docs + optional modular JS) |

---

## 2. Should you adopt React?

### 2.1 Reasons **for** React (or similar)

| Benefit | Application to LuxScale |
|---------|-------------------------|
| **Component reuse** | Standard picker block, result row card, compliance badge, PDF toolbar |
| **State** | Multi-step flow (dimensions → standard → review → submit) without spaghetti DOM updates |
| **Ecosystem** | **React Three Fiber** for `maha` viewer; **react-pdf** alternative to hand-built pdf-lib flows |
| **Typing** | TypeScript interfaces for API responses (`CalculationMeta`, `StandardRow`) |
| **Testing** | React Testing Library for forms; MSW for API mocks |

### 2.2 Reasons **against** (or deferring)

| Cost | Detail |
|------|--------|
| **Build system** | Vite + npm CI; deploy pipeline change |
| **Migration effort** | `result.html` is large; pdf-lib integration must be regression-tested |
| **MPA simplicity** | Current XAMPP drop-in works without Node on the server |

### 2.3 Recommendation

| Phase | Approach |
|-------|----------|
| **Now** | Stay **MPA**; extract **`assets/api-config.js`**, **`assets/validation.js`** shared by index2/3 |
| **If** product adds auth, dashboards, real-time collaboration | Introduce **Vite + React** for a **`/app`** subtree or new host |
| **Three.js** | Either **iframe** existing `maha` pages or migrate to **R3F** after calc↔viewer contract is stable |

---

## 3. If you choose React: suggested stack

| Piece | Choice |
|-------|--------|
| **Bundler** | Vite 5+ |
| **UI** | React 18+ |
| **Typing** | TypeScript |
| **Routing** | React Router (MPA migration: `/`, `/study`, `/result/:token`) |
| **Server state** | TanStack Query for `/calculate` and `/api/get` |
| **3D** | `@react-three/fiber` + `@react-three/drei` |
| **PDF** | Keep **pdf-lib** in React, or **@react-pdf/renderer** for declarative docs |

**Folder suggestion:** `frontend/` or `client/` at repo root; build output to `dist/` deployed behind nginx or copied into Flask `static/`.

---

## 4. Phased development plan

### Phase 0 — Documentation (ongoing)

- [x] Split **`documentation/front-end/`** markdown set.
- [ ] Add **`documentation/api-contract.md`** (mirror Flask).

### Phase 1 — Hardening (no framework)

| Task | Outcome |
|------|---------|
| Central **`api-config.js`** | All pages resolve Flask vs production the same way |
| Shared **`ceiling-validation.js`** | DRY with server messages |
| **Error UI** | Replace critical `alert()` with dismissible banner + `aria-live` |
| **result.html** | Defensive JSON parse for API errors |

### Phase 2 — 3D integration (product optional)

| Task | Outcome |
|------|---------|
| URL or `postMessage` contract | `maha` reads L/W/H + fixture grid from calc |
| **Dispose** | No WebGL leak when leaving page |
| **iframe embed** | Tab “3D view” on `result.html` |

### Phase 3 — Developer experience

| Task | Outcome |
|------|---------|
| ESLint + Prettier for `assets/*.js` | Consistent style |
| Playwright smoke test | `index3` → mock API → assert token redirect |

### Phase 4 — React spike (optional)

| Task | Outcome |
|------|---------|
| Vite app with **one** route | Port standard picker + calculate only |
| Compare bundle size and DX | Go/no-go for full migration |

---

## 5. Quarterly roadmap (indicative)

| Quarter | Focus |
|---------|--------|
| **Q1** | Phase 1 hardening; api-config module |
| **Q2** | Phase 2 3D tab; document viewer parameters |
| **Q3** | Phase 3 tests; a11y pass on study forms |
| **Q4** | Phase 4 React spike **or** commit to modular MPA for another year |

Adjust dates to your release calendar.

---

## 6. Risk register (front-end)

| Risk | Mitigation |
|------|------------|
| **API host drift** | Single env-based config; document in deployment |
| **localStorage quota** | Don’t stash huge result sets; rely on server payload |
| **Three.js GPU crash** | Feature-detect WebGL; show static image fallback |
| **CORS** | Flask origins env; never use `*` with credentials |

---

## 7. Related documentation

| Topic | Location (planned or existing) |
|-------|--------------------------------|
| Flask routes | `documentation/backend/` (add separately) |
| Standards JSON | `documentation/standards-data/` |
| Deployment | `documentation/deployment/` |

---

*End of front-end split documentation set.*
