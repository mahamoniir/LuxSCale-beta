# Development plan — Room function & standards

This folder documents where **Room function / place** is defined in LuxScaleAI and how to evolve the UI toward **`standards/standards_keywords_upgraded.json`** with **datalist** inputs.

| Document | Purpose |
|----------|---------|
| [01-room-function-code-locations.md](01-room-function-code-locations.md) | Exact files and lines where “place” / Room function is chosen and consumed |
| [02-standards-json-datalist-upgrade.md](02-standards-json-datalist-upgrade.md) | How to wire `standards_keywords_upgraded.json` and replace `<select>` with two `<input list="…">` + `<datalist>` |
| [03-ies-sc-database-lighting-calc-integration.md](03-ies-sc-database-lighting-calc-integration.md) | SC-Database `.ies` paths and parser integration with `lighting_calc` |
| [05-ies-json-index-and-usage.md](05-ies-json-index-and-usage.md) | Split `ies.json` manifest + `ies_json/` photometry blobs; use in uniformity, spacing, and reporting |

Start with **01** for the current map, then **02** for the upgrade path.
