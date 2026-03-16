import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { useApi } from "../hooks/useApi";

const CATEGORIES = ["A", "B", "C", "D", "E"];
const FUEL_TYPES = ["essence", "diesel", "electrique", "hybride", "hybride_rechargeable"];
const CONDITIONS = ["excellent", "bon", "correct", "acceptable"];
const COMFORTS = ["basique", "standard", "confort", "premium"];

export default function AddVehicle() {
  const { user } = useAuth();
  const { apiFetch } = useApi();
  const navigate = useNavigate();

  const [form, setForm] = useState({
    plate: "", vin: "", ct_expiry: "", insurance_expiry: "",
    make: "", model: "", year: new Date().getFullYear(),
    category: "B", fuel_type: "essence", consumption_real: 6.0,
    seats: 5, transmission: "manuelle",
    owner_name: user?.name || "",
    odometer_km: 0, condition: "bon", comfort: "standard", fuel_level_pct: 100,
    known_defects: "", age_years: 1, annual_km_owner: 12000,
    include_fuel_default: false, min_booking_hours: 4, max_booking_days: 7,
    available: true, photo_url: "",
  });
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  if (!user) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500 mb-4">Vous devez être connecté pour ajouter un véhicule.</p>
        <Link to="/login" className="text-brand-600 underline">Se connecter</Link>
      </div>
    );
  }

  function set(field, value) {
    setForm((f) => ({ ...f, [field]: value }));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await apiFetch("/vehicles", {
        method: "POST",
        body: JSON.stringify({
          ...form,
          photo_url: form.photo_url || `https://picsum.photos/seed/${form.plate.replace(/-/g, "")}/800/500`,
        }),
      });
      navigate("/");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  function field(label, key, type = "text", props = {}) {
    return (
      <div>
        <label className="block text-xs text-gray-500 mb-1">{label}</label>
        <input
          type={type}
          value={form[key]}
          onChange={(e) => set(key, type === "number" ? Number(e.target.value) : e.target.value)}
          className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
          {...props}
        />
      </div>
    );
  }

  function selectField(label, key, options) {
    return (
      <div>
        <label className="block text-xs text-gray-500 mb-1">{label}</label>
        <select
          value={form[key]}
          onChange={(e) => set(key, e.target.value)}
          className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
        >
          {options.map((o) => <option key={o} value={o}>{o}</option>)}
        </select>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-4 pb-8">
      <div className="flex items-center gap-2">
        <Link to="/" className="text-brand-600 text-sm">← Retour</Link>
        <h1 className="text-lg font-bold">Ajouter un véhicule</h1>
      </div>

      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <section className="bg-white border border-gray-100 rounded-xl p-4 flex flex-col gap-3">
          <h2 className="font-semibold text-sm">Immatriculation</h2>
          {field("Plaque (ex: AB-123-CD)", "plate", "text", { required: true, pattern: "[A-Z]{2}-[0-9]{3}-[A-Z]{2}" })}
          {field("VIN (17 caractères)", "vin", "text", { required: true, minLength: 17, maxLength: 17 })}
          {field("Expiry CT", "ct_expiry", "date", { required: true })}
          {field("Expiry assurance", "insurance_expiry", "date", { required: true })}
        </section>

        <section className="bg-white border border-gray-100 rounded-xl p-4 flex flex-col gap-3">
          <h2 className="font-semibold text-sm">Véhicule</h2>
          {field("Marque", "make", "text", { required: true })}
          {field("Modèle", "model", "text", { required: true })}
          {field("Année", "year", "number", { min: 2000, max: 2030 })}
          {selectField("Catégorie", "category", CATEGORIES)}
          {selectField("Carburant", "fuel_type", FUEL_TYPES)}
          {field("Consommation réelle (L/100km)", "consumption_real", "number", { min: 0, step: 0.1 })}
          {field("Nombre de places", "seats", "number", { min: 2, max: 9 })}
          {selectField("Boîte", "transmission", ["manuelle", "automatique"])}
        </section>

        <section className="bg-white border border-gray-100 rounded-xl p-4 flex flex-col gap-3">
          <h2 className="font-semibold text-sm">État actuel</h2>
          {field("Kilométrage", "odometer_km", "number", { min: 0 })}
          {selectField("Condition", "condition", CONDITIONS)}
          {selectField("Confort", "comfort", COMFORTS)}
          {field("Niveau carburant (%)", "fuel_level_pct", "number", { min: 0, max: 100 })}
          {field("Défauts connus", "known_defects")}
        </section>

        <section className="bg-white border border-gray-100 rounded-xl p-4 flex flex-col gap-3">
          <h2 className="font-semibold text-sm">Tarification</h2>
          {field("Âge du véhicule (années)", "age_years", "number", { min: 0, step: 0.5 })}
          {field("Km annuels propriétaire", "annual_km_owner", "number", { min: 0 })}
          {field("Durée min. réservation (h)", "min_booking_hours", "number", { min: 1 })}
          {field("Durée max. réservation (jours)", "max_booking_days", "number", { min: 1 })}
          <label className="flex items-center gap-2 text-sm cursor-pointer">
            <input
              type="checkbox"
              checked={form.include_fuel_default}
              onChange={(e) => set("include_fuel_default", e.target.checked)}
              className="w-4 h-4 accent-brand-600"
            />
            Inclure carburant par défaut
          </label>
        </section>

        <section className="bg-white border border-gray-100 rounded-xl p-4 flex flex-col gap-3">
          <h2 className="font-semibold text-sm">Photo</h2>
          {field("URL de la photo (optionnel)", "photo_url", "url")}
          <p className="text-xs text-gray-400">
            Si vide, une photo générique sera utilisée.
          </p>
        </section>

        {error && <p className="text-red-500 text-sm">{error}</p>}

        <button
          type="submit"
          disabled={loading}
          className="bg-brand-600 hover:bg-brand-700 text-white rounded-xl py-3 text-sm font-semibold disabled:opacity-60"
        >
          {loading ? "Ajout en cours…" : "Ajouter le véhicule"}
        </button>
      </form>
    </div>
  );
}
