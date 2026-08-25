# My Itineraries — Backend

Backend Fase 1 (MVP Tier 1 — Community Itinerary) untuk platform **My Itineraries**.
Dibangun dengan FastAPI + SQLAlchemy + PostgreSQL, mengikuti pola deployment `undangan-digital` (Railway).

## Sudah tersedia di versi ini

- **Auth**: register & login dengan JWT (`/auth/register`, `/auth/login`)
- **Places (CRUD dasar)**: tambah tempat manual, list dengan filter kota/kategori/budget, laporkan tempat bermasalah
- **Deduplication sederhana**: cek `gmaps_url` yang sudah ada sebelum simpan tempat baru
- **Auto-import dari TikTok & YouTube**: `POST /places/import/preview` — tempel link, sistem ambil metadata via oEmbed resmi lalu AI (Claude) ekstrak jadi field terstruktur (nama, kategori, estimasi harga, kota). Hasilnya draft/preview, BELUM tersimpan — user edit dulu di frontend baru submit ke `POST /places` untuk publish beneran.
- **Plans**: buat plan manual (pilih tempat sendiri), generate plan otomatis (dengan/tanpa kategori pilihan), lihat & hapus plan milik user

**Belum ada di versi ini** (menyusul di fase berikutnya sesuai roadmap dokumen produk):
trip planner premium (Tier 2), upload foto ke object storage.

**Catatan soal auto-import:**
- Hanya **TikTok** dan **YouTube** yang didukung — keduanya punya oEmbed publik gratis tanpa perlu API key, jadi stabil untuk production. Instagram & Twitter/X sengaja tidak didukung karena butuh developer app + review dari platform masing-masing (lebih rumit & rawan berubah) — link dari platform itu akan ditolak dengan pesan error yang jelas, user diarahkan ke form manual.
- Fitur ini butuh `ANTHROPIC_API_KEY` diisi di `.env` — daftar di [console.anthropic.com](https://console.anthropic.com/) untuk dapat key-nya. Tanpa key ini, endpoint akan mengembalikan error 422 yang jelas (bukan crash).

## Menjalankan di lokal

1. Install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. Jalankan database Postgres lokal via Docker:
   ```bash
   docker compose up -d
   ```

3. Salin env:
   ```bash
   cp .env.example .env
   ```
   (default `.env.example` sudah cocok dengan `docker-compose.yml` di atas)

4. Jalankan server:
   ```bash
   uvicorn app.main:app --reload
   ```

5. Buka dokumentasi API interaktif di `http://localhost:8000/docs` — tabel database otomatis dibuat saat pertama kali run.

## Deploy ke Railway

1. Push folder ini ke repo GitHub baru (misal `my-itineraries-backend`, atau taruh di sub-folder `backend/` kalau mau satu repo dengan frontend).
2. Di Railway: **New Project → Deploy from GitHub repo**, pilih repo ini.
3. Tambahkan **plugin PostgreSQL** di project Railway yang sama — Railway otomatis kasih env var `DATABASE_URL`, tinggal di-reference ke service backend (Settings → Variables → Add Reference).
4. Set environment variables di Railway (Settings → Variables):
   - `JWT_SECRET` — random string panjang, jangan dipakai bareng repo lain
   - `CORS_ORIGINS` — domain frontend kamu di Vercel, misal `https://my-itineraries.vercel.app`
   - `ANTHROPIC_API_KEY` — untuk fitur auto-import TikTok/YouTube (dari console.anthropic.com)
5. Railway otomatis detect `Dockerfile` dan build dari situ. Deploy selesai, backend punya URL publik seperti `https://my-itineraries-backend-production.up.railway.app`.

## Struktur folder

```
app/
├── main.py           # entrypoint FastAPI, register router & CORS
├── config.py          # baca environment variables
├── database.py         # koneksi SQLAlchemy ke Postgres
├── models.py           # tabel: users, places, place_reports, plans, plan_items
├── schemas.py          # skema request/response (Pydantic)
├── auth.py             # hashing password, JWT, dependency get_current_user
├── services/
│   ├── social_extractor.py   # deteksi platform (TikTok/YouTube) & fetch oEmbed
│   └── ai_extract.py          # kirim caption ke Claude, parse jadi field terstruktur
└── routers/
    ├── auth.py         # /auth/register, /auth/login
    ├── places.py       # /places (CRUD + filter + report + import/preview)
    └── plans.py        # /plans (manual + generate)
```

## Langkah berikutnya (urutan yang disarankan)

1. Test semua endpoint lewat `/docs` (Swagger UI bawaan FastAPI) sebelum lanjut ke frontend.
2. Setelah backend ini jalan & di-deploy ke Railway → lanjut scaffold frontend Next.js + Tailwind (responsive dari awal), connect ke API ini.
3. Fase 4–5: tabel & endpoint untuk Trip Planner Rombongan (Tier 2) — modelnya sudah dirancang di dokumen produk (`trips`, `trip_members`, `trip_transport`, dst), tinggal diimplementasikan setelah Tier 1 stabil.
