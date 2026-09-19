import { useState, type FormEvent } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link, useParams } from "react-router-dom";
import { getTrip } from "../api/trips";
import {
  addTripMember,
  listTripMembers,
  removeTripMember,
  setMemberTransportPrice,
} from "../api/tripMembers";
import { createVehicleGroup, listVehicleGroups, updateVehicleGroupCost } from "../api/tripVehicles";
import { addTripHotel, listTripHotels, removeTripHotel } from "../api/tripHotels";
import { addTripActivity, listTripActivities, removeTripActivity } from "../api/tripActivities";
import { calculateTripBudget, getTripBudget } from "../api/tripBudget";
import {
  adjustInstallments,
  generateInstallments,
  listInstallments,
  payInstallment,
} from "../api/tripInstallments";
import { listPlaces } from "../api/places";
import { ApiError } from "../api/client";
import type { TripBudgetDetails } from "../types/budget";
import type { TripMember } from "../types/member";

const transportModeLabel: Record<string, string> = {
  kereta: "Kereta",
  mobil_pribadi: "Mobil Pribadi",
  pesawat: "Pesawat",
  travel: "Travel",
  bis: "Bis",
};

function formatRupiah(value: number): string {
  return new Intl.NumberFormat("id-ID", { style: "currency", currency: "IDR", maximumFractionDigits: 0 }).format(value);
}

function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString("id-ID", { day: "numeric", month: "long", year: "numeric" });
}

function formatMonthYear(iso: string): string {
  return new Date(iso).toLocaleDateString("id-ID", { month: "long", year: "numeric" });
}

type Tab = "anggota" | "hotel" | "aktivitas" | "budget" | "cicilan";

function TripDetail() {
  const { tripId } = useParams<{ tripId: string }>();
  const [tab, setTab] = useState<Tab>("anggota");

  const { data: trip, isLoading, isError } = useQuery({
    queryKey: ["trip", tripId],
    queryFn: () => getTrip(tripId!),
    enabled: !!tripId,
  });

  if (!tripId) return null;

  const isMobilPribadi = trip?.transport_mode === "mobil_pribadi";

  const tabs: { id: Tab; label: string }[] = [
    { id: "anggota", label: isMobilPribadi ? "Anggota & Kendaraan" : "Anggota & Transport" },
    { id: "hotel", label: "Hotel" },
    { id: "aktivitas", label: "Aktivitas" },
    { id: "budget", label: "Budget" },
    { id: "cicilan", label: "Cicilan" },
  ];

  return (
    <div className="bg-brand-50 min-h-screen">
      <section className="max-w-6xl mx-auto px-8 pt-10 pb-6">
        <Link to="/trips" className="text-sm text-brand-700 underline underline-offset-4">
          ← Semua Trip
        </Link>

        {isLoading && <p className="text-muted mt-6">Memuat trip...</p>}
        {isError && <p className="text-red-600 mt-6">Trip tidak ditemukan atau kamu tidak punya akses.</p>}

        {trip && (
          <div className="mt-4">
            <p className="font-body text-xs tracking-[0.25em] uppercase text-brand-400 mb-2">
              {trip.destination_city} &middot; {transportModeLabel[trip.transport_mode]}
            </p>
            <h1 className="font-heading text-3xl text-brand-700 mb-2">{trip.name}</h1>
            <p className="text-muted">
              {trip.duration_days} hari &middot; Target berangkat {formatMonthYear(trip.departure_month_target)}
            </p>
          </div>
        )}
      </section>

      {trip && (
        <>
          <section className="max-w-6xl mx-auto px-8">
            <div className="flex flex-wrap gap-1 border-b border-brand-100">
              {tabs.map((t) => (
                <button
                  key={t.id}
                  onClick={() => setTab(t.id)}
                  className={`px-4 py-2.5 text-sm font-medium border-b-2 -mb-px transition-colors ${
                    tab === t.id
                      ? "border-brand-700 text-brand-700"
                      : "border-transparent text-muted hover:text-brand-700"
                  }`}
                >
                  {t.label}
                </button>
              ))}
            </div>
          </section>

          <section className="max-w-6xl mx-auto px-8 py-8">
            {tab === "anggota" && <MembersTab tripId={tripId} isMobilPribadi={isMobilPribadi} />}
            {tab === "hotel" && <HotelsTab tripId={tripId} />}
            {tab === "aktivitas" && <ActivitiesTab tripId={tripId} />}
            {tab === "budget" && <BudgetTab tripId={tripId} />}
            {tab === "cicilan" && <InstallmentsTab tripId={tripId} />}
          </section>
        </>
      )}
    </div>
  );
}

