import base64
import json
import re
from typing import List, Optional

import httpx

from app.config import settings
from app.services.social_extractor import ExtractionError

# Batas jumlah tempat yang diterima dari satu video, untuk jaga-jaga kalau AI
# "ngarang" terlalu banyak butir dari teks yang ambigu.
_MAX_PLACES_PER_VIDEO = 15

_RESPONSE_FORMAT_INSTRUCTIONS = """Kembalikan HANYA objek JSON (tanpa markdown, tanpa penjelasan) \
dengan bentuk persis seperti ini:

{
  "is_compilation": boolean,    // true jika sumbernya menyebutkan lebih dari satu tempat berbeda
  "places": [
    {
      "name": string,               // nama tempat, sebaik mungkin ditebak
      "category": string,           // salah satu dari: "kuliner", "fun", "sport", "alam"
      "price_min": integer,         // estimasi harga termurah dalam rupiah, 0 jika tidak disebutkan
      "price_max": integer,         // estimasi harga termahal dalam rupiah, sama dengan price_min jika hanya ada 1 angka
      "city": string,               // kota tempat berada, string kosong jika tidak yakin
      "confidence": string          // "high" jika jelas menyebutkan nama tempat & kota, "low" jika banyak menebak
    }
    // ... satu objek per tempat yang terdeteksi, minimal 1 objek
  ]
}

Jika informasi tertentu benar-benar tidak ada petunjuknya, isi dengan nilai default \
(price 0, city string kosong) -- JANGAN mengarang nama tempat, kota, atau tempat tambahan yang \
tidak ada dasarnya. Jika sama sekali tidak ada tempat yang bisa diidentifikasi, kembalikan \
"places" sebagai array kosong. Selalu kembalikan JSON valid, tidak ada teks lain di luar JSON."""

_TEXT_SYSTEM_PROMPT = f"""Kamu membantu mengekstrak informasi tempat (kuliner/wisata/hangout) dari caption \
dan/atau deskripsi video media sosial Indonesia.

PENTING -- video bisa berisi SATU tempat saja, atau berupa KOMPILASI banyak tempat sekaligus \
(contoh ciri kompilasi: "5 kuliner hits di Bandung", "10 spot healing Jogja", daftar bernomor/emoji, \
beberapa nama tempat berbeda disebutkan berurutan, dsb). Kamu harus mendeteksi mana kasusnya, \
lalu mengekstrak SEMUA tempat yang disebutkan secara eksplisit di teks -- jangan hanya ambil satu \
kalau sebenarnya ada lebih dari satu, dan jangan memecah satu tempat jadi beberapa entri palsu.

Baca teks yang diberikan lalu {_RESPONSE_FORMAT_INSTRUCTIONS}"""

_IMAGE_SYSTEM_PROMPT = f"""Kamu membantu mengekstrak informasi tempat (kuliner/wisata/hangout) dari \
gambar cover/thumbnail video media sosial Indonesia. Gambar ini SERINGKALI cuma menunjukkan SATU \
frame/slide dari video (bukan seluruh isi video) -- jadi kalau video aslinya kompilasi banyak \
tempat, kemungkinan besar kamu cuma bisa membaca tempat yang tampil di frame ini saja, dan itu \
tidak apa-apa, jangan menebak tempat lain yang tidak terlihat di gambar.

Baca tulisan yang tampak di gambar (nama tempat, nama kota, kisaran harga, dsb -- baik berupa teks \
overlay/caption di gambar maupun tulisan pada papan nama/banner yang terfoto) lalu {_RESPONSE_FORMAT_INSTRUCTIONS}"""

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


def _call_gemini(system_prompt: str, parts: list) -> List[dict]:
    """
    Kirim request ke Gemini API (Google AI Studio, free tier) dan parse hasilnya
    jadi list tempat. `parts` adalah list of content parts ala Gemini -- bisa
    {"text": "..."} untuk teks, atau {"inline_data": {...}} untuk gambar.
    Dipakai bersama oleh jalur ekstraksi teks maupun gambar.
    """
    if not settings.GEMINI_API_KEY:
        raise ExtractionError(
            "GEMINI_API_KEY belum diset di server. Fitur auto-extract butuh ini untuk jalan. "
            "Ambil key gratis di https://aistudio.google.com/apikey, lalu tambahkan baris "
            "GEMINI_API_KEY=AIza... di file .env backend, lalu restart server."
        )

    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{settings.GEMINI_MODEL}:generateContent"
    )

    try:
        with httpx.Client(timeout=30.0) as client:
            resp = client.post(
                url,
                params={"key": settings.GEMINI_API_KEY},
                headers={"content-type": "application/json"},
                json={
                    "system_instruction": {"parts": [{"text": system_prompt}]},
                    "contents": [{"role": "user", "parts": parts}],
                    "generationConfig": {
                        # minta Gemini balikin JSON murni -- lebih andal daripada
                        # cuma mengandalkan instruksi prompt saja
                        "response_mime_type": "application/json",
                        "maxOutputTokens": 2000,
                        "temperature": 0.2,
                    },
                },
            )
            resp.raise_for_status()
            data = resp.json()
    except httpx.HTTPStatusError as e:
        detail = e.response.text[:300] if e.response is not None else ""
        raise ExtractionError(f"AI extraction gagal (status {e.response.status_code}). {detail}")
    except httpx.RequestError as e:
        raise ExtractionError(f"Tidak bisa menghubungi layanan AI: {e}")

    try:
        candidates = data.get("candidates") or []
        if not candidates:
            # Bisa terjadi kalau request diblokir oleh safety filter Gemini
            feedback = data.get("promptFeedback", {})
            raise ExtractionError(
                f"AI tidak mengembalikan hasil (kemungkinan diblokir filter konten Gemini: "
                f"{feedback.get('blockReason', 'alasan tidak diketahui')})."
            )
        response_parts = candidates[0].get("content", {}).get("parts", [])
        raw_json_text = "".join(p.get("text", "") for p in response_parts).strip()
    except (KeyError, IndexError, AttributeError):
        raise ExtractionError("Format respons dari Gemini tidak dikenali.")

    # Jaga-jaga kalau model tetap membungkus jawaban dengan ```json ... ```
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

    places = [_normalize_place(p) for p in raw_places[:_MAX_PLACES_PER_VIDEO] if isinstance(p, dict)]
    return places


