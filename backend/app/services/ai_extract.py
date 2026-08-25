import json
import re
from typing import List

import httpx

from app.config import settings
from app.services.social_extractor import ExtractionError

# Batas jumlah tempat yang diterima dari satu video, untuk jaga-jaga kalau AI
# "ngarang" terlalu banyak butir dari teks yang ambigu.
_MAX_PLACES_PER_VIDEO = 15

_SYSTEM_PROMPT = """Kamu membantu mengekstrak informasi tempat (kuliner/wisata/hangout) dari caption \
dan/atau deskripsi video media sosial Indonesia.

PENTING -- video bisa berisi SATU tempat saja, atau berupa KOMPILASI banyak tempat sekaligus \
(contoh ciri kompilasi: "5 kuliner hits di Bandung", "10 spot healing Jogja", daftar bernomor/emoji, \
beberapa nama tempat berbeda disebutkan berurutan, dsb). Kamu harus mendeteksi mana kasusnya, \
lalu mengekstrak SEMUA tempat yang disebutkan secara eksplisit di teks -- jangan hanya ambil satu \
kalau sebenarnya ada lebih dari satu, dan jangan memecah satu tempat jadi beberapa entri palsu.

Baca teks yang diberikan lalu kembalikan HANYA objek JSON (tanpa markdown, tanpa penjelasan) \
dengan bentuk persis seperti ini:

{
  "is_compilation": boolean,    // true jika teks menyebutkan lebih dari satu tempat berbeda
  "places": [
    {
      "name": string,               // nama tempat, sebaik mungkin ditebak dari teks
      "category": string,           // salah satu dari: "kuliner", "fun", "sport", "alam"
      "price_min": integer,         // estimasi harga termurah dalam rupiah, 0 jika tidak disebutkan
      "price_max": integer,         // estimasi harga termahal dalam rupiah, sama dengan price_min jika hanya ada 1 angka
      "city": string,               // kota tempat berada, string kosong jika tidak yakin
      "confidence": string          // "high" jika teks jelas menyebutkan nama tempat & kota, "low" jika banyak menebak
    }
    // ... satu objek per tempat yang terdeteksi, minimal 1 objek
  ]
}

Jika informasi tertentu benar-benar tidak ada petunjuknya di teks, isi dengan nilai default \
(price 0, city string kosong) -- JANGAN mengarang nama tempat, kota, atau tempat tambahan yang \
tidak ada dasarnya di teks. Jika teks sama sekali tidak menyebutkan tempat apa pun yang bisa \
diidentifikasi, kembalikan "places" sebagai array kosong. Selalu kembalikan JSON valid, tidak \
ada teks lain di luar JSON."""

_VALID_CATEGORIES = ("kuliner", "fun", "sport", "alam")


def _normalize_place(raw: dict) -> dict:
    return {
        "name": raw.get("name") or "",
        "category": raw.get("category") if raw.get("category") in _VALID_CATEGORIES else "fun",
        "price_min": int(raw.get("price_min") or 0),
        "price_max": int(raw.get("price_max") or raw.get("price_min") or 0),
        "city": raw.get("city") or "",
        "confidence": raw.get("confidence", "low"),
    }


def extract_places_from_text(raw_text: str) -> List[dict]:
    """
    Kirim caption/deskripsi mentah ke Claude untuk diubah jadi satu atau lebih
    tempat terstruktur. Mengembalikan list -- berisi 1 item untuk video biasa,
    atau beberapa item kalau video terdeteksi sebagai kompilasi banyak tempat.

    Melempar ExtractionError kalau API key belum diset, request gagal, parsing
    gagal, atau tidak ada satupun tempat yang berhasil diekstrak.
    """
    if not raw_text.strip():
        raise ExtractionError("Tidak ada teks caption/deskripsi yang bisa dianalisis dari link ini.")

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
                    # dinaikkan dari 500 -> cukup untuk video kompilasi berisi belasan tempat
                    "max_tokens": 2000,
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

    # Bentuk normal: {"is_compilation": bool, "places": [...]}.
    # Fallback jaga-jaga kalau suatu saat model malah balikin satu objek tempat
    # langsung (bentuk lama) -- tetap dianggap valid, dibungkus jadi list 1 item.
    if isinstance(parsed, dict) and "places" in parsed:
        raw_places = parsed.get("places") or []
    elif isinstance(parsed, list):
        raw_places = parsed
    elif isinstance(parsed, dict) and "name" in parsed:
        raw_places = [parsed]
    else:
        raw_places = []

    if not raw_places:
        raise ExtractionError(
            "AI tidak menemukan tempat yang bisa dikenali dari video ini. Coba isi manual."
        )

    places = [_normalize_place(p) for p in raw_places[:_MAX_PLACES_PER_VIDEO] if isinstance(p, dict)]

    if not places:
        raise ExtractionError(
            "AI tidak menemukan tempat yang bisa dikenali dari video ini. Coba isi manual."
        )

    return places
