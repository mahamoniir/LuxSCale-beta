# LuxScaleAI — Production Deployment URL Changes

Target host: `https://bkr3800.pythonanywhere.com`

---

## index3.html

### Line 572 — fallback calculate URL
**OLD:**
```
            return "https://mahamonir.pythonanywhere.com/calculate";
```
**NEW:**
```
            return "https://bkr3800.pythonanywhere.com/calculate";
```

---

### Line 578 — fallback places URL
**OLD:**
```
            return "https://mahamonir.pythonanywhere.com/places";
```
**NEW:**
```
            return "https://bkr3800.pythonanywhere.com/places";
```

---

### Line 584 — fallback ui-settings URL
**OLD:**
```
            return "https://mahamonir.pythonanywhere.com/api/ui-settings";
```
**NEW:**
```
            return "https://bkr3800.pythonanywhere.com/api/ui-settings";
```

---

### Lines 772–780 — submit endpoint resolution block
> These lines build a list of endpoints to try for saving results.
> On production (PythonAnywhere), `window.location.origin` IS the Flask
> server, so `fromCurrentPage` and `sameOriginRoot` will already resolve
> correctly. The localhost lines are harmless but will silently fail.
> **No change required** — the `origin + "/api/submit"` path on line 771
> handles PythonAnywhere automatically.

---

## index4.html

### Line 708 — fallback calculate URL
**OLD:**
```
            return "https://mahamonir.pythonanywhere.com/calculate";
```
**NEW:**
```
            return "https://bkr3800.pythonanywhere.com/calculate";
```

---

### Line 714 — fallback places URL
**OLD:**
```
            return "https://mahamonir.pythonanywhere.com/places";
```
**NEW:**
```
            return "https://bkr3800.pythonanywhere.com/places";
```

---

### Line 720 — fallback ui-settings URL
**OLD:**
```
            return "https://mahamonir.pythonanywhere.com/api/ui-settings";
```
**NEW:**
```
            return "https://bkr3800.pythonanywhere.com/api/ui-settings";
```

---

### Lines 908–916 — submit endpoint resolution block
> Same logic as index3.html above — the `origin + "/api/submit"` path
> handles PythonAnywhere automatically. **No change required.**

---

## result.html

### Line 335 — FLASK_BASE fallback
**OLD:**
```
  if (h === "localhost" || h === "127.0.0.1") return "http://127.0.0.1:5000";
```
**NEW:**
```
  if (h === "localhost" || h === "127.0.0.1") return "http://127.0.0.1:5000";
  return "https://bkr3800.pythonanywhere.com";
```
> This line sets `FLASK_BASE` which is used for `/api/report/` calls on
> lines 414 and 432. On PythonAnywhere the host check falls through and
> `FLASK_BASE` becomes undefined — add the return above so it resolves
> correctly in production.

---

### Lines 320–328 — api/get endpoint resolution block
> Same pattern as the submit block in index3/4 — on PythonAnywhere,
> `window.location.origin` is the Flask server, so `fromCurrentPage`
> resolves correctly. **No change required.**

---

### Lines 1155–1156 — ui-settings localhost fallback inside loop
> These are fallback attempts inside a loop that already tries all
> `API_ENDPOINTS`. They will fail silently on production and the function
> will continue. **No change required.**

---

## Summary — lines you MUST change

| File        | Line | What to replace                                    |
|-------------|------|----------------------------------------------------|
| index3.html | 572  | `mahamonir.pythonanywhere.com/calculate`           |
| index3.html | 578  | `mahamonir.pythonanywhere.com/places`              |
| index3.html | 584  | `mahamonir.pythonanywhere.com/api/ui-settings`     |
| index4.html | 708  | `mahamonir.pythonanywhere.com/calculate`           |
| index4.html | 714  | `mahamonir.pythonanywhere.com/places`              |
| index4.html | 720  | `mahamonir.pythonanywhere.com/api/ui-settings`     |
| result.html | 335  | Add `return "https://bkr3800.pythonanywhere.com";` |

---

## One-liner to apply all changes on PythonAnywhere bash

```bash
cd /home/bkr3800/LuxSCale

sed -i 's|mahamonir.pythonanywhere.com|bkr3800.pythonanywhere.com|g' index3.html index4.html result.html
```

Then fix `result.html` line 335 manually — add the production return line
after the localhost check so `FLASK_BASE` is set correctly on PythonAnywhere:

```bash
sed -i 's|if (h === "localhost" || h === "127.0.0.1") return "http://127.0.0.1:5000";|if (h === "localhost" \|\| h === "127.0.0.1") return "http://127.0.0.1:5000";\n  return "https://bkr3800.pythonanywhere.com";|' result.html
```

After editing, reload the web app from the **Web tab** on PythonAnywhere.
