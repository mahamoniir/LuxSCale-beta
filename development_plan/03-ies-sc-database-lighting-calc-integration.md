# IES library, SC-Database, and `lighting_calc.py` integration

## Short answer

**Yes, you can** use the Python code under `ies-render/`—primarily **`module/ies_parser.py`** (`IES_Parser` → `IESData`)—to read each `.ies` file in `ies-render/SC-Database` and extract photometric parameters (lumens from the file, candela arrays, angular sampling, luminaire dimensions, etc.).

**But:** `lighting_calc.py` today does **not** use photometric distributions. It uses **simple lumen-density** math (`lumens = power × efficacy`, then average illuminance on area). **Uniformity `Uo`** is taken from standards or presets, **not** computed from IES. So:

| Use case | Feasible with `IES_Parser` + SC-Database? |
|----------|-------------------------------------------|
| Replace **assumed** lm/W and **nominal** lumens with **IES-derived** total lumens (and optional beam metrics) | **Yes** (with a clear mapping from product → `.ies` path) |
| Replace fixed **120°** beam with an angle derived from candela (e.g. half-intensity cone) | **Yes** (derive from `IESData` numerically) |
| Compute **true** average illuminance and **true Uo** on a work plane from many fixtures | **Only with a new layer** (grid / radiosity / ray-style sampling), not by dropping a few numbers into the current formulas |

The **`*_complete.json`** files next to many `.ies` files are a **parallel export** (rich metadata + arrays). You may read them **instead of** parsing `.ies` at runtime, or use them to **validate** parser output—**but** they are not required if you always parse `.ies` with `IES_Parser`.

---

## What exists in the repo

### `ies-render/module/ies_parser.py`

- **`IES_Parser(path)`** reads LM-63 IES and returns **`IESData`** (`namedtuple`) with:
  - `vertical_angles`, `horizontal_angles`
  - `candela_values` — `dict` keyed by horizontal angle → list of candela per vertical angle
  - `max_value` (max candela)
  - `num_lamps`, `lumens_per_lamp`, `multiplier`
  - `width`, `length`, `height` (opening dimensions, meters after unit conversion)
  - `shape` (string classification from dimensions)

This is the **correct** library entry point for **numeric** photometry in Python inside this project.

### Other `ies-render` modules

- **`ies_polar.py`**: Cartesian ↔ polar for **image / render** geometry; not needed for a first pass of **calc-only** integration.
- **`ies_gen.py` / viewer**: Thumbnails and UI; optional for reports, not for core lux math.

### `ies-render/SC-Database`

Folder layout groups fixtures (e.g. `Highbay 150 w/`, `Flood 500 w/`). Typical files per product:

- `*.ies` — source photometry for `IES_Parser`
- `*_complete.json` — export with `metadata`, `lamp_info` (lumens, wattage fields—**verify** against datasheet; sample files may have placeholder watts)
- `*_summary.csv` — summary table where present
- `*.ies.json` — alternate JSON in some folders

You need a **single catalog** (YAML/JSON/Python dict) mapping **logical luminaire name + wattage** (what `lighting_calc.py` uses) → **filesystem path** to the right `.ies` (or to `_complete.json` if you prefer not to parse).

### `lighting_calc.py` (current behaviour)

Relevant parts:

- **`led_efficacy`**, **`beam_angle = 120`**, **`maintenance_factor`**
- **`calculate_lighting`**: `lumens = power * efficacy`, fixture count from total lumens needed, spacing search, then  
  `avg_lux = (num_fixtures * lumens * maintenance_factor) / area`  
  **`Uniformity`** is **not** calculated from optics—it is **`required_uniformity`** from `standard_row` or `define_places`.

So integrating IES is **not** a one-line swap: you decide **which** outputs of `IES_Parser` replace **which** constants, and whether you later add a **second** module for **distribution-based** illuminance (future work).

---

## Full integration plan (recommended phases)

### Phase 1 — Catalog + read parameters (no change to core formula)

1. Add a **fixture catalog** mapping `(luminaire_key, power_w)` → `Path` to `.ies` under `SC-Database` (or glob conventions).
2. Add a small module, e.g. `ies_fixture_params.py` (next to `lighting_calc.py` or under `ies-render` with `sys.path` / package), that:
   - Calls `IES_Parser(ies_path)`
   - Returns a plain dict/dataclass: `lumens_per_lamp`, `max_candela`, `vertical_angles`, optional **derived** `beam_angle_deg` (definition to freeze: e.g. FWHM on plane 0–180°).
3. In **`calculate_lighting`**, where you today set `lumens = power * efficacy`, optionally use **`lumens = ies["lumens_per_lamp"]`** (and keep `power` from your product line for **total_power** display). If IES lumens and **rated** watts disagree, define policy: **trust IES lumens** for flux, **trust catalog** for electrical watts.

### Phase 2 — Replace fixed beam angle where needed

1. Derive a scalar **beam angle** from candela vs angle (document the exact definition).
2. Use it wherever `beam_angle` is emitted in results (UI/export).

### Phase 3 — Real uniformity / illuminance grid (optional, large)

1. Implement a **work-plane grid** and sum **direct** illuminance from candela (inverse-square + cosine), for a single fixture then superpose.
2. Compare **simulated U0** to `standard_row["Uo"]`—this is a **new** product feature, not a tweak to the current formula.

### Cross-cutting

- **Tests**: One `.ies` from `SC-Database` in `pytest`, assert parser runs and lumens > 0.
- **Packaging**: Either install `ies-render` as a package or add `ies-render` to `PYTHONPATH`; avoid copying `ies_parser.py` twice.
- **Performance**: Cache `IESData` per path (LRU) if you call many times per request.

---