// ============================== ANGGOTA & TRANSPORT ==============================

function MembersTab({ tripId, isMobilPribadi }: { tripId: string; isMobilPribadi: boolean }) {
  const queryClient = useQueryClient();
  const { data: members } = useQuery({
    queryKey: ["trip-members", tripId],
    queryFn: () => listTripMembers(tripId),
  });

  const [name, setName] = useState("");
  const [originCity, setOriginCity] = useState("");
  const [error, setError] = useState<string | null>(null);

  const addMemberMutation = useMutation({
    mutationFn: () => addTripMember(tripId, { name, origin_city: originCity, role: "member" }),
    onSuccess: () => {
      setName("");
      setOriginCity("");
      setError(null);
      queryClient.invalidateQueries({ queryKey: ["trip-members", tripId] });
    },
    onError: (err) => setError(err instanceof ApiError ? err.message : "Gagal menambah anggota."),
  });

  const removeMemberMutation = useMutation({
    mutationFn: (memberId: string) => removeTripMember(tripId, memberId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["trip-members", tripId] }),
  });

  const [transportInputs, setTransportInputs] = useState<Record<string, string>>({});
  const transportMutation = useMutation({
    mutationFn: ({ memberId, price }: { memberId: string; price: number }) =>
      setMemberTransportPrice(tripId, memberId, { price }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["trip-members", tripId] }),
  });

  const handleAddMember = (e: FormEvent) => {
    e.preventDefault();
    if (!name || !originCity) {
      setError("Isi nama dan kota asal.");
      return;
    }
    addMemberMutation.mutate();
  };

  return (
    <div className="space-y-6">
      <div className="bg-white border border-brand-100 rounded-lg p-6">
        <h2 className="font-heading text-xl text-brand-700 mb-4">Tambah Anggota</h2>
        <form onSubmit={handleAddMember} className="flex flex-col sm:flex-row gap-3">
          <input
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Nama anggota"
            className="flex-1 border border-brand-100 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-400/40"
          />
          <input
            value={originCity}
            onChange={(e) => setOriginCity(e.target.value)}
            placeholder="Kota asal"
            className="flex-1 border border-brand-100 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-400/40"
          />
          <button
            type="submit"
            disabled={addMemberMutation.isPending}
            className="bg-brand-700 text-white px-5 py-2.5 rounded-md hover:bg-brand-800 transition-colors font-medium disabled:opacity-60 shrink-0"
          >
            {addMemberMutation.isPending ? "Menambah..." : "Tambah"}
          </button>
        </form>
        {error && <p className="text-sm text-red-600 mt-3">{error}</p>}
        <p className="text-xs text-muted mt-2">
          Anggota tanpa akun (keluarga/teman) tetap bisa ditambahkan cukup dengan nama.
        </p>
      </div>

      <div className="bg-white border border-brand-100 rounded-lg overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-brand-50 text-left text-xs uppercase tracking-wide text-muted">
            <tr>
              <th className="px-4 py-3">Nama</th>
              <th className="px-4 py-3">Kota Asal</th>
              <th className="px-4 py-3">Peran</th>
              {!isMobilPribadi && <th className="px-4 py-3">Biaya Transport PP</th>}
              <th className="px-4 py-3"></th>
            </tr>
          </thead>
          <tbody>
            {members?.map((member) => (
              <tr key={member.id} className="border-t border-brand-50">
                <td className="px-4 py-3">{member.name}</td>
                <td className="px-4 py-3">{member.origin_city}</td>
                <td className="px-4 py-3">
                  <span className="text-xs px-2 py-0.5 rounded-full bg-brand-100 text-brand-700">
                    {member.role === "admin" ? "Admin" : "Anggota"}
                  </span>
                </td>
                {!isMobilPribadi && (
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2">
                      <input
                        type="number"
                        min={0}
                        placeholder="Rp"
                        value={transportInputs[member.id] ?? ""}
                        onChange={(e) => setTransportInputs({ ...transportInputs, [member.id]: e.target.value })}
                        className="w-28 border border-brand-100 rounded-md px-2 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-brand-400/40"
                      />
                      <button
                        onClick={() =>
                          transportMutation.mutate({
                            memberId: member.id,
                            price: Number(transportInputs[member.id]) || 0,
                          })
                        }
                        className="text-xs text-brand-700 underline underline-offset-4"
                      >
                        Simpan
                      </button>
                    </div>
                  </td>
                )}
                <td className="px-4 py-3 text-right">
                  <button
                    onClick={() => removeMemberMutation.mutate(member.id)}
                    className="text-xs text-red-600 hover:underline"
                  >
                    Hapus
                  </button>
                </td>
              </tr>
            ))}
            {members && members.length === 0 && (
              <tr>
                <td colSpan={5} className="px-4 py-8 text-center text-muted">
                  Belum ada anggota. Tambahkan di atas.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {!isMobilPribadi && (
        <p className="text-xs text-muted">
          Kosongkan biaya transport untuk memakai referensi harga otomatis (kalau tersedia) saat kalkulasi budget dilakukan.
        </p>
      )}

      {isMobilPribadi && members && <VehicleGroupsSection tripId={tripId} members={members} />}
    </div>
  );
}

function VehicleGroupsSection({ tripId, members }: { tripId: string; members: TripMember[] }) {
  const queryClient = useQueryClient();
  const { data: groups } = useQuery({
    queryKey: ["vehicle-groups", tripId],
    queryFn: () => listVehicleGroups(tripId),
  });

  const [label, setLabel] = useState("");
  const [selectedMemberIds, setSelectedMemberIds] = useState<string[]>([]);
  const [error, setError] = useState<string | null>(null);

  const createGroupMutation = useMutation({
    mutationFn: () => createVehicleGroup(tripId, { vehicle_label: label, member_ids: selectedMemberIds }),
    onSuccess: () => {
      setLabel("");
      setSelectedMemberIds([]);
      setError(null);
      queryClient.invalidateQueries({ queryKey: ["vehicle-groups", tripId] });
    },
    onError: (err) => setError(err instanceof ApiError ? err.message : "Gagal membuat kelompok kendaraan."),
  });

  const [costInputs, setCostInputs] = useState<Record<string, string>>({});
  const updateCostMutation = useMutation({
    mutationFn: ({ groupId, cost }: { groupId: string; cost: number }) =>
      updateVehicleGroupCost(tripId, groupId, { total_cost: cost }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["vehicle-groups", tripId] }),
  });

  const toggleMember = (id: string) => {
    setSelectedMemberIds((prev) => (prev.includes(id) ? prev.filter((m) => m !== id) : [...prev, id]));
  };

  const handleCreateGroup = (e: FormEvent) => {
    e.preventDefault();
    if (!label || selectedMemberIds.length === 0) {
      setError("Isi label kendaraan dan pilih minimal satu anggota.");
      return;
    }
    createGroupMutation.mutate();
  };

  return (
    <div className="bg-white border border-brand-100 rounded-lg p-6">
      <h2 className="font-heading text-xl text-brand-700 mb-1">Kelompok Kendaraan</h2>
      <p className="text-sm text-muted mb-4">
        Khusus mobil pribadi — tentukan siapa nebeng di mobil siapa. Biaya dibagi per kendaraan, bukan langsung per orang.
      </p>

      <form onSubmit={handleCreateGroup} className="mb-6 space-y-3">
        <input
          value={label}
          onChange={(e) => setLabel(e.target.value)}
          placeholder="Label kendaraan, mis. Mobil 1 (Avanza)"
          className="w-full border border-brand-100 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-400/40"
        />
        <div className="flex flex-wrap gap-2">
          {members.map((m) => (
            <button
              type="button"
              key={m.id}
              onClick={() => toggleMember(m.id)}
              className={`px-3 py-1.5 rounded-full text-sm border transition-colors ${
                selectedMemberIds.includes(m.id)
                  ? "bg-brand-700 text-white border-brand-700"
                  : "border-brand-100 text-muted hover:bg-brand-50"
              }`}
            >
              {m.name}
            </button>
          ))}
        </div>
        {error && <p className="text-sm text-red-600">{error}</p>}
        <button
          type="submit"
          disabled={createGroupMutation.isPending}
          className="bg-brand-700 text-white px-5 py-2.5 rounded-md hover:bg-brand-800 transition-colors font-medium disabled:opacity-60"
        >
          {createGroupMutation.isPending ? "Menyimpan..." : "Buat Kelompok"}
        </button>
      </form>

      <div className="space-y-3">
        {groups?.map((group) => (
          <div
            key={group.id}
            className="border border-brand-100 rounded-md p-4 flex flex-col sm:flex-row sm:items-center gap-3 justify-between"
          >
            <div>
              <p className="font-medium text-ink">{group.vehicle_label}</p>
              <p className="text-xs text-muted">
                {group.member_ids.length} penumpang
                {group.total_cost != null ? ` · ${formatRupiah(group.total_cost)}` : ""}
              </p>
            </div>
            <div className="flex items-center gap-2">
              <input
                type="number"
                min={0}
                placeholder="Total biaya (Rp)"
                value={costInputs[group.id] ?? ""}
                onChange={(e) => setCostInputs({ ...costInputs, [group.id]: e.target.value })}
                className="w-36 border border-brand-100 rounded-md px-2 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-brand-400/40"
              />
              <button
                onClick={() => updateCostMutation.mutate({ groupId: group.id, cost: Number(costInputs[group.id]) || 0 })}
                className="text-xs text-brand-700 underline underline-offset-4"
              >
                Simpan Biaya
              </button>
            </div>
          </div>
        ))}
        {groups && groups.length === 0 && <p className="text-sm text-muted">Belum ada kelompok kendaraan.</p>}
      </div>
    </div>
  );
}

