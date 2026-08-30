import { useState, type FormEvent } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { deletePlan, generatePlan, listMyPlans } from "../api/plans";
import Divider from "../components/Divider";
import { ApiError } from "../api/client";
import type { PlaceCategory } from "../types/place";

const categories: { value: PlaceCategory; label: string }[] = [
  { value: "kuliner", label: "Kuliner" },
  { value: "fun", label: "Fun" },
  { value: "sport", label: "Sport" },
  { value: "alam", label: "Alam" },
];

function formatRupiah(value: number): string {
  return new Intl.NumberFormat("id-ID", { style: "currency", currency: "IDR", maximumFractionDigits: 0 }).format(value);
}

function MyPlans() {
  const queryClient = useQueryClient();
  const { data: plans, isLoading } = useQuery({ queryKey: ["plans"], queryFn: listMyPlans });

  const [city, setCity] = useState("");
  const [budget, setBudget] = useState(300000);
  const [jumlahTempat, setJumlahTempat] = useState(3);
  const [selectedCategories, setSelectedCategories] = useState<PlaceCategory[]>([]);
  const [error, setError] = useState<string | null>(null);

  const generateMutation = useMutation({
    mutationFn: () =>
      generatePlan({
        city,
        budget,
        jumlah_tempat: jumlahTempat,
        categories: selectedCategories.length > 0 ? selectedCategories : undefined,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["plans"] });
      setError(null);
    },
    onError: (err) => {
      setError(err instanceof ApiError ? err.message : "Gagal membuat plan otomatis.");
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (planId: string) => deletePlan(planId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["plans"] }),
  });

  const toggleCategory = (cat: PlaceCategory) => {
    setSelectedCategories((prev) =>
      prev.includes(cat) ? prev.filter((c) => c !== cat) : [...prev, cat],
    );
  };

  const handleGenerate = (e: FormEvent) => {
    e.preventDefault();
    generateMutation.mutate();
  };

  return (
    <div className="bg-brand-50 min-h-screen">
      <section className="max-w-4xl mx-auto px-8 pt-16 pb-8 text-center">
        <p className="font-body text-xs tracking-[0.25em] uppercase text-brand-400 mb-2">
          Trip Planner
        </p>
        <h1 className="font-heading text-4xl text-brand-700 mb-4">Plan Saya</h1>
        <p className="text-muted max-w-xl mx-auto">
          Lihat plan yang sudah kamu buat, atau generate plan baru otomatis sesuai kota dan budget.
        </p>
      </section>

      <Divider />

      {/* Generate otomatis */}
      <section className="max-w-4xl mx-auto px-8 py-8">
        <div className="bg-white border border-brand-100 rounded-lg p-6">
          <h2 className="font-heading text-xl text-brand-700 mb-4">Generate Plan Otomatis</h2>
          <form onSubmit={handleGenerate} className="space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <div>
                <label className="block text-xs font-medium text-ink mb-1">Kota</label>
                <input
                  required
                  value={city}
                  onChange={(e) => setCity(e.target.value)}
                  className="w-full border border-brand-100 rounded-md px-3 py-2 text-sm"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-ink mb-1">Budget per tempat</label>
                <input
                  type="number"
                  required
                  value={budget}
                  onChange={(e) => setBudget(Number(e.target.value))}
                  className="w-full border border-brand-100 rounded-md px-3 py-2 text-sm"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-ink mb-1">Jumlah tempat</label>
                <input
                  type="number"
                  min={1}
                  required
                  value={jumlahTempat}
                  onChange={(e) => setJumlahTempat(Number(e.target.value))}
                  className="w-full border border-brand-100 rounded-md px-3 py-2 text-sm"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-medium text-ink mb-2">
                Kategori (opsional — kosongkan untuk kombinasi variatif)
              </label>
              <div className="flex flex-wrap gap-2">
                {categories.map((c) => (
                  <button
                    type="button"
                    key={c.value}
                    onClick={() => toggleCategory(c.value)}
                    className={`px-3 py-1.5 rounded-full text-sm border transition-colors ${
                      selectedCategories.includes(c.value)
                        ? "bg-brand-700 text-white border-brand-700"
                        : "border-brand-100 text-muted hover:bg-brand-50"
                    }`}
                  >
                    {c.label}
                  </button>
                ))}
              </div>
            </div>

            {error && <p className="text-sm text-red-600">{error}</p>}

            <button
              type="submit"
              disabled={generateMutation.isPending}
              className="bg-brand-700 text-white px-5 py-2.5 rounded-md hover:bg-brand-800 transition-colors font-medium disabled:opacity-60"
            >
              {generateMutation.isPending ? "Membuat..." : "Generate Plan"}
            </button>
          </form>
        </div>
      </section>

      {/* Daftar plan */}
      <section className="max-w-4xl mx-auto px-8 pb-16">
        <h2 className="font-heading text-xl text-brand-700 mb-4">Daftar Plan</h2>

        {isLoading && <p className="text-muted">Memuat plan...</p>}
        {plans && plans.length === 0 && (
          <p className="text-muted">Belum ada plan. Buat manual dari halaman Jelajahi Tempat, atau generate otomatis di atas.</p>
        )}

        <div className="space-y-4">
          {plans?.map((plan) => (
            <div key={plan.id} className="bg-white border border-brand-100 rounded-lg p-5">
              <div className="flex items-start justify-between mb-3">
                <div>
                  <h3 className="font-heading text-lg text-brand-700">
                    {plan.name || (plan.type === "generated" ? "Plan Otomatis" : "Plan Manual")}
                  </h3>
                  <p className="text-xs text-muted">
                    {plan.items.length} tempat
                    {plan.budget ? ` · budget ${formatRupiah(plan.budget)}` : ""}
                  </p>
                </div>
                <button
                  onClick={() => deleteMutation.mutate(plan.id)}
                  className="text-sm text-red-600 hover:underline"
                >
                  Hapus
                </button>
              </div>
              <ul className="space-y-2">
                {plan.items.map((item) => (
                  <li key={item.id} className="text-sm text-ink flex justify-between border-t border-brand-50 pt-2">
                    <span>{item.place.name}</span>
                    <span className="text-muted">{item.place.city}</span>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}

export default MyPlans;
