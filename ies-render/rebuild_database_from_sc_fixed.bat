@echo off
REM Rebuild LuxScale IES index + photometry blobs, then fixture_map / catalog snapshot.
REM Run from repo root is NOT required if this file lives under ies-render: we cd to parent.
set "REPO=%~dp0.."
cd /d "%REPO%"

echo === 1/2 luxscale.ies_json_builder (examples\SC_FIXED only) ===
py -m luxscale.ies_json_builder --clean-blobs --only-under examples/SC_FIXED
if errorlevel 1 exit /b 1

echo === 2/2 luxscale.regenerate_fixture_catalog ===
py -m luxscale.regenerate_fixture_catalog
if errorlevel 1 exit /b 1

echo Done. Restart the Flask app if it is running so IES caches reload.
exit /b 0
