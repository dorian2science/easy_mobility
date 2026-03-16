import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import VehicleCard from "../components/VehicleCard";
import { useApi } from "../hooks/useApi";
import { useAuth } from "../context/AuthContext";

export default function Home() {
  const { apiFetch } = useApi();
  const { user } = useAuth();
  const [vehicles, setVehicles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    apiFetch("/vehicles")
      .then(setVehicles)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p className="text-center text-gray-400 py-12">Chargement…</p>;
  if (error) return <p className="text-center text-red-500 py-12">Erreur : {error}</p>;

  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold">Véhicules disponibles</h1>
          <p className="text-sm text-gray-500">
            {vehicles.length} véhicule{vehicles.length !== 1 ? "s" : ""} dans le club
          </p>
        </div>
        {user && (
          <Link
            to="/vehicles/new"
            className="text-sm border border-brand-300 text-brand-600 rounded-lg px-3 py-1.5 hover:bg-brand-50"
          >
            + Ajouter
          </Link>
        )}
      </div>

      {vehicles.length === 0 && (
        <p className="text-gray-400 text-sm">Aucun véhicule enregistré pour l'instant.</p>
      )}
      {vehicles.map((v) => (
        <VehicleCard key={v.id} vehicle={v} />
      ))}
    </div>
  );
}
