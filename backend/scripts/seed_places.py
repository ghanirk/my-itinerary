"""
Seed 5 kota besar x 10 tempat (total 50 tempat) supaya listing tempat di app
tidak kosong dan menarik dilihat calon user baru.

Cara pakai (dijalankan SEKALI saja, aman di-run ulang -- otomatis skip tempat
yang namanya sama di kota yang sama, jadi tidak bikin duplikat):

    python scripts/seed_places.py

Jalankan dari dalam folder `backend/` (baik lokal maupun lewat tab "Console"
di Railway, yang working directory-nya sudah /code -- itu sama dengan folder
backend/ di repo ini).
"""
import sys
from pathlib import Path
from urllib.parse import quote

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database import SessionLocal
from app.models import User, Place
from app.models.enums import PlaceCategory, SourceType, PlaceStatus
from app.auth import hash_password

SEED_ADMIN_EMAIL = "seed-admin@my-itinerary.local"
SEED_ADMIN_NAME = "Seed Admin"

# (name, category, price_min, price_max, opening_hours, notes)
PLACES_BY_CITY: dict[str, list[tuple]] = {
    "Jakarta": [
        ("Ancol Dreamland", PlaceCategory.fun, 25000, 150000, "06:00 - 22:00", "Kawasan rekreasi tepi pantai dengan Dufan, Sea World, dan area pantai."),
        ("Taman Mini Indonesia Indah", PlaceCategory.fun, 20000, 25000, "07:00 - 22:00", "Taman budaya yang menampilkan miniatur rumah adat dari seluruh Indonesia."),
        ("Museum MACAN", PlaceCategory.fun, 60000, 100000, "10:00 - 19:00", "Museum seni modern dan kontemporer, cocok buat foto-foto estetik."),
        ("Kota Tua Jakarta", PlaceCategory.fun, 0, 5000, "09:00 - 18:00", "Kawasan bersejarah era kolonial, ramai penyewaan sepeda ontel."),
        ("Kebun Binatang Ragunan", PlaceCategory.alam, 4000, 4000, "07:00 - 16:00", "Kebun binatang luas dengan banyak area hijau untuk piknik keluarga."),
        ("Lapangan GBK Senayan", PlaceCategory.sport, 0, 20000, "05:00 - 22:00", "Trek jogging dan olahraga outdoor favorit warga Jakarta."),
        ("Sate Khas Senayan", PlaceCategory.kuliner, 30000, 80000, "10:00 - 22:00", "Sate ayam dan kambing legendaris dengan bumbu kacang khas."),
        ("Kopi Tuku", PlaceCategory.kuliner, 18000, 35000, "08:00 - 21:00", "Kedai kopi susu gula aren yang jadi tren di seluruh Indonesia."),
        ("Bakmi GM Kelapa Gading", PlaceCategory.kuliner, 35000, 60000, "10:00 - 21:00", "Bakmi ayam legendaris Jakarta sejak 1959."),
        ("Pasar Baru Culinary Walk", PlaceCategory.kuliner, 15000, 50000, "09:00 - 20:00", "Deretan jajanan legendaris peranakan di kawasan Pasar Baru."),
    ],
    "Bandung": [
        ("Kawah Putih", PlaceCategory.alam, 30000, 50000, "07:00 - 17:00", "Danau kawah vulkanik berwarna putih kehijauan di dataran tinggi Ciwidey."),
        ("Tangkuban Perahu", PlaceCategory.alam, 30000, 50000, "07:00 - 17:00", "Gunung berapi ikonik dengan kawah yang bisa dilihat dari dekat."),
        ("Dusun Bambu", PlaceCategory.fun, 25000, 40000, "10:00 - 21:00", "Wisata keluarga dengan suasana pedesaan dan spot foto hijau."),
        ("Farmhouse Lembang", PlaceCategory.fun, 30000, 50000, "09:00 - 21:00", "Wisata bertema Eropa dengan kandang domba dan spot foto unik."),
        ("Trans Studio Bandung", PlaceCategory.fun, 180000, 280000, "10:00 - 22:00", "Taman hiburan indoor terbesar dengan puluhan wahana."),
        ("Saung Angklung Udjo", PlaceCategory.fun, 60000, 100000, "09:00 - 17:00", "Pertunjukan budaya angklung yang interaktif dan edukatif."),
        ("Mie Kocok Mang Dadeng", PlaceCategory.kuliner, 20000, 35000, "08:00 - 20:00", "Mie kocok kikil legendaris khas Bandung."),
        ("Sate Maranggi Purwakarta", PlaceCategory.kuliner, 25000, 50000, "10:00 - 21:00", "Sate sapi khas dengan bumbu kecap dan sambal tomat segar."),
        ("Kopi Aroma", PlaceCategory.kuliner, 15000, 30000, "08:00 - 17:00", "Kedai kopi tua sejak 1930-an, favorit pecinta kopi klasik."),
        ("Punclut Jogging Track", PlaceCategory.sport, 0, 10000, "05:00 - 18:00", "Jalur lari dan sepeda dengan pemandangan kota Bandung dari atas bukit."),
    ],
    "Yogyakarta": [
        ("Candi Prambanan", PlaceCategory.fun, 50000, 375000, "06:00 - 17:00", "Kompleks candi Hindu terbesar di Indonesia, situs warisan dunia UNESCO."),
        ("Candi Borobudur", PlaceCategory.fun, 50000, 375000, "06:30 - 17:00", "Candi Buddha terbesar di dunia, ikon wisata Yogyakarta."),
        ("Malioboro Street", PlaceCategory.fun, 0, 0, "24 jam", "Jalan legendaris pusat belanja, kuliner, dan seni jalanan."),
        ("Pantai Parangtritis", PlaceCategory.alam, 10000, 10000, "24 jam", "Pantai berpasir dengan gumuk pasir dan sunset yang ikonik."),
        ("Kaliurang", PlaceCategory.alam, 15000, 15000, "07:00 - 17:00", "Kawasan sejuk di lereng Gunung Merapi dengan udara pegunungan."),
        ("Gudeg Yu Djum", PlaceCategory.kuliner, 20000, 40000, "07:00 - 22:00", "Gudeg legendaris khas Yogyakarta dengan rasa manis gurih."),
        ("Angkringan Kopi Joss", PlaceCategory.kuliner, 5000, 20000, "17:00 - 02:00", "Angkringan khas dengan kopi arang membara yang unik."),
        ("Bakpia Pathok 25", PlaceCategory.kuliner, 15000, 40000, "07:00 - 21:00", "Bakpia legendaris oleh-oleh wajib dari Yogyakarta."),
        ("Sate Klathak Pak Pong", PlaceCategory.kuliner, 25000, 45000, "17:00 - 23:00", "Sate kambing muda ditusuk jeruji besi, khas daerah Bantul."),
        ("Hutan Pinus Mangunan", PlaceCategory.sport, 5000, 10000, "06:00 - 18:00", "Jalur trekking dan sepeda hutan pinus dengan spot foto instagramable."),
    ],
    "Surabaya": [
        ("Kebun Binatang Surabaya", PlaceCategory.alam, 15000, 25000, "08:00 - 17:00", "Kebun binatang tertua dan terlengkap koleksi satwanya di Indonesia."),
        ("House of Sampoerna", PlaceCategory.fun, 0, 0, "09:00 - 22:00", "Museum sejarah rokok kretek dalam bangunan kolonial yang megah."),
        ("Taman Bungkul", PlaceCategory.fun, 0, 0, "24 jam", "Taman kota ramai dengan area kuliner dan spot olahraga malam."),
        ("Jembatan Suramadu", PlaceCategory.fun, 0, 15000, "24 jam", "Jembatan terpanjang di Indonesia yang menghubungkan Surabaya-Madura."),
        ("Pantai Kenjeran", PlaceCategory.alam, 15000, 15000, "07:00 - 21:00", "Pantai kota dengan kuil Tiongkok dan wahana permainan pantai."),
        ("Rawon Setan", PlaceCategory.kuliner, 25000, 45000, "18:00 - 02:00", "Rawon legendaris yang buka sampai dini hari."),
        ("Rujak Cingur Genteng", PlaceCategory.kuliner, 20000, 35000, "09:00 - 20:00", "Rujak cingur otentik khas Surabaya dengan bumbu petis."),
        ("Lontong Balap Pak Gendut", PlaceCategory.kuliner, 15000, 25000, "07:00 - 21:00", "Lontong balap legendaris sejak puluhan tahun lalu."),
        ("Sate Klopo Ondomohen", PlaceCategory.kuliner, 25000, 40000, "08:00 - 21:00", "Sate ayam/sapi dengan taburan kelapa sangrai yang khas."),
        ("GOR Kertajaya Jogging Track", PlaceCategory.sport, 0, 10000, "05:00 - 21:00", "Fasilitas olahraga umum favorit warga Surabaya."),
    ],
    "Bali": [
        ("Pantai Kuta", PlaceCategory.alam, 0, 0, "24 jam", "Pantai paling ikonik di Bali, favorit untuk sunset dan surfing."),
        ("Tanah Lot", PlaceCategory.alam, 60000, 60000, "07:00 - 19:00", "Pura di atas batu karang di tengah laut, ikon wisata Bali."),
        ("Ubud Monkey Forest", PlaceCategory.fun, 80000, 80000, "08:30 - 18:00", "Hutan suci dengan ratusan monyet ekor panjang dan pura kuno."),
        ("Tegallalang Rice Terrace", PlaceCategory.alam, 15000, 30000, "07:00 - 18:00", "Terasering sawah hijau ikonik dengan spot foto ayunan."),
        ("GWK Cultural Park", PlaceCategory.fun, 125000, 125000, "09:00 - 22:00", "Taman budaya dengan patung Garuda Wisnu Kencana raksasa."),
        ("Waterbom Bali", PlaceCategory.fun, 450000, 650000, "09:00 - 18:00", "Taman air terbesar dan terbaik di Asia menurut banyak penghargaan."),
        ("Bebek Bengil", PlaceCategory.kuliner, 80000, 150000, "10:00 - 22:00", "Restoran bebek goreng legendaris dengan suasana sawah di Ubud."),
        ("Warung Babi Guling Ibu Oka", PlaceCategory.kuliner, 40000, 70000, "11:00 - 21:00", "Babi guling paling terkenal di Ubud, sering antre panjang."),
        ("Kebun Kopi Luwak Ubud", PlaceCategory.kuliner, 0, 50000, "08:00 - 18:00", "Perkebunan kopi dengan pengalaman cicip berbagai kopi khas Bali."),
        ("Kursus Surfing Pantai Kuta", PlaceCategory.sport, 250000, 400000, "07:00 - 18:00", "Kelas surfing untuk pemula dengan instruktur lokal berpengalaman."),
    ],
}


