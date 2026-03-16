const STATUS_LABEL = {
  pending: { label: "En attente", cls: "bg-yellow-100 text-yellow-700" },
  active: { label: "En cours", cls: "bg-blue-100 text-blue-700" },
  completed: { label: "Terminé", cls: "bg-green-100 text-green-700" },
  cancelled: { label: "Annulé", cls: "bg-gray-100 text-gray-500" },
};

export default function BookingHistoryTable({ bookings }) {
  if (!bookings || bookings.length === 0) {
    return <p className="text-sm text-gray-400 text-center py-4">Aucune réservation.</p>;
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm border-collapse">
        <thead>
          <tr className="border-b border-gray-100 text-xs text-gray-400 text-left">
            <th className="py-2 pr-3">Début</th>
            <th className="py-2 pr-3">Fin</th>
            <th className="py-2 pr-3">Statut</th>
            <th className="py-2 pr-3 text-right">Coût</th>
          </tr>
        </thead>
        <tbody>
          {bookings.map((b) => {
            const s = STATUS_LABEL[b.status] || { label: b.status, cls: "bg-gray-100 text-gray-500" };
            const start = new Date(b.start_time).toLocaleDateString("fr-FR");
            const end = new Date(b.end_time).toLocaleDateString("fr-FR");
            return (
              <tr key={b.id} className="border-b border-gray-50 hover:bg-gray-50">
                <td className="py-2 pr-3">{start}</td>
                <td className="py-2 pr-3">{end}</td>
                <td className="py-2 pr-3">
                  <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${s.cls}`}>
                    {s.label}
                  </span>
                </td>
                <td className="py-2 text-right font-medium">{b.total_cost.toFixed(2)} €</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
