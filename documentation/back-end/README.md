# LuxScaleAI — Back-end documentation

Split reference for the **Python/Flask server**, **lighting calculation**, **IES photometry**, **compliance**, **logging**, and **deployment**.

## Document map

| # | File | Topic |
|---|------|--------|
| 1 | [architecture-and-runtime.md](./architecture-and-runtime.md) | Repo layout, `luxscale` package, entrypoint, environment variables |
| 2 | [flask-api-and-routes.md](./flask-api-and-routes.md) | Every HTTP route, auth, static files, standards resolution |
| 3 | [calculation-engine.md](./calculation-engine.md) | `calculate_lighting`: lumen method, spacing sweep, fast mode, heatmaps |
| 4 | [compliance-and-standards.md](./compliance-and-standards.md) | Standard rows, lux/U₀ gaps, `is_compliant`, fallback sweeps |
| 5 | [ies-catalog-and-resolution.md](./ies-catalog-and-resolution.md) | `fixture_map.json`, merged catalog, `resolve_ies_path`, folder scan |
| 6 | [ies-parsing-and-photometry.md](./ies-parsing-and-photometry.md) | LM-63 parser, `ies.json` index, JSON blobs, beam angle, caching |
| 7 | [uniformity-grid-and-reports.md](./uniformity-grid-and-reports.md) | `compute_uniformity_metrics`, work-plane grid, `uniformity_reports/*.txt` |
| 8 | [logging-and-artifacts.md](./logging-and-artifacts.md) | `luxscale_app.log`, `calculation_logs/`, traces, uniformity session files |
| 9 | [dependencies-and-python-libraries.md](./dependencies-and-python-libraries.md) | `requirements.txt`, NumPy, Matplotlib, FPDF, OpenAI note |
|10 | [deployment-local-and-production.md](./deployment-local-and-production.md) | Local Flask, XAMPP PHP API, CORS, Railway/port, admin dashboard bridge |

## Quick data flow

```
POST /calculate
  → validate_ceiling_height_m
  → _resolve_calculate_inputs (standards_cleaned row or place)
  → calculate_lighting(...)
       → determine_zone / determine_luminaire (catalog options)
       → lumen-method average lux + IES grid U₀
       → compliance rows + optional uniformity fallback
  → JSON + calculation_meta + optional trace file path
```

## Related

- Front-end: [../front-end/README.md](../front-end/README.md)
- Lighting (tool behaviour, standards): [../lighting/README.md](../lighting/README.md)
- Math (formulas, inequalities, pipeline, IES): [../math/README.md](../math/README.md)
- Parent index: [../README.md](../README.md)
