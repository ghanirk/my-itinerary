# My Itineraries — Frontend

Frontend untuk platform **My Itineraries** (Community Itinerary — MVP Tier 1 & 2).
Dibangun dengan React + TypeScript + Vite + TailwindCSS, mengikuti pola struktur
folder & konvensi yang sama dengan project `undangan-digital` (satu pembuat),
supaya gampang dirawat lintas project.

## Fitur yang sudah tersedia (mengikuti backend MVP 1 & 2)

- **Auth**: register & login (JWT disimpan di `localStorage`, dipakai otomatis di setiap request yang butuh)
- **Jelajahi Tempat**: list tempat dengan filter kota/kategori/pencarian nama + pagination
- **Auto-import dari TikTok/YouTube**: tempel link → preview hasil ekstraksi AI (bisa multi-tempat untuk video kompilasi) → edit → simpan sekaligus (bulk)
- **Plan Saya**: buat plan manual (tambah tempat langsung dari halaman Jelajahi Tempat), generate plan otomatis (kota + budget + jumlah tempat, kategori opsional), hapus plan

## Struktur folder

Mengikuti pola yang sama dengan frontend `undangan-digital`: satu file per domain/resource
di `api/` dan `types/`, komponen shared di `components/`, halaman di `pages/`.

```
src/
├── main.tsx              # entrypoint, bungkus App dengan QueryClientProvider + AuthProvider
├── App.tsx                # routing (react-router-dom)
├── index.css              # Tailwind v4 + design tokens (@theme: warna brand, font)
├── App.css                # style tambahan spesifik (kosong/opsional)
│
├── lib/
│   └── authStorage.ts     # simpan/ambil token JWT & user dari localStorage
│
├── context/
│   └── AuthContext.tsx    # state auth global (user, isAuthenticated, login, logout)
│
├── api/                   # satu file per resource, fetch ke backend FastAPI
│   ├── client.ts           # wrapper fetch: base URL, header Authorization, error handling
│   ├── auth.ts              # POST /auth/register, /auth/login
│   ├── places.ts            # GET/POST /places, import/preview, import/bulk, report
│   └── plans.ts             # GET/POST /plans, /plans/generate, DELETE /plans/{id}
│
├── types/                 # tipe TypeScript, sejajar dengan schema Pydantic backend
│   ├── auth.ts
│   ├── place.ts
│   └── plan.ts
│
├── components/
│   ├── Layout.tsx           # shell halaman (Navbar + Outlet)
│   ├── Navbar.tsx            # navigasi + status login/logout
│   ├── Divider.tsx           # pemisah dekoratif antar section
│   ├── HeroShowcase.tsx      # kartu fitur berputar di halaman Beranda
│   ├── PlaceCard.tsx         # kartu tempat (dipakai di halaman Jelajahi Tempat)
│   └── ProtectedRoute.tsx    # guard halaman yang butuh login
│
└── pages/
    ├── Beranda.tsx           # landing page
    ├── Places.tsx            # jelajahi tempat + filter + pagination
    ├── PlaceImport.tsx       # alur import dari TikTok/YouTube (protected)
    ├── MyPlans.tsx           # list plan, generate otomatis, hapus (protected)
    ├── Login.tsx
    ├── Register.tsx
    └── NotFound.tsx
```

## Menjalankan di lokal

1. Install dependencies:
   ```bash
   npm install
   ```

2. Salin env dan sesuaikan URL backend:
   ```bash
   cp .env.example .env
   ```
   (default sudah cocok kalau backend jalan lokal di `http://127.0.0.1:8000` lewat `uvicorn app.main:app --reload`)

3. Jalankan dev server:
   ```bash
   npm run dev
   ```

4. Buka `http://localhost:5173`.

Pastikan backend juga jalan (lihat `../backend/README.md`) dan `CORS_ORIGINS` di `.env` backend
sudah menyertakan origin frontend ini (`http://localhost:5173` untuk lokal).

## Build & deploy

```bash
npm run build   # output ke dist/
npm run preview # preview hasil build
```

Untuk deploy ke Vercel: import repo ini (root directory diarahkan ke `frontend/`),
`vercel.json` sudah menyediakan rewrite untuk SPA routing. Set environment variable
`VITE_API_BASE_URL` di Vercel ke URL backend production (mis. dari Railway).

## Langkah berikutnya

Trip Planner Rombongan (Tier 2 — `trips`, `trip_members`, `trip_vehicles`, dst.) sudah
ada endpoint-nya di backend tapi belum diimplementasikan di frontend ini; tinggal
tambahkan folder `api/`, `types/`, dan `pages/` baru mengikuti pola yang sama begitu
fase itu siap dipakai.
