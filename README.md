# LuxScaleAI

LuxScaleAI is a lighting design platform that combines:
- a web UI for project input and result review,
- a Python calculation service for lighting recommendations,
- and server-side APIs that store/retrieve studies and support quoting workflows.

This README focuses on the Python-powered calculation pipeline and how it connects to the frontend.

## Project Overview

The repository currently contains:
- Modern frontend pages (`index2.html`, `result.html`, `about.html`) and legacy pages (`index.html`, `results.html`, `online-result.html`).
- Python lighting engines and API wrappers (`app.py`, `lighting_calc.py`, plus legacy/duplicate copies under `maha/` and `lighting_calc_old.py`).
- 3D visualization page (`maha/3d_model.html`) used to inspect fixture layout geometry.
- Static assets and standards JSON files.

## Python Components

## 1) `app.py` (root)

Flask API wrapper exposing:
- `POST /calculate`
- `POST /pdf`
- `GET /`

Core behavior:
- Accepts project inputs (`place`, `sides`, `height`, `project_info`).
- Calls `calculate_lighting()` from `lighting_calc.py`.
- Returns structured JSON results.
- Generates basic PDF reports using `FPDF`.
- Uses `flask_cors.CORS(app)` to allow browser clients.

Note:
- In production-like mode, it reads `PORT` from environment and binds `0.0.0.0`.

## 2) `lighting_calc.py` (root)

Primary lighting engine logic:
- Room/area evaluation (`cyclic_quadrilateral_area`).
- Zone classification by mounting height (`determine_zone`).
- Luminaire/power option selection (`determine_luminaire`).
- Spacing constraints by zone (`get_spacing_constraints`).
- Grid balancing (`calculate_spacing`).
- Final recommendation generation (`calculate_lighting`).

Outputs per option include:
- luminaire name,
- power and efficacy,
- fixture count,
- spacing X/Y,
- average lux,
- uniformity target,
- total power.

Utility functions for visuals/exports:
- `draw_heatmap`
- GUI export helpers (CSV/PDF) from legacy desktop workflow.

## 3) Legacy or Duplicate Python Files

- `lighting_calc_old.py`: earlier desktop-oriented implementation; contains hardcoded OpenAI key placeholder and GUI workflow.
- `maha/app.py`, `maha/lighting_calc.py`: duplicate branch of API/engine code used by older sub-project pages.

Recommendation:
- Treat root `app.py` + `lighting_calc.py` as the canonical Python service for future maintenance.

## Python Dependencies

From `requirements.txt` (core only):
- `Flask`, `flask-cors`, `fpdf`, `matplotlib`, `numpy`, `openai`

`tensorflow` and `scikit-learn` were removed: they are not imported by LuxScale’s Python code, and **TensorFlow has no PyPI wheels for Python 3.14**, which caused `pip install` to fail.

If you still see resolver noise on very new Python versions, use **Python 3.11 or 3.12** for the widest wheel support.

## API Contract (Python Service)

## `POST /calculate`

Request body:
```json
{
  "place": "Office",
  "sides": [5, 8, 5, 8],
  "height": 3,
  "project_info": {
    "project_name": "Example",
    "name": "Client Name",
    "company": "Company",
    "phone": "01000000000",
    "email": "client@example.com"
  }
}
```

Response (success):
```json
{
  "status": "success",
  "project_info": {},
  "results": [
    {
      "Luminaire": "SC downlight",
      "Power (W)": 9
    }
  ],
  "length": 8,
  "width": 5
}
```

## `POST /pdf`

Uses the same input payload and returns a generated PDF file download.

## Frontend Integration Notes

Current frontend flow generally works like this:
1. Browser calls Python `/calculate` API.
2. Browser posts selected result set to server-side submit API (`/api/submit.php` in web host stack).
3. Results page reads by token via `/api/get.php`.
4. Quote action can share result via WhatsApp and/or submit quote requests depending on page variant.

Important:
- On production pages, avoid `localhost` API URLs in browser JavaScript.
- Prefer same-origin or project-root relative URLs to avoid CORS failures.

## Running Python Service Locally (Quick Start)

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Default local API:
- `http://127.0.0.1:5000/calculate`
- `http://127.0.0.1:5000/pdf`

For a safe local workflow that does not impact online usage, read `tool_guide.md`.

## Python Technical Documentation

Detailed engineering documentation is available in:
- `PYTHON_TECHNICAL_DESCRIPTION.md`

It includes algorithm decisions, data flow, module responsibilities, and improvement roadmap.

## Security and Operational Notes

- Never hardcode secrets (API keys, SMTP credentials, tokens) in code.
- Keep production and local endpoints separated.
- Validate input server-side before calculations.
- Restrict CORS origins for production APIs if possible.
- Use isolated local environments for testing.

## Recommended Next Cleanup

- Consolidate duplicate Python files (`maha/` vs root).
- Remove unused heavy dependencies if not needed.
- Add automated tests for `calculate_lighting`.
- Move configuration (thresholds, lux targets, endpoint URLs) into external config files.