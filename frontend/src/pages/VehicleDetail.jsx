import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import ReviewList from "../components/ReviewList";
import ReviewForm from "../components/ReviewForm";
import { useApi } from "../hooks/useApi";
import { useAuth } from "../context/AuthContext";

const CONDITION_LABEL = {
  excellent: { label: "Excellent", cls: "bg-green-100 text-green-700" },
  bon: { label: "Bon", cls: "bg-blue-100 text-blue-700" },
  correct: { label: "Correct", cls: "bg-yellow-100 text-yellow-700" },
  acceptable: { label: "Acceptable", cls: "bg-orange-100 text-orange-700" },
};

const COMFORT_LABEL = {
  basique: "Basique",
  standard: "Standard",
  confort: "Confort",
  premium: "Premium",
};

const CATEGORY_LABEL = {
  A: "Citadine",
  B: "Berline/Break",
  C: "SUV 5pl",
  D: "SUV 7pl",
  E: "Utilitaire",
};

export default function VehicleDetail() {
  const { vehicleId } = useParams();
  const { apiFetch } = useApi();
  const { user } = useAuth();
  const [vehicle, setVehicle] = useState(null);
  const [reviews, setReviews] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    apiFetch(`/vehicles/${vehicleId}`)
      .then((v) => {
        setVehicle(v);
        setReviews(v.reviews || []);
      })
      .catch((e) => setError(e.message));
  }, [vehicleId]);

  if (error) return (
    <div className="text-center py-12">
      <p className="text-red-500 mb-4">{error}</p>
      <Link to="/" className="text-brand-600 underline text-sm">Retour à la liste</Link>
    </div>
  );

  if (!vehicle) return <p className="text-center text-gray-400 py-12">Chargement…</p>;

  const condStyle = CONDITION_LABEL[vehicle.condition] || { label: vehicle.condition, cls: "bg-gray-100 text-gray-600" };
  const plateMasked = user?.id === vehicle.owner_id
    ? vehicle.plate
    : vehicle.plate.replace(/^(.{2}-)(\d{3})(-.{2})$/, "$1***$3");

  return (
    <div className="flex flex-col gap-6 pb-8">
      {/* Header photo */}
      {vehicle.photo_url ? (
        <img
          src={vehicle.photo_url}
          alt={`${vehicle.make} ${vehicle.model}`}
          className="w-full h-52 object-cover rounded-xl"
        />
      ) : (
        <div className="w-full h-52 rounded-xl bg-gray-100 flex items-center justify-center text-gray-300 text-lg">
          Pas de photo
        </div>
      )}

      {/* Back + title */}
      <div className="flex items-center gap-2">
        <Link to="/" className="text-brand-600 text-sm">← Retour</Link>
        <span className="text-gray-300">|</span>
        <h1 className="text-lg font-bold">
          {vehicle.make} {vehicle.model} <span className="text-gray-400 font-normal">({vehicle.year})</span>
        </h1>
      </div>

      {/* Identity */}
      <section className="bg-white rounded-xl border border-gray-100 p-4 grid grid-cols-2 gap-3 text-sm">
        <div>
          <p className="text-xs text-gray-400">Catégorie</p>
          <p className="font-medium">{vehicle.category} — {CATEGORY_LABEL[vehicle.category]}</p>
        </div>
        <div>
          <p className="text-xs text-gray-400">Immatriculation</p>
          <p className="font-medium font-mono">{plateMasked}</p>
        </div>
        <div>
          <p className="text-xs text-gray-400">CT expire</p>
          <p className="font-medium">{vehicle.ct_expiry}</p>
        </div>
        <div>
          <p className="text-xs text-gray-400">Assurance expire</p>
          <p className="font-medium">{vehicle.insurance_expiry}</p>
        </div>
        <div>
          <p className="text-xs text-gray-400">Kilométrage</p>
          <p className="font-medium">{vehicle.odometer_km.toLocaleString("fr-FR")} km</p>
        </div>
        <div>
          <p className="text-xs text-gray-400">Places / Boîte</p>
          <p className="font-medium">{vehicle.seats} places · {vehicle.transmission}</p>
        </div>
      </section>

      {/* State */}
      <section className="bg-white rounded-xl border border-gray-100 p-4 flex flex-col gap-3">
        <h2 className="font-semibold text-sm">État du véhicule</h2>
        <div className="flex gap-2 flex-wrap">
          <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${condStyle.cls}`}>
            {condStyle.label}
          </span>
          <span className="text-xs font-medium px-2 py-0.5 rounded-full bg-purple-100 text-purple-700">
            {COMFORT_LABEL[vehicle.comfort] || vehicle.comfort}
          </span>
          <span
            className={`text-xs font-medium px-2 py-0.5 rounded-full ${
              vehicle.available ? "bg-green-100 text-green-700" : "bg-red-100 text-red-600"
            }`}
          >
            {vehicle.available ? "Disponible" : "Indisponible"}
          </span>
        </div>

        {/* Fuel level bar */}
        <div>
          <p className="text-xs text-gray-400 mb-1">Niveau carburant</p>
          <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
            <div
              className={`h-full rounded-full ${vehicle.fuel_level_pct < 25 ? "bg-red-400" : "bg-green-400"}`}
              style={{ width: `${vehicle.fuel_level_pct}%` }}
            />
          </div>
          <p className="text-xs text-gray-500 mt-0.5">{vehicle.fuel_level_pct}%</p>
        </div>

        {vehicle.known_defects && (
          <p className="text-xs text-orange-600">Défauts connus : {vehicle.known_defects}</p>
        )}
      </section>

      {/* Maintenance timeline */}
      {vehicle.maintenance_events && vehicle.maintenance_events.length > 0 && (
        <section className="bg-white rounded-xl border border-gray-100 p-4">
          <h2 className="font-semibold text-sm mb-3">Historique entretien</h2>
          <ol className="relative border-l border-gray-200 ml-2">
            {vehicle.maintenance_events.map((m) => (
              <li key={m.id} className="mb-4 ml-4">
                <div className="absolute -left-1.5 w-3 h-3 bg-brand-400 rounded-full border-2 border-white" />
                <p className="text-xs text-gray-400">{m.date} · {m.km.toLocaleString("fr-FR")} km</p>
                <p className="text-sm font-medium capitalize">{m.type}</p>
                {m.description && <p className="text-xs text-gray-500">{m.description}</p>}
              </li>
            ))}
          </ol>
        </section>
      )}

      {/* CTA */}
      {vehicle.available && (
        <Link
          to={`/quote/${vehicle.id}`}
          className="w-full text-center bg-brand-600 hover:bg-brand-700 text-white rounded-xl py-3 text-sm font-semibold transition-colors"
        >
          Obtenir un devis
        </Link>
      )}

      {/* Reviews */}
      <section>
        <h2 className="font-semibold text-sm mb-3">
          Avis ({reviews.length})
        </h2>
        <ReviewList reviews={reviews} />

        {user && (
          <div className="mt-4">
            <ReviewForm
              vehicleId={vehicle.id}
              onSubmitted={(newReview) => setReviews((prev) => [newReview, ...prev])}
            />
          </div>
        )}
      </section>
    </div>
  );
}
