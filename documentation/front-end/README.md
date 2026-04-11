# LuxScaleAI — Front-end documentation

This folder contains **detailed**, **topic-split** documentation for the LuxScaleAI web interface. Read in order for a full picture, or jump to a single file.

| # | Document | Contents |
|---|----------|----------|
| 1 | [architecture-and-stack.md](./architecture-and-stack.md) | MPA model, tech stack table, build/deploy model, browser support |
| 2 | [pages-inventory.md](./pages-inventory.md) | Every HTML page: purpose, UI sections, scripts, user flows |
| 3 | [assets-and-modules.md](./assets-and-modules.md) | `assets/*` JS/CSS/JSON, `standards/`, shared patterns |
| 4 | [api-client-and-state.md](./api-client-and-state.md) | Flask/PHP endpoints, payloads, `localStorage` keys, errors |
| 5 | [threejs-and-maha.md](./threejs-and-maha.md) | Three.js usage, file map, performance, integration with calc |
| 6 | [styling-and-accessibility.md](./styling-and-accessibility.md) | CSS variables, fonts, Bootstrap, a11y checklist |
| 7 | [roadmap-react-and-phases.md](./roadmap-react-and-phases.md) | React decision, Vite, phased plan, quarterly roadmap |

**Related:** [../back-end/README.md](../back-end/README.md) (API, calculation, IES, logs); [../lighting/README.md](../lighting/README.md) (lumen method, uniformity, compliance math); parent [../README.md](../README.md).

---

## Quick orientation

- **Primary user journeys:** `index2.html` (room function) and `index3.html` (Egyptian code standards picker) → calculate → submit → **`result.html?token=…`**.
- **Legacy:** `index.html` uses `style.css` and older submit wiring to PHP.
- **3D prototypes:** `maha/` (Three.js) — not part of the main result pipeline unless embedded later.

---

*Maintainers: keep page-specific details in `pages-inventory.md` when adding new routes or assets.*
