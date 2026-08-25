import respx
import httpx

from app.config import settings
from app.models import Place, PlaceCategory, PlaceStatus, SourceType


def _make_place(db_session_factory, **overrides):
    from tests.conftest import TestingSessionLocal

    db = TestingSessionLocal()
    defaults = dict(
        name="Tempat Test",
        category=PlaceCategory.kuliner,
        price_min=10000,
        price_max=20000,
        city="Jakarta",
        gmaps_url="https://maps.google.com/?q=test",
        source_type=SourceType.manual,
        status=PlaceStatus.published,
        created_by=overrides.pop("created_by"),
    )
    defaults.update(overrides)
    place = Place(**defaults)
    db.add(place)
    db.commit()
    db.close()


def _get_user_id(client, auth_headers):
    """
    App ini tidak punya endpoint /auth/me, jadi ambil user_id dengan cara paling
    murah: register user baru khusus buat test ini & pakai id dari response-nya.
    (auth_headers fixture generik dipakai bareng test lain jadi tidak dipakai di sini.)
    """
    import uuid

    email = f"user-{uuid.uuid4().hex[:8]}@example.com"
    resp = client.post(
        "/auth/register",
        json={"name": "Place Owner", "email": email, "password": "secret123"},
    )
    return resp.json()["user"]["id"]


# ---------- Pagination & search on GET /places ----------

def test_list_places_pagination_defaults(client, auth_headers):
    user_id = _get_user_id(client, auth_headers)
    for i in range(25):
        _make_place(None, name=f"Tempat {i}", created_by=user_id)

    resp = client.get("/places")
    body = resp.json()

    assert resp.status_code == 200
    assert body["total"] == 25
    assert body["limit"] == 20  # default
    assert body["offset"] == 0
    assert len(body["items"]) == 20


def test_list_places_pagination_second_page(client, auth_headers):
    user_id = _get_user_id(client, auth_headers)
    for i in range(25):
        _make_place(None, name=f"Tempat {i}", created_by=user_id)

    resp = client.get("/places?limit=20&offset=20")
    body = resp.json()

    assert body["total"] == 25
    assert len(body["items"]) == 5  # sisa 5 item di halaman kedua


def test_list_places_limit_capped_at_100(client, auth_headers):
    resp = client.get("/places?limit=500")
    assert resp.status_code == 422  # ditolak validasi, bukan diam-diam dipotong


def test_list_places_search_by_name(client, auth_headers):
    user_id = _get_user_id(client, auth_headers)
    _make_place(None, name="Bangi Kopi Lokantara", created_by=user_id)
    _make_place(None, name="Warung Nasi Padang", created_by=user_id)

    resp = client.get("/places?q=kopi")
    body = resp.json()

    assert body["total"] == 1
    assert body["items"][0]["name"] == "Bangi Kopi Lokantara"


def test_list_places_search_case_insensitive(client, auth_headers):
    user_id = _get_user_id(client, auth_headers)
    _make_place(None, name="Bangi Kopi Lokantara", created_by=user_id)

    resp = client.get("/places?q=KOPI")
    assert resp.json()["total"] == 1


# ---------- Rate limit on /places/import/preview ----------

@respx.mock
def test_import_preview_blocked_after_daily_quota_exceeded(client, auth_headers, monkeypatch):
    monkeypatch.setattr(settings, "MAX_IMPORTS_PER_DAY", 2)

    respx.get("https://www.tiktok.com/oembed").mock(
        return_value=httpx.Response(
            200,
            json={"title": "Kopi enak di Jakarta", "author_name": "acc", "thumbnail_url": None},
        )
    )
    respx.get("https://www.tiktok.com/@user/video/1").mock(
        return_value=httpx.Response(200, text="<html></html>")
    )
    respx.post(
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
    ).mock(
        return_value=httpx.Response(
            200,
            json={
                "candidates": [
                    {
                        "content": {
                            "parts": [
                                {
                                    "text": (
                                        '{"is_compilation": false, "places": '
                                        '[{"name": "Kopi X", "category": "kuliner", '
                                        '"price_min": 0, "price_max": 0, "city": "Jakarta", '
                                        '"confidence": "high"}]}'
                                    )
                                }
                            ]
                        }
                    }
                ]
            },
        )
    )

    url = "https://www.tiktok.com/@user/video/1"

    r1 = client.post("/places/import/preview", json={"url": url}, headers=auth_headers)
    assert r1.status_code == 200

    r2 = client.post("/places/import/preview", json={"url": url}, headers=auth_headers)
    assert r2.status_code == 200

    # panggilan ke-3 harus kena limit (quota di-set 2 di test ini)
    r3 = client.post("/places/import/preview", json={"url": url}, headers=auth_headers)
    assert r3.status_code == 429


def test_import_preview_unknown_platform_not_counted_toward_quota(client, auth_headers, monkeypatch):
    """Link yang gagal duluan (platform tidak dikenal) tidak boleh makan kuota harian."""
    monkeypatch.setattr(settings, "MAX_IMPORTS_PER_DAY", 1)

    r1 = client.post(
        "/places/import/preview",
        json={"url": "https://instagram.com/reel/abc"},
        headers=auth_headers,
    )
    assert r1.status_code == 400

    r2 = client.post(
        "/places/import/preview",
        json={"url": "https://instagram.com/reel/xyz"},
        headers=auth_headers,
    )
    # masih 400 (platform tetap tidak didukung), BUKAN 429 -- membuktikan quota belum kepakai
    assert r2.status_code == 400