def gmaps_search_url(name: str, city: str) -> str:
    query = quote(f"{name} {city}")
    return f"https://www.google.com/maps/search/?api=1&query={query}"


def get_or_create_seed_admin(db) -> User:
    user = db.query(User).filter(User.email == SEED_ADMIN_EMAIL).first()
    if user:
        return user

    # Kalau sudah ada user lain (misal akun kamu sendiri), pakai itu saja
    # supaya tidak bikin akun seed yang tidak perlu.
    existing = db.query(User).first()
    if existing:
        return existing

    user = User(
        name=SEED_ADMIN_NAME,
        email=SEED_ADMIN_EMAIL,
        # Password acak -- akun ini cuma dipakai sebagai "created_by",
        # tidak dimaksudkan untuk login manual.
        password_hash=hash_password("seed-admin-not-for-login-" + gmaps_search_url("x", "y")[:12]),
        is_admin=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def main():
    db = SessionLocal()
    try:
        admin = get_or_create_seed_admin(db)
        created, skipped = 0, 0

        for city, places in PLACES_BY_CITY.items():
            for name, category, price_min, price_max, opening_hours, notes in places:
                exists = (
                    db.query(Place)
                    .filter(Place.name == name, Place.city == city)
                    .first()
                )
                if exists:
                    skipped += 1
                    continue

                place = Place(
                    name=name,
                    category=category,
                    price_min=price_min,
                    price_max=price_max,
                    gmaps_url=gmaps_search_url(name, city),
                    city=city,
                    source_type=SourceType.manual,
                    photo_url=None,
                    opening_hours=opening_hours,
                    notes=notes,
                    status=PlaceStatus.published,
                    created_by=admin.id,
                )
                db.add(place)
                created += 1

        db.commit()
        print(f"Selesai. {created} tempat baru dibuat, {skipped} dilewati (sudah ada).")
    finally:
        db.close()


if __name__ == "__main__":
    main()