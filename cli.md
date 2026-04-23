# LuxScale IES CLI Commands

All commands below are for Windows PowerShell and should be run from the repo root.

```powershell
cd C:\xampp\htdocs\LuxScaleAI
```

Use `py` (recommended on Windows). If your machine uses `python` instead, replace `py` with `python`.

## Dataset truth (important)

Current runtime default in this repo:

- `LUXSCALE_IES_DATASET = SC_IES_Fixed_v3`
- `LUXSCALE_FIXTURE_MAP = fixture_map_SC_IES_Fixed_v3.json`

This default comes from `luxscale/ies_dataset_config.py` (`_DEFAULT_IES_DATASET` and `_DEFAULT_FIXTURE_MAP_BASENAME`).

Why `SC_FIXED` still appears in this document:

- It is a **legacy fallback path** kept for compatibility / old rebuild workflows.
- Section `## 4) Legacy SC_FIXED Rebuild (if needed)` is optional and only for teams still on the old dataset.

## 1) Reader / Parser Validation (IES file reading)

### 1.1 Check one file type + axis labels

```powershell
py ies-render/module/ies_parser.py --type "ies-render/examples/SC_IES_Fixed_v3/SC_FLOOD_100W.ies"
```

### 1.2 Full parser print for one file

```powershell
py ies-render/module/ies_parser.py "ies-render/examples/SC_IES_Fixed_v3/SC_FLOOD_100W.ies"
```

### 1.3 Parse all `.ies` files and report broken files

```powershell
py -c "import glob, sys; sys.path.insert(0, r'ies-render/module'); from ies_parser import IES_Parser, BrokenIESFileError; bad=[]; files=glob.glob(r'ies-render/**/*.ies', recursive=True); \
for p in files: \
    try: IES_Parser(p) \
    except Exception as e: bad.append((p, str(e))); \
print(f'files={len(files)} broken={len(bad)}'); \
[print(f'BROKEN: {p} :: {e}') for p,e in bad[:50]]"
```

### 1.4 Type distribution summary (C/B/A)

```powershell
py -c "import glob, sys; sys.path.insert(0, r'ies-render/module'); from ies_parser import IES_Parser; counts={}; \
for p in glob.glob(r'ies-render/**/*.ies', recursive=True): \
    try: d=IES_Parser(p).ies_data \
    except Exception: continue \
    key=(d.photometric_type, d.photometric_type_name, d.vertical_angle_label, d.horizontal_angle_label); counts[key]=counts.get(key,0)+1; \
[print(f'type={k[0]} ({k[1]}) V={k[2]} H={k[3]} count={v}') for k,v in sorted(counts.items())]"
```

## 2) Analyzer / Drawing Validation (plots + reports)

### 2.1 Full analysis (PDF + PNGs)

```powershell
py -m luxscale.ies_analyzer "ies-render/examples/SC_IES_Fixed_v3/SC_FLOOD_100W.ies"
```

### 2.2 PNG-only quick draw test

```powershell
py -m luxscale.ies_analyzer "ies-render/examples/SC_IES_Fixed_v3/SC_FLOOD_100W.ies" --no-pdf
```

### 2.3 JSON metrics export (includes type + angle labels)

```powershell
py -m luxscale.ies_analyzer "ies-render/examples/SC_IES_Fixed_v3/SC_FLOOD_100W.ies" --export-json --no-pdf --no-png
```

### 2.4 Interactive editor (roundtrip save test)

```powershell
py -m luxscale.ies_analyzer "ies-render/examples/SC_IES_Fixed_v3/SC_FLOOD_100W.ies" --edit --no-pdf --no-png
```

## 3) Build IES JSON Database (used by fixture selecting)

This is the runtime photometry database:

- `ies-render/ies.json` (manifest/index)
- `ies-render/ies_json/**/*.json` (per-file photometry blobs)

### 3.1 Build for default production dataset (`SC_IES_Fixed_v3`)

```powershell
py -m luxscale.ies_json_builder --clean-blobs --only-under examples/SC_IES_Fixed_v3
```

### 3.2 Rebuild fixture-selection map + snapshot catalog for same dataset

```powershell
py -m luxscale.regenerate_fixture_catalog --ies-dataset SC_IES_Fixed_v3 --out-map assets/fixture_map_SC_IES_Fixed_v3.json --out-catalog assets/fixture_ies_catalog_SC_IES_Fixed_v3.json
```

This regenerates the data used by fixture selection (`fixture_map*.json`) and keeps `photometry_json` links aligned with `ies.json`.

## 4) Legacy SC_FIXED Rebuild (if needed)

### 4.1 One-shot batch script

```powershell
.\ies-render\rebuild_database_from_sc_fixed.bat
```

### 4.2 Equivalent manual commands

```powershell
py -m luxscale.ies_json_builder --clean-blobs --only-under examples/SC_FIXED
py -m luxscale.regenerate_fixture_catalog
```

## 5) Post-build Sanity Checks

### 5.1 Check `ies.json` summary

```powershell
py -c "import json; d=json.load(open('ies-render/ies.json', encoding='utf-8')); print(d.get('layout')); print(d.get('summary'))"
```

### 5.2 Check fixture map entry count

```powershell
py -c "import json; d=json.load(open('assets/fixture_map_SC_IES_Fixed_v3.json', encoding='utf-8')); print('entries=', len(d.get('entries', [])))"
```

### 5.3 Verify runtime resolver returns a valid path

```powershell
py -c "from luxscale.ies_fixture_params import resolve_ies_path; print(resolve_ies_path('SC flood light exterior', 100))"
```

## 6) Important Runtime Step

After rebuilding `ies.json` / `ies_json` / `fixture_map`, restart the Flask app so caches reload.

