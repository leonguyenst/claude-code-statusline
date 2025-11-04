@echo off
REM Installation script for Claude Code Statusline (Windows)

setlocal enabledelayedexpansion

echo ========================================
echo   Claude Code Statusline - Installation
echo ========================================
echo.

REM Directories
set "CLAUDE_DIR=%USERPROFILE%\.claude"
set "STATUSLINE_PY=%CLAUDE_DIR%\statusline.py"
set "SETTINGS_JSON=%CLAUDE_DIR%\settings.json"

REM Check Python
echo [1/5] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% equ 0 (
    set "PYTHON_CMD=python"
    for /f "tokens=*" %%i in ('python --version') do set "PYTHON_VERSION=%%i"
    echo [OK] Found: !PYTHON_VERSION!
) else (
    python3 --version >nul 2>&1
    if %errorlevel% equ 0 (
        set "PYTHON_CMD=python3"
        for /f "tokens=*" %%i in ('python3 --version') do set "PYTHON_VERSION=%%i"
        echo [OK] Found: !PYTHON_VERSION!
    ) else (
        echo [ERROR] Python not found!
        echo Please install Python 3.6+ from https://www.python.org/
        pause
        exit /b 1
    )
)

REM Create .claude directory
echo [2/5] Creating .claude directory...
if not exist "%CLAUDE_DIR%" (
    mkdir "%CLAUDE_DIR%"
)
echo [OK] Directory ready: %CLAUDE_DIR%

REM Copy statusline.py
echo [3/5] Installing statusline.py...
if exist "%STATUSLINE_PY%" (
    echo [WARNING] Existing statusline.py found. Creating backup...
    copy "%STATUSLINE_PY%" "%STATUSLINE_PY%.backup.%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%" >nul
)
copy "statusline.py" "%STATUSLINE_PY%" >nul
echo [OK] Installed: %STATUSLINE_PY%

REM Configure settings.json
echo [4/5] Configuring settings.json...
if not exist "%SETTINGS_JSON%" (
    REM Create new settings.json
    (
        echo {
        echo   "statusLine": {
        echo     "type": "command",
        echo     "command": "%PYTHON_CMD% %STATUSLINE_PY%"
        echo   }
        echo }
    ) > "%SETTINGS_JSON%"
    echo [OK] Created new settings.json
) else (
    findstr /C:"statusLine" "%SETTINGS_JSON%" >nul
    if %errorlevel% equ 0 (
        echo [WARNING] statusLine already configured in settings.json
        echo Please manually update if needed:
        echo   "statusLine": {
        echo     "type": "command",
        echo     "command": "%PYTHON_CMD% %STATUSLINE_PY%"
        echo   }
    ) else (
        echo [WARNING] settings.json exists but statusLine not configured
        echo Creating backup...
        copy "%SETTINGS_JSON%" "%SETTINGS_JSON%.backup.%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%" >nul
        echo.
        echo Please manually add to settings.json:
        echo   "statusLine": {
        echo     "type": "command",
        echo     "command": "%PYTHON_CMD% %STATUSLINE_PY%"
        echo   }
    )
)

REM Test installation
echo [5/5] Testing installation...
echo {"model":{"display_name":"Test"},"workspace":{"current_dir":"."},"transcript_path":"","cost":{}} | %PYTHON_CMD% "%STATUSLINE_PY%" >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Test passed!
) else (
    echo [ERROR] Test failed!
    echo Please check your Python installation and try again.
    pause
    exit /b 1
)

echo.
echo ========================================
echo       Installation Complete!
echo ========================================
echo.
echo Next steps:
echo   1. Restart Claude Code to see your new statusline
echo   2. (Optional) Install ccusage for full features:
echo      npm install -g ccusage
echo.
echo Happy coding with Claude!
echo.
pause
