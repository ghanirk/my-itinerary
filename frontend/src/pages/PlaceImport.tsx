import { useState, type FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import { importBulk, importPreview } from "../api/places";
import { ApiError } from "../api/client";
import type { ImportBulkPlaceItem, ImportPreviewResponse } from "../types/place";

function PlaceImport() {
  const [url, setUrl] = useState("");
  const [preview, setPreview] = useState<ImportPreviewResponse | null>(null);
  const [items, setItems] = useState<ImportBulkPlaceItem[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loadingPreview, setLoadingPreview] = useState(false);
  const [loadingSave, setLoadingSave] = useState(false);
  const [resultMessage, setResultMessage] = useState<string | null>(null);
  const navigate = useNavigate();

  const handlePreview = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);
    setResultMessage(null);
    setLoadingPreview(true);
    try {
      const res = await importPreview(url);
      setPreview(res);
      setItems(
        res.items.map((item) => ({
          name: item.name,
          category: item.category,
          price_min: item.price_min,
          price_max: item.price_max,
          gmaps_url: item.gmaps_url,
          city: item.city,
          photo_url: res.photo_url,
        })),
      );
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Gagal memproses link.");
      setPreview(null);
    } finally {
      setLoadingPreview(false);
    }
  };

  const updateItem = (index: number, patch: Partial<ImportBulkPlaceItem>) => {
    setItems((prev) => prev.map((it, i) => (i === index ? { ...it, ...patch } : it)));
  };

  const handleSaveAll = async () => {
    if (!preview) return;
    setError(null);
    setLoadingSave(true);
    try {
      const res = await importBulk({
        source_type: preview.source_type,
        source_url: preview.source_url,
        items,
      });
      setResultMessage(`${res.created_count} tempat tersimpan, ${res.skipped_count} dilewati.`);
      setTimeout(() => navigate("/places"), 1500);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Gagal menyimpan tempat.");
    } finally {
      setLoadingSave(false);
    }
  };

  return (
    <div className="bg-brand-50 min-h-screen">
      <section className="max-w-3xl mx-auto px-8 pt-16 pb-8">
        <p className="font-body text-xs tracking-[0.25em] uppercase text-brand-400 mb-2">
          Auto-import
        </p>
        <h1 className="font-heading text-3xl text-brand-700 mb-2">Import dari TikTok/YouTube</h1>
        <p className="text-muted mb-8">
          Tempel link video, AI akan mengekstrak nama tempat, kategori, dan estimasi harga.
          Periksa dulu hasilnya sebelum disimpan — video kompilasi bisa menghasilkan lebih dari satu tempat.
        </p>

        <form onSubmit={handlePreview} className="flex gap-3 mb-6">
          <input
            type="url"
            required
            placeholder="https://www.tiktok.com/... atau https://youtube.com/..."
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            className="flex-1 border border-brand-100 rounded-md px-3 py-2 text-sm bg-white focus:outline-none focus:ring-2 focus:ring-brand-400/40"
          />
          <button
            type="submit"
            disabled={loadingPreview}
            className="bg-brand-700 text-white px-5 py-2 rounded-md hover:bg-brand-800 transition-colors font-medium disabled:opacity-60"
          >
            {loadingPreview ? "Memproses..." : "Preview"}
          </button>
        </form>

        {error && <p className="text-sm text-red-600 mb-4">{error}</p>}
        {resultMessage && <p className="text-sm text-brand-700 mb-4">{resultMessage}</p>}

        {preview && (
          <div className="space-y-4">
            {preview.is_compilation && (
              <p className="text-sm text-brand-700 bg-brand-100 px-4 py-2 rounded-md">
                Video ini terdeteksi berisi {preview.items.length} tempat sekaligus.
              </p>
            )}

            {items.map((item, index) => {
              const original = preview.items[index];
              return (
                <div key={index} className="bg-white border border-brand-100 rounded-lg p-5">
                  {original.warning && (
                    <p className="text-xs text-amber-700 bg-amber-50 px-3 py-2 rounded-md mb-3">
                      ⚠ {original.warning}
                    </p>
                  )}
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    <div>
                      <label className="block text-xs font-medium text-ink mb-1">Nama</label>
                      <input
                        value={item.name}
                        onChange={(e) => updateItem(index, { name: e.target.value })}
                        className="w-full border border-brand-100 rounded-md px-3 py-1.5 text-sm"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-ink mb-1">Kota</label>
                      <input
                        value={item.city}
                        onChange={(e) => updateItem(index, { city: e.target.value })}
                        className="w-full border border-brand-100 rounded-md px-3 py-1.5 text-sm"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-ink mb-1">Kategori</label>
                      <select
                        value={item.category}
                        onChange={(e) => updateItem(index, { category: e.target.value as ImportBulkPlaceItem["category"] })}
                        className="w-full border border-brand-100 rounded-md px-3 py-1.5 text-sm"
                      >
                        <option value="kuliner">Kuliner</option>
                        <option value="fun">Fun</option>
                        <option value="sport">Sport</option>
                        <option value="alam">Alam</option>
                      </select>
                    </div>
                    <div className="flex gap-2">
                      <div className="flex-1">
                        <label className="block text-xs font-medium text-ink mb-1">Harga min</label>
                        <input
                          type="number"
                          value={item.price_min}
                          onChange={(e) => updateItem(index, { price_min: Number(e.target.value) })}
                          className="w-full border border-brand-100 rounded-md px-3 py-1.5 text-sm"
                        />
                      </div>
                      <div className="flex-1">
                        <label className="block text-xs font-medium text-ink mb-1">Harga max</label>
                        <input
                          type="number"
                          value={item.price_max}
                          onChange={(e) => updateItem(index, { price_max: Number(e.target.value) })}
                          className="w-full border border-brand-100 rounded-md px-3 py-1.5 text-sm"
                        />
                      </div>
                    </div>
                    <div className="sm:col-span-2">
                      <label className="block text-xs font-medium text-ink mb-1">Link Google Maps</label>
                      <input
                        value={item.gmaps_url}
                        onChange={(e) => updateItem(index, { gmaps_url: e.target.value })}
                        className="w-full border border-brand-100 rounded-md px-3 py-1.5 text-sm"
                      />
                      <p className="text-xs text-muted mt-1">
                        Link ini hasil pencarian otomatis — periksa & ganti dengan link lokasi yang benar sebelum disimpan.
                      </p>
                    </div>
                  </div>
                </div>
              );
            })}

            <button
              onClick={handleSaveAll}
              disabled={loadingSave}
              className="w-full bg-brand-700 text-white py-2.5 rounded-md hover:bg-brand-800 transition-colors font-medium disabled:opacity-60"
            >
              {loadingSave ? "Menyimpan..." : `Simpan ${items.length} Tempat`}
            </button>
          </div>
        )}
      </section>
    </div>
  );
}

export default PlaceImport;
