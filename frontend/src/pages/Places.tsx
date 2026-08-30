import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { listPlaces } from "../api/places";
import { createPlan } from "../api/plans";
import PlaceCard from "../components/PlaceCard";
import Divider from "../components/Divider";
import { useAuth } from "../context/useAuth";
import type { Place, PlaceCategory, PlaceListParams } from "../types/place";

const categories: { value: PlaceCategory; label: string }[] = [
  { value: "kuliner", label: "Kuliner" },
  { value: "fun", label: "Fun" },
  { value: "sport", label: "Sport" },
  { value: "alam", label: "Alam" },
];

const PAGE_SIZE = 12;

function Places() {
  const { isAuthenticated } = useAuth();
  const [city, setCity] = useState("");
  const [category, setCategory] = useState<PlaceCategory | "">("");
  const [q, setQ] = useState("");
  const [page, setPage] = useState(0);
  const [addMessage, setAddMessage] = useState<string | null>(null);

  const params: PlaceListParams = {
    city: city || undefined,
    category: category || undefined,
    q: q || undefined,
    limit: PAGE_SIZE,
    offset: page * PAGE_SIZE,
  };

  const { data, isLoading, isError } = useQuery({
    queryKey: ["places", params],
    queryFn: () => listPlaces(params),
  });

  const totalPages = data ? Math.max(1, Math.ceil(data.total / PAGE_SIZE)) : 1;

  const handleAddToPlan = async (place: Place) => {
    if (!isAuthenticated) {
      setAddMessage("Masuk dulu untuk menambahkan tempat ke plan.");
      return;
    }
    try {
      await createPlan({ items: [{ place_id: place.id, order_index: 0 }] });
      setAddMessage(`"${place.name}" ditambahkan sebagai plan baru.`);
    } catch {
      setAddMessage("Gagal menambahkan ke plan, coba lagi.");
    }
    setTimeout(() => setAddMessage(null), 3000);
  };

  return (
    <div className="bg-brand-50 min-h-screen">
      <section className="max-w-6xl mx-auto px-8 pt-16 pb-8 text-center">
        <p className="font-body text-xs tracking-[0.25em] uppercase text-brand-400 mb-2">
          Database Komunitas
        </p>
        <h1 className="font-heading text-4xl text-brand-700 mb-4">Jelajahi Tempat</h1>
        <p className="text-muted max-w-xl mx-auto">
          Cari tempat kuliner, wisata, dan aktivitas seru berdasarkan kota, kategori, atau nama.
        </p>
        {isAuthenticated && (
          <Link
            to="/places/import"
            className="inline-block mt-6 text-sm font-medium text-brand-700 border border-brand-700/40 px-4 py-2 rounded-md hover:bg-brand-100 transition-colors"
          >
            + Import dari TikTok/YouTube
          </Link>
        )}
      </section>

      <Divider />

      <section className="max-w-6xl mx-auto px-8 py-8">
        {/* Filter */}
        <div className="flex flex-wrap gap-3 mb-8">
          <input
            type="text"
            placeholder="Cari nama tempat..."
            value={q}
            onChange={(e) => {
              setQ(e.target.value);
              setPage(0);
            }}
            className="flex-1 min-w-[180px] border border-brand-100 rounded-md px-3 py-2 text-sm bg-white focus:outline-none focus:ring-2 focus:ring-brand-400/40"
          />
          <input
            type="text"
            placeholder="Kota"
            value={city}
            onChange={(e) => {
              setCity(e.target.value);
              setPage(0);
            }}
            className="w-40 border border-brand-100 rounded-md px-3 py-2 text-sm bg-white focus:outline-none focus:ring-2 focus:ring-brand-400/40"
          />
          <select
            value={category}
            onChange={(e) => {
              setCategory(e.target.value as PlaceCategory | "");
              setPage(0);
            }}
            className="w-40 border border-brand-100 rounded-md px-3 py-2 text-sm bg-white focus:outline-none focus:ring-2 focus:ring-brand-400/40"
          >
            <option value="">Semua Kategori</option>
            {categories.map((c) => (
              <option key={c.value} value={c.value}>
                {c.label}
              </option>
            ))}
          </select>
        </div>

        {addMessage && (
          <div className="mb-6 text-sm bg-brand-100 text-brand-700 px-4 py-2 rounded-md">
            {addMessage}
          </div>
        )}

        {isLoading && <p className="text-muted text-center py-12">Memuat tempat...</p>}
        {isError && <p className="text-red-600 text-center py-12">Gagal memuat data tempat.</p>}

        {data && data.items.length === 0 && (
          <p className="text-muted text-center py-12">Belum ada tempat yang cocok dengan filter ini.</p>
        )}

        {data && data.items.length > 0 && (
          <>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
              {data.items.map((place) => (
                <PlaceCard key={place.id} place={place} onAdd={handleAddToPlan} />
              ))}
            </div>

            <div className="flex items-center justify-center gap-4 mt-10">
              <button
                onClick={() => setPage((p) => Math.max(0, p - 1))}
                disabled={page === 0}
                className="px-4 py-2 text-sm rounded-md border border-brand-100 disabled:opacity-40"
              >
                Sebelumnya
              </button>
              <span className="text-sm text-muted">
                Halaman {page + 1} dari {totalPages}
              </span>
              <button
                onClick={() => setPage((p) => (p + 1 < totalPages ? p + 1 : p))}
                disabled={page + 1 >= totalPages}
                className="px-4 py-2 text-sm rounded-md border border-brand-100 disabled:opacity-40"
              >
                Selanjutnya
              </button>
            </div>
          </>
        )}
      </section>
    </div>
  );
}

export default Places;
