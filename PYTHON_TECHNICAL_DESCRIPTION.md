# Python Technical Description - LuxScaleAI

This document provides a technical engineering description of the Python subsystem in LuxScaleAI.

## 1) Scope and Runtime Context

The Python subsystem is responsible for:
- computing lighting recommendations from geometric and functional room inputs,
- returning machine-readable option sets to frontend/API consumers,
- generating report content (PDF support),
- supporting legacy desktop GUI export workflows (historical).

Primary runtime modes in this repository:
1. **Web API mode** (`app.py` + `lighting_calc.py`).
2. **Legacy desktop mode** (`lighting_calc.py` and `lighting_calc_old.py` GUI paths).

## 2) Module Inventory

## Root modules

- `app.py`
  - Flask application layer.
  - Exposes `/calculate` and `/pdf`.
  - Imports `calculate_lighting` and visual helpers from `lighting_calc.py`.
  - Applies `CORS(app)` for browser usage.

- `lighting_calc.py`
  - Core domain logic and engineering heuristics.
  - Computes fixture counts, spacing, lux output, and option ranking set.
  - Includes utility exporters/plotting and GUI entrypoint.

- `lighting_calc_old.py`
  - Older branch of similar logic.
  - Contains legacy OpenAI-related placeholder usage and GUI functionality.
  - Should be treated as archival unless explicitly needed.

## Duplicate branch under `maha/`

- `maha/app.py`, `maha/lighting_calc.py`
  - Parallel copies of root code with minor differences.
  - Represents maintenance risk due to logic divergence potential.

## 3) API Layer Design (`app.py`)

## Endpoint: `POST /calculate`

Input fields:
- `place` (string)
- `sides` (4-number list)
- `height` (number)
- `project_info` (object)

Execution path:
1. Parse JSON body.
2. Convert `height` to float.
3. Call `calculate_lighting(place, sides, height)`.
4. Return structured response:
   - `status`
   - `project_info`
   - `results`
   - `length`
   - `width`

Failure mode:
- broad `except Exception` -> HTTP 400 with message.

## Endpoint: `POST /pdf`

Input fields mirror `/calculate`.

Execution path:
1. Recompute results server-side.
2. Build PDF pages using `FPDF`.
3. Return binary stream as attachment.

Notes:
- PDF output is straightforward textual rendering.
- Heatmap/image embedding is richer in legacy GUI export path than in API path.

## 4) Calculation Engine Design (`lighting_calc.py`)

## 4.1 Domain constants

Core static dictionaries define:
- target lux and uniformity by place type (`define_places`),
- luminaire categories and available power sets (interior/exterior),
- efficacy assumptions (`led_efficacy`),
- maintenance factor (`maintenance_factor`),
- beam angle.

These constants are currently hardcoded in module scope.

## 4.2 Geometry model

The area is estimated using:
- `cyclic_quadrilateral_area(a, b, c, d)`
- Formula equivalent to Brahmagupta for cyclic quadrilateral approximation:
  - `s = (a + b + c + d) / 2`
  - `area = sqrt((s-a)(s-b)(s-c)(s-d))`

Operational behavior in current web UI often sends rectangular dimensions (`a==c`, `b==d`), which keeps this estimate practical.

## 4.3 Zone and luminaire selection

- `determine_zone(height)`:
  - `< 5m`: interior
  - `>= 5m`: exterior

- `determine_luminaire(height)`:
  - interior uses downlight/triproof/backlight sets.
  - higher heights progressively choose highbay powers.

## 4.4 Spacing strategy

- `get_spacing_constraints(zone)` returns min/max spacing bounds.
- `calculate_spacing(length, width, count, margin)` searches integer X/Y grid factors to minimize spacing difference (`|spacing_x - spacing_y|`).

This is a heuristic balancing approach, not an optimizer over photometric files.

## 4.5 Lux and fixture calculation

