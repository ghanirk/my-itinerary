import type { Place } from "../types/place";

const categoryLabel: Record<Place["category"], string> = {
  kuliner: "Kuliner",
  fun: "Fun",
  sport: "Sport",
  alam: "Alam",
};

function formatRupiah(value: number): string {
  return new Intl.NumberFormat("id-ID", { style: "currency", currency: "IDR", maximumFractionDigits: 0 }).format(value);
}

interface PlaceCardProps {
  place: Place;
  onAdd?: (place: Place) => void;
}

function PlaceCard({ place, onAdd }: PlaceCardProps) {
  return (
    <div className="bg-white border border-brand-100 rounded-lg overflow-hidden flex flex-col hover:shadow-md transition-shadow">
      <div className="aspect-video bg-brand-50 overflow-hidden">
        {place.photo_url ? (
          <img src={place.photo_url} alt={place.name} className="w-full h-full object-cover" />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-brand-400/50 font-heading italic text-3xl">
            {place.name.charAt(0)}
          </div>
        )}
      </div>
      <div className="p-4 flex flex-col flex-1">
        <span className="text-xs tracking-[0.15em] uppercase text-brand-400 mb-1">
          {categoryLabel[place.category]} &middot; {place.city}
        </span>
        <h3 className="font-heading text-lg text-brand-700 mb-1">{place.name}</h3>
        <p className="text-sm text-muted mb-3">
          {formatRupiah(place.price_min)} - {formatRupiah(place.price_max)}
        </p>
        {place.opening_hours && (
          <p className="text-xs text-muted mb-3">Jam buka: {place.opening_hours}</p>
        )}
        <div className="mt-auto flex items-center gap-3 pt-2">
          <a
            href={place.gmaps_url}
            target="_blank"
            rel="noreferrer"
            className="text-sm font-medium text-brand-700 underline underline-offset-4"
          >
            Buka di Maps
          </a>
          {onAdd && (
            <button
              onClick={() => onAdd(place)}
              className="ml-auto text-sm font-medium bg-brand-700 text-white px-3 py-1.5 rounded-md hover:bg-brand-800 transition-colors"
            >
              + Plan
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

export default PlaceCard;
