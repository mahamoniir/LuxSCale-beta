# Python dependencies and libraries

## 1. `requirements.txt` (declared)

```
Flask>=2.0
flask-cors
python-dotenv>=1.0
fpdf
matplotlib
numpy
openai
```

| Package | Usage in project |
|---------|------------------|
| **Flask** | HTTP API (`app.py`) |
| **flask-cors** | CORS for cross-origin browser clients |
| **python-dotenv** | Load **`.env`** at Flask startup |
| **fpdf** | **`/pdf`** route and legacy PDF generation |
| **matplotlib** | **`draw_heatmap`** and plotting helpers in `luxscale.lighting_calc` |
| **numpy** | Area/geometry (`cyclic_quadrilateral_area`), uniformity arrays, candela math |
| **openai** | Listed for optional/future features — **not required** for core `/calculate` |

**Python version:** Comment in `requirements.txt` suggests **3.10–3.14** for listed packages.

---

## 2. Standard library (heavy use)

| Module | Use |
|--------|-----|
| **`json`** | Standards, settings, API bodies, log detail serialization |
| **`os`, `pathlib`-style paths** | All file I/O |
| **`importlib.util`** | Dynamic load **`ies_parser.py`** |
| **`functools.lru_cache`** | IES data, settings, fixture map |
| **`datetime`, `time`** | Trace timestamps, perf_counter |
| **`threading`** | Admin token lock |
| **`secrets`** | Study tokens, admin tokens |
| **`re`** | `sc_ies_scan`, ref validation |
| **`tempfile`, `io`** | PDF buffer |

---

## 3. Internal “libraries” (project modules)

Not pip packages — **`luxscale.*`** as documented in [architecture-and-runtime.md](./architecture-and-runtime.md).

---

## 4. `ies-render` coupling

- **`ies-render/module/ies_parser.py`**: LM-63 **without** importing the full Qt viewer stack.
- Optional **NumPy** in other `ies-render` modules not imported by default calc path.

---

## 5. Installing

```bash
cd /path/to/LuxScaleAI
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

---

## 6. Optional dev dependencies (not in repo)

- **pytest** — unit tests for `geometry`, compliance helpers
- **ruff** / **black** — lint/format

---

Next: [deployment-local-and-production.md](./deployment-local-and-production.md)