## Proposed new file (draft): `ies_fixture_params.py`

Place at project root next to `lighting_calc.py`, or under `ies-render` and import with package path. Adjust **`IES_RENDER_ROOT`** for your deployment.

```python
"""
Load photometric parameters from SC-Database .ies files using ies-render's IES_Parser.
"""
from __future__ import annotations

import os
from functools import lru_cache
from typing import Any, Dict, Optional

# Resolve repo root (example: LuxScaleAI/ contains both lighting_calc.py and ies-render/)
_REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
IES_RENDER_ROOT = os.path.join(_REPO_ROOT, "ies-render")

def _ensure_ies_render_on_path() -> None:
    if IES_RENDER_ROOT not in os.environ.get("PYTHONPATH", "") and IES_RENDER_ROOT not in __import__("sys").path:
        import sys
        if IES_RENDER_ROOT not in sys.path:
            sys.path.insert(0, IES_RENDER_ROOT)

@lru_cache(maxsize=128)
def load_ies_data(ies_path: str):
    _ensure_ies_render_on_path()
    from module.ies_parser import IES_Parser  # noqa: WPS433 (runtime import after path fix)
    return IES_Parser(ies_path).ies_data

def ies_params_for_file(ies_path: str) -> Dict[str, Any]:
    """Return a dict safe to merge into lighting_calc option rows."""
    if not os.path.isfile(ies_path):
        raise FileNotFoundError(ies_path)
    d = load_ies_data(ies_path)
    return {
        "ies_path": ies_path,
        "lumens_per_lamp": float(d.lumens_per_lamp) * float(d.multiplier),
        "num_lamps": int(d.num_lamps),
        "max_candela": float(d.max_value),
        "shape": d.shape,
        "opening_width_m": float(d.width),
        "opening_length_m": float(d.length),
        "opening_height_m": float(d.height),
    }

# Example: map your product key to a file under SC-Database (extend or replace with JSON catalog)
SC_DATABASE_ROOT = os.path.join(IES_RENDER_ROOT, "SC-Database")

def resolve_ies_path(luminaire_name: str, power_w: int | float) -> Optional[str]:
    """
    TODO: replace with real mapping from luminaire_name + power_w to .ies path.
    Returns absolute path or None if unknown.
    """
    # Placeholder: no glob here — you maintain an explicit dict or YAML.
    return None
```

---

## Proposed edits to `lighting_calc.py` (draft snippets — not applied)

**Goal:** When `resolve_ies_path(...)` returns a path, use **IES lumens** instead of `power * efficacy` for that option branch.

### 1) Imports (top of `lighting_calc.py`)

```python
# Optional IES-backed lumens (see development_plan/03-ies-sc-database-lighting-calc-integration.md)
try:
    from ies_fixture_params import resolve_ies_path, ies_params_for_file
except ImportError:
    resolve_ies_path = None
    ies_params_for_file = None
```

### 2) Inside `calculate_lighting`, inner loop where `lumens` is set

**Current (conceptually):**

```python
lumens = power * efficacy
```

**Proposed:**

```python
lumens = None
ies_meta = None
if resolve_ies_path and ies_params_for_file:
    ies_path = resolve_ies_path(lum_name, power)
    if ies_path:
        ies_meta = ies_params_for_file(ies_path)
        lumens = ies_meta["lumens_per_lamp"]
if lumens is None:
    lumens = power * efficacy
```

### 3) Optional: attach IES metadata to each result row

```python
row = {
    "Luminaire": lum_name,
    "Power (W)": power,
    # ... existing keys ...
}
if ies_meta:
    row["IES lumens (lm)"] = round(ies_meta["lumens_per_lamp"], 2)
    row["IES file"] = os.path.basename(ies_meta.get("ies_path", ""))
```

### 4) Beam angle

**Current:**

```python
"Beam Angle (°)": beam_angle
```

**Proposed (after you implement `beam_angle_from_candela(ies_data)`):**

```python
"Beam Angle (°)": derived_beam if derived_beam is not None else beam_angle
```

(Implement `derived_beam` in `ies_fixture_params.py` from `IESData`—definition of “beam angle” must be fixed in the spec.)

---

## Risks and checks

1. **Catalog accuracy**: `SC-Database` file names do not match `lighting_calc` names (`"SC highbay"` vs folder `Highbay 150 w`). You **must** maintain an explicit mapping.
2. **JSON vs IES**: `_complete.json` may be easier for batch inspection, but **`IES_Parser` is the single source of truth** aligned with LM-63 if you parse `.ies` directly.
3. **Wattage in JSON**: Some exports show inconsistent `wattage`; use **your** SKU power for **energy** columns if IES lists photometric lumens only.
4. **Uniformity**: Do **not** claim IES-based U0 until you implement a grid/simulation; keep passing **standard** Uo as today unless Phase 3 is done.

---

## Conclusion

- **Yes**: use **`ies-render/module/ies_parser.py`** to read **`ies-render/SC-Database/**/*.ies`** and feed **lumens** (and later **beam metrics**) into **`lighting_calc.py`**.
- **Not automatic**: you need a **catalog**, optional **caching**, and a **policy** for watts vs lumens.
- **Real optical uniformity** is a **separate** engineering step from wiring `IES_Parser` into the current lumen-density calculator.

When you approve this plan, implementation can proceed in order: **catalog → `ies_fixture_params.py` → conditional branch in `calculate_lighting` → tests**.

---

## See also

- **[05-ies-json-index-and-usage.md](./05-ies-json-index-and-usage.md)** — split `ies.json` manifest + `ies_json/` photometry blobs, regeneration with `luxscale.ies_json_builder`, and how we plan to use them for uniformity, spacing, and reporting.
