import { useState } from "react";

export default function ReviewForm({ vehicleId, onSubmitted }) {
  const [ratingVehicle, setRatingVehicle] = useState(5);
  const [ratingOwner, setRatingOwner] = useState(5);
  const [comment, setComment] = useState("");
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setError(null);
    setLoading(true);

    const token = localStorage.getItem("club_token");
    if (!token) {
      setError("Vous devez être connecté pour laisser un avis.");
      setLoading(false);
      return;
    }

    try {
      const resp = await fetch(`/api/vehicles/${vehicleId}/reviews`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          rating_vehicle: ratingVehicle,
          rating_owner: ratingOwner,
          comment,
        }),
      });
      const data = await resp.json();
      if (!resp.ok) throw new Error(data.detail || `Erreur ${resp.status}`);
      setComment("");
      onSubmitted && onSubmitted(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="border border-gray-200 rounded-xl p-4 bg-white flex flex-col gap-3">
      <h3 className="text-sm font-semibold">Laisser un avis</h3>

      <div className="flex gap-6">
        <label className="flex flex-col gap-1 text-xs text-gray-600">
          Véhicule
          <select
            value={ratingVehicle}
            onChange={(e) => setRatingVehicle(Number(e.target.value))}
            className="border border-gray-300 rounded px-2 py-1 text-sm"
          >
            {[1, 2, 3, 4, 5].map((n) => (
              <option key={n} value={n}>{n} ★</option>
            ))}
          </select>
        </label>

        <label className="flex flex-col gap-1 text-xs text-gray-600">
          Propriétaire
          <select
            value={ratingOwner}
            onChange={(e) => setRatingOwner(Number(e.target.value))}
            className="border border-gray-300 rounded px-2 py-1 text-sm"
          >
            {[1, 2, 3, 4, 5].map((n) => (
              <option key={n} value={n}>{n} ★</option>
            ))}
          </select>
        </label>
      </div>

      <textarea
        value={comment}
        onChange={(e) => setComment(e.target.value)}
        placeholder="Votre commentaire (optionnel)"
        rows={3}
        className="border border-gray-300 rounded-lg px-3 py-2 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-brand-500"
      />

      {error && <p className="text-red-500 text-xs">{error}</p>}

      <button
        type="submit"
        disabled={loading}
        className="bg-brand-600 hover:bg-brand-700 text-white rounded-lg py-2 text-sm font-medium disabled:opacity-60"
      >
        {loading ? "Envoi…" : "Publier l'avis"}
      </button>
    </form>
  );
}
