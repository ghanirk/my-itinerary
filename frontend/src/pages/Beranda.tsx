import { Link } from "react-router-dom";
import Divider from "../components/Divider";
import HeroShowcase from "../components/HeroShowcase";

function Beranda() {
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
              Kumpulan tempat kuliner, wisata, dan aktivitas seru dari rekomendasi
              komunitas — lalu susun jadi rencana jalan-jalanmu sendiri, manual
              atau otomatis sesuai budget.
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

      {/* Ringkasan Layanan */}
      <section className="max-w-6xl mx-auto py-16 px-8">
        <p className="font-body text-xs tracking-[0.25em] uppercase text-brand-400 text-center mb-2">
          Yang Bisa Kamu Lakukan
        </p>
        <h2 className="font-heading text-3xl text-brand-700 text-center mb-12">
          Semua yang kamu butuhkan untuk merencanakan trip
        </h2>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
          {[
            {
              to: "/places",
              title: "Database Tempat Komunitas",
              desc: "Cari tempat berdasarkan kota, kategori, dan budget — hasil dari kontribusi sesama traveler.",
            },
            {
              to: "/places",
              title: "Auto-import dari Video",
              desc: "Tempel link TikTok/YouTube, AI otomatis ekstrak nama tempat, kategori, dan estimasi harga.",
            },
            {
              to: "/plans",
              title: "Plan Manual & Otomatis",
              desc: "Pilih sendiri tempatnya, atau biarkan sistem generate kombinasi sesuai kota & budget kamu.",
            },
          ].map((item) => (
            <Link
              key={item.title}
              to={item.to}
              className="block bg-white border border-brand-100 rounded-lg p-6 hover:shadow-md transition-shadow"
            >
              <h3 className="font-heading text-lg text-brand-700 mb-2">{item.title}</h3>
              <p className="text-sm text-muted leading-relaxed">{item.desc}</p>
            </Link>
          ))}
        </div>
      </section>
    </div>
  );
}

export default Beranda;
