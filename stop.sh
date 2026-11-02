#!/usr/bin/env bash

# ==============================================================================
# MiroFish Stop Script (Penghenti Layanan MiroFish)
# ==============================================================================

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🛑 Menghentikan seluruh proses MiroFish..."

if [ -f "$PROJECT_DIR/.pids" ]; then
    PIDS=$(cat "$PROJECT_DIR/.pids")
    kill $PIDS 2>/dev/null
    rm -f "$PROJECT_DIR/.pids"
fi

# Pastikan port 5001 dan 3000 bebas
lsof -ti:5001 | xargs kill -9 2>/dev/null
lsof -ti:3000 | xargs kill -9 2>/dev/null

echo "✓ Seluruh layanan MiroFish telah dihentikan dengan aman."
