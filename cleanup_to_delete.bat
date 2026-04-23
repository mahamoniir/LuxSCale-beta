@echo off
setlocal EnableExtensions EnableDelayedExpansion

REM -----------------------------------------------------------------------------
REM Move likely-legacy / non-runtime files into delete\<timestamp>\ for safe testing.
REM This does NOT delete anything permanently.
REM -----------------------------------------------------------------------------

set "REPO_ROOT=%~dp0"
if not exist "%REPO_ROOT%app.py" (
  echo [ERROR] Could not find app.py next to this script.
  echo         Put cleanup_to_delete.bat in repo root and run again.
  exit /b 1
)

for /f %%I in ('powershell -NoProfile -Command "Get-Date -Format yyyyMMdd_HHmmss"') do set "STAMP=%%I"
set "DEST_ROOT=%REPO_ROOT%delete\%STAMP%"
if not exist "%DEST_ROOT%" mkdir "%DEST_ROOT%"

echo.
echo =====================================================================
echo  Cleanup staging (move only) - LuxScaleAI
echo =====================================================================
echo  Source repo : %REPO_ROOT%
echo  Move target : %DEST_ROOT%
echo.
echo  This script moves selected legacy/unreferenced files so you can test.
echo  Nothing is permanently deleted.
echo.
echo  Excluded on purpose (risky / legacy fallback still useful):
echo   - assets\fixture_map.json
echo   - ies-render\examples\SC_FIXED\  (except results + old analyzer below)
echo   - index3.html
echo   - index.html (still linked from index2/index3 nav; optional section below)
echo   - luxscale_deploy\
echo.
set /p "CONFIRM=Proceed with move list? (y/N): "
if /I not "%CONFIRM%"=="Y" (
  echo Cancelled.
  exit /b 0
)

echo.
echo [INFO] Starting moves...

REM ---- Auto-scan all archive files and move them (except existing delete\) ----
call :move_archive_files

REM ---- Docs / planning / snapshot copies ----
call :move_path "GemDocs"
call :move_path "guide"
call :move_path "development_plan"
call :move_path "tool_guide.md"
call :move_path "documentation\claude\AI_PIPELINE_DOCUMENTATION.html"
call :move_path "uniformity"
call :move_path "security_camera_lux_reference_guide_md.md"

REM ---- Legacy / standalone scripts ----
call :move_path "lighting_calc_old.py"
call :move_path "gemini_key_tester.py"
call :move_path "ies-render\batch.py"
call :move_path "ies-render\batch_ies_render.bat"
call :move_path "ies-render\examples\SC_FIXED\ies_analyzer.py"
call :move_path "ies-render\examples\SC_FIXED\results"

REM ---- Non-primary / alternate HTML pages ----
call :move_path "ai_panel_for_result_html.html"
call :move_path "charger.html"
call :move_path "index4.html"
call :move_path "online-result.html"
call :move_path "polar_modal_snippet.html"
call :move_path "res.html"
call :move_path "results.html"
call :move_path "spec.html"
call :move_path "pipeline\luxscaleai_full_pipeline_explorer.html"

REM ---- Orphan static assets (legacy) ----
call :move_path "style.css"
call :move_path "spritespin.min.js"

echo.
set /p "EXTRA=Also move review-first extras (can break old nav links)? (y/N): "
if /I "%EXTRA%"=="Y" (
  echo [INFO] Moving review-first extras...
  call :move_path "index.html"
)

echo.
echo [DONE] Move staging completed.
echo.
echo Verify your app, then delete manually if everything is good:
echo   %DEST_ROOT%
echo.
echo To restore all items manually, move files/folders back from:
echo   %DEST_ROOT%
echo to:
echo   %REPO_ROOT%
echo.
exit /b 0

:move_path
set "REL=%~1"
set "SRC=%REPO_ROOT%%REL%"
set "DST=%DEST_ROOT%\%REL%"

if not exist "%SRC%" (
  echo [SKIP] Not found: %REL%
  goto :eof
)

for %%P in ("%DST%") do set "DST_PARENT=%%~dpP"
if not exist "%DST_PARENT%" mkdir "%DST_PARENT%" >nul 2>&1

move "%SRC%" "%DST%" >nul
if errorlevel 1 (
  echo [FAIL] %REL%
) else (
  echo [MOVED] %REL%
)
goto :eof

:move_archive_files
echo [INFO] Scanning for *.zip *.rar *.7z (excluding delete\) ...
for /r "%REPO_ROOT%" %%F in (*.zip *.rar *.7z) do (
  set "ABS=%%~fF"
  if /I not "!ABS:%REPO_ROOT%delete\=!"=="!ABS!" (
    echo [SKIP] already in delete\: %%~fF
  ) else (
    set "REL=!ABS:%REPO_ROOT%=!"
    call :move_path "!REL!"
  )
)
goto :eof

