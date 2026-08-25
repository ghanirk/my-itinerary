from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.config import settings
from app.routers import auth, places, plans

# MVP: buat tabel langsung dari model. Untuk produksi nanti, ganti ke Alembic migrations.
Base.metadata.create_all(bind=engine)

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
