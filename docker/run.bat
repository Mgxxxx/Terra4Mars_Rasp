@echo off
setlocal

set SCRIPT_DIR=%~dp0
for %%i in ("%SCRIPT_DIR%..") do set PROJECT_ROOT=%%~fi

docker run -it --rm ^
    --name terra4mars ^
    --privileged ^
    --net=host ^
    -v /dev:/dev ^
    -v "%PROJECT_ROOT%\rover_commands:/home/xplore/dev_ws/src/rover_commands" ^
    terra4mars:latest

endlocal