// ============================== HOTEL ==============================

function HotelsTab({ tripId }: { tripId: string }) {
  const queryClient = useQueryClient();
  const { data: hotels } = useQuery({
    queryKey: ["trip-hotels", tripId],
    queryFn: () => listTripHotels(tripId),
  });

  const [cityFilter, setCityFilter] = useState("");
  const { data: placesResult } = useQuery({
    queryKey: ["hotel-places", cityFilter],
    queryFn: () => listPlaces({ city: cityFilter || undefined, limit: 12 }),
  });

  const [placeId, setPlaceId] = useState("");
  const [nights, setNights] = useState(1);
  const [pricePerNight, setPricePerNight] = useState(0);
  const [capacity, setCapacity] = useState(2);
  const [error, setError] = useState<string | null>(null);

  const addHotelMutation = useMutation({
    mutationFn: () =>
      addTripHotel(tripId, { place_id: placeId, nights, price_per_night: pricePerNight, capacity_per_room: capacity }),
    onSuccess: () => {
      setPlaceId("");
      setPricePerNight(0);
      setError(null);
      queryClient.invalidateQueries({ queryKey: ["trip-hotels", tripId] });
    },
    onError: (err) => setError(err instanceof ApiError ? err.message : "Gagal menambah hotel."),
  });

  const removeHotelMutation = useMutation({
    mutationFn: (hotelId: string) => removeTripHotel(tripId, hotelId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["trip-hotels", tripId] }),
  });

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (!placeId) {
      setError("Pilih hotel dari daftar tempat, atau tambahkan dulu lewat halaman Jelajahi Tempat.");
      return;
    }
    addHotelMutation.mutate();
  };

  return (
    <div className="space-y-6">
      <div className="bg-white border border-brand-100 rounded-lg p-6">
        <h2 className="font-heading text-xl text-brand-700 mb-1">Tambah Hotel</h2>
        <p className="text-sm text-muted mb-4">
          Pilih dari database tempat yang sudah ada. Belum ada di database? Tambahkan dulu lewat halaman{" "}
          <Link to="/places" className="text-brand-700 underline underline-offset-4">
            Jelajahi Tempat
          </Link>
          .
        </p>

        <input
          value={cityFilter}
          onChange={(e) => setCityFilter(e.target.value)}
          placeholder="Cari kota tujuan..."
          className="w-full border border-brand-100 rounded-md px-3 py-2 text-sm mb-3 focus:outline-none focus:ring-2 focus:ring-brand-400/40"
        />

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 mb-4 max-h-64 overflow-y-auto pr-1">
          {placesResult?.items.map((place) => (
            <button
              type="button"
              key={place.id}
              onClick={() => setPlaceId(place.id)}
              className={`text-left border rounded-md p-3 text-sm transition-colors ${
                placeId === place.id ? "border-brand-700 ring-2 ring-brand-400/40" : "border-brand-100 hover:bg-brand-50"
              }`}
            >
              <p className="font-medium text-ink">{place.name}</p>
              <p className="text-xs text-muted">{place.city}</p>
            </button>
          ))}
        </div>

        <form onSubmit={handleSubmit} className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          <div>
            <label className="block text-xs font-medium text-ink mb-1">Jumlah Malam</label>
            <input
              type="number"
              min={1}
              value={nights}
              onChange={(e) => setNights(Number(e.target.value))}
              className="w-full border border-brand-100 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-400/40"
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-ink mb-1">Harga per Malam</label>
            <input
              type="number"
              min={0}
              value={pricePerNight}
              onChange={(e) => setPricePerNight(Number(e.target.value))}
              className="w-full border border-brand-100 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-400/40"
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-ink mb-1">Kapasitas per Kamar</label>
            <input
              type="number"
              min={1}
              value={capacity}
              onChange={(e) => setCapacity(Number(e.target.value))}
              className="w-full border border-brand-100 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-400/40"
            />
          </div>
          {error && <p className="sm:col-span-3 text-sm text-red-600">{error}</p>}
          <div className="sm:col-span-3">
            <button
              type="submit"
              disabled={addHotelMutation.isPending}
              className="bg-brand-700 text-white px-5 py-2.5 rounded-md hover:bg-brand-800 transition-colors font-medium disabled:opacity-60"
            >
              {addHotelMutation.isPending ? "Menambah..." : "Tambah Hotel"}
            </button>
          </div>
        </form>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {hotels?.map((hotel) => (
          <div key={hotel.id} className="bg-white border border-brand-100 rounded-lg p-4 flex items-start justify-between gap-3">
            <div>
              <p className="font-heading text-lg text-brand-700">{hotel.place.name}</p>
              <p className="text-sm text-muted">
                {hotel.nights} malam &middot; {formatRupiah(hotel.price_per_night)}/malam &middot; {hotel.capacity_per_room} orang/kamar
              </p>
            </div>
            <button
              onClick={() => removeHotelMutation.mutate(hotel.id)}
              className="text-xs text-red-600 hover:underline shrink-0"
            >
              Hapus
            </button>
          </div>
        ))}
        {hotels && hotels.length === 0 && <p className="text-sm text-muted">Belum ada hotel dipilih.</p>}
      </div>
    </div>
  );
}

