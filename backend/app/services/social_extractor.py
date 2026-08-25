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


def build_raw_text_for_ai(metadata: dict) -> str:
    """Gabungkan field metadata jadi satu teks yang siap dikirim ke AI untuk diparse."""
    parts = []
    if metadata.get("title"):
        parts.append(f"Judul/caption: {metadata['title']}")
    if metadata.get("author_name"):
        parts.append(f"Akun: {metadata['author_name']}")
    return "\n".join(parts) if parts else ""
