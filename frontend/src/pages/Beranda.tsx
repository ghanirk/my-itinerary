import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import Divider from "../components/Divider";
import HeroShowcase from "../components/HeroShowcase";
import PlaceCard from "../components/PlaceCard";
import { listPlaces } from "../api/places";
import { useAuth } from "../context/useAuth";

const layanan = [
  {
    no: "01",
    to: "/places",
    title: "Database Tempat Komunitas",
    desc: "Cari tempat berdasarkan kota, kategori, dan budget — hasil dari kontribusi sesama traveler.",
  },
  {
    no: "02",
    to: "/places",
    title: "Auto-import dari Video",
    desc: "Tempel link TikTok/YouTube, AI otomatis ekstrak nama tempat, kategori, dan estimasi harga.",
  },
  {
    no: "03",
    to: "/plans",
    title: "Plan Manual & Otomatis",
    desc: "Pilih sendiri tempatnya, atau biarkan sistem generate kombinasi sesuai kota & budget kamu.",
  },
];

const caraKerja = [
  {
    step: "1",
    title: "Jelajahi & Cari Tempat",
    desc: "Telusuri database komunitas, filter berdasarkan kota, kategori (kuliner, fun, sport, alam), atau budget.",
  },
  {
    step: "2",
    title: "Susun Jadi Plan",
    desc: "Tambahkan tempat pilihanmu ke plan secara manual, atau biarkan sistem generate kombinasi otomatis sesuai kota & budget.",
  },
  {
    step: "3",
    title: "Berangkat Sesuai Rencana",
    desc: "Buka plan-mu kapan saja, lengkap dengan link Google Maps dan estimasi biaya tiap tempat.",
  },
];

const faq = [
  {
    q: "Apakah My Itineraries gratis digunakan?",
    a: "Ya, semua fitur — menjelajahi tempat, membuat plan manual, dan generate plan otomatis — bisa dipakai tanpa biaya.",
  },
  {
    q: "Dari mana data tempatnya berasal?",
    a: "Sebagian besar berasal dari kontribusi komunitas, termasuk hasil auto-import dari link TikTok/YouTube yang diproses AI.",
  },
  {
    q: "Apa bedanya plan manual dan otomatis?",
    a: "Plan manual berarti kamu memilih sendiri tempat mana saja yang masuk itinerary. Plan otomatis membiarkan sistem menyusun kombinasi tempat berdasarkan kota, jumlah tempat, dan budget yang kamu tentukan.",
  },
  {
    q: "Perlu akun untuk melihat tempat?",
    a: "Tidak, menjelajahi database tempat bisa dilakukan tanpa akun. Kamu baru perlu masuk atau daftar saat ingin menyimpan plan atau menambahkan tempat baru.",
  },
];