def extract_places_from_text(raw_text: str) -> List[dict]:
    """
    Kirim caption/deskripsi mentah ke Gemini untuk diubah jadi satu atau lebih
    tempat terstruktur. Mengembalikan list -- berisi 1 item untuk video biasa,
    atau beberapa item kalau video terdeteksi sebagai kompilasi banyak tempat.

    Melempar ExtractionError kalau raw_text kosong, API key belum diset, request
    gagal, parsing gagal, atau tidak ada satupun tempat yang berhasil diekstrak.
    """
    if not raw_text.strip():
        raise ExtractionError("Tidak ada teks caption/deskripsi yang bisa dianalisis dari link ini.")

    places = _call_gemini(_TEXT_SYSTEM_PROMPT, [{"text": raw_text}])

    if not places:
        raise ExtractionError(
            "AI tidak menemukan tempat yang bisa dikenali dari teks caption/deskripsi video ini."
        )

    return places


def _download_image_as_base64(image_url: str) -> tuple[str, str]:
    """Unduh gambar dan kembalikan (base64_data, mime_type) untuk dikirim ke Gemini."""
    try:
        with httpx.Client(timeout=15.0, follow_redirects=True) as client:
            resp = client.get(image_url)
            resp.raise_for_status()
            mime_type = resp.headers.get("content-type", "image/jpeg").split(";")[0].strip()
            if not mime_type.startswith("image/"):
                mime_type = "image/jpeg"
            return base64.b64encode(resp.content).decode("ascii"), mime_type
    except httpx.HTTPError as e:
        raise ExtractionError(f"Gagal mengunduh gambar thumbnail: {e}")


def extract_places_from_image(image_url: str) -> List[dict]:
    """
    Fallback untuk video yang tidak punya caption/deskripsi teks (mis. video berisi
    slideshow screenshot tanpa keterangan tertulis di caption): coba baca gambar
    cover/thumbnail video lewat vision, kalau ada tulisan tempat di situ.

    CATATAN PENTING: thumbnail cuma satu frame (biasanya frame pertama/cover), BUKAN
    seluruh isi video. Kalau video aslinya kompilasi banyak screenshot, kemungkinan
    besar cuma tempat di frame cover itu yang bisa terbaca -- tempat lain di
    screenshot-screenshot berikutnya tidak akan ikut terdeteksi lewat jalur ini.
    Untuk membaca semua frame video dibutuhkan fitur terpisah yang mengunduh &
    mengambil sample tiap frame video, yang belum diimplementasikan di sini.

    Melempar ExtractionError kalau image_url kosong, gambar gagal diunduh, API key
    belum diset, request gagal, atau AI tidak menemukan tempat apa pun di gambar.
    """
    if not image_url:
        raise ExtractionError("Tidak ada gambar thumbnail yang bisa dianalisis dari link ini.")

    image_b64, mime_type = _download_image_as_base64(image_url)

    parts = [
        {"inline_data": {"mime_type": mime_type, "data": image_b64}},
        {"text": "Baca gambar ini dan ekstrak tempat yang tertulis di dalamnya, jika ada."},
    ]
    places = _call_gemini(_IMAGE_SYSTEM_PROMPT, parts)

    if not places:
        raise ExtractionError(
            "AI tidak menemukan tempat yang bisa dikenali, baik dari teks maupun gambar cover video ini. "
            "Kemungkinan videonya berupa slideshow screenshot tanpa teks yang terbaca di frame cover -- "
            "silakan isi manual."
        )

    return places


def extract_places(raw_text: str, thumbnail_url: Optional[str] = None) -> tuple[List[dict], bool]:
    """
    Titik masuk utama: coba ekstraksi dari teks dulu (lebih akurat & bisa multi-tempat
    penuh). Kalau teksnya kosong atau AI tidak menemukan apa pun dari teks, DAN ada
    thumbnail -- coba fallback baca gambar cover-nya.

    Mengembalikan (places, used_image_fallback) supaya caller tahu & bisa kasih
    peringatan yang sesuai ke user (karena hasil dari gambar cover kemungkinan
    tidak selengkap kalau videonya kompilasi banyak screenshot).
    """
    try:
        return extract_places_from_text(raw_text), False
    except ExtractionError as text_error:
        if not thumbnail_url:
            raise
        try:
            return extract_places_from_image(thumbnail_url), True
        except ExtractionError:
            # Kalau fallback gambar juga gagal, lempar error dari jalur teks --
            # pesannya biasanya lebih informatif ("tidak ada teks caption...").
            raise text_error
