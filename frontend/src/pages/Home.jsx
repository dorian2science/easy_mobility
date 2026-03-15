import { useEffect, useState } from "react";
import VehicleCard from "../components/VehicleCard";

const API_KEY = import.meta.env.VITE_CLUB_API_KEY ?? "dev-secret-key-change-in-prod";

export default function Home() {
  const [vehicles, setVehicles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch("/api/vehicles", { headers: { "X-Club-Key": API_KEY } })
      .then((r) => {
        if (!r.ok) throw new Error(`Erreur ${r.status}`);
        return r.json();
      })
      .then(setVehicles)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p className="text-center text-gray-400 py-12">Chargement…</p>;
  if (error) return <p className="text-center text-red-500 py-12">Erreur : {error}</p>;

  return (
    <div className="flex flex-col gap-4">
      <h1 className="text-xl font-bold">Véhicules disponibles</h1>
      <p className="text-sm text-gray-500">
        {vehicles.length} véhicule{vehicles.length !== 1 ? "s" : ""} dans le club
      </p>
      {vehicles.length === 0 && (
        <p className="text-gray-400 text-sm">Aucun véhicule enregistré pour l'instant.</p>
      )}
      {vehicles.map((v) => (
        <VehicleCard key={v.id} vehicle={v} />
      ))}
    </div>
  );
}
