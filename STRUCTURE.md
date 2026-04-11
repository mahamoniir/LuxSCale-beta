# LuxScaleAI - Project Structure Documentation

**Generated:** 2026-04-07

---

## Table of Contents

1. [Overview](#overview)
2. [Directory Structure](#directory-structure)
3. [Core Components](#core-components)
4. [File Relationships](#file-relationships)
5. [Duplicate & Unused Files](#duplicate--unused-files)
6. [Recommendations](#recommendations)

---

## Overview

LuxScaleAI is a lighting design platform that combines:
- Web UI for project input and result review
- Python calculation service for lighting recommendations
- Server-side APIs for storing/retrieving studies
- 3D visualization for fixture layout inspection

---

## Directory Structure

```
LuxScaleAI/
├── app.py                          # Main Flask API (root)
├── lighting_calc_old.py            # Legacy GUI app (Tkinter) - DUPLICATE
├── requirements.txt                # Python dependencies
├── README.md                       # Project documentation
├── STRUCTURE.md                    # This file
│
├── luxscale/                       # Main Python package (canonical)
│   ├── __init__.py
│   ├── ai_routes.py                # AI/NLP routes for standard selection
│   ├── app_logging.py              # Logging utilities
│   ├── app_settings.py             # Settings management
│   ├── calculation_trace.py        # Calculation trace/debugging
│   ├── fixture_catalog.py          # Fixture catalog management
│   ├── fixture_ies_catalog.py      # IES fixture catalog
│   ├── fixture_map_builder.py      # Fixture map builder
│   ├── fixture_online_merge.py     # Online fixture merge
│   ├── gemini_manager.py           # Gemini AI integration
│   ├── ies_dataset_config.py       # IES dataset configuration
│   ├── ies_fixture_params.py       # IES fixture parameters
│   ├── ies_json_builder.py         # IES JSON builder
│   ├── ies_json_loader.py          # IES JSON loader
│   ├── lighting_calc/              # Lighting calculation subpackage
│   │   ├── __init__.py
│   │   ├── ai_lux.py               # AI lux recommendation
│   │   ├── calculate.py            # Core calculation engine (CANONICAL)
│   │   ├── constants.py            # Calculation constants
│   │   ├── export_io.py            # Export I/O utilities
│   │   ├── geometry.py             # Geometry calculations
│   │   ├── gui.py                  # GUI utilities (legacy)
│   │   ├── plotting.py             # Plotting utilities
│   │   └── state.py                # State management
│   ├── paths.py                    # Path utilities
│   ├── photometry_ies_adapter.py   # IES photometry adapter
│   ├── regenerate_fixture_catalog.py
│   ├── sc_ies_scan.py              # SC IES scanner
│   └── uniformity_calculator.py    # Uniformity calculations
│
├── ies-render/                     # IES rendering utilities
│   ├── __init__.py
│   ├── batch.py                    # Batch processing
│   ├── run.py                      # Runner script
│   ├── run_v.py                    # Version runner
│   ├── examples/
│   │   └── SC_FIXED/
│   │       └── ies_analyzer.py
│   ├── module/
│   │   ├── __init__.py
│   │   ├── _ies_render_strategy.py
│   │   ├── ies_coverage.py
│   │   ├── ies_gen.py
│   │   ├── ies_parser.py
│   │   ├── ies_polar.py
│   │   ├── ies_viewer.py
│   │   └── utils.py
│   └── tests/
│       ├── __init__.py
│       ├── test_calc.py
│       └── test_ies_polar.py
│
├── api/                            # PHP API endpoints
│   ├── submit.php                  # Store study (returns token)
│   ├── get.php                     # Retrieve study by token
│   └── data/studies/               # Stored study JSON files
│
├── admin/
│   └── dashboard.html              # Admin dashboard
│
├── assets/                         # Static assets
│   ├── logo.svg
│   ├── favicon.svg
│   ├── myvideo.mp4                 # Background video
│   ├── app_settings.json           # UI configuration
│   ├── fixture_map.json            # Fixture image mapping
│   ├── fixture_map_SC_IES_Fixed_v3.json
│   ├── standard-display.js         # Standard display logic
│   └── standards-picker.js         # Standards picker UI
│
├── standards/                      # Standards JSON files
│   ├── standards_cleaned.json      # Cleaned standards data
│   ├── standards_keywords_upgraded.json
│   └── aliases_upgraded.json
│
├── maha/                           # LEGACY/SUB-PROJECT (mostly unused)
│   ├── app.py                      # Duplicate Flask API - DUPLICATE
│   ├── lighting_calc.py            # Duplicate calc engine - DUPLICATE
│   ├── config.php                  # PHP config
│   ├── 3d_model.html               # 3D visualization (USED)
│   ├── 3d_view.html                # Alternative 3D view
│   ├── solid.html                  # Solid view
│   ├── view.html                   # View page
│   ├── in.html                     # Input page
│   ├── index.html                  # Legacy index
│   ├── test.html                   # Test page
│   ├── test-ex.html                # Extended test
│   ├── vendor/                     # PHPMailer (via Composer)
│   └── js/                         # Three.js addons (for 3D views)
│       ├── animation/
│       ├── cameras/
│       ├── controls/
│       ├── curves/
│       ├── effects/
│       ├── exporters/
│       ├── geometries/
│       ├── interactive/
│       ├── libs/                   # Third-party JS libs
│       ├── lights/
│       ├── lines/
│       ├── loaders/
│       ├── math/
│       ├── modifiers/
│       ├── objects/
│       ├── physics/
│       ├── postprocessing/
│       ├── renderers/
│       ├── textures/
│       ├── utils/
│       └── viewers/
│
├── documentation/
│   └── claude/
│       └── AI_PIPELINE_DOCUMENTATION.html
│
├── pipeline/
│   └── luxscaleai_full_pipeline_explorer.html
│
├── HTML Files (Root)
│   ├── index.html                  # Legacy landing page - UNUSED
│   ├── index2.html                 # CURRENT main landing page
│   ├── index3.html                 # Alternative index - UNUSED
│   ├── result.html                 # CURRENT results page
│   ├── results.html                # Legacy results - UNUSED
│   ├── online-result.html          # Legacy online result - UNUSED
│   ├── about.html                  # About page (USED)
│   ├── ai_panel_for_result_html.html
│   ├── res.html                    # Unused result variant
│   ├── spec.html                   # Unused spec page
│   └── style.css                   # Stylesheet
│
└── spritespin.min.js               # 360° viewer library
```

---

## Core Components

### Python Backend

| File | Purpose | Status |
|------|---------|--------|
| `app.py` | Main Flask API (`/calculate`, `/pdf`, `/api/submit`, `/api/get`, admin routes) | **ACTIVE** |
| `luxscale/lighting_calc/calculate.py` | Core lighting calculation engine | **ACTIVE** |
| `luxscale/ies_fixture_params.py` | IES file parsing for photometry | **ACTIVE** |
| `luxscale/uniformity_calculator.py` | Point-by-point uniformity calculations | **ACTIVE** |
| `luxscale/ai_routes.py` | NLP for standard selection via Gemini | **ACTIVE** |
| `luxscale/gemini_manager.py` | Google Gemini AI integration | **ACTIVE** |
| `lighting_calc_old.py` | Old Tkinter GUI app with embedded OpenAI key placeholder | **DUPLICATE/UNUSED** |

### PHP Backend (XAMPP)

| File | Purpose | Status |
|------|---------|--------|
| `api/submit.php` | Store study JSON, return token | **ACTIVE** |
| `api/get.php` | Retrieve study by token | **ACTIVE** |
| `maha/config.php` | Legacy PHP config (PHPMailer setup) | **PARTIALLY USED** |
| `maha/vendor/` | PHPMailer dependency | **USED BY maha/config.php** |

### Frontend Pages

| File | Purpose | Status |
|------|---------|--------|
| `index2.html` | Main landing page with study form | **ACTIVE** |
| `result.html` | Results display page | **ACTIVE** |
| `about.html` | About page | **ACTIVE** |
| `maha/3d_model.html` | 3D fixture layout visualization | **ACTIVE** (linked from result.html) |
| `admin/dashboard.html` | Admin settings dashboard | **ACTIVE** |
| `index.html` | Original landing page | **LEGACY/UNUSED** |
| `index3.html` | Alternative index | **UNUSED** |
| `results.html` | Legacy results page | **UNUSED** |
| `online-result.html` | Legacy online result page | **UNUSED** |
| `res.html` | Result variant | **UNUSED** |
| `spec.html` | Specification page | **UNUSED** |
| `maha/index.html` | Maha sub-project index | **UNUSED** |
| `maha/in.html` | Maha input form | **UNUSED** |
| `maha/view.html` | Maha view page | **UNUSED** |
| `maha/test.html` | Test page | **UNUSED** |
| `maha/test-ex.html` | Extended test | **UNUSED** |
| `maha/solid.html` | Solid view | **UNUSED** |
| `maha/3d_view.html` | Alternative 3D view | **UNUSED** (3d_model.html is used) |

---

## File Relationships

### Request Flow

```
┌─────────────────┐
│  index2.html    │  User enters dimensions
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ POST /calculate │  Flask API (app.py)
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────┐
│ luxscale/lighting_calc/calculate.py │
│ - Geometry calculations             │
│ - IES photometry lookup             │
│ - Uniformity computation            │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────┐
│  result.html    │  Display results
└────────┬────────┘
         │
         ├──────────────┐
         │              │
         ▼              ▼
┌────────────────┐ ┌───────────────────┐
│ api/submit.php │ │ maha/3d_model.html│
│ Store study    │ │ View 3D layout    │
└────────┬───────┘ └───────────────────┘
         │
         ▼
┌─────────────────┐
│ api/get.php     │
│ Retrieve study  │
└─────────────────┘
```

### Module Dependencies

```
app.py
├── luxscale.app_logging
├── luxscale.calculation_trace
├── luxscale.app_settings
├── luxscale.lighting_calc (calculate.py, geometry.py, constants.py, etc.)
├── luxscale.ai_routes
│   └── luxscale.gemini_manager
├── luxscale.ies_dataset_config
├── luxscale.fixture_catalog
└── luxscale.uniformity_calculator
    └── luxscale.ies_fixture_params
        └── luxscale.ies_json_loader

luxscale/lighting_calc/calculate.py
├── luxscale.lighting_calc.geometry
├── luxscale.lighting_calc.constants
├── luxscale.ies_fixture_params
├── luxscale.uniformity_calculator
├── luxscale.app_settings
└── luxscale.app_logging
```

---

## Duplicate & Unused Files

### DUPLICATES (Safe to Remove)

| File | Reason | Action |
|------|--------|--------|
| `lighting_calc_old.py` | Duplicate of `luxscale/lighting_calc/calculate.py` with old Tkinter GUI code and hardcoded OpenAI key placeholder | **DELETE** |
| `maha/app.py` | Duplicate Flask API (simpler version, missing modern features) | **DELETE** |
| `maha/lighting_calc.py` | Duplicate calculation engine (outdated) | **DELETE** |

### UNUSED HTML PAGES (Safe to Remove)

| File | Reason | Action |
|------|--------|--------|
| `index.html` | Replaced by `index2.html` | **DELETE** |
| `index3.html` | Alternative index never used | **DELETE** |
| `results.html` | Replaced by `result.html` | **DELETE** |
| `online-result.html` | Legacy result page | **DELETE** |
| `res.html` | Unused result variant | **DELETE** |
| `spec.html` | Unused specification page | **DELETE** |
| `maha/index.html` | Maha sub-project not in use | **DELETE** |
| `maha/in.html` | Maha input form not in use | **DELETE** |
| `maha/view.html` | Maha view page not in use | **DELETE** |
| `maha/test.html` | Test page not in use | **DELETE** |
| `maha/test-ex.html` | Extended test not in use | **DELETE** |
| `maha/solid.html` | Solid view not in use | **DELETE** |
| `maha/3d_view.html` | Replaced by `3d_model.html` | **DELETE** |
| `ai_panel_for_result_html.html` | Unused AI panel template | **DELETE** |

### UNUSED DOCUMENTATION

| File | Reason | Action |
|------|--------|--------|
| `documentation/claude/AI_PIPELINE_DOCUMENTATION.html` | Internal documentation, can be moved or deleted | **OPTIONAL DELETE** |
| `pipeline/luxscaleai_full_pipeline_explorer.html` | Pipeline explorer not integrated | **OPTIONAL DELETE** |

### PARTIALLY USED - KEEP WITH CAUTION

| File/Folder | Reason | Action |
|-------------|--------|--------|
| `maha/vendor/` | PHPMailer used by `maha/config.php` only | Keep if maha config is needed, else DELETE |
| `maha/config.php` | Only used if maha pages are accessed | Consider DELETE with maha cleanup |
| `maha/js/` | Three.js addons used BY `maha/3d_model.html` | **KEEP** (required for 3D visualization) |

---

## Recommendations

### Immediate Cleanup (High Priority)

```bash
# Delete duplicate Python files
rm lighting_calc_old.py
rm maha/app.py
rm maha/lighting_calc.py

# Delete unused HTML pages
rm index.html
rm index3.html
rm results.html
rm online-result.html
rm res.html
rm spec.html
rm ai_panel_for_result_html.html

# Delete unused maha pages
rm maha/in.html
rm maha/view.html
rm maha/test.html
rm maha/test-ex.html
rm maha/solid.html
rm maha/3d_view.html
```

### Secondary Cleanup (Medium Priority)

```bash
# Optional: Remove entire maha/ directory EXCEPT 3d_model.html and js/
# This requires moving 3d_model.html and js/ to a maintained location first

# Or consolidate:
mv maha/3d_model.html visualization/
mv maha/js/ visualization/js-threejs-addons/
rm -rf maha/
```

### Configuration Updates

After cleanup, update these files to remove references to deleted files:

1. **result.html** - Verify all navigation links point to existing pages
2. **index2.html** - Update any references to legacy pages
3. **README.md** - Update file references if any point to deleted files

---

## Active Files Summary

### Python (Active)
- `app.py`
- `luxscale/` (entire package)
- `ies-render/` (entire package)

### PHP (Active)
- `api/submit.php`
- `api/get.php`

### HTML (Active)
- `index2.html`
- `result.html`
- `about.html`
- `admin/dashboard.html`
- `maha/3d_model.html`

### Assets (Active)
- `assets/` (all files)
- `standards/` (all JSON files)
- `spritespin.min.js`

---

## Notes

- The `maha/` directory appears to be a legacy sub-project that was partially integrated
- The 3D visualization (`maha/3d_model.html`) is still actively linked from `result.html`
- Three.js addons in `maha/js/` are required for the 3D visualization to work
- PHPMailer in `maha/vendor/` is only used if maha PHP pages are accessed