For each candidate `(luminaire, power, efficacy)`:
1. `lumens = power * efficacy`
2. `total_lumens_needed = (required_lux * area) / maintenance_factor`
3. `num_fixtures = int(total_lumens_needed / lumens) + 1`
4. Compute spacing from selected grid dimensions.
5. Clamp spacing to zone constraints.
6. Compute:
   - `avg_lux = (num_fixtures * lumens * maintenance_factor) / area`
   - `total_power = num_fixtures * power`
7. Accept option if `avg_lux >= required_lux`.

## 4.6 Output schema

Each result option contains:
- `Luminaire`
- `Power (W)`
- `Efficacy (lm/W)`
- `Fixtures`
- `Spacing X (m)`
- `Spacing Y (m)`
- `Average Lux`
- `Uniformity`
- `Total Power (W/H)` (or variant naming in old code)
- `Beam Angle (°)` in some paths

## 5) Legacy GUI and Export Subsystem

`lighting_calc.py` contains a Tkinter app (`run_gui`) that:
- collects project/client fields,
- executes the same calculation engine,
- allows CSV/PDF export,
- stores user history in `all_user_data.json`.

This path is decoupled from browser workflow but still present in source.

## 6) Data Flow Across Full System

Typical web flow:
1. Browser form sends payload to Python `/calculate`.
2. Browser receives options and normalizes keys.
3. Browser submits selected/processed payload to web-host API (`/api/submit.php`).
4. Result pages load by token through `/api/get.php`.
5. Optional quote workflow via WhatsApp and/or submit-price API path.

Important:
- Python service and PHP token persistence service are separate concerns.
- Browser endpoint strategy must avoid production `localhost` calls.

## 7) Dependencies and Their Actual Usage

Used directly in active API path:
- Flask
- flask-cors
- fpdf
- numpy
- matplotlib (mostly utility/legacy)

Optional / legacy:
- `openai` is referenced in `ask_ai_lux` in some `lighting_calc` variants but is not required for `/calculate` in `app.py`.

Removed from `requirements.txt` (not used by imports):
- `tensorflow` (also unavailable on Python 3.14 wheels)
- `scikit-learn`

## 8) Technical Risks and Limitations

1. **Duplicate code branches**
   - root and `maha/` copies can drift.

2. **Hardcoded constants**
   - lux targets, efficacy, spacing bounds should be externalized.

3. **Broad exception handling**
   - generic 400 messages hide root causes.

4. **No automated tests**
   - regression risk in formulas and output keys.

5. **Potential stale/unsafe legacy patterns**
   - hardcoded OpenAI placeholder key in old file.

6. **Output field naming drift**
   - `Total Power (W/H)` vs `Total Power (W)` across files.

## 9) Recommended Refactor Plan

Priority roadmap:
1. Make root Python modules canonical and deprecate duplicates.
2. Split engine into pure functions package:
   - `engine/geometry.py`
   - `engine/fixtures.py`
   - `engine/calc.py`
3. Add config layer (`json`/`yaml`) for standards and constants.
4. Add unit tests for:
   - area function,
   - zone selection,
   - fixture count and spacing constraints,
   - output schema contract.
5. Add API validation (Pydantic/Marshmallow or manual schema checks).
6. Normalize response field names and version API contract.

## 10) Local Validation Checklist (Python)

Before release:
1. Start API locally and test `/calculate` with representative room types.
2. Verify no negative/zero spacing outputs.
3. Verify `avg_lux >= required_lux` for each option.
4. Confirm frontend can parse all expected keys.
5. Confirm production pages do not reference localhost endpoints.

## 11) Quick Commands

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Smoke test:

```bash
curl -X POST "http://127.0.0.1:5000/calculate" ^
  -H "Content-Type: application/json" ^
  -d "{\"place\":\"Office\",\"sides\":[5,8,5,8],\"height\":3,\"project_info\":{\"project_name\":\"Tech Test\"}}"
```

---

For safe local testing procedures without affecting online usage, follow `tool_guide.md`.