function Beranda() {
  const { isAuthenticated } = useAuth();

  const { data, isLoading, isError } = useQuery({
    queryKey: ["home-places-preview"],
    queryFn: () => listPlaces({ limit: 4 }),
  });

  const stats = [
    {
      value: isLoading ? "…" : isError ? "—" : String(data?.total ?? 0),
      label: "Tempat Terdaftar",
    },
    { value: "4", label: "Kategori Tempat" },
    { value: "2", label: "Cara Bikin Plan" },
    { value: "100%", label: "Gratis Dipakai" },
  ];

  return (
    <div className="bg-brand-50">
      {/* Hero Section */}
      <section className="max-w-6xl mx-auto px-8 pt-20 pb-16">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
          <div className="text-center lg:text-left">
            <p className="font-body text-xs tracking-[0.25em] uppercase text-brand-400 mb-4">
              Community Itinerary Planner
            </p>
            <h1 className="font-heading text-5xl sm:text-6xl font-semibold text-brand-700 leading-tight">
              Rencanakan Perjalanan,
              <br />
              <span className="italic font-medium">Bareng Komunitas</span>
            </h1>
            <p className="text-muted max-w-xl mx-auto lg:mx-0 mt-6 leading-relaxed">
              Kumpulan tempat kuliner, wisata, dan aktivitas seru dari
              rekomendasi komunitas — lalu susun jadi rencana jalan-jalanmu
              sendiri, manual atau otomatis sesuai budget.
            </p>

            <div className="flex flex-wrap justify-center lg:justify-start gap-4 mt-8">
              <Link
                to="/places"
                className="bg-brand-700 text-white px-6 py-3 rounded-md hover:bg-brand-800 transition-colors font-medium"
              >
                Jelajahi Tempat
              </Link>
              <Link
                to="/plans"
                className="border border-brand-700 text-brand-700 px-6 py-3 rounded-md hover:bg-brand-100 transition-colors font-medium"
              >
                Susun Plan Saya
              </Link>
            </div>
          </div>

          <HeroShowcase />
        </div>
      </section>

      <Divider />

      {/* Statistik Singkat */}
      <section className="max-w-6xl mx-auto px-8 py-12">
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-6">
          {stats.map((s) => (
            <div key={s.label} className="text-center">
              <p className="font-heading text-3xl sm:text-4xl text-brand-700">
                {s.value}
              </p>
              <p className="text-xs sm:text-sm text-muted mt-1">{s.label}</p>
            </div>
          ))}
        </div>
      </section>

      <Divider />

      {/* Ringkasan Layanan */}
      <section className="max-w-6xl mx-auto py-16 px-8">
        <p className="font-body text-xs tracking-[0.25em] uppercase text-brand-400 text-center mb-2">
          Yang Bisa Kamu Lakukan
        </p>
        <h2 className="font-heading text-3xl text-brand-700 text-center mb-12">
          Semua yang kamu butuhkan untuk merencanakan trip
        </h2>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
          {layanan.map((item) => (
            <Link
              key={item.title}
              to={item.to}
              className="block bg-white border border-brand-100 rounded-lg p-6 hover:shadow-md transition-shadow"
            >
              <span className="font-heading italic text-2xl text-brand-400/50">
                {item.no}
              </span>
              <h3 className="font-heading text-lg text-brand-700 mt-2 mb-2">
                {item.title}
              </h3>
              <p className="text-sm text-muted leading-relaxed">{item.desc}</p>
            </Link>
          ))}
        </div>
      </section>

      <Divider />

      {/* Cara Kerja */}
      <section className="max-w-6xl mx-auto py-16 px-8">
        <p className="font-body text-xs tracking-[0.25em] uppercase text-brand-400 text-center mb-2">
          Cara Kerja
        </p>
        <h2 className="font-heading text-3xl text-brand-700 text-center mb-12">
          Tiga langkah menuju rencana jalan-jalanmu
        </h2>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-10">
          {caraKerja.map((item) => (
            <div key={item.step} className="text-center sm:text-left">
              <div className="w-10 h-10 rounded-full bg-brand-700 text-white flex items-center justify-center font-heading mx-auto sm:mx-0">
                {item.step}
              </div>
              <h3 className="font-heading text-lg text-brand-700 mt-4 mb-2">
                {item.title}
              </h3>
              <p className="text-sm text-muted leading-relaxed">{item.desc}</p>
            </div>
          ))}
        </div>
      </section>

      <Divider />

      {/* Tempat Populer */}
      <section className="max-w-6xl mx-auto py-16 px-8">
        <p className="font-body text-xs tracking-[0.25em] uppercase text-brand-400 text-center mb-2">
          Baru Ditambahkan
        </p>
        <h2 className="font-heading text-3xl text-brand-700 text-center mb-12">
          Tempat dari komunitas
        </h2>

        {isLoading && (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {[0, 1, 2, 3].map((i) => (
              <div
                key={i}
                className="bg-white border border-brand-100 rounded-lg overflow-hidden animate-pulse"
              >
                <div className="aspect-video bg-brand-100" />
                <div className="p-4 space-y-2">
                  <div className="h-3 w-1/2 bg-brand-100 rounded" />
                  <div className="h-4 w-3/4 bg-brand-100 rounded" />
                  <div className="h-3 w-1/3 bg-brand-100 rounded" />
                </div>
              </div>
            ))}
          </div>
        )}

        {isError && (
          <p className="text-muted text-center py-8">
            Belum bisa memuat tempat terbaru saat ini. Coba refresh halaman ini
            sebentar lagi.
          </p>
        )}

        {!isLoading && !isError && data && data.items.length === 0 && (
          <p className="text-muted text-center py-8">
            Belum ada tempat yang ditambahkan komunitas. Jadilah yang pertama
            menambahkan!
          </p>
        )}

        {!isLoading && !isError && data && data.items.length > 0 && (
          <>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
              {data.items.map((place) => (
                <PlaceCard key={place.id} place={place} />
              ))}
            </div>
            <div className="text-center mt-10">
              <Link
                to="/places"
                className="inline-block text-sm font-medium text-brand-700 border border-brand-700/40 px-5 py-2.5 rounded-md hover:bg-brand-100 transition-colors"
              >
                Lihat Semua Tempat
              </Link>
            </div>
          </>
        )}
      </section>

      <Divider />

      {/* FAQ */}
      <section className="max-w-3xl mx-auto py-16 px-8">
        <p className="font-body text-xs tracking-[0.25em] uppercase text-brand-400 text-center mb-2">
          Sering Ditanyakan
        </p>
        <h2 className="font-heading text-3xl text-brand-700 text-center mb-12">
          Pertanyaan Umum
        </h2>

        <div className="space-y-3">
          {faq.map((item) => (
            <details
              key={item.q}
              className="group bg-white border border-brand-100 rounded-lg px-5 py-4 open:shadow-sm"
            >
              <summary className="font-heading text-brand-700 cursor-pointer list-none flex items-center justify-between gap-4">
                {item.q}
                <span className="text-brand-400 transition-transform group-open:rotate-45 shrink-0">
                  +
                </span>
              </summary>
              <p className="text-sm text-muted leading-relaxed mt-3">
                {item.a}
              </p>
            </details>
          ))}
        </div>
      </section>

      {/* CTA Akhir */}
      <section className="bg-brand-700">
        <div className="max-w-6xl mx-auto px-8 py-16 text-center">
          <h2 className="font-heading text-3xl text-white mb-4">
            Siap susun rencana jalan-jalan berikutnya?
          </h2>
          <p className="text-brand-100/80 max-w-xl mx-auto mb-8">
            Jelajahi tempat rekomendasi komunitas dan buat itinerary-mu sendiri,
            gratis tanpa ribet.
          </p>
          <div className="flex flex-wrap justify-center gap-4">
            <Link
              to="/places"
              className="bg-white text-brand-700 px-6 py-3 rounded-md hover:bg-brand-50 transition-colors font-medium"
            >
              Jelajahi Tempat
            </Link>
            {isAuthenticated ? (
              <Link
                to="/plans"
                className="border border-white text-white px-6 py-3 rounded-md hover:bg-brand-800 transition-colors font-medium"
              >
                Buka Plan Saya
              </Link>
            ) : (
              <Link
                to="/register"
                className="border border-white text-white px-6 py-3 rounded-md hover:bg-brand-800 transition-colors font-medium"
              >
                Daftar Gratis
              </Link>
            )}
          </div>
        </div>
      </section>
    </div>
  );
}

export default Beranda;
