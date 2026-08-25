import json
import re

import httpx

from app.config import settings
from app.services.social_extractor import ExtractionError

_SYSTEM_PROMPT = """Kamu membantu mengekstrak informasi tempat (kuliner/wisata/hangout) dari caption \
video media sosial Indonesia. Baca teks yang diberikan lalu kembalikan HANYA objek JSON \
(tanpa markdown, tanpa penjelasan) dengan field berikut:

{
  "name": string,               // nama tempat, sebaik mungkin ditebak dari teks
  "category": string,           // salah satu dari: "kuliner", "fun", "sport", "alam"
  "price_min": integer,         // estimasi harga termurah dalam rupiah, 0 jika tidak disebutkan
  "price_max": integer,         // estimasi harga termahal dalam rupiah, sama dengan price_min jika hanya ada 1 angka
  "city": string,               // kota tempat berada, string kosong jika tidak yakin
  "confidence": string          // "high" jika teks jelas menyebutkan nama tempat & kota, "low" jika banyak menebak
}

Jika informasi tertentu benar-benar tidak ada petunjuknya di teks, isi dengan nilai default \
(price 0, city string kosong) -- JANGAN mengarang nama tempat atau kota yang tidak ada dasarnya \
di teks. Selalu kembalikan JSON valid, tidak ada teks lain di luar JSON."""


def extract_place_from_text(raw_text: str) -> dict:
    """
    Kirim caption/judul mentah ke Claude untuk diubah jadi field terstruktur.
    Melempar ExtractionError kalau API key belum diset atau parsing gagal.
    """
    if not raw_text.strip():
        raise ExtractionError("Tidak ada teks caption/judul yang bisa dianalisis dari link ini.")

    if not settings.ANTHROPIC_API_KEY:
        raise ExtractionError(
            "ANTHROPIC_API_KEY belum diset di server. Fitur auto-extract butuh ini untuk jalan."
        )

    try:
        with httpx.Client(timeout=30.0) as client:
            resp = client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": settings.ANTHROPIC_API_KEY,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": settings.ANTHROPIC_MODEL,
                    "max_tokens": 500,
                    "system": _SYSTEM_PROMPT,
                    "messages": [{"role": "user", "content": raw_text}],
                },
            )
            resp.raise_for_status()
            data = resp.json()
    except httpx.HTTPStatusError as e:
        raise ExtractionError(f"AI extraction gagal (status {e.response.status_code}).")
    except httpx.RequestError as e:
        raise ExtractionError(f"Tidak bisa menghubungi layanan AI: {e}")

    text_blocks = [b["text"] for b in data.get("content", []) if b.get("type") == "text"]
    raw_json_text = "".join(text_blocks).strip()

    # Jaga-jaga kalau model membungkus jawaban dengan ```json ... ```
    raw_json_text = re.sub(r"^```json\s*|\s*```$", "", raw_json_text.strip())

    try:
        parsed = json.loads(raw_json_text)
    except json.JSONDecodeError:
        raise ExtractionError("AI mengembalikan format yang tidak bisa dibaca. Coba lagi atau isi manual.")

    return {
        "name": parsed.get("name") or "",
        "category": parsed.get("category") if parsed.get("category") in
            ("kuliner", "fun", "sport", "alam") else "fun",
        "price_min": int(parsed.get("price_min") or 0),
        "price_max": int(parsed.get("price_max") or parsed.get("price_min") or 0),
        "city": parsed.get("city") or "",
        "confidence": parsed.get("confidence", "low"),
    }
