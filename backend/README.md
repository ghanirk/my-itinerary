# My Itineraries — Backend

Backend Fase 1 (MVP Tier 1 — Community Itinerary) untuk platform **My Itineraries**.
Dibangun dengan FastAPI + SQLAlchemy + PostgreSQL, mengikuti pola deployment `undangan-digital` (Railway).

## Sudah tersedia di versi ini

- **Auth**: register & login dengan JWT (`/auth/register`, `/auth/login`)
- **Places (CRUD dasar)**: tambah tempat manual, list dengan filter kota/kategori/budget/pencarian nama (dengan pagination), laporkan tempat bermasalah
- **Deduplication sederhana**: cek `gmaps_url` yang sudah ada sebelum simpan tempat baru
- **Auto-import dari TikTok & YouTube**: `POST /places/import/preview` — tempel link, sistem ambil metadata via oEmbed resmi lalu AI (Google Gemini) ekstrak jadi field terstruktur (nama, kategori, estimasi harga, kota). Hasilnya draft/preview, BELUM tersimpan — user edit dulu di frontend baru submit ke `POST /places/import/bulk` untuk publish beneran. Dibatasi kuota harian per user (lihat `MAX_IMPORTS_PER_DAY`) supaya tidak bisa di-spam.
- **Plans**: buat plan manual (pilih tempat sendiri), generate plan otomatis (dengan/tanpa kategori pilihan), lihat & hapus plan milik user
- **Skema database dikelola via Alembic migrations** (bukan `create_all` lagi) — aman untuk perubahan schema di production
- **Test suite (pytest)** untuk service AI-extraction & social-extractor (paling rawan berubah), plus test integrasi pagination/search/rate-limit

**Belum ada di versi ini** (menyusul di fase berikutnya sesuai roadmap dokumen produk):
trip planner premium (Tier 2), upload foto ke object storage.

