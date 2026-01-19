@echo off
echo ========================================
echo Rebuilding Podman Container
echo ========================================

echo.
echo Step 1: Stopping existing container...
podman stop job-optimizer 2>nul
if %errorlevel% equ 0 (
    echo Container stopped successfully.
) else (
    echo No running container found, skipping...
)

echo.
echo Step 2: Removing old container...
podman rm job-optimizer 2>nul
if %errorlevel% equ 0 (
    echo Container removed successfully.
) else (
    echo No existing container found, skipping...
)

echo.
echo Step 3: Removing old image...
podman rmi localhost/job-optimizer:latest 2>nul
if %errorlevel% equ 0 (
    echo Image removed successfully.
) else (
    echo No existing image found, skipping...
)

echo.
echo Step 4: Building new image...
podman build -t job-optimizer .
if %errorlevel% neq 0 (
    echo ERROR: Build failed!
    pause
    exit /b 1
)

echo.
echo Step 5: Starting container...
podman run -d ^
    --name job-optimizer ^
    -p 8501:8501 ^
    --env-file .env ^
    -v "%cd%\ui:/app/ui:Z" ^
    -v "%cd%\agents:/app/agents:Z" ^
    -v "%cd%\models:/app/models:Z" ^
    -v "%cd%\utils:/app/utils:Z" ^
    -v "%cd%\sample_jobs.csv:/app/sample_jobs.csv:Z" ^
    job-optimizer

if %errorlevel% neq 0 (
    echo ERROR: Container failed to start!
    pause
    exit /b 1
)

echo.
echo ========================================
echo SUCCESS! Container is running
echo Access at: http://localhost:8501
echo ========================================
echo.
pause
