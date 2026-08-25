import httpx
import pytest
import respx

from app.services.social_extractor import (
    DetectedPlatform,
    ExtractionError,
    build_gmaps_search_url,
    build_raw_text_for_ai,
    detect_platform,
    fetch_oembed_metadata,
    fetch_page_description,
)


# ---------- detect_platform ----------

@pytest.mark.parametrize(
    "url,expected",
    [
        ("https://www.tiktok.com/@user/video/123", DetectedPlatform.tiktok),
        ("https://vt.tiktok.com/abc123/", DetectedPlatform.tiktok),
        ("https://www.youtube.com/watch?v=abc", DetectedPlatform.youtube),
        ("https://youtu.be/abc123", DetectedPlatform.youtube),
        ("https://www.instagram.com/reel/abc", DetectedPlatform.unknown),
        ("https://twitter.com/user/status/123", DetectedPlatform.unknown),
        ("not a url at all", DetectedPlatform.unknown),
    ],
)
def test_detect_platform(url, expected):
    assert detect_platform(url) == expected


# ---------- fetch_oembed_metadata ----------

@respx.mock
def test_fetch_oembed_metadata_tiktok_success():
    url = "https://www.tiktok.com/@nurin.staniawan/video/7665154967497444629"
    respx.get("https://www.tiktok.com/oembed").mock(
        return_value=httpx.Response(
            200,
            json={
                "title": "5 kuliner hits di Bandung yang wajib dicoba!",
                "author_name": "nurin.staniawan",
                "thumbnail_url": "https://example.com/thumb.jpg",
                "html": "<blockquote>...</blockquote>",
            },
        )
    )

    result = fetch_oembed_metadata(url, DetectedPlatform.tiktok)

    assert result["title"] == "5 kuliner hits di Bandung yang wajib dicoba!"
    assert result["author_name"] == "nurin.staniawan"
    assert result["thumbnail_url"] == "https://example.com/thumb.jpg"


@respx.mock
def test_fetch_oembed_metadata_http_error_raises_extraction_error():
    url = "https://www.tiktok.com/@user/video/deleted"
    respx.get("https://www.tiktok.com/oembed").mock(return_value=httpx.Response(404))

    with pytest.raises(ExtractionError):
        fetch_oembed_metadata(url, DetectedPlatform.tiktok)


@respx.mock
def test_fetch_oembed_metadata_network_error_raises_extraction_error():
    url = "https://www.youtube.com/watch?v=abc"
    respx.get("https://www.youtube.com/oembed").mock(
        side_effect=httpx.ConnectError("boom")
    )

    with pytest.raises(ExtractionError):
        fetch_oembed_metadata(url, DetectedPlatform.youtube)


def test_fetch_oembed_metadata_unsupported_platform_raises():
    with pytest.raises(ExtractionError):
        fetch_oembed_metadata("https://instagram.com/reel/abc", DetectedPlatform.unknown)


# ---------- fetch_page_description ----------

@respx.mock
def test_fetch_page_description_extracts_og_description():
    url = "https://www.tiktok.com/@user/video/123"
    html = """
    <html><head>
    <meta property="og:description" content="5 kuliner hits di Bandung: 1. Warung A 2. Warung B">
    </head></html>
    """
    respx.get(url).mock(return_value=httpx.Response(200, text=html))

    description = fetch_page_description(url)

    assert description == "5 kuliner hits di Bandung: 1. Warung A 2. Warung B"


@respx.mock
def test_fetch_page_description_returns_none_on_failure():
    """Best-effort: kalau gagal, harus return None, BUKAN raise -- karena caller
    (import_preview) tetap harus bisa lanjut pakai title oEmbed saja."""
    url = "https://www.tiktok.com/@user/video/123"
    respx.get(url).mock(side_effect=httpx.ConnectTimeout("timeout"))

    assert fetch_page_description(url) is None


@respx.mock
def test_fetch_page_description_returns_none_when_no_meta_tag():
    url = "https://www.tiktok.com/@user/video/123"
    respx.get(url).mock(return_value=httpx.Response(200, text="<html><body>no meta here</body></html>"))

    assert fetch_page_description(url) is None


# ---------- build_gmaps_search_url ----------

def test_build_gmaps_search_url_includes_name_and_city():
    url = build_gmaps_search_url("Bangi Kopi Lokantara", "Jakarta")
    assert url.startswith("https://www.google.com/maps/search/?api=1&query=")
    assert "Bangi" in url and "Jakarta" in url


def test_build_gmaps_search_url_handles_empty_city():
    url = build_gmaps_search_url("Warung Tanpa Kota", "")
    assert "Warung" in url
    # tidak boleh nyisain ", " nyangkut kalau city kosong
    assert "%2C" not in url or "Warung%20Tanpa%20Kota" in url


# ---------- build_raw_text_for_ai ----------

def test_build_raw_text_for_ai_combines_title_description_author():
    metadata = {"title": "Judul pendek", "author_name": "akun_tester"}
    text = build_raw_text_for_ai(metadata, description="Deskripsi lengkap yang beda dari title")

    assert "Judul pendek" in text
    assert "Deskripsi lengkap yang beda dari title" in text
    assert "akun_tester" in text


def test_build_raw_text_for_ai_skips_duplicate_description():
    """Kalau deskripsi sama persis dengan title, jangan diulang dua kali di teks."""
    metadata = {"title": "Sama saja"}
    text = build_raw_text_for_ai(metadata, description="Sama saja")

    assert text.count("Sama saja") == 1


def test_build_raw_text_for_ai_empty_metadata_returns_empty_string():
    assert build_raw_text_for_ai({}) == ""
