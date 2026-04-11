# Local Python Testing Safety Guide

This guide explains how to test LuxScaleAI Python components locally without affecting online usage.

## Goal

Run and validate Python calculations (`/calculate`, `/pdf`) on your machine while keeping production behavior unchanged.

## Safety Principles

1. **Never test against production endpoints directly.**
2. **Never keep `localhost` URLs in production-bound files when deploying.**
3. **Use an isolated Python environment (`venv`).**
4. **Keep local-only edits in a separate branch or temporary file variants.**
5. **Do not commit secrets or temporary endpoint overrides.**

## 1) Create an Isolated Local Environment

From project root:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Optional verification:

```bash
python --version
pip --version
pip list
```

## 2) Run Python API Locally

```bash
python app.py
```

Expected local server:
- `http://127.0.0.1:5000`

Test quickly:

```bash
curl -X POST "http://127.0.0.1:5000/calculate" ^
  -H "Content-Type: application/json" ^
  -d "{\"place\":\"Office\",\"sides\":[5,8,5,8],\"height\":3,\"project_info\":{\"project_name\":\"Local Test\"}}"
```

If this works, Python side is healthy.

## 3) Keep Frontend Testing Safe

## Recommended approach

Use local-only copies of pages for endpoint testing, for example:
- `index2.local.html`
- `result.local.html`

In those local files only, point calculate API to:
- `http://127.0.0.1:5000/calculate`

Do not change production deployment files unless you are intentionally preparing a release.

## Alternative approach

Use endpoint fallback logic that:
- tries same-origin production path first,
- falls back to localhost only when host is `localhost`/`127.0.0.1`.

This pattern already exists in parts of your project and is the safest long-term strategy.

## 4) Prevent Online Impact During Development

Before any deploy:

1. Search for local URLs:
   - `http://localhost`
   - `127.0.0.1`
2. Ensure production pages use same-origin or absolute production URLs.
3. Confirm CORS policy is valid for live domains.
4. Verify no local test artifacts are referenced.

Suggested checks:

```bash
rg "localhost|127\.0\.0\.1"
```

## 5) Validate Full Flow Safely

Recommended sequence:

1. Test Python `calculate` API locally via `curl`.
2. Open local frontend page and submit a sample study.
3. Check browser console for:
   - CORS errors,
   - endpoint resolution,
   - JSON parsing issues.
4. Verify result page load and export actions.
5. Verify WhatsApp copy/open behavior.

## 6) Rollback Checklist Before Deploy

Run before publishing:

```bash
git status
git diff
rg "localhost|127\.0\.0\.1" index2.html result.html online-result.html results.html spec.html
```

Ensure:
- no local URLs remain in production path,
- no debug-only code remains,
- no API keys/secrets are exposed.

## 7) Common Failure Modes and Safe Fixes

## CORS error on production

Cause:
- frontend calling `localhost` from live domain.

Fix:
- switch to same-origin endpoint (for example `./api/get.php`, `./api/submit.php`) or properly configured production API domain.

## `Failed to fetch` with status 200

Cause:
- response is not valid JSON (HTML/PHP warning output).

Fix:
- inspect response text first,
- harden parser and endpoint fallback,
- check server logs.

## Layout/export mismatch

Cause:
- export logic and 3D model logic diverge.

Fix:
- use shared placement formulas and persist same `lightingModelData`.

## 8) Recommended Operational Workflow

1. Develop locally in branch: `feature/local-python-testing`.
2. Validate API + frontend using local copies.
3. Merge only safe endpoint logic (host-aware fallback or same-origin).
4. Smoke test on staging domain.
5. Deploy to production.

---

If you want, this guide can be extended with a one-command PowerShell script that:
- activates venv,
- starts Python API,
- opens a local test URL,
- and runs automatic endpoint sanity checks.
