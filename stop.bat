@echo off
echo Menghentikan seluruh proses MiroFish di port 5001 dan 3000...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5001') do taskkill /f /pid %%a >nul 2>nul
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :3000') do taskkill /f /pid %%a >nul 2>nul
echo Seluruh proses MiroFish telah dihentikan.
