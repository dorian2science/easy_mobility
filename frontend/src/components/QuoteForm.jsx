import { useState } from "react";

export default function QuoteForm({ vehicle, onSubmit, loading }) {
  const [hours, setHours] = useState(vehicle?.min_booking_hours ?? 4);
  const [km, setKm] = useState(100);
  const [fuel, setFuel] = useState(vehicle?.include_fuel_default ?? false);
  const [errors, setErrors] = useState({});

  function validate() {
    const e = {};
    if (hours < (vehicle?.min_booking_hours ?? 1))
      e.hours = `Minimum ${vehicle?.min_booking_hours ?? 1} heure(s)`;
    if (hours > (vehicle?.max_booking_days ?? 7) * 24)
      e.hours = `Maximum ${vehicle?.max_booking_days ?? 7} jours`;
    if (km <= 0) e.km = "La distance doit être > 0";
    return e;
  }

  function handleSubmit(e) {
    e.preventDefault();
    const errs = validate();
    if (Object.keys(errs).length > 0) {
      setErrors(errs);
      return;
    }
    setErrors({});
    onSubmit({ duration_hours: parseFloat(hours), distance_km: parseFloat(km), include_fuel: fuel });
  }

  return (
    <form onSubmit={handleSubmit} className="bg-white rounded-xl shadow-sm border border-gray-100 p-4 flex flex-col gap-4">
      <h3 className="font-semibold text-base">Paramètres de la location</h3>

      <div>
        <label className="text-sm font-medium text-gray-700 block mb-1">
          Durée (heures)
        </label>
        <input
          type="number"
          min={vehicle?.min_booking_hours ?? 1}
          max={(vehicle?.max_booking_days ?? 7) * 24}
          step="0.5"
          value={hours}
          onChange={(e) => setHours(e.target.value)}
          className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
        />
        {errors.hours && <p className="text-red-500 text-xs mt-1">{errors.hours}</p>}
        <p className="text-xs text-gray-400 mt-0.5">
          Min {vehicle?.min_booking_hours ?? 4}h · Max {(vehicle?.max_booking_days ?? 7) * 24}h
        </p>
      </div>

      <div>
        <label className="text-sm font-medium text-gray-700 block mb-1">
          Distance estimée (km)
        </label>
        <input
          type="number"
          min={1}
          value={km}
          onChange={(e) => setKm(e.target.value)}
          className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
        />
        {errors.km && <p className="text-red-500 text-xs mt-1">{errors.km}</p>}
      </div>

      {vehicle?.fuel_type !== "electrique" && (
        <label className="flex items-center gap-2 text-sm text-gray-700 cursor-pointer">
          <input
            type="checkbox"
            checked={fuel}
            onChange={(e) => setFuel(e.target.checked)}
            className="rounded text-brand-600"
          />
          Inclure le carburant dans le devis
        </label>
      )}

      <button
        type="submit"
        disabled={loading}
        className="w-full bg-brand-600 hover:bg-brand-700 disabled:opacity-50 text-white rounded-lg py-2.5 text-sm font-semibold transition-colors"
      >
        {loading ? "Calcul en cours…" : "Calculer le devis"}
      </button>
    </form>
  );
}
