FROM python:3.12-slim

WORKDIR /code

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Railway inject PORT secara dinamis
# Jalankan migration Alembic dulu sebelum server start -- supaya schema database
# di production selalu sinkron dengan migration terbaru sebelum app mulai terima traffic.
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
