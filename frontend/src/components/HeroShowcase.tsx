import { useState, useEffect } from "react";
import { Link } from "react-router-dom";

const features = [
  {
    label: "Jelajahi Tempat",
    eyebrow: "Fitur 01",
    desc: "Temukan tempat kuliner, wisata alam, sport & fun rekomendasi komunitas.",
    to: "/places",
    initial: "J",
  },
  {
    label: "Import dari TikTok/YouTube",
    eyebrow: "Fitur 02",
    desc: "Tempel link video, AI otomatis ekstrak jadi daftar tempat siap pakai.",
    to: "/places",
    initial: "I",
  },
  {
    label: "Plan Otomatis",
    eyebrow: "Fitur 03",
    desc: "Buat rencana jalan-jalan manual atau generate otomatis sesuai budget & kota.",
    to: "/plans",
    initial: "P",
  },
];

function HeroShowcase() {
  const [active, setActive] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setActive((prev) => (prev + 1) % features.length);
    }, 4000);
    return () => clearInterval(interval);
  }, []);

  const current = features[active];

  return (
    <div className="relative mx-auto w-full max-w-xs">
      {/* Kartu bertumpuk di belakang, kesan "kartu itinerary" */}
      <div className="absolute inset-0 rotate-3 bg-brand-100 rounded-sm border border-brand-400/30" />
      <div className="absolute inset-0 -rotate-2 bg-white rounded-sm border border-brand-400/30" />

      {/* Kartu utama */}
      <div className="relative bg-white border border-brand-400/50 rounded-sm p-8 aspect-[3/4] flex flex-col">
        <div className="border border-brand-400/30 flex-1 flex flex-col items-center justify-center text-center px-4">
          <span className="font-heading italic text-6xl text-brand-400/40 mb-4">
            {current.initial}
          </span>
          <p className="text-xs tracking-[0.2em] uppercase text-brand-400 mb-2">
            {current.eyebrow}
          </p>
          <h3 className="font-heading text-2xl text-brand-700 mb-3">
            {current.label}
          </h3>
          <p className="text-sm text-muted leading-relaxed mb-4">
            {current.desc}
          </p>
          <Link to={current.to} className="text-sm font-medium text-brand-700 underline underline-offset-4">
            Lihat selengkapnya
          </Link>
        </div>
      </div>

      {/* Indikator titik */}
      <div className="flex justify-center gap-1.5 mt-4">
        {features.map((f, i) => (
          <button
            key={f.label}
            onClick={() => setActive(i)}
            aria-label={`Tampilkan ${f.label}`}
            className={`h-1.5 rounded-full transition-all ${i === active ? "w-6 bg-brand-700" : "w-1.5 bg-brand-400/30"}`}
          />
        ))}
      </div>
    </div>
  );
}

export default HeroShowcase;
