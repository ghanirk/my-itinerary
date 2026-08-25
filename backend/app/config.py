import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/my_itineraries")
    JWT_SECRET: str = os.getenv("JWT_SECRET", "change-this-secret-in-production")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = int(os.getenv("JWT_EXPIRE_MINUTES", "10080"))  # 7 days
    CORS_ORIGINS: list[str] = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")

    # Batas berapa kali satu user boleh memanggil /places/import/preview (yang manggil
    # Gemini API) dalam 24 jam terakhir. Mencegah spam yang bisa menghabiskan quota/cost
    # AI. Set ke 0 untuk menonaktifkan limit (tidak disarankan di production).
    MAX_IMPORTS_PER_DAY: int = int(os.getenv("MAX_IMPORTS_PER_DAY", "20"))


settings = Settings()
