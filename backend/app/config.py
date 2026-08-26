import os
from dotenv import load_dotenv

load_dotenv()

_jwt_secret = os.getenv("JWT_SECRET")
if not _jwt_secret:
    raise RuntimeError(
        "Environment variable JWT_SECRET belum di-set. App sengaja tidak "
        "dijalankan dengan secret default yang predictable -- set JWT_SECRET "
        "(mis. lewat Railway > Variables) sebelum start server."
    )


class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/my_itineraries")
    JWT_SECRET: str = _jwt_secret
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = int(os.getenv("JWT_EXPIRE_MINUTES", "10080"))  # 7 days
    CORS_ORIGINS: list[str] = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")
    MAX_IMPORTS_PER_DAY: int = int(os.getenv("MAX_IMPORTS_PER_DAY", "20"))


settings = Settings()
