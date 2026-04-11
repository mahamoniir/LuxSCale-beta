# Standard-based lux (index3) and export

## Goal

Replace the fixed **`define_places`** lux/uniformity pair for **index3** with **per–`ref_no` parameters** from **`standards/standards_cleaned.json`**, while carrying **all** relevant fields through the API, submit payload, and **result** exports (UI summary, PDF, CSV, WhatsApp) in a clear structure.

## Current behaviour

- **`calculate_lighting(place, sides, height)`** reads **`required_lux`** and **`required_uniformity`** only from **`define_places[place]`** in `lighting_calc.py`.
- **index3** combined Room function + standard pickers; Room function drove the calc, standard row was mostly metadata.

## Target behaviour

1. **index3** uses **only** standard category + task (datalists) and resolves a **single row** from **`standards_cleaned.json`** (`ref_no`, `Em_r_lx`, `Uo`, etc.).
2. **Calculation** uses:
   - **`Em_r_lx`** → **`required_lux`** (maintained illuminance target for fixture count / average lux check).
   - **`Uo`** → **`required_uniformity`** (stored on each result row as today; matches “uniformity” column semantics).
3. **Other fields** (`Em_u_lx`, `Ra`, `RUGL`, `Ez_lx`, `Em_wall_lx`, `Em_ceiling_lx`, `specific_requirements`, `category_base`, `category_sub`, `tasks`) are **not** fed into the spacing loop today; they are **exported** for reporting and traceability.
4. **Server trust**: Prefer resolving **`standard_ref_no`** via **`standards_cleaned.json`** on the server so lux targets are not silently tampered with; echo **`standard_row`** on **`/calculate`** responses.

## API contract

- **`POST /calculate`**
  - **`place`**: optional when **`project_info.standard_ref_no`** is present and resolves.
  - **`project_info.standard_ref_no`**: required for the standard-only flow.
  - Response may include **`standard_row`** (full row from cleaned JSON) when a ref was used.

- **`POST /pdf`**: Same resolution rules as **`/calculate`**.

## Frontend (index3)

- Remove **Room function** `<select>` and **`/places`** usage for calculator places (keep **`/places`** or static keywords for **category list** only).
- Before submit: require a resolved standard row (**`ref_no`**).
- Send **`project_info.standard_ref_no`** and a structured **`project_info.standard_lighting`** (all exported keys) for downstream storage.

## Results page (result.html)

- **Summary card**: Section **“Standard reference”** with labelled fields (ref, category, task, illuminance parameters, notes).
- **PDF / CSV / WhatsApp**: Include the same block so exports stay aligned; if **`place`** is absent, show **standard ref** instead of “Place”.

## Files touched

| File | Change |
|------|--------|
| `lighting_calc.py` | Optional **`standard_row`** → map **`Em_r_lx`**, **`Uo`**; keep **`define_places`** path when **`standard_row`** is absent. |
| `app.py` | Resolve row by ref; call **`calculate_lighting`** with **`standard_row`**; PDF route aligned. |
| `index3.html` | Remove room select; simplify config load; validate standard; payload without **`place`** (or null). |
| `result.html` | Summary + PDF + CSV + price message for **`standard_lighting`**. |

## Future (not in this step)

- Use **`Em_u_lx`** or cylindrical constraints in a richer uniformity model.
- Persist **`standard_lighting`** in **`submit.php`** schema if the DB stores a fixed column set.

---

## Troubleshooting: `{"message":"'place'","status":"error"}`

That response is a Python **`KeyError('place')`**: something used **`data["place"]`** while the JSON body had **no `place` key** (typical of an **older** `/calculate` handler that required `place`).

- **Run the LuxScaleAI `app.py`** from this repo (not `maha/app.py` / another copy that still does `place = data["place"]`).
- **Restart Flask** after pulling changes (no auto-reload unless you use `debug=True` or a reloader).

Current API uses **`data.get("place")`** and accepts **`project_info.standard_ref_no`** or top-level **`standard_ref_no`**.

---

## Implemented (this pass)

- **`lighting_calc.calculate_lighting(..., standard_row=None)`** — **`Em_r_lx`** → target lux, **`Uo`** → uniformity column (else 0.6).
- **`app.py`** — **`/calculate`** and **`/pdf`**: resolve **`standard_ref_no`** via **`standards_cleaned.json`**; **`place`** optional when ref resolves.
- **`index3.html`** — Room Function removed; submit requires resolved standard; **`project_info.standard_lighting`** sent (full export object).
- **`result.html`** — Summary block, PDF first page, CSV prefix (`Section,Field,Value`), WhatsApp line, **`generateCSV(..., request)`**.
