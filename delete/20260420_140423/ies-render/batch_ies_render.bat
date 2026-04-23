@echo off
setlocal enabledelayedexpansion

set "REPO=C:\xampp\htdocs\LuxScaleAI\ies-render"
set "IES_DIR=%REPO%\examples\SC_FIXED"
set "OUT_DIR=%REPO%\examples\SC_FIXED\results"
set "LOG=%OUT_DIR%\ALL_RESULTS.txt"

:: Create results folder
mkdir "%OUT_DIR%" 2>nul

:: Verify folder exists
if not exist "%OUT_DIR%\" (
    echo ERROR: Could not create results folder: %OUT_DIR%
    pause
    exit /b 1
)

:: Init combined log
echo IES Batch Render Results > "%LOG%"
echo Generated: %DATE% %TIME% >> "%LOG%"
echo ============================================================ >> "%LOG%"

echo.
echo Starting batch render...
echo Output folder: %OUT_DIR%
echo.

:: Loop over all .IES files
for %%F in ("%IES_DIR%\*.IES") do (

    echo Processing: %%~nxF

    set "TXTOUT=%OUT_DIR%\%%~nF.txt"

    :: Header to individual file
    echo ------------------------------------------------------------ > "!TXTOUT!"
    echo FILE: %%~nxF >> "!TXTOUT!"
    echo PATH: %%~fF >> "!TXTOUT!"
    echo ------------------------------------------------------------ >> "!TXTOUT!"

    :: Run run.py
    python "%REPO%\run.py" "%%~fF" >> "!TXTOUT!" 2>&1

    :: Append to combined log
    echo. >> "%LOG%"
    echo ------------------------------------------------------------ >> "%LOG%"
    echo FILE: %%~nxF >> "%LOG%"
    echo ------------------------------------------------------------ >> "%LOG%"
    type "!TXTOUT!" >> "%LOG%"

    echo   Done: %%~nF.txt
    echo.
)

echo ============================================================
echo All done!
echo Per-file TXT : %OUT_DIR%\filename.txt
echo Combined log : %LOG%
echo ============================================================
pause
