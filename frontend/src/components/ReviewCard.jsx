function Stars({ rating }) {
  const full = Math.round(rating);
  return (
    <span className="text-yellow-400 text-sm" aria-label={`Note ${rating}/5`}>
      {"★".repeat(full)}{"☆".repeat(5 - full)}
      <span className="text-gray-500 ml-1 text-xs">{rating.toFixed(1)}</span>
    </span>
  );
}

export default function ReviewCard({ review }) {
  const { reviewer_name, reviewer_avatar, rating_vehicle, rating_owner, comment, created_at } = review;
  const date = new Date(created_at).toLocaleDateString("fr-FR", { year: "numeric", month: "long", day: "numeric" });

  return (
    <article className="border border-gray-100 rounded-xl p-4 bg-white">
      <div className="flex items-center gap-3 mb-2">
        {reviewer_avatar ? (
          <img src={reviewer_avatar} alt="" className="w-8 h-8 rounded-full" />
        ) : (
          <div className="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center text-xs text-gray-500">
            {(reviewer_name || "?")[0].toUpperCase()}
          </div>
        )}
        <div>
          <p className="text-sm font-medium">{reviewer_name || "Membre anonyme"}</p>
          <p className="text-xs text-gray-400">{date}</p>
        </div>
      </div>

      <div className="flex gap-4 text-xs text-gray-500 mb-2">
        <span>Véhicule : <Stars rating={rating_vehicle} /></span>
        <span>Proprio : <Stars rating={rating_owner} /></span>
      </div>

      {comment && <p className="text-sm text-gray-700 italic">"{comment}"</p>}
    </article>
  );
}
