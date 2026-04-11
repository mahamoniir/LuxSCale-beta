# Three.js and the `maha/` 3D track

## 1. Relationship to the main product

| Fact | Detail |
|------|--------|
| **Main UX** | `index2` / `index3` → **`result.html`** has **no** Three.js dependency. |
| **`maha/`** | Separate **WebGL** prototypes: visualize a room, luminaire positions, spacing grid, dimensions. |
| **Photometry** | Real **lux / U₀** come from the **Python** IES pipeline, not from Three.js materials. |

Treat Three.js here as **communication and design validation**, not a lighting compliance engine.

---

## 2. File and dependency layout

```
maha/
  js/
    three.min.js      # Legacy UMD build, global THREE
    OrbitControls.js  # Attaches THREE.OrbitControls (legacy pattern)
  3d_model.html       # Full-featured scene
  test.html             # Alternate materials + sRGB
  solid.html            # Minimalist room + fixtures
  3d_view.html          # JSON-driven high-bay viewer
  view.html
  index.html, in.html   # 2D canvas + API demos
```

**Version:** The bundled `three.min.js` follows the **global script** pattern (r125-era style). Upgrading requires checking **`OrbitControls`** API compatibility or switching to **ES modules**.

---

## 3. Scene construction (typical pattern)

Every full viewer follows the same skeleton:

### 3.1 Renderer and canvas

```text
WebGLRenderer({ antialias: true })
  → setSize(window.innerWidth, window.innerHeight)
  → appendChild(renderer.domElement) to document.body
```

Some files set **`renderer.outputEncoding = THREE.sRGBEncoding`** (`test.html`) for more correct albedo display on modern Three.js builds.

### 3.2 Camera and controls

```text
PerspectiveCamera(fov, aspect, near, far)
OrbitControls(camera, renderer.domElement)
  → enableDamping, min/max distance as needed
```

### 3.3 Lights

| Light type | Typical use |
|------------|-------------|
| `AmbientLight` | Fill |
| `DirectionalLight` | Sun-like key (shadow-capable if enabled) |
| `PointLight` | Near a fixture in `3d_model.html` for local glow |

Shadows are **not** always enabled; enabling them increases GPU cost.

### 3.4 Room geometry

| Part | Implementation |
|------|----------------|
| Floor / ceiling | `PlaneGeometry`, rotated to horizontal |
| Box walls | `BoxGeometry` with known width/height/thickness |
| Front wall with door | `Shape` + `Path` hole → **`ExtrudeGeometry`** (`3d_model.html`, `test.html`, `solid.html`) |

Room dimensions are often **hardcoded variables** (`roomWidth`, `roomLength`, `wallHeight`) at the top of the script — good candidates for **query parameters** or **`postMessage`** from `result.html`.

### 3.5 Luminaire representation

**Group** per fixture:

- **Stem:** `CylinderGeometry`
- **Housing / dome:** `SphereGeometry` with phi limits (hemisphere) or similar
- **Lens:** `CircleGeometry` + emissive or basic material
- **Optional beam:** `ConeGeometry` with **transparent** `MeshBasicMaterial`, `side: DoubleSide`
- **Optional glow:** small sphere with opacity

This is **symbolic** geometry, not CAD-accurate IES solids.

### 3.6 Annotations

| Technique | Use |
|-----------|-----|
| `Line` / `BufferGeometry().setFromPoints` | Grid outline, spacing ticks |
| `ArrowHelper` | Room axis dimensions (length / width / height labels in world space) |
| `Sprite` + `CanvasTexture` | Text labels (billboard sprites) |

---

## 4. Animation loop

```text
function animate() {
  requestAnimationFrame(animate);
  controls.update();
  renderer.render(scene, camera);
}
animate();
```

**Resize handler:** update `camera.aspect`, `camera.updateProjectionMatrix()`, `renderer.setSize`.

---

## 5. Performance checklist

| Technique | Why |
|-----------|-----|
| **`setPixelRatio(Math.min(window.devicePixelRatio, 2))`** | Avoids 3× retina fill cost |
| **Merge static meshes** | Fewer draw calls for large static rooms |
| **Reuse `BufferGeometry`** | Clone or instancing for repeated fixtures |
| **Disable shadows** | Unless needed for marketing screenshots |
| **Cap cone/beam segments** | `ConeGeometry(radius, height, radialSegments)` — lower segments on mobile |
| **Dispose on teardown** | `geometry.dispose()`, `material.dispose()`, `renderer.dispose()` when embedding in SPA or iframe |

---

## 6. Integrating with calculator output (recommended)

Map **`result.html`** / API JSON to viewer inputs:

| API field | 3D use |
|-----------|--------|
| `length`, `width` (or sides) | Floor `PlaneGeometry` size |
| `height` | Wall height, camera far plane |
| `Fixtures` | Count → grid `nx` × `ny` from spacing logic (match backend `best_x`, `best_y`) |
| `Spacing X (m)`, `Spacing Y (m)` | Distance between luminaire centres |
| `Luminaire` | Icon choice (highbay vs panel — different prefab Group) |

**Delivery options:**

1. **Query string:** `3d_model.html?L=5&W=4&H=3&nx=2&ny=2` (short, limited size).
2. **`postMessage`** from parent `result.html` iframe.
3. **Shared `sessionStorage`** key (same tab).

---

## 7. Migration path to modern Three.js

| Step | Action |
|------|--------|
| 1 | Add **npm** `three` + Vite rollup, or import map in dev |
| 2 | Replace globals with `import * as THREE from 'three'` |
| 3 | `import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js'` |
| 4 | Optional: **React Three Fiber** if the rest of the app moves to React |

---

## 8. React Three Fiber (future)

If using React:

- **`@react-three/fiber`** — declarative scene (`<mesh>`, `<ambientLight>`).
- **`@react-three/drei`** — `OrbitControls`, `Environment`, `Html` labels.
- **Benefits:** Automatic **dispose** on unmount, props-driven room size, easier unit tests with mocked canvas.

---

## 9. Security

- Do not **`eval`** user input when parsing room parameters.
- If loading **external** GLTF/IES-based meshes later, validate origins (CORS + CSP).

---

Next: [styling-and-accessibility.md](./styling-and-accessibility.md).
