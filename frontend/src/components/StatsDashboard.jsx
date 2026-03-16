export default function StatsDashboard({ stats }) {
  if (!stats) return null;

  const tiles = [
    { label: "Gagné (proprio)", value: `${stats.earned_eur.toFixed(2)} €` },
    { label: "Dépensé (locataire)", value: `${stats.spent_eur.toFixed(2)} €` },
    { label: "Locations effectuées", value: stats.total_rentals_as_renter },
    {
      label: "Note moyenne reçue",
      value: stats.avg_rating_as_owner != null
        ? `${stats.avg_rating_as_owner.toFixed(1)} ★`
        : "—",
    },
  ];

  return (
    <div className="grid grid-cols-2 gap-3">
      {tiles.map((t) => (
        <div key={t.label} className="bg-white border border-gray-100 rounded-xl p-4 text-center">
          <p className="text-xl font-bold text-brand-600">{t.value}</p>
          <p className="text-xs text-gray-500 mt-1">{t.label}</p>
        </div>
      ))}
    </div>
  );
}
