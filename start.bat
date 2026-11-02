@echo off
chcp 65001 >nul
echo ==================================================
echo   MiroFish (Swarm Intelligence Engine) Windows Launcher
echo ==================================================

where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Error: Python belum terpasang di sistem PATH.
    pause
    exit /b 1
)

where node >nul 2>nul
if %errorlevel% neq 0 (
    echo Error: Node.js belum terpasang di sistem PATH.
    pause
    exit /b 1
)

if not exist ".env" (
    if exist ".env.example" (
        copy .env.example .env >nul
        echo Berkas .env otomatis dibuat dari .env.example
    )
)

echo Menyalakan Backend API di port 5001...
start "MiroFish Backend" cmd /k "cd backend && python run.py"

echo Menyalakan Frontend di port 3000...
start "MiroFish Frontend" cmd /k "cd frontend && npm run dev"

echo Menunggu layanan siap...
timeout /t 3 /nobreak >nul

echo Membuka peramban di http://localhost:3000...
start http://localhost:3000

echo ==================================================
echo   MiroFish Berhasil Dijalankan!
echo ==================================================
