@echo off
echo Starting Anomaly Detection Frontend...
echo.

REM Check if node_modules exists
if not exist "node_modules\" (
    echo Installing dependencies...
    npm install
    echo.
)

echo Starting development server...
echo Frontend will be available at: http://localhost:3000
echo Backend should be running at: http://localhost:8000
echo.

npm start