**Catatan soal auto-import:**
- Hanya **TikTok** dan **YouTube** yang didukung — keduanya punya oEmbed publik gratis tanpa perlu API key, jadi stabil untuk production. Instagram & Twitter/X sengaja tidak didukung karena butuh developer app + review dari platform masing-masing (lebih rumit & rawan berubah) — link dari platform itu akan ditolak dengan pesan error yang jelas, user diarahkan ke form manual.
- Fitur ini butuh `GEMINI_API_KEY` diisi di `.env` — ambil key gratis (tanpa kartu kredit) di [aistudio.google.com/apikey](https://aistudio.google.com/apikey). Tanpa key ini, endpoint akan mengembalikan error 422 yang jelas (bukan crash).
- Kuota harian: default `MAX_IMPORTS_PER_DAY=20` per user (bisa diubah di `.env`, set `0` untuk menonaktifkan). Kalau limit terlampaui, endpoint balikin `429` dengan pesan yang jelas.

## Menjalankan di lokal

1. Install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   # opsional, kalau mau jalanin test suite juga:
   pip install -r requirements-dev.txt
   ```

2. Jalankan database Postgres lokal via Docker:
   ```bash
   docker compose up -d
   ```

3. Salin env:
   ```bash
   cp .env.example .env
   ```
   (default `.env.example` sudah cocok dengan `docker-compose.yml` di atas — isi juga `GEMINI_API_KEY` kalau mau coba fitur auto-import)

4. Terapkan skema database lewat Alembic (ganti dari `create_all`, jadi WAJIB dijalankan sebelum start server pertama kali, dan tiap kali ada migration baru):
   ```bash
   alembic upgrade head
   ```

5. Jalankan server:
   ```bash
   uvicorn app.main:app --reload
   ```

6. Buka dokumentasi API interaktif di `http://localhost:8000/docs`.

## Menjalankan test

```bash
pip install -r requirements-dev.txt
# butuh Postgres lokal jalan (docker compose up -d), test otomatis pakai DB
# terpisah "my_itineraries_test" (dibuat/dibersihkan sendiri oleh test suite)
createdb my_itineraries_test  # sekali saja, kalau belum ada
pytest
```

Test suite fokus di `services/ai_extract.py` dan `services/social_extractor.py` (paling rawan
berubah karena bergantung ke API eksternal Gemini/TikTok/YouTube) — semua panggilan HTTP di-mock
pakai `respx`, jadi test tidak butuh API key beneran atau koneksi internet. Ada juga test
integrasi untuk pagination/search di `GET /places` dan rate limit di `/places/import/preview`.

## Migrasi database (Alembic)

Skema database dikelola lewat Alembic, bukan `Base.metadata.create_all()` lagi — supaya
perubahan schema di production (nambah/ubah kolom, dst) bisa di-track & di-apply dengan aman.

- **Ubah model** di `app/models.py`, lalu generate migration otomatis:
  ```bash
  alembic revision --autogenerate -m "deskripsi singkat perubahan"
  ```
- **Selalu review** file migration yang dihasilkan di `migrations/versions/` sebelum apply —
  autogenerate kadang meleset (terutama untuk rename kolom atau perubahan tipe data kompleks).
- **Terapkan** migration:
  ```bash
  alembic upgrade head
  ```
- **Rollback** satu langkah kalau perlu:
  ```bash
  alembic downgrade -1
  ```
- Di production (Railway dst), jalankan `alembic upgrade head` sebagai bagian dari proses
  deploy/start (misal di `Dockerfile` atau start command), sebelum `uvicorn` start.

## Deploy ke Railway

1. Push folder ini ke repo GitHub baru (misal `my-itineraries-backend`, atau taruh di sub-folder `backend/` kalau mau satu repo dengan frontend).
2. Di Railway: **New Project → Deploy from GitHub repo**, pilih repo ini.
3. Tambahkan **plugin PostgreSQL** di project Railway yang sama — Railway otomatis kasih env var `DATABASE_URL`, tinggal di-reference ke service backend (Settings → Variables → Add Reference).
4. Set environment variables di Railway (Settings → Variables):
   - `JWT_SECRET` — random string panjang, jangan dipakai bareng repo lain
   - `CORS_ORIGINS` — domain frontend kamu di Vercel, misal `https://my-itineraries.vercel.app`
   - `GEMINI_API_KEY` — untuk fitur auto-import TikTok/YouTube (dari aistudio.google.com/apikey)
   - `MAX_IMPORTS_PER_DAY` — opsional, default 20
5. Railway otomatis detect `Dockerfile` dan build dari situ. Pastikan `alembic upgrade head` dijalankan sebelum server start (tambahkan ke start command/entrypoint). Deploy selesai, backend punya URL publik seperti `https://my-itineraries-backend-production.up.railway.app`.

## Struktur folder

```
app/
├── main.py           # entrypoint FastAPI, register router & CORS
├── config.py          # baca environment variables
├── database.py         # koneksi SQLAlchemy ke Postgres
├── models.py           # tabel: users, places, place_reports, plans, plan_items, import_logs
├── schemas.py          # skema request/response (Pydantic)
├── auth.py             # hashing password, JWT, dependency get_current_user
├── services/
│   ├── social_extractor.py   # deteksi platform (TikTok/YouTube) & fetch oEmbed
│   └── ai_extract.py          # kirim caption ke Gemini, parse jadi field terstruktur
└── routers/
    ├── auth.py         # /auth/register, /auth/login
    ├── places.py       # /places (CRUD + filter + pagination + report + import/preview + rate limit)
    └── plans.py        # /plans (manual + generate)
migrations/              # Alembic migration scripts
tests/                   # pytest -- unit test service AI/extractor + integration test router
```

## Langkah berikutnya (urutan yang disarankan)

1. Setelah backend ini jalan & di-deploy ke Railway → lanjut scaffold frontend Next.js + Tailwind (responsive dari awal), connect ke API ini.
2. Upload foto ke object storage (S3/Cloudinary/Supabase Storage) — thumbnail dari hasil auto-import saat ini masih pakai link CDN TikTok/YouTube yang bisa expired.
3. Fase 4–5: tabel & endpoint untuk Trip Planner Rombongan (Tier 2) — modelnya sudah dirancang di dokumen produk (`trips`, `trip_members`, `trip_transport`, dst), tinggal diimplementasikan setelah Tier 1 stabil.
