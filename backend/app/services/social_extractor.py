import html
import re
from enum import Enum
from typing import Optional
from urllib.parse import quote

import httpx


class DetectedPlatform(str, Enum):
    youtube = "youtube"
    tiktok = "tiktok"
    unknown = "unknown"


_PATTERNS = {
    DetectedPlatform.youtube: re.compile(r"(youtube\.com|youtu\.be)", re.IGNORECASE),
    DetectedPlatform.tiktok: re.compile(r"tiktok\.com", re.IGNORECASE),
}

_OEMBED_ENDPOINTS = {
    DetectedPlatform.youtube: "https://www.youtube.com/oembed?url={url}&format=json",
    DetectedPlatform.tiktok: "https://www.tiktok.com/oembed?url={url}",
}


class ExtractionError(Exception):
    """Raised when we can't fetch or parse metadata from a social media URL."""


def detect_platform(url: str) -> DetectedPlatform:
    for platform, pattern in _PATTERNS.items():
        if pattern.search(url):
            return platform
    return DetectedPlatform.unknown


def fetch_oembed_metadata(url: str, platform: DetectedPlatform) -> dict:
    """
    Ambil metadata publik (title/caption, author, thumbnail) via oEmbed resmi.
    Hanya YouTube & TikTok yang didukung -- keduanya oEmbed publik gratis
    tanpa perlu API key/app review, jadi stabil dipakai di production.
    """
    if platform not in _OEMBED_ENDPOINTS:
        raise ExtractionError(
            f"Platform '{platform.value}' belum didukung untuk auto-extract. "
            "Silakan isi form manual."
        )

    endpoint = _OEMBED_ENDPOINTS[platform].format(url=quote(url, safe=""))

    try:
        with httpx.Client(timeout=10.0, follow_redirects=True) as client:
            resp = client.get(endpoint)
            resp.raise_for_status()
            data = resp.json()
    except httpx.HTTPStatusError as e:
        raise ExtractionError(
            f"Gagal mengambil data dari {platform.value} (status {e.response.status_code}). "
            "Link mungkin privat, sudah dihapus, atau formatnya tidak dikenali."
        )
    except httpx.RequestError as e:
        raise ExtractionError(f"Gagal terhubung ke {platform.value}: {e}")
    except ValueError:
        raise ExtractionError(f"Respons dari {platform.value} tidak bisa dibaca.")

    return {
        "title": data.get("title"),
        "author_name": data.get("author_name"),
        "thumbnail_url": data.get("thumbnail_url"),
        "html": data.get("html"),  # kadang caption penuh ada di sini untuk TikTok
    }


_META_DESCRIPTION_PATTERNS = [
    # og:description biasanya paling lengkap (caption penuh / deskripsi video,
    # termasuk daftar tempat + timestamp kalau video kompilasi)
    re.compile(r'<meta[^>]+property=["\']og:description["\'][^>]+content=["\'](.*?)["\']', re.IGNORECASE | re.DOTALL),
    re.compile(r'<meta[^>]+content=["\'](.*?)["\'][^>]+property=["\']og:description["\']', re.IGNORECASE | re.DOTALL),
    re.compile(r'<meta[^>]+name=["\']description["\'][^>]+content=["\'](.*?)["\']', re.IGNORECASE | re.DOTALL),
]

_BROWSER_HEADERS = {
    # Beberapa platform (terutama TikTok) menolak/mengembalikan HTML kosong untuk
    # request tanpa User-Agent yang wajar.
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
}


def fetch_page_description(url: str) -> Optional[str]:
    """
    Ambil og:description (atau meta description) langsung dari halaman video.
    Ini best-effort: kalau gagal (diblokir, timeout, struktur halaman berubah, dll)
    kita tidak boleh menggagalkan seluruh alur import -- cukup kembalikan None dan
    AI akan bekerja dengan teks yang lebih terbatas dari oEmbed saja.

    Untuk video kompilasi (misal "5 kuliner hits di Bandung", "10 spot healing Jogja"),
    daftar tempatnya biasanya ada di deskripsi lengkap ini, bukan di title oEmbed yang
    sering terpotong pendek -- jadi field ini penting supaya AI bisa mendeteksi &
    mengekstrak semua tempat, bukan cuma satu.
    """
    try:
        with httpx.Client(timeout=8.0, follow_redirects=True, headers=_BROWSER_HEADERS) as client:
            resp = client.get(url)
            if resp.status_code >= 400:
                return None
            body = resp.text
    except httpx.HTTPError:
        return None

    for pattern in _META_DESCRIPTION_PATTERNS:
        match = pattern.search(body)
        if match:
            description = html.unescape(match.group(1)).strip()
            if description:
                return description
    return None


def build_raw_text_for_ai(metadata: dict, description: Optional[str] = None) -> str:
    """Gabungkan field metadata jadi satu teks yang siap dikirim ke AI untuk diparse."""
    parts = []
    if metadata.get("title"):
        parts.append(f"Judul/caption (oEmbed): {metadata['title']}")
    if description and description.strip() and description.strip() != (metadata.get("title") or "").strip():
        parts.append(f"Deskripsi lengkap video: {description.strip()}")
    if metadata.get("author_name"):
        parts.append(f"Akun: {metadata['author_name']}")
    return "\n".join(parts) if parts else ""