// ============================== AKTIVITAS ==============================

function ActivitiesTab({ tripId }: { tripId: string }) {
  const queryClient = useQueryClient();
  const { data: activities } = useQuery({
    queryKey: ["trip-activities", tripId],
    queryFn: () => listTripActivities(tripId),
  });

  const [cityFilter, setCityFilter] = useState("");
  const { data: placesResult } = useQuery({
    queryKey: ["activity-places", cityFilter],
    queryFn: () => listPlaces({ city: cityFilter || undefined, limit: 12 }),
  });

  const [placeId, setPlaceId] = useState("");
  const [dayIndex, setDayIndex] = useState(1);
  const [error, setError] = useState<string | null>(null);

  const addActivityMutation = useMutation({
    mutationFn: () => addTripActivity(tripId, { place_id: placeId, day_index: dayIndex }),
    onSuccess: () => {
      setPlaceId("");
      setError(null);
      queryClient.invalidateQueries({ queryKey: ["trip-activities", tripId] });
    },
    onError: (err) => setError(err instanceof ApiError ? err.message : "Gagal menambah aktivitas."),
  });

  const removeActivityMutation = useMutation({
    mutationFn: (activityId: string) => removeTripActivity(tripId, activityId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["trip-activities", tripId] }),
  });

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (!placeId) {
      setError("Pilih tempat aktivitas dari daftar.");
      return;
    }
    addActivityMutation.mutate();
  };

  const groupedByDay = (activities ?? []).reduce<Record<number, typeof activities>>((acc, activity) => {
    const arr = acc[activity.day_index] ?? [];
    arr.push(activity);
    acc[activity.day_index] = arr;
    return acc;
  }, {});

  return (
    <div className="space-y-6">
      <div className="bg-white border border-brand-100 rounded-lg p-6">
        <h2 className="font-heading text-xl text-brand-700 mb-1">Tambah Aktivitas</h2>
        <p className="text-sm text-muted mb-4">Pilih tempat wisata untuk dijadwalkan di hari tertentu.</p>

        <input
          value={cityFilter}
          onChange={(e) => setCityFilter(e.target.value)}
          placeholder="Cari kota tujuan..."
          className="w-full border border-brand-100 rounded-md px-3 py-2 text-sm mb-3 focus:outline-none focus:ring-2 focus:ring-brand-400/40"
        />

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 mb-4 max-h-64 overflow-y-auto pr-1">
          {placesResult?.items.map((place) => (
            <button
              type="button"
              key={place.id}
              onClick={() => setPlaceId(place.id)}
              className={`text-left border rounded-md p-3 text-sm transition-colors ${
                placeId === place.id ? "border-brand-700 ring-2 ring-brand-400/40" : "border-brand-100 hover:bg-brand-50"
              }`}
            >
              <p className="font-medium text-ink">{place.name}</p>
              <p className="text-xs text-muted">{place.city}</p>
            </button>
          ))}
        </div>

        <form onSubmit={handleSubmit} className="flex flex-col sm:flex-row gap-3 items-start sm:items-end">
          <div className="flex-1">
            <label className="block text-xs font-medium text-ink mb-1">Hari ke-</label>
            <input
              type="number"
              min={1}
              value={dayIndex}
              onChange={(e) => setDayIndex(Number(e.target.value))}
              className="w-full border border-brand-100 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-400/40"
            />
          </div>
          <button
            type="submit"
            disabled={addActivityMutation.isPending}
            className="bg-brand-700 text-white px-5 py-2.5 rounded-md hover:bg-brand-800 transition-colors font-medium disabled:opacity-60"
          >
            {addActivityMutation.isPending ? "Menambah..." : "Tambah ke Jadwal"}
          </button>
        </form>
        {error && <p className="text-sm text-red-600 mt-3">{error}</p>}
      </div>

      <div className="space-y-6">
        {Object.keys(groupedByDay)
          .sort((a, b) => Number(a) - Number(b))
          .map((day) => (
            <div key={day}>
              <h3 className="font-heading text-lg text-brand-700 mb-3">Hari ke-{day}</h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {groupedByDay[Number(day)]?.map((activity) => (
                  <div key={activity.id} className="bg-white border border-brand-100 rounded-lg p-4 flex items-start justify-between gap-3">
                    <div>
                      <p className="font-medium text-ink">{activity.place.name}</p>
                      <p className="text-xs text-muted">{activity.place.city}</p>
                    </div>
                    <button
                      onClick={() => removeActivityMutation.mutate(activity.id)}
                      className="text-xs text-red-600 hover:underline shrink-0"
                    >
                      Hapus
                    </button>
                  </div>
                ))}
              </div>
            </div>
          ))}
        {activities && activities.length === 0 && <p className="text-sm text-muted">Belum ada aktivitas dijadwalkan.</p>}
      </div>
    </div>
  );
}

