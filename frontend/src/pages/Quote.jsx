import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import QuoteForm from "../components/QuoteForm";
import PriceBreakdown from "../components/PriceBreakdown";
import { useApi } from "../hooks/useApi";

export default function Quote() {
  const { vehicleId } = useParams();
  const { apiFetch } = useApi();
  const [vehicle, setVehicle] = useState(null);
  const [quoteData, setQuoteData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [fetchError, setFetchError] = useState(null);

  useEffect(() => {
    apiFetch(`/vehicles/${vehicleId}`)
      .then(setVehicle)
      .catch((e) => setFetchError(e.message));
  }, [vehicleId]);

  async function handleQuote(params) {
    setLoading(true);
    setQuoteData(null);
    try {
      const data = await apiFetch("/quote", {
        method: "POST",
        body: JSON.stringify({ vehicle_id: parseInt(vehicleId), ...params }),
      });
      setQuoteData(data);
    } catch (e) {
      alert(e.message);
    } finally {
      setLoading(false);
    }
  }

  if (fetchError) return (
    <div className="text-center py-12">
      <p className="text-red-500 mb-4">{fetchError}</p>
      <Link to="/" className="text-brand-600 underline text-sm">Retour à la liste</Link>
    </div>
  );

  if (!vehicle) return <p className="text-center text-gray-400 py-12">Chargement…</p>;

  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-center gap-2">
        <Link to={`/vehicles/${vehicleId}`} className="text-brand-600 text-sm">← Retour</Link>
        <span className="text-gray-300">|</span>
        <h1 className="text-lg font-bold">
          {vehicle.make} {vehicle.model} ({vehicle.year})
        </h1>
      </div>

      <QuoteForm vehicle={vehicle} onSubmit={handleQuote} loading={loading} />

      {quoteData && <PriceBreakdown data={quoteData} />}
    </div>
  );
}
