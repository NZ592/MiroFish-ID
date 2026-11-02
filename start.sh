#!/usr/bin/env bash

# ==============================================================================
# MiroFish One-Click Startup Script (Peluncur 1-Klik MiroFish)
# ==============================================================================

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

echo "=================================================="
echo "  🐟 Memulai MiroFish (Swarm Intelligence Engine)"
echo "=================================================="

# 1. Periksa ketersediaan Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 belum terpasang. Harap pasang Python >= 3.11."
    exit 1
fi

# 2. Periksa ketersediaan Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Error: Node.js belum terpasang. Harap pasang Node.js >= 18."
    exit 1
fi

# 3. Buat file .env default jika belum ada
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "✓ Berkas .env otomatis dibuat dari .env.example"
    else
        touch .env
    fi
fi

# 4. Hentikan proses lama jika masih berjalan di port 5001 atau 3000
lsof -ti:5001 | xargs kill -9 2>/dev/null
lsof -ti:3000 | xargs kill -9 2>/dev/null

echo "🚀 Menyalakan Backend (Flask API :5001)..."
cd "$PROJECT_DIR/backend"
if [ -d ".venv" ]; then
    .venv/bin/python run.py > "$PROJECT_DIR/backend.log" 2>&1 &
else
    python3 run.py > "$PROJECT_DIR/backend.log" 2>&1 &
fi
BACKEND_PID=$!

echo "🚀 Menyalakan Frontend (Vue 3 Vite :3000)..."
cd "$PROJECT_DIR/frontend"
if [ ! -d "node_modules" ]; then
    echo "📦 Memasang dependensi frontend..."
    npm install --cache /tmp/.npm-cache
fi
npm run dev > "$PROJECT_DIR/frontend.log" 2>&1 &
FRONTEND_PID=$!

cd "$PROJECT_DIR"

# Simpan PID untuk script stop
echo "$BACKEND_PID $FRONTEND_PID" > "$PROJECT_DIR/.pids"

# 5. Tunggu hingga layanan siap
echo "⏳ Menunggu layanan siap..."
sleep 3

# 6. Buka peramban (browser) otomatis
URL="http://localhost:3000"
echo "🌐 Membuka peramban di $URL..."

if [[ "$OSTYPE" == "darwin"* ]]; then
    open "$URL"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    if command -v xdg-open &> /dev/null; then
        xdg-open "$URL"
    fi
fi

echo "=================================================="
echo "  ✅ MiroFish Berhasil Berjalan!"
echo "  - Antarmuka Web : http://localhost:3000"
echo "  - Backend API   : http://localhost:5001"
echo "  - Pengaturan    : Klik ikon ⚙️ di pojok kanan atas web"
echo "=================================================="
echo "Tekan Ctrl+C untuk menghentikan, atau jalankan ./stop.sh"

# Tangkap sinyal interrupt (Ctrl+C) untuk mematikan kedua proses
trap 'echo "🛑 Menghentikan MiroFish..."; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; rm -f "$PROJECT_DIR/.pids"; exit 0' SIGINT SIGTERM

wait
