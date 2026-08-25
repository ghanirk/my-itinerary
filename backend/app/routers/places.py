from datetime import datetime, timedelta
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import Place, PlaceReport, ImportLog, User, PlaceCategory, PlaceStatus, SourceType
from app.schemas import (
    PlaceCreate,
    PlaceOut,
    PlaceListResponse,
    PlaceReportCreate,
    ImportUrlRequest,
    ImportPreviewResponse,
    ImportPreviewItem,
    ImportBulkRequest,
    ImportBulkResponse,
    ImportBulkResultItem,
)
from app.auth import get_current_user
from app.services.social_extractor import (
    detect_platform,
    fetch_oembed_metadata,
    fetch_page_description,
    build_raw_text_for_ai,
    build_gmaps_search_url,
    DetectedPlatform,
    ExtractionError,
)
from app.services.ai_extract import extract_places

router = APIRouter(prefix="/places", tags=["places"])

_PLATFORM_TO_SOURCE = {
    DetectedPlatform.youtube: SourceType.youtube,
    DetectedPlatform.tiktok: SourceType.tiktok,
}


@router.get("", response_model=PlaceListResponse)
def list_places(
    city: Optional[str] = None,
    category: Optional[PlaceCategory] = None,
    budget_min: Optional[int] = Query(None, ge=0),
    budget_max: Optional[int] = Query(None, ge=0),
    q_search: Optional[str] = Query(None, alias="q", description="Cari berdasarkan nama tempat"),
    limit: int = Query(20, ge=1, le=100, description="Jumlah item per halaman, maksimal 100"),
    offset: int = Query(0, ge=0, description="Jumlah item yang dilewati (untuk halaman berikutnya)"),
    db: Session = Depends(get_db),
):
    """
    Filter tempat: by kota, kategori, rentang budget, dan pencarian nama (opsional).
    Sesuai dokumen: tempat cocok jika rentang harganya overlap dengan budget user.

    Hasil di-paginate (default 20 item/halaman) supaya endpoint ini tetap ringan
    walau jumlah places sudah banyak -- pakai `limit`/`offset` untuk "load more"
    atau nomor halaman di sisi frontend. `total` di response = jumlah total item
    yang cocok dengan filter (sebelum pagination), dipakai frontend untuk hitung
    ada berapa halaman / apakah masih ada data selanjutnya.
    """
    q = db.query(Place).filter(Place.status == PlaceStatus.published)

    if city:
        q = q.filter(Place.city.ilike(f"%{city}%"))
    if category:
        q = q.filter(Place.category == category)
    if budget_min is not None:
        q = q.filter(Place.price_max >= budget_min)
    if budget_max is not None:
        q = q.filter(Place.price_min <= budget_max)
    if q_search:
        q = q.filter(Place.name.ilike(f"%{q_search}%"))

    total = q.count()
    items = (
        q.order_by(Place.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    return PlaceListResponse(items=items, total=total, limit=limit, offset=offset)


@router.get("/{place_id}", response_model=PlaceOut)
def get_place(place_id: str, db: Session = Depends(get_db)):
    place = db.query(Place).filter(Place.id == place_id).first()
    if not place:
        raise HTTPException(status_code=404, detail="Tempat tidak ditemukan.")
    return place


@router.post("", response_model=PlaceOut, status_code=201)
def create_place(
    payload: PlaceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # gmaps_url wajib diisi (baik dari form manual maupun hasil koreksi user atas draft AI)
    if not payload.gmaps_url or not payload.gmaps_url.strip():
        raise HTTPException(status_code=422, detail="Link Google Maps wajib diisi.")

    # Deduplication sederhana: cek gmaps_url yang sama persis sebelum simpan
    dup = db.query(Place).filter(Place.gmaps_url == payload.gmaps_url).first()
    if dup:
        raise HTTPException(
            status_code=409,
            detail=f"Tempat dengan link Google Maps ini sudah ada: '{dup.name}'.",
        )

    place = Place(**payload.model_dump(), created_by=current_user.id)
    db.add(place)
    db.commit()
    db.refresh(place)
    return place


@router.post("/import/preview", response_model=ImportPreviewResponse)
def import_preview(
    payload: ImportUrlRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Alur (lihat dokumen produk 8.1):
    1. User tempel URL TikTok atau YouTube
    2. Deteksi platform & ambil metadata (oEmbed) + deskripsi lengkap halaman
    3. AI ekstrak jadi satu atau LEBIH tempat terstruktur (video kompilasi ->
       banyak tempat sekaligus, video biasa -> tetap 1 tempat)
    4. Kembalikan semuanya sebagai draft/preview -- BELUM disimpan ke database bersama.

    User mengedit tiap hasil ini di frontend, baru submit ke POST /places/import/bulk
    untuk publish sekaligus. Instagram & Twitter/X sengaja belum didukung (butuh akses
    developer app pihak ketiga yang lebih rumit & kurang stabil) -- untuk itu user
    pakai form manual.

    Rate limited per user (lihat settings.MAX_IMPORTS_PER_DAY) karena tiap panggilan
    endpoint ini memanggil Gemini API -- tanpa limit, satu user bisa menghabiskan
    quota/cost AI untuk semua orang.
    """
    if settings.MAX_IMPORTS_PER_DAY > 0:
        since = datetime.utcnow() - timedelta(hours=24)
        usage_count = (
            db.query(ImportLog)
            .filter(ImportLog.user_id == current_user.id, ImportLog.created_at >= since)
            .count()
        )
        if usage_count >= settings.MAX_IMPORTS_PER_DAY:
            raise HTTPException(
                status_code=429,
                detail=(
                    f"Kamu sudah mencapai batas {settings.MAX_IMPORTS_PER_DAY}x import otomatis "
                    "dalam 24 jam terakhir. Coba lagi nanti, atau isi tempat ini lewat form manual."
                ),
            )

    platform = detect_platform(payload.url)

    if platform == DetectedPlatform.unknown:
        raise HTTPException(
            status_code=400,
            detail="Link tidak dikenali. Saat ini auto-import hanya mendukung link TikTok atau YouTube.",
        )

    try:
        metadata = fetch_oembed_metadata(payload.url, platform)
        # Best-effort: deskripsi lengkap halaman (kalau berhasil diambil) memberi AI
        # jauh lebih banyak konteks dibanding title oEmbed saja -- ini kunci supaya
        # video kompilasi ("5 kuliner hits di ...") bisa terdeteksi & dipecah dengan benar.
        description = fetch_page_description(payload.url)
        raw_text = build_raw_text_for_ai(metadata, description)
        # extract_places mencoba teks dulu; kalau teksnya kosong/nihil DAN ada thumbnail,
        # otomatis fallback membaca gambar cover video (untuk video screenshot tanpa caption).
        extracted_places, used_image_fallback = extract_places(raw_text, metadata.get("thumbnail_url"))
    except ExtractionError as e:
        raise HTTPException(status_code=422, detail=str(e))

    # Baru dicatat sebagai "pemakaian kuota" setelah AI beneran berhasil dipanggil --
    # kalau gagal duluan (link salah, platform tidak didukung, dll) tidak dihitung.
    db.add(ImportLog(user_id=current_user.id, source_url=payload.url))
    db.commit()

    items = []
    for extracted in extracted_places:
        warning = None
        if used_image_fallback:
            warning = (
                "Tidak ada caption/deskripsi teks di video ini, jadi hasil ini dibaca AI dari "
                "gambar cover/thumbnail saja. Kalau video ini sebenarnya berisi beberapa tempat "
                "lain (mis. slideshow screenshot), tempat-tempat itu TIDAK ikut terbaca -- mohon "
                "tambahkan manual dan periksa hasil ini sebelum disimpan."
            )
        elif extracted["confidence"] == "low":
            warning = "AI kurang yakin dengan hasil ekstraksi ini -- mohon periksa & lengkapi sebelum disimpan."
        items.append(
            ImportPreviewItem(
                name=extracted["name"],
                category=extracted["category"],
                price_min=extracted["price_min"],
                price_max=extracted["price_max"],
                city=extracted["city"],
                gmaps_url=build_gmaps_search_url(extracted["name"], extracted["city"]),
                confidence=extracted["confidence"],
                warning=warning,
            )
        )

    return ImportPreviewResponse(
        is_compilation=len(items) > 1,
        source_type=_PLATFORM_TO_SOURCE[platform],
        source_url=payload.url,
        photo_url=metadata.get("thumbnail_url"),
        items=items,
    )


@router.post("/import/bulk", response_model=ImportBulkResponse, status_code=201)
def import_bulk(
    payload: ImportBulkRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Simpan satu atau banyak tempat sekaligus hasil koreksi user dari /import/preview
    (dipakai terutama untuk video kompilasi yang menghasilkan >1 tempat).

    Tiap item diproses independen -- kalau satu item duplikat/gagal, item lain tetap
    lanjut tersimpan. Hasil per item dikembalikan supaya frontend bisa menampilkan
    status masing-masing (mis. "4 tersimpan, 1 duplikat").
    """
    if not payload.items:
        raise HTTPException(status_code=400, detail="Tidak ada tempat untuk disimpan.")

    results = []
    created_count = 0
    skipped_count = 0

    for item in payload.items:
        if not item.gmaps_url or not item.gmaps_url.strip():
            results.append(
                ImportBulkResultItem(
                    name=item.name,
                    status="error",
                    detail="Link Google Maps wajib diisi sebelum disimpan.",
                )
            )
            skipped_count += 1
            continue

        dup = db.query(Place).filter(Place.gmaps_url == item.gmaps_url).first()
        if dup:
            results.append(
                ImportBulkResultItem(
                    name=item.name,
                    status="duplicate",
                    detail=f"Tempat dengan link Google Maps ini sudah ada: '{dup.name}'.",
                )
            )
            skipped_count += 1
            continue

        try:
            place = Place(
                name=item.name,
                category=item.category,
                price_min=item.price_min,
                price_max=item.price_max,
                gmaps_url=item.gmaps_url,
                city=item.city,
                source_type=payload.source_type,
                source_url=payload.source_url,
                photo_url=item.photo_url,
                opening_hours=item.opening_hours,
                notes=item.notes,
                status=PlaceStatus.published,
                created_by=current_user.id,
            )
            db.add(place)
            db.commit()
            db.refresh(place)
            results.append(ImportBulkResultItem(name=item.name, status="created", place=place))
            created_count += 1
        except Exception as e:
            db.rollback()
            results.append(ImportBulkResultItem(name=item.name, status="error", detail=str(e)))
            skipped_count += 1

    return ImportBulkResponse(results=results, created_count=created_count, skipped_count=skipped_count)


@router.post("/{place_id}/report", status_code=201)
def report_place(
    place_id: str,
    payload: PlaceReportCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    place = db.query(Place).filter(Place.id == place_id).first()
    if not place:
        raise HTTPException(status_code=404, detail="Tempat tidak ditemukan.")

    report = PlaceReport(place_id=place_id, user_id=current_user.id, reason=payload.reason)
    db.add(report)
    db.commit()
    return {"message": "Laporan diterima, terima kasih."}