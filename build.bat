@echo off
REM Build script for POS System

echo Building POS System executable...

python -m PyInstaller --clean --noconfirm POS.spec

if %ERRORLEVEL% neq 0 (
    echo.
    echo ============================================
    echo Build failed.
    echo Make sure PyInstaller is installed: pip install pyinstaller
    echo ============================================
    pause
    exit /b 1
)

echo.
echo ============================================
echo Build successful!
echo The executable is in the 'dist' folder.
echo ============================================
pause
