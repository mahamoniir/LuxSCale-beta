# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Quick Start

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

API endpoints: `POST /calculate`, `POST /pdf`, `GET /api/get?token=...`

## Architecture Overview

LuxScaleAI is a lighting design platform with three layers:

1. **Flask API (`app.py`)** - Exposes `/calculate`, `/pdf`, and admin routes. Accepts room geometry (`sides`, `height`) + functional requirement (`place` or `standard_ref_no`), returns fixture options with spacing/lux/uniformity.
2. **Calculation Engine (`luxscale/lighting_calc/`)** - Lumen-method calculations + IES photometric grid analysis for uniformity (U₀). Key modules:
   - `calculate.py` - Main algorithm: fixture count search, spacing optimization, IES uniformity evaluation
   - `geometry.py` - Room area (cyclic quadrilateral), zone determination, spacing constraints
   - `constants.py` - Luminaire catalog, efficacy tables, place definitions
3. **Frontend** - Modern pages (`index2.html`, `result.html`) + legacy variants. Submit studies via PHP (`api/submit.php`) or Python (`/api/submit`), retrieve by token (`/api/get`).

## Key Design Decisions

- **Dual input modes**: Calculator places (legacy `define_places`) OR standards-based (EN 12464-1 via `standards_cleaned.json` with `Em_r_lx` + `Uo`)
- **IES-backed uniformity**: When IES files exist, computes point-by-point grid uniformity (U₀, U₁) with inter-reflection estimates
- **Fast mode**: `fast=true` caps at 3 options, coarser fixture steps—useful for UI previews
- **Fallback strategy**: When no compliant solution exists, returns "closest non-compliant" + optional uniformity sweep upward in fixture count

## Data Flow

```
Browser → POST /calculate → calculate_lighting() → [IES uniformity eval] → results[] → Browser
Browser → POST /api/submit → stores JSON → returns token
Browser → GET /api/get?token=XXX → loads study JSON → result.html renders
```

## Standards Directory

- `standards/standards_cleaned.json` - Canonical EN 12464-1 rows (ref_no, category, task, Em_r_lx, Uo, etc.)
- `standards/standards_keywords_upgraded.json` - Category/task search keywords
- `standards/aliases_upgraded.json` - Ref_no alias mapping

## Fixture Catalog

- `assets/fixtures_online.json` + `assets/ies_fixture_map.json` - Map luminaire names + powers to IES files under `ies-render/SC-Database/`
- IES params parsed by `luxscale/ies_*.py`: beam angle, lumens, candela distribution

## Admin Routes

- `/api/admin/login`, `/api/admin/logout` - Session + bearer token auth
- `/api/admin/settings` - App configuration (maintenance factor, max solutions, reflectance presets)
- `/api/admin/fixture-map` - Edit IES fixture mapping

## AI Analysis Pipeline

Post-calculation AI analysis for quality scoring and improvement suggestions:

- **Endpoint**: `POST /api/ai/analyze` (body: `{token: "..."}` or inline payload)
- **Modules**:
  - `luxscale/ai_routes.py` - Flask endpoints (`/api/ai/analyze`, `/api/ai/approve-fix`, `/api/ai/status`)
  - `luxscale/gemini_manager.py` - Multi-account waterfall orchestrator (quota tracking, rate limit handling)
  - `luxscale/ollama_manager.py` - Local Ollama model interface (free, unlimited)
  - `luxscale/ai_prompt.py` - Shared prompt builder (identical format for all AI sources)
  - `gemini_config.json` - Runtime config: accounts, API keys, `ollama_priority`, `min_confidence`
  - `gemini_snapshot.json` - Last approved analysis (fallback when all AI sources unavailable)

**Waterfall order** (controlled by `ollama_priority` in `gemini_config.json`):
- `ollama_priority: true` → Ollama → Gemini accounts → Snapshot → Default
- `ollama_priority: false` → Gemini accounts → Ollama → Snapshot → Default

**Environment variables** (for Ollama):
- `OLLAMA_ENABLED=true`
- `OLLAMA_URL=http://localhost:11434`
- `OLLAMA_MODEL=llama3.2:3b`

## Technical Docs

See `PYTHON_TECHNICAL_DESCRIPTION.md` for algorithm details, module responsibilities, and refactor roadmap.
See `documentation/claude/AI_PIPELINE_DOCUMENTATION.md` for full AI pipeline architecture.
