from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import auth, places, plans

# Skema database sekarang dikelola lewat Alembic migrations (folder migrations/),
# bukan lagi Base.metadata.create_all() -- supaya perubahan schema di production
# (nambah/ubah kolom, dst) bisa di-track & di-apply dengan aman tanpa risiko
# create_all "lupa" nge-alter tabel yang sudah ada. Jalankan `alembic upgrade head`
# sebelum start server (lihat README bagian "Menjalankan di lokal").

app = FastAPI(
    title="My Itineraries API",
    description="Backend untuk platform Community Itinerary & Trip Planner Rombongan.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(places.router)
app.include_router(plans.router)


@app.get("/")
def root():
    return {"status": "ok", "message": "My Itineraries API is running."}


@app.get("/health")
def health():
    return {"status": "healthy"}
