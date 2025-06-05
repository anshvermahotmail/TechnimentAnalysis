@echo off
setlocal enabledelayedexpansion

REM === Step 1: Find pip and python paths ===
for /f "delims=" %%i in ('where pip') do (
    set "PIP_PATH=%%i"
    goto :foundpip
)
:foundpip

for /f "delims=" %%i in ('where python') do (
    set "PYTHON_PATH=%%i"
    goto :foundpython
)
:foundpython

echo ?? Detected pip at: %PIP_PATH%
echo ?? Detected python at: %PYTHON_PATH%

REM === Step 2: Get pip's site-packages path ===
for /f "delims=" %%i in ('%PIP_PATH% show pip ^| findstr "Location"') do (
    set "PIP_SITE_PACKAGES=%%i"
)

REM Trim "Location: " prefix
set "PIP_SITE_PACKAGES=%PIP_SITE_PACKAGES:Location: =%"

echo ?? pip is installing to: %PIP_SITE_PACKAGES%

REM === Step 3: Get embedded python's site-packages path (based on its folder) ===
for %%i in ("%PYTHON_PATH%") do (
    set "PYTHON_DIR=%%~dpi"
)
set "PYTHON_DIR=%PYTHON_DIR:~0,-1%"  REM Remove trailing backslash
set "EMBED_SITE_PACKAGES=%PYTHON_DIR%\Lib\site-packages"

echo ?? Embedded Python site-packages expected at: %EMBED_SITE_PACKAGES%

REM === Step 4: Install desired packages ===
set PACKAGES=regex json5

echo ?? Installing packages via pip...
%PIP_PATH% install %PACKAGES%

REM === Step 5: Copy installed packages to embedded Python ===
echo ?? Copying packages...

for %%P in (%PACKAGES%) do (
    echo Copying %%P...
    xcopy /E /I /Y "%PIP_SITE_PACKAGES%\%%P" "%EMBED_SITE_PACKAGES%\%%P" >nul 2>&1
    xcopy /E /I /Y "%PIP_SITE_PACKAGES%\%%P-*" "%EMBED_SITE_PACKAGES%\" >nul 2>&1
)

echo ? Done copying to: %EMBED_SITE_PACKAGES%
pause
