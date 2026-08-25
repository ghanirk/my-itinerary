import base64

import httpx
import pytest
import respx

from app.services.ai_extract import (
    extract_places,
    extract_places_from_image,
    extract_places_from_text,
)
from app.services.social_extractor import ExtractionError

GEMINI_URL_PATTERN = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"


def _gemini_json_response(payload: dict) -> httpx.Response:
    """Bentuk response Gemini yang wajar: JSON hasil ekstraksi dibungkus di candidates[0].content.parts[0].text."""
    import json

    return httpx.Response(
        200,
        json={
            "candidates": [
                {"content": {"parts": [{"text": json.dumps(payload)}]}}
            ]
        },
    )


# ---------- extract_places_from_text: kasus normal ----------

@respx.mock
def test_extract_places_from_text_single_place():
    respx.post(GEMINI_URL_PATTERN).mock(
        return_value=_gemini_json_response(
            {
                "is_compilation": False,
                "places": [
                    {
                        "name": "Bangi Kopi Lokantara",
                        "category": "kuliner",
                        "price_min": 20000,
                        "price_max": 45000,
                        "city": "Jakarta",
                        "confidence": "high",
                    }
                ],
            }
        )
    )

    places = extract_places_from_text("Nongkrong santai di Bangi Kopi Lokantara, Jakarta")

    assert len(places) == 1
    assert places[0]["name"] == "Bangi Kopi Lokantara"
    assert places[0]["category"] == "kuliner"
    assert places[0]["price_max"] == 45000


@respx.mock
def test_extract_places_from_text_compilation_video_multiple_places():
    respx.post(GEMINI_URL_PATTERN).mock(
        return_value=_gemini_json_response(
            {
                "is_compilation": True,
                "places": [
                    {"name": "Warung A", "category": "kuliner", "price_min": 15000, "price_max": 15000, "city": "Bandung", "confidence": "high"},
                    {"name": "Warung B", "category": "kuliner", "price_min": 0, "price_max": 0, "city": "Bandung", "confidence": "low"},
                    {"name": "Warung C", "category": "kuliner", "price_min": 25000, "price_max": 30000, "city": "Bandung", "confidence": "high"},
                ],
            }
        )
    )

    places = extract_places_from_text("5 kuliner hits di Bandung: 1. Warung A 2. Warung B 3. Warung C")

    assert len(places) == 3
    assert [p["name"] for p in places] == ["Warung A", "Warung B", "Warung C"]


# ---------- Normalisasi field (kategori invalid, price_max hilang, dll) ----------

@respx.mock
def test_normalize_place_fills_missing_price_max_from_price_min():
    respx.post(GEMINI_URL_PATTERN).mock(
        return_value=_gemini_json_response(
            {"places": [{"name": "Kedai X", "price_min": 20000, "city": "Solo"}]}
        )
    )

    places = extract_places_from_text("Kedai X di Solo, harga 20rb")

    assert places[0]["price_max"] == 20000  # fallback ke price_min saat price_max tidak ada


@respx.mock
def test_normalize_place_defaults_invalid_category_to_fun():
    respx.post(GEMINI_URL_PATTERN).mock(
        return_value=_gemini_json_response(
            {"places": [{"name": "Taman Y", "category": "kategori-ngasal", "city": "Bogor"}]}
        )
    )

    places = extract_places_from_text("Healing di Taman Y, Bogor")

    assert places[0]["category"] == "fun"


# ---------- Edge case & error handling ----------

def test_extract_places_from_text_empty_raw_text_raises_without_calling_api():
    with pytest.raises(ExtractionError):
        extract_places_from_text("   ")


@respx.mock
def test_extract_places_from_text_no_places_found_raises():
    respx.post(GEMINI_URL_PATTERN).mock(
        return_value=_gemini_json_response({"is_compilation": False, "places": []})
    )

    with pytest.raises(ExtractionError):
        extract_places_from_text("Video ngobrol santai gak ada tempat spesifik disebutin")


@respx.mock
def test_extract_places_from_text_blocked_by_safety_filter_raises():
    respx.post(GEMINI_URL_PATTERN).mock(
        return_value=httpx.Response(
            200,
            json={"candidates": [], "promptFeedback": {"blockReason": "SAFETY"}},
        )
    )

    with pytest.raises(ExtractionError, match="SAFETY"):
        extract_places_from_text("teks apapun")


@respx.mock
def test_extract_places_from_text_malformed_json_raises():
    respx.post(GEMINI_URL_PATTERN).mock(
        return_value=httpx.Response(
            200,
            json={"candidates": [{"content": {"parts": [{"text": "ini bukan JSON sama sekali {{{"}]}}]},
        )
    )

    with pytest.raises(ExtractionError):
        extract_places_from_text("teks apapun")


