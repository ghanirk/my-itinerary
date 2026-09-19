import { useState, type FormEvent } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link, useNavigate } from "react-router-dom";
import { createTrip, listTrips } from "../api/trips";
import { ApiError } from "../api/client";
import Divider from "../components/Divider";
import type { TransportMode } from "../types/trip";

const transportModes: { value: TransportMode; label: string }[] = [
  { value: "kereta", label: "Kereta" },
  { value: "pesawat", label: "Pesawat" },
  { value: "travel", label: "Travel" },
  { value: "bis", label: "Bis" },
  { value: "mobil_pribadi", label: "Mobil Pribadi" },
];

const statusLabel: Record<string, string> = {
  draft: "Draft",
  confirmed: "Dikonfirmasi",
};

function formatMonthYear(iso: string): string {
  return new Date(iso).toLocaleDateString("id-ID", { month: "long", year: "numeric" });
}

function Trips() {
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const { data: trips, isLoading, isError } = useQuery({ queryKey: ["trips"], queryFn: listTrips });

  const [showForm, setShowForm] = useState(false);
  const [name, setName] = useState("");
  const [destinationCity, setDestinationCity] = useState("");
  const [durationDays, setDurationDays] = useState(3);
  const [departureMonthTarget, setDepartureMonthTarget] = useState("");
  const [transportMode, setTransportMode] = useState<TransportMode>("kereta");
  const [error, setError] = useState<string | null>(null);

  const createTripMutation = useMutation({
    mutationFn: createTrip,
    onSuccess: (trip) => {
      queryClient.invalidateQueries({ queryKey: ["trips"] });
      navigate(`/trips/${trip.id}`);
    },
    onError: (err) => {
      setError(err instanceof ApiError ? err.message : "Gagal membuat trip.");
    },
  });

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (!departureMonthTarget) {
      setError("Isi target bulan keberangkatan.");
      return;
    }
    setError(null);
    createTripMutation.mutate({
      name,
      destination_city: destinationCity,
      duration_days: durationDays,
      departure_month_target: new Date(departureMonthTarget).toISOString(),
      transport_mode: transportMode,
    });
  };

  return (
    <div className="bg-brand-50 min-h-screen">
      <section className="max-w-6xl mx-auto px-8 pt-16 pb-8 text-center">
        <p className="font-body text-xs tracking-[0.25em] uppercase text-brand-400 mb-2">
          Trip Planner Rombongan
        </p>
        <h1 className="font-heading text-4xl text-brand-700 mb-4">Trip Saya</h1>
        <p className="text-muted max-w-xl mx-auto">
          Atur trip keluar kota bersama rombongan — anggota dari kota berbeda,
          pilihan moda transportasi, hotel, aktivitas, sampai skema cicilan per orang.
        </p>
        <button
          onClick={() => setShowForm((v) => !v)}
          className="inline-block mt-6 text-sm font-medium text-brand-700 border border-brand-700/40 px-4 py-2 rounded-md hover:bg-brand-100 transition-colors"
        >
          {showForm ? "Batal" : "+ Buat Trip Baru"}
        </button>
      </section>

      <Divider />

      {showForm && (
        <section className="max-w-4xl mx-auto px-8 py-8">
          <div className="bg-white border border-brand-100 rounded-lg p-6">
            <h2 className="font-heading text-xl text-brand-700 mb-4">Setup Trip</h2>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-medium text-ink mb-1">Nama Trip</label>
                  <input
                    required
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="mis. Liburan Keluarga ke Jogja"
                    className="w-full border border-brand-100 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-400/40"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-ink mb-1">Kota Tujuan</label>
                  <input
                    required
                    value={destinationCity}
                    onChange={(e) => setDestinationCity(e.target.value)}
                    className="w-full border border-brand-100 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-400/40"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-ink mb-1">Durasi (hari)</label>
                  <input
                    type="number"
                    min={1}
                    required
                    value={durationDays}
                    onChange={(e) => setDurationDays(Number(e.target.value))}
                    className="w-full border border-brand-100 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-400/40"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-ink mb-1">Target Bulan Berangkat</label>
                  <input
                    type="date"
                    required
                    value={departureMonthTarget}
                    onChange={(e) => setDepartureMonthTarget(e.target.value)}
                    className="w-full border border-brand-100 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-400/40"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-medium text-ink mb-2">
                  Moda Transportasi Bersama
                </label>
                <div className="flex flex-wrap gap-2">
                  {transportModes.map((m) => (
                    <button
                      type="button"
                      key={m.value}
                      onClick={() => setTransportMode(m.value)}
                      className={`px-3 py-1.5 rounded-full text-sm border transition-colors ${
                        transportMode === m.value
                          ? "bg-brand-700 text-white border-brand-700"
                          : "border-brand-100 text-muted hover:bg-brand-50"
                      }`}
                    >
                      {m.label}
                    </button>
                  ))}
                </div>
                <p className="text-xs text-muted mt-2">
                  Moda ini berlaku untuk seluruh anggota — bukan dikunci sistem, sesuai kesepakatan rombongan.
                </p>
              </div>

              {error && <p className="text-sm text-red-600">{error}</p>}

              <button
                type="submit"
                disabled={createTripMutation.isPending}
                className="bg-brand-700 text-white px-5 py-2.5 rounded-md hover:bg-brand-800 transition-colors font-medium disabled:opacity-60"
              >
                {createTripMutation.isPending ? "Membuat..." : "Buat Trip"}
              </button>
            </form>
          </div>
        </section>
      )}

      <section className="max-w-6xl mx-auto px-8 pb-16">
        {isLoading && <p className="text-muted text-center py-12">Memuat trip...</p>}
        {isError && <p className="text-red-600 text-center py-12">Gagal memuat daftar trip.</p>}
        {trips && trips.length === 0 && (
          <p className="text-muted text-center py-12">
            Belum ada trip. Buat trip pertamamu di atas.
          </p>
        )}

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {trips?.map((trip) => (
            <Link
              key={trip.id}
              to={`/trips/${trip.id}`}
              className="block bg-white border border-brand-100 rounded-lg p-5 hover:shadow-md transition-shadow"
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-medium px-2 py-0.5 rounded-full bg-brand-100 text-brand-700">
                  {statusLabel[trip.status] ?? trip.status}
                </span>
                <span className="text-xs text-muted">
                  {transportModes.find((m) => m.value === trip.transport_mode)?.label}
                </span>
              </div>
              <h3 className="font-heading text-lg text-brand-700 mb-1">{trip.name}</h3>
              <p className="text-sm text-muted mb-1">Tujuan: {trip.destination_city}</p>
              <p className="text-sm text-muted">
                {trip.duration_days} hari · Target {formatMonthYear(trip.departure_month_target)}
              </p>
            </Link>
          ))}
        </div>
      </section>
    </div>
  );
}

export default Trips;
