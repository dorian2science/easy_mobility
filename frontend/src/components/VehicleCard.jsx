import { Link } from "react-router-dom";

const CATEGORY_LABEL = {
  A: "Citadine",
  B: "Berline/Break",
  C: "SUV 5pl",
  D: "SUV 7pl",
  E: "Utilitaire",
};

export function Stars({ rating }) {
  const full = Math.round(rating);
  return (
    <span className="text-yellow-400 text-sm" aria-label={`Note ${rating}/5`}>
      {"★".repeat(full)}{"☆".repeat(5 - full)}
      <span className="text-gray-500 ml-1 text-xs">{rating.toFixed(1)}</span>
    </span>
  );
}

export default function VehicleCard({ vehicle }) {
  const { id, make, model, year, category, owner_name, nb_reviews, rating, condition, comfort, available, photo_url } = vehicle;

  return (
    <article className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden flex flex-col">
      {photo_url ? (
        <img
          src={photo_url}
          alt={`${make} ${model}`}
          className="w-full h-36 object-cover"
        />
      ) : (
        <div className="w-full h-36 bg-gray-100 flex items-center justify-center text-gray-300 text-sm">
          Pas de photo
        </div>
      )}

      <div className="p-4 flex flex-col gap-2">
        <div className="flex items-start justify-between">
          <div>
            <h2 className="font-semibold text-base">
              {make} {model} <span className="text-gray-400 font-normal">({year})</span>
            </h2>
            <p className="text-xs text-gray-500">
              Cat. {category} — {CATEGORY_LABEL[category]} · {condition} · {comfort}
            </p>
          </div>
          <span
            className={`text-xs font-medium px-2 py-0.5 rounded-full ${
              available ? "bg-green-100 text-green-700" : "bg-red-100 text-red-600"
            }`}
          >
            {available ? "Disponible" : "Indisponible"}
          </span>
        </div>

        <div className="flex items-center gap-2 text-sm text-gray-600">
          <span>Propriétaire : <strong>{owner_name}</strong></span>
          <span className="text-gray-300">|</span>
          <Stars rating={rating} />
          <span className="text-xs text-gray-400">({nb_reviews} avis)</span>
        </div>

        <Link
          to={`/vehicles/${id}`}
          className="mt-1 w-full text-center bg-brand-600 hover:bg-brand-700 text-white rounded-lg py-2 text-sm font-medium transition-colors"
        >
          Voir le détail
        </Link>
      </div>
    </article>
  );
}
