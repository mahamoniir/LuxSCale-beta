# Styling, theming, and accessibility

## 1. Design tokens (`:root` pattern)

Modern pages (**index2**, **index3**, **result**, **about**, **admin**) define CSS variables such as:

| Variable | Typical role |
|----------|----------------|
| `--fm-heading` | `"Anton", sans-serif` |
| `--fm-body` | `"IBM Plex Sans Arabic", sans-serif` |
| `--bg-dark` | Page background `#111` |
| `--white` / `--muted` | Text hierarchy |
| `--accent` | Brand red `#e51d2f` |
| `--glass` | Translucent panels `rgba(255,255,255,0.1–0.12)` |
| `--border` | Subtle borders on cards and headers |

**Headings:** Anton, uppercase or wide letter-spacing in hero areas.  
**Body:** IBM Plex Sans Arabic supports **Latin + Arabic** for bilingual UI.

---

## 2. Typography loading

```html
<link href="https://fonts.googleapis.com/css2?family=Anton&family=IBM+Plex+Sans+Arabic:wght@300;400;500;600;700&display=swap" rel="stylesheet">
```

Use **`font-display: swap`** (default in Google’s CSS) to reduce FOIT.

---

## 3. Layout patterns

| Pattern | Where |
|---------|--------|
| **Full-screen video** | `#myVideo` fixed, `object-fit: cover`, `z-index` below content |
| **Dark overlay** | Gradient `linear-gradient` on `.overlay` for text contrast |
| **Container** | `width: min(1120px, 92%); margin-inline: auto` |
| **Hero grid** | Two columns on desktop; stacks on narrow viewports |
| **Study form** | CSS grid `study-form-grid`, hidden via `[hidden]` or class until opened |

---

## 4. Bootstrap usage

**Bootstrap 5.3** is loaded on **`result.html`**, **`results.html`**, **`spec.html`**, **`online-result.html`**:

- **Grid** for report columns
- **Modals** for dialogs (if used)
- **Utilities** (`mb-3`, `text-muted`, etc.)

The marketing pages (**index2/index3**) are **Bootstrap-free** to keep custom branding.

---

## 5. Forms and validation

| Feature | Implementation |
|---------|----------------|
| **HTML5 validation** | `required`, `min`, `type="number"` on inputs |
| **Custom rules** | JS: rectangle equality, **`validateCeilingHeightM`** |
| **novalidate** | `index2`/`index3` study forms use `novalidate` to allow custom alert flow — ensure JS always validates before submit |

---

## 6. Accessibility (a11y) — current state and targets

### 6.1 What exists

| Item | Status |
|------|--------|
| **Semantic landmarks** | `header`, `main`, `footer`, `nav` on some pages |
| **Labels** | `<label for="dimA">` tied to inputs |
| **Video** | Decorative; no `prefers-reduced-motion` alternative documented |

### 6.2 Gaps (recommended backlog)

| Priority | Item |
|----------|------|
| High | **`aria-live="polite"`** region for calculation errors instead of only `alert()` |
| High | **Focus management** when opening/closing study panel (`focus()` first field, trap optional) |
| Medium | **Skip link** to main content |
| Medium | **Color contrast** audit on `--muted` vs `--bg-dark` |
| Low | **Reduced motion:** pause or hide video background when `prefers-reduced-motion: reduce` |

### 6.3 PDF output

pdf-lib generated PDFs are **not** automatically tagged for PDF/UA; if compliance PDFs are required, add tagging pass or server-side PDF.

---

## 7. Internationalization (i18n)

- **Fonts** support Arabic script; **content** is mostly English in current HTML.
- **RTL:** For Arabic-first layout, add `dir="rtl"` on `<html>` or a wrapper and mirror flex/grid as needed.

---

## 8. Print

Report pages may define **`@media print`** in places; ensure PDF export path matches on-screen critical fields.

---

Next: [roadmap-react-and-phases.md](./roadmap-react-and-phases.md).
