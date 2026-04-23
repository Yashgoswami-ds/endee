@echo off
REM Start Endee Vector Database Server on Windows

echo Starting Endee Vector Database...
echo.

docker run `
  --ulimit nofile=100000:100000 `
  -p 8080:8080 `
  -v ./endee-data:/data `
  --name endee-server `
  endeeio/endee-server:latest

if %ERRORLEVEL% EQU 0 (
    echo.
    echo Endee is running at http://localhost:8080
) else (
    echo.
    echo ERROR: Failed to start Endee
    echo Make sure Docker Desktop is installed and running
    echo.
    pause
)
