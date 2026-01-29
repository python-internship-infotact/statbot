@echo off
echo Starting StatBot Pro Development Environment
echo ================================================

echo Starting backend server...
set ENVIRONMENT=development
start "Backend" python main.py

echo Waiting for backend to start...
timeout /t 3 /nobreak > nul

echo Starting frontend server...
cd frontend
if not exist node_modules (
    echo Installing frontend dependencies...
    npm install
)
start "Frontend" npm run dev

echo.
echo Both servers started successfully!
echo Backend API: http://localhost:8001
echo Frontend UI: http://localhost:8080
echo.
echo Press any key to stop servers...
pause > nul

echo Stopping servers...
taskkill /f /im python.exe /fi "WINDOWTITLE eq Backend*" 2>nul
taskkill /f /im node.exe /fi "WINDOWTITLE eq Frontend*" 2>nul
echo Servers stopped.