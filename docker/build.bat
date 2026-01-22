@echo off
setlocal

set SCRIPT_DIR=%~dp0
for %%i in ("%SCRIPT_DIR%..") do set PROJECT_ROOT=%%~fi

echo Building Docker image...
docker build --progress=plain -t terra4mars:latest -f "%SCRIPT_DIR%Dockerfile" "%PROJECT_ROOT%"

echo Build complete.
pause
endlocal