// ============================== BUDGET ==============================

const budgetLabel: Record<keyof TripBudgetDetails, string> = {
  transport: "Transport PP",
  hotel: "Hotel",
  activities: "Tiket Aktivitas",
  makan: "Makan",
  lokal: "Transport Lokal (Grab)",
  num_members: "Jumlah Anggota",
  duration_days: "Durasi (hari)",
};

function BudgetTab({ tripId }: { tripId: string }) {
  const queryClient = useQueryClient();
  const { data: summary, isLoading } = useQuery({
    queryKey: ["trip-budget", tripId],
    queryFn: () => getTripBudget(tripId),
    retry: false,
  });

  const calculateMutation = useMutation({
    mutationFn: () => calculateTripBudget(tripId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["trip-budget", tripId] }),
  });

  let details: TripBudgetDetails | null = null;
  if (summary?.details) {
    try {
      details = JSON.parse(summary.details) as TripBudgetDetails;
    } catch {
      details = null;
    }
  }

  return (
    <div className="bg-white border border-brand-100 rounded-lg p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="font-heading text-xl text-brand-700">Kalkulasi Budget</h2>
        <button
          onClick={() => calculateMutation.mutate()}
          disabled={calculateMutation.isPending}
          className="bg-brand-700 text-white px-4 py-2 rounded-md hover:bg-brand-800 transition-colors font-medium disabled:opacity-60"
        >
          {calculateMutation.isPending ? "Menghitung..." : summary ? "Hitung Ulang" : "Hitung Budget"}
        </button>
      </div>

      {calculateMutation.isError && (
        <p className="text-sm text-red-600 mb-4">
          {calculateMutation.error instanceof ApiError
            ? calculateMutation.error.message
            : "Gagal menghitung budget. Pastikan trip sudah punya anggota."}
        </p>
      )}

      {!summary && !isLoading && !calculateMutation.isPending && (
        <p className="text-sm text-muted">
          Belum ada perhitungan budget. Pastikan anggota, hotel, dan aktivitas sudah diisi, lalu klik "Hitung Budget".
        </p>
      )}

      {summary && (
        <div className="space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="bg-brand-50 rounded-md p-4">
              <p className="text-xs text-muted uppercase tracking-wide mb-1">Total Biaya Trip</p>
              <p className="font-heading text-2xl text-brand-700">{formatRupiah(summary.total_cost)}</p>
            </div>
            <div className="bg-brand-700 text-white rounded-md p-4">
              <p className="text-xs text-white/70 uppercase tracking-wide mb-1">Biaya per Orang</p>
              <p className="font-heading text-2xl">{formatRupiah(summary.cost_per_member)}</p>
            </div>
          </div>

          {details && (
            <div>
              <p className="text-sm font-medium text-ink mb-2">Rincian</p>
              <ul className="divide-y divide-brand-50 border border-brand-100 rounded-md overflow-hidden">
                {(["transport", "hotel", "activities", "makan", "lokal"] as const).map((key) => (
                  <li key={key} className="flex items-center justify-between px-4 py-2.5 text-sm">
                    <span className="text-muted">{budgetLabel[key]}</span>
                    <span className="font-medium text-ink">{formatRupiah(Number(details![key]) || 0)}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          <p className="text-xs text-muted">Terakhir dihitung {formatDate(summary.calculated_at)}</p>
        </div>
      )}
    </div>
  );
}

// ============================== CICILAN ==============================

function InstallmentsTab({ tripId }: { tripId: string }) {
  const queryClient = useQueryClient();
  const { data: installments } = useQuery({
    queryKey: ["trip-installments", tripId],
    queryFn: () => listInstallments(tripId),
  });
  const { data: members } = useQuery({
    queryKey: ["trip-members", tripId],
    queryFn: () => listTripMembers(tripId),
  });

  const generateMutation = useMutation({
    mutationFn: () => generateInstallments(tripId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["trip-installments", tripId] }),
  });

  const [newMonths, setNewMonths] = useState("");
  const adjustMutation = useMutation({
    mutationFn: () => adjustInstallments(tripId, { new_months: Number(newMonths) || 1 }),
    onSuccess: () => {
      setNewMonths("");
      queryClient.invalidateQueries({ queryKey: ["trip-installments", tripId] });
    },
  });

  const [payInputs, setPayInputs] = useState<Record<string, string>>({});
  const payMutation = useMutation({
    mutationFn: ({ installmentId, amount }: { installmentId: string; amount: number }) =>
      payInstallment(tripId, installmentId, { amount_paid: amount }),
    onSuccess: (_data, variables) => {
      setPayInputs((prev) => ({ ...prev, [variables.installmentId]: "" }));
      queryClient.invalidateQueries({ queryKey: ["trip-installments", tripId] });
    },
  });

  const memberNameById = new Map((members ?? []).map((m) => [m.id, m.name]));

  const groupedByMember = (installments ?? []).reduce<Record<string, typeof installments>>((acc, inst) => {
    const arr = acc[inst.member_id] ?? [];
    arr.push(inst);
    acc[inst.member_id] = arr;
    return acc;
  }, {});

  return (
    <div className="space-y-6">
      <div className="bg-white border border-brand-100 rounded-lg p-6">
        <h2 className="font-heading text-xl text-brand-700 mb-1">Skema Cicilan</h2>
        <p className="text-sm text-muted mb-4">
          Cicilan dihitung dari biaya per orang dibagi jumlah bulan menuju keberangkatan. Hitung budget dulu di tab Budget sebelum generate cicilan.
        </p>

        {generateMutation.isError && (
          <p className="text-sm text-red-600 mb-4">
            {generateMutation.error instanceof ApiError ? generateMutation.error.message : "Gagal generate cicilan."}
          </p>
        )}

        <div className="flex flex-wrap items-center gap-3">
          <button
            onClick={() => generateMutation.mutate()}
            disabled={generateMutation.isPending}
            className="bg-brand-700 text-white px-5 py-2.5 rounded-md hover:bg-brand-800 transition-colors font-medium disabled:opacity-60"
          >
            {generateMutation.isPending ? "Membuat..." : "Generate Cicilan (dari target bulan)"}
          </button>

          <span className="text-sm text-muted">atau</span>

          <input
            type="number"
            min={1}
            placeholder="Jumlah bulan baru"
            value={newMonths}
            onChange={(e) => setNewMonths(e.target.value)}
            className="w-40 border border-brand-100 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-400/40"
          />
          <button
            onClick={() => adjustMutation.mutate()}
            disabled={adjustMutation.isPending || !newMonths}
            className="border border-brand-700/40 text-brand-700 px-4 py-2.5 rounded-md hover:bg-brand-100 transition-colors font-medium disabled:opacity-60"
          >
            Ubah Jangka Waktu
          </button>
        </div>
      </div>

      <div className="space-y-6">
        {Object.entries(groupedByMember).map(([memberId, memberInstallments]) => {
          const totalDue = memberInstallments?.reduce((s, i) => s + i.amount_due, 0) ?? 0;
          const totalPaid = memberInstallments?.reduce((s, i) => s + i.amount_paid, 0) ?? 0;
          return (
            <div key={memberId} className="bg-white border border-brand-100 rounded-lg overflow-hidden">
              <div className="flex items-center justify-between px-6 py-4 border-b border-brand-100 bg-brand-50">
                <p className="font-medium text-ink">{memberNameById.get(memberId) ?? "Anggota"}</p>
                <p className="text-xs text-muted">
                  Terbayar {formatRupiah(totalPaid)} / {formatRupiah(totalDue)}
                </p>
              </div>
              <ul className="divide-y divide-brand-50">
                {memberInstallments
                  ?.slice()
                  .sort((a, b) => a.month_index - b.month_index)
                  .map((inst) => {
                    const isPaid = inst.amount_paid >= inst.amount_due;
                    const remaining = inst.amount_due - inst.amount_paid;
                    return (
                      <li key={inst.id} className="flex items-center justify-between px-6 py-3 text-sm">
                        <div>
                          <p className="text-ink">Bulan ke-{inst.month_index}</p>
                          <p className="text-xs text-muted">
                            {formatRupiah(inst.amount_paid)} / {formatRupiah(inst.amount_due)}
                            {isPaid && inst.paid_at ? ` · Lunas ${formatDate(inst.paid_at)}` : ""}
                          </p>
                        </div>
                        {isPaid ? (
                          <span className="text-xs font-medium text-emerald-700 bg-emerald-50 px-2 py-1 rounded-full">Lunas</span>
                        ) : (
                          <div className="flex items-center gap-2">
                            <input
                              type="number"
                              min={0}
                              max={remaining}
                              placeholder={`Maks ${formatRupiah(remaining)}`}
                              value={payInputs[inst.id] ?? ""}
                              onChange={(e) => setPayInputs({ ...payInputs, [inst.id]: e.target.value })}
                              className="w-36 border border-brand-100 rounded-md px-2 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-brand-400/40"
                            />
                            <button
                              onClick={() =>
                                payMutation.mutate({ installmentId: inst.id, amount: Number(payInputs[inst.id]) || 0 })
                              }
                              className="text-xs text-brand-700 underline underline-offset-4"
                            >
                              Catat Bayar
                            </button>
                          </div>
                        )}
                      </li>
                    );
                  })}
              </ul>
            </div>
          );
        })}
        {installments && installments.length === 0 && <p className="text-sm text-muted">Belum ada cicilan. Generate dulu di atas.</p>}
      </div>
    </div>
  );
}

export default TripDetail;