@respx.mock
def test_extract_places_from_text_strips_markdown_json_fence():
    """Model kadang bandel & tetap bungkus jawaban dengan ```json ... ``` walau sudah diminta JSON murni."""
    import json

    payload = {"places": [{"name": "Kafe Z", "city": "Malang"}]}
    wrapped = "```json\n" + json.dumps(payload) + "\n```"
    respx.post(GEMINI_URL_PATTERN).mock(
        return_value=httpx.Response(
            200,
            json={"candidates": [{"content": {"parts": [{"text": wrapped}]}}]},
        )
    )

    places = extract_places_from_text("Kafe Z enak banget di Malang")
    assert places[0]["name"] == "Kafe Z"


@respx.mock
def test_extract_places_from_text_gemini_500_raises_extraction_error():
    respx.post(GEMINI_URL_PATTERN).mock(return_value=httpx.Response(500, text="internal error"))

    with pytest.raises(ExtractionError):
        extract_places_from_text("teks apapun")


@respx.mock
def test_extract_places_from_text_network_error_raises_extraction_error():
    respx.post(GEMINI_URL_PATTERN).mock(side_effect=httpx.ConnectError("no route to host"))

    with pytest.raises(ExtractionError):
        extract_places_from_text("teks apapun")


def test_extract_places_from_text_missing_api_key_raises(monkeypatch):
    from app.config import settings

    monkeypatch.setattr(settings, "GEMINI_API_KEY", "")
    with pytest.raises(ExtractionError, match="GEMINI_API_KEY"):
        extract_places_from_text("teks apapun")


def test_extract_places_caps_at_max_places_per_video():
    """Kalau AI 'ngarang' kebanyakan tempat dari teks ambigu, hasil harus dipotong ke batas aman."""
    import json as _json

    many_places = [
        {"name": f"Tempat {i}", "category": "kuliner", "city": "Jakarta"} for i in range(30)
    ]
    with respx.mock:
        respx.post(GEMINI_URL_PATTERN).mock(
            return_value=httpx.Response(
                200,
                json={
                    "candidates": [
                        {"content": {"parts": [{"text": _json.dumps({"places": many_places})}]}}
                    ]
                },
            )
        )
        places = extract_places_from_text("teks berisi banyak sekali tempat")

    assert len(places) == 15  # _MAX_PLACES_PER_VIDEO


# ---------- extract_places_from_image (fallback thumbnail) ----------

@respx.mock
def test_extract_places_from_image_downloads_and_sends_to_gemini():
    image_bytes = b"\xff\xd8\xff\xe0fake-jpeg-bytes"
    respx.get("https://example.com/thumb.jpg").mock(
        return_value=httpx.Response(200, content=image_bytes, headers={"content-type": "image/jpeg"})
    )
    respx.post(GEMINI_URL_PATTERN).mock(
        return_value=_gemini_json_response(
            {"places": [{"name": "Dari Gambar", "category": "kuliner", "city": "Jakarta", "confidence": "low"}]}
        )
    )

    places = extract_places_from_image("https://example.com/thumb.jpg")

    assert places[0]["name"] == "Dari Gambar"
    # pastikan gambar beneran dikirim sebagai inline_data base64 ke Gemini
    sent_body = respx.calls.last.request.content
    assert base64.b64encode(image_bytes).decode("ascii")[:20] in sent_body.decode("utf-8", errors="ignore")


def test_extract_places_from_image_empty_url_raises():
    with pytest.raises(ExtractionError):
        extract_places_from_image("")


@respx.mock
def test_extract_places_from_image_download_failure_raises():
    respx.get("https://example.com/broken.jpg").mock(return_value=httpx.Response(404))

    with pytest.raises(ExtractionError):
        extract_places_from_image("https://example.com/broken.jpg")


# ---------- extract_places: orkestrasi teks -> fallback gambar ----------

@respx.mock
def test_extract_places_falls_back_to_image_when_text_empty():
    image_bytes = b"fake-image-bytes"
    respx.get("https://example.com/thumb.jpg").mock(
        return_value=httpx.Response(200, content=image_bytes, headers={"content-type": "image/jpeg"})
    )
    respx.post(GEMINI_URL_PATTERN).mock(
        return_value=_gemini_json_response(
            {"places": [{"name": "Dari Thumbnail", "category": "fun", "city": "Bali", "confidence": "low"}]}
        )
    )

    places, used_image_fallback = extract_places("", thumbnail_url="https://example.com/thumb.jpg")

    assert used_image_fallback is True
    assert places[0]["name"] == "Dari Thumbnail"


@respx.mock
def test_extract_places_prefers_text_over_image_when_both_available():
    respx.post(GEMINI_URL_PATTERN).mock(
        return_value=_gemini_json_response(
            {"places": [{"name": "Dari Teks", "category": "kuliner", "city": "Jakarta", "confidence": "high"}]}
        )
    )

    places, used_image_fallback = extract_places(
        "Ada nama tempat jelas di sini", thumbnail_url="https://example.com/thumb.jpg"
    )

    assert used_image_fallback is False
    assert places[0]["name"] == "Dari Teks"


def test_extract_places_raises_original_text_error_when_no_thumbnail():
    with pytest.raises(ExtractionError, match="caption"):
        extract_places("   ", thumbnail_url=None)
