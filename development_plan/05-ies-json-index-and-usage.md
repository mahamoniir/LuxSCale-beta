# IES JSON index and photometry blobs

## What we store

After running `python -m luxscale.ies_json_builder` (from the repository root), the catalog is split into:

| Artifact | Role |
|----------|------|
| `ies-render/ies.json` | **Small manifest**: schema version, generation time, summary counts, and one row per `.ies` file with `header`, `derived`, `flags`, `photometry_json` (relative path to the blob), and parser metadata. No candela arrays here. |
| `ies-render/ies_json/<mirror path>.json` | **Large blob per file**: `photometry` (angles + candela-by-horizontal) and `polar.curves` (vertical-angle vs candela per horizontal plane). Mirrors the path of the source `.ies` under `ies-render/`, with `.ies` replaced by `.json`. |

Optional modes:

- `--legacy-monolithic` — single `ies.json` with everything inline (debug or one-file export only).
- `--meta-only` — manifest only; blobs not written (headers for CI or quick audits).
- `--clean-blobs` — delete `ies_json/` before rebuilding (drops stale blobs if files were removed).

Loader: `luxscale.ies_json_loader` (`load_ies_index`, `load_photometry_blob(relative_path)`).

### `assets/fixture_map.json` (API ↔ IES ↔ product images)

Generated with `python -m luxscale.fixture_map_builder` from the same catalog as `ies_fixture_params._IES_RELATIVE`. Each row ties:

- **`api_luminaire_name`** + **`power_w`** — matches the **`Luminaire`** and **`Power (W)`** fields returned by the calculate API.
- **`relative_ies_path`** / **`photometry_json`** — paths under `ies-render/` to the source `.ies` and the precomputed JSON blob (same strings as `ies.json` entries).
- **`image_urls`** — four rotation frames; naming matches `result.html` (`NAME_TO_BASE` + wattage + transparent0001..4).

Use this for UIs, PDFs, or services that need a single lookup from an API result row to photometry files and marketing images.

### Runtime integration (implemented)

1. **`resolve_ies_path`** (`luxscale.ies_fixture_params`) first uses **`assets/fixture_map.json`** (same rows as the generator); if missing or no match, falls back to the embedded `_IES_RELATIVE` map. Absolute paths are unchanged when both exist.

2. **`_load_ies_data_cached`** (used for beam, lumens metadata, and uniformity) **prefers catalog data**: if `ies-render/ies.json` points to a `photometry_json` blob and the file exists, **`luxscale.photometry_ies_adapter`** rebuilds the same **`IESData`** structure the LM-63 parser would produce from the binary `.ies` file (angles + candela table). **Illuminance and uniformity formulas are unchanged** — inverse-square law with candela scaling — only the numeric source is the pre-serialized catalog to avoid re-parsing text and to keep one consistent snapshot.

3. If the index or blob is missing, behavior falls back to **`IES_Parser`** on the `.ies` file (same math).

4. After regenerating `ies.json` or blobs, **`clear_ies_data_cache()`** in `ies_fixture_params` and **`clear_index_cache()`** in `ies_json_loader` run from the builder; long-lived Flask workers should restart or call those clears if you hot-swap files.

---

## How we will use this in calculations

### Uniformity (grid U0 / U1)

**Today:** `luxscale.uniformity_calculator` and `luxscale.lighting_calc.calculate` load photometry by parsing the **binary `.ies`** via `IES_Parser` (`luxscale.ies_fixture_params._load_ies_data_cached`).

**Planned use of JSON:**

1. **Fast path / offline tools:** Read the blob for the resolved `relative_path` (same string as in the manifest) and build an in-memory structure equivalent to `IESData` (vertical and horizontal angles + candela table). Feed that into the same illuminance summation as today, **without** running the LM-63 text parser again.
2. **Consistency:** The blob was generated from the same parser as runtime, so numeric results should match `.ies` parsing, modulo floating-point serialization.
3. **Fallback:** If a blob is missing or schema is old, fall back to parsing `.ies` from disk (current behavior).

**Why:** Avoids repeated parsing cost in batch jobs, enables uniformity precomputation or caching, and supports shipping precomputed photometry without distributing raw `.ies` if policy requires (not the default today).

### Spacing and fixture counts

**Today:** Spacing uses `calculate_spacing` (geometry), constraints from zone, and **lumen method** (target lux × area / maintenance → lumens per fixture → count). Beam angle for display comes from IES when header lumens are valid, else a catalog default.

**Planned use of JSON:**

1. **Index-only (no blob):** The manifest row already includes `header` (rated lumens, opening dimensions, shape), `derived.beam_angle_deg_half_power_vertical_slice`, and `flags` (e.g. `non_positive_rated_lumens`). Spacing and option ranking can use **beam angle and effective lumens** without loading candela arrays.
2. **Blob when needed:** Refine beam or symmetry assumptions using actual photometry from the blob only when implementing stricter layout rules (e.g. aisle vs open area).

### Standards compliance and reporting

- **Required Uo** vs **calculated Uo:** Still from the grid engine; JSON blobs supply the candela field used in that engine when we switch to blob-backed photometry.
- **PDF / CSV / API:** Continue to expose the same result keys; data source (`.ies` vs JSON blob) is an implementation detail behind a small adapter.

### UI and polar visualization

- **Polar diagrams:** Use `polar.curves` from the blob (or recompute from `candela_by_horizontal_deg` + angle lists). The `ies-render` module `ies_polar.py` is **not** photometry; it is pixel geometry for thumbnails only.
- **Fixture thumbnails / 3D:** Unchanged; still driven by `ies-render` viewers or assets where applicable.

### Operational notes

- Regenerate the index after adding or replacing `.ies` files under `ies-render/`.
- Call `luxscale.ies_json_loader.clear_index_cache()` after regeneration if a long-running process already loaded the old index (the builder does this after a successful run).
- Entries with `non_positive_rated_lumens` still have valid candela tables in many cases; design lumens (power × efficacy) remain the fallback for scaling in uniformity, as implemented in `uniformity_calculator`.

---

## Relation to [03-ies-sc-database-lighting-calc-integration.md](./03-ies-sc-database-lighting-calc-integration.md)

Document 03 describes wiring the SC-Database **`.ies`** paths into `lighting_calc` and the IES parser. This document adds the **JSON mirror** of that photometry for indexing, tooling, and future cache paths; the physical `.ies` files remain the source of truth for regeneration.
