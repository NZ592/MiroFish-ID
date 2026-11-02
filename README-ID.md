<div align="center">

<img src="./static/image/MiroFish_logo_compressed.jpeg" alt="MiroFish Logo" width="75%"/>

### 🐟 Mesin Kecerdasan Kolektif & Simulasi Prediksi Masa Depan Multi-Agen
*A Simple and Universal Swarm Intelligence Engine, Predicting Anything*

[English](./README.md) | [Bahasa Indonesia](./README-ID.md) | [中文文档](./README-ZH.md)

</div>

---

## ⚡ Ikhtisar (Overview)

**MiroFish** adalah platform simulasi prediksi berbasis kecerdasan buatan (*AI Swarm Intelligence*) dan teknologi *multi-agent* generasi baru. 

Dengan mengekstraksi informasi awal dari dunia nyata (berita terkini, draf kebijakan publik, atau fenomena sosial), MiroFish secara otomatis membangun dunia digital paralel. Di dalamnya, puluhan hingga ribuan agen cerdas berkepribadian independen (KOL, jurnalis, analis, akademisi, hingga warganet biasa) saling berinteraksi, berdiskusi, dan mengalami evolusi sosial secara bebas.

### ✨ Fitur Unggulan Edisi Ini
1. **Dukungan Penuh Bahasa Indonesia**: Seluruh alur kerja (5 langkah simulasi, visualisasi graf, persona agen, hingga hasil laporan) tersedia dalam Bahasa Indonesia yang alami.
2. **Ekspor Laporan PDF & Markdown Eksekutif**: Sekali klik tombol **"Unduh PDF"**, hasil laporan prediksi siap dicetak atau disimpan dalam tata letak A4 profesional berkualitas tinggi.
3. **Pengaturan Model AI Visual (No-Code)**: Ganti API Key, Base URL, dan nama model (TokenKoding, DeepSeek, Google Gemini, OpenAI, Qwen, Ollama, Groq) langsung dari jendela pop-up ⚙️ di web browser tanpa perlu restart server.
4. **Engine Chat Persona Mandiri**: Mengobrol langsung dengan persona agen mana pun kapan saja secara offline berdasarkan biodata dan riwayat postingannya.
5. **Survei Massal Multi-Agen Paralel**: Ajukan pertanyaan jajak pendapat (*polling/survey*) ke banyak agen secara serentak dalam hitungan detik (*multi-threading*).
6. **Peluncur 1-Klik (One-Click Launcher)**: Cukup jalankan `./start.sh` (Mac/Linux) atau `start.bat` (Windows), sistem otomatis menyiapkan dependensi dan membuka peramban web.

---

## 🚀 Panduan Memulai Cepat (Quick Start)

### 1. Prasyarat
- **Python** >= 3.11
- **Node.js** >= 18

### 2. Kloning Repositori
```bash
git clone https://github.com/username-anda/MiroFish-ID.git
cd MiroFish-ID
```

### 3. Siapkan Virtual Environment Python (Cukup 1x di awal)
```bash
cd backend
python3 -m venv .venv

# Di macOS / Linux:
source .venv/bin/activate

# Di Windows:
# .venv\Scripts\activate

pip install -r requirements.txt
cd ..
```

### 4. Jalankan Aplikasi
- **macOS / Linux:**
  ```bash
  chmod +x start.sh stop.sh
  ./start.sh
  ```
- **Windows:**
  Cukup klik dua kali berkas **`start.bat`**.

Peramban akan terbuka secara otomatis di `http://localhost:3000`.

### 5. Masukkan Kunci API
1. Klik ikon **⚙️ (Pengaturan Sistem)** di pojok kanan atas antarmuka web.
2. Masukkan **Base URL** dan **Kunci API** model AI Anda.
3. Klik tombol **Tes Koneksi API**, lalu klik **Simpan Pengaturan**.
4. Sistem siap digunakan untuk simulasi!

---

## 🛑 Cara Menghentikan Layanan
- Tekan `Ctrl + C` pada jendela Terminal yang sedang berjalan, atau
- Jalankan skrip penghenti:
  ```bash
  ./stop.sh       # di macOS / Linux
  # stop.bat      # di Windows
  ```

---

## 📄 Lisensi
Didistribusikan di bawah lisensi AGPL-3.0. Lihat berkas `LICENSE` untuk informasi selengkapnya.
