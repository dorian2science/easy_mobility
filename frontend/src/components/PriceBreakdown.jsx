function Row({ label, value, bold }) {
  return (
    <div className={`flex justify-between text-sm py-1 ${bold ? "font-semibold" : ""}`}>
      <span className="text-gray-600">{label}</span>
      <span className={bold ? "text-gray-900" : "text-gray-700"}>{value}</span>
    </div>
  );
}

function fmt(n) {
  return `${Number(n).toFixed(2)} €`;
}

export default function PriceBreakdown({ data }) {
  if (!data) return null;

  const { breakdown, result, warnings, input } = data;

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-4 flex flex-col gap-3">
      <h3 className="font-semibold text-base">Détail du devis</h3>

      <div className="divide-y divide-gray-100">
        <Row label={`PRK ajusté (×${input.distance_km} km)`} value={fmt(breakdown.km_cost)} />
        <Row label="Coût temporel (charges fixes)" value={fmt(breakdown.time_cost)} />
        {input.include_fuel && (
          <Row label="Carburant estimé" value={fmt(breakdown.fuel_cost)} />
        )}
        <Row
          label={`Assurance Cartage (${breakdown.cartage_days} jour${breakdown.cartage_days > 1 ? "s" : ""})`}
          value={fmt(breakdown.cartage_cost)}
        />
        <Row label="Sous-total" value={fmt(breakdown.subtotal)} bold />
        <Row
          label={`Marge propriétaire (${(breakdown.owner_margin_rate * 100).toFixed(1)}%)`}
          value={fmt(breakdown.owner_margin)}
        />
      </div>

      <div className="bg-brand-50 rounded-lg p-3 mt-1">
        <div className="flex justify-between items-center">
          <span className="font-bold text-brand-700">Total suggéré</span>
          <span className="font-bold text-xl text-brand-700">{fmt(result.total)}</span>
        </div>
        <div className="flex justify-between text-xs text-gray-500 mt-1">
          <span>Plancher : {fmt(result.floor)}</span>
          <span>Plafond : {fmt(result.ceiling)}</span>
        </div>
      </div>

      {warnings && warnings.length > 0 && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
          <p className="text-xs font-semibold text-yellow-800 mb-1">Avertissements</p>
          {warnings.map((w, i) => (
            <p key={i} className="text-xs text-yellow-700">⚠ {w}</p>
          ))}
        </div>
      )}

      <p className="text-xs text-gray-400 text-center mt-1">
        Le paiement s'effectue directement entre membres · Commission : 0%
      </p>
    </div>
  );
}
