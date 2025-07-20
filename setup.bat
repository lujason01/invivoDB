@echo off
echo 🚀 Setting up InvivoDB Environment
echo ========================================

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

echo ✅ Python found
python --version

echo.
echo 🔄 Installing Python dependencies...
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo ❌ Failed to install some dependencies
    echo Try running manually: pip install -r requirements.txt
    pause
    exit /b 1
)

echo ✅ Dependencies installed successfully

REM Create necessary directories
if not exist "src\instance" mkdir "src\instance"
if not exist "src\web\static\uploads" mkdir "src\web\static\uploads"
if not exist "logs" mkdir "logs"

echo ✅ Created necessary directories

echo.
echo ========================================
echo 🎉 Setup completed!
echo.
echo To start the application:
echo    cd src\web
echo    python app.py
echo.
echo Then visit: http://localhost:5000
echo API Documentation: http://localhost:5000/api/v1/docs/
echo.
pause
