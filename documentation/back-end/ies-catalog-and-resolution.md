# IES catalog, merge, and path resolution

## 1. Overview

The back-end maps **(API luminaire name, wattage)** → **absolute path** to an **`.ies`** file under **`ies-render/`** using active dataset-aware sources:

1. **Examples dataset scan** via `scan_examples_ies_dataset(active_ies_dataset())`
2. Optional **storefront filtering** (`fixture_online_merge.calc_keys_allowed_by_storefront`)
3. Active fixture-map document rows (`fixture_catalog`) when direct entries exist

`merged_ies_relative_map()` returns `Dict[(luminaire_name, power_w), relative_path]` for the active dataset.

---

## 2. Generated JSON snapshot (not runtime-only)

`write_fixture_ies_catalog_json()` writes snapshot files for review/diff (for example dataset-specific `fixture_ies_catalog_*.json`).  
Runtime uses in-memory merged maps for the active dataset.

---

## 3. `sc_ies_scan` — active dataset scanning

`luxscale/sc_ies_scan.py` includes:

- `scan_examples_ies_dataset(dataset_name)` for `ies-render/examples/<dataset_name>/`
- Support for `SC_FIXED` and `SC_IES_Fixed_v3` with normalization overrides
- Legacy `SC-ies` helpers retained for compatibility, but active runtime merge is examples-dataset based

---

## 4. Active fixture map document

**`luxscale/fixture_catalog.py`**:

- Loads **`assets/<active_fixture_map_basename()>`** (cached).
- Each **entry** includes **`api_luminaire_name`**, **`power_w`**, **`relative_ies_path`**, **`ies_file_exists`**, image URLs, optional **`online`** block.

**`resolve_ies_path`** order (**`luxscale/ies_fixture_params.py`**):

1. **`fixture_entry_for_api(name, power)`** — if **`ies_file_exists`** and file on disk → return absolute path under **`ies-render/`**.
2. Else **`merged_ies_relative_map().get((name, int(power)))`** + **`normalize_relative_ies_path`** + join with **`IES_RENDER_ROOT`**.

`normalize_relative_ies_path` normalizes relative path forms under the active `ies-render` tree.

---

## 5. `catalog_luminaire_power_options()`

Used by **`determine_luminaire`**: builds **`{ luminaire: sorted unique wattages }`** from all keys of **`merged_ies_relative_map()`**.

---

## 6. Admin updates

`PUT /api/admin/fixture-map` overwrites **`assets/<active_fixture_map_basename()>`** and calls `clear_fixture_map_cache()` so the next resolve picks up new IES links.

---

## 7. “Database” wording

There is **no SQL database**. The **IES database** in product terms is:

- **Merged in-memory map** + optional **`fixture_ies_catalog.json`** snapshot  
- **`ies.json`** index + **`ies_json/*.json`** photometry blobs (see next doc)

---

Next: [ies-parsing-and-photometry.md](./ies-parsing-and-photometry.md)
