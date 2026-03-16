import { useEffect, useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { useApi } from "../hooks/useApi";
import StatsDashboard from "../components/StatsDashboard";
import BookingHistoryTable from "../components/BookingHistoryTable";

export default function Profile() {
  const { user, logout } = useAuth();
  const { apiFetch } = useApi();
  const navigate = useNavigate();

  const [profile, setProfile] = useState(null);
  const [stats, setStats] = useState(null);
  const [renterBookings, setRenterBookings] = useState([]);
  const [ownerBookings, setOwnerBookings] = useState([]);
  const [tab, setTab] = useState("renter");
  const [phone, setPhone] = useState("");
  const [notifWhatsapp, setNotifWhatsapp] = useState(false);
  const [saving, setSaving] = useState(false);
  const [saveMsg, setSaveMsg] = useState(null);

  useEffect(() => {
    if (!user) { navigate("/login"); return; }
    Promise.all([
      apiFetch("/users/me"),
      apiFetch("/users/me/stats"),
      apiFetch("/bookings/me"),
      apiFetch("/bookings/my-vehicles"),
    ]).then(([p, s, rb, ob]) => {
      setProfile(p);
      setPhone(p.phone || "");
      setNotifWhatsapp(p.notif_whatsapp);
      setStats(s);
      setRenterBookings(rb);
      setOwnerBookings(ob);
    }).catch(console.error);
  }, [user]);

  async function handleSave(e) {
    e.preventDefault();
    setSaving(true);
    setSaveMsg(null);
    try {
      await apiFetch("/users/me", {
        method: "PUT",
        body: JSON.stringify({ phone, notif_whatsapp: notifWhatsapp }),
      });
      setSaveMsg("Sauvegardé !");
    } catch (err) {
      setSaveMsg(`Erreur : ${err.message}`);
    } finally {
      setSaving(false);
    }
  }

  if (!user) return null;
  if (!profile) return <p className="text-center text-gray-400 py-12">Chargement…</p>;

  return (
    <div className="flex flex-col gap-6 pb-8">
      {/* Avatar + identity */}
      <div className="flex items-center gap-4">
        {profile.avatar_url ? (
          <img src={profile.avatar_url} alt="" className="w-16 h-16 rounded-full" />
        ) : (
          <div className="w-16 h-16 rounded-full bg-brand-100 flex items-center justify-center text-2xl font-bold text-brand-600">
            {profile.name[0].toUpperCase()}
          </div>
        )}
        <div>
          <h1 className="text-lg font-bold">{profile.name}</h1>
          <p className="text-sm text-gray-500">{profile.email}</p>
          <div className="flex gap-2 mt-1">
            {profile.id_doc_verified && (
              <span className="text-xs px-2 py-0.5 rounded-full bg-green-100 text-green-700 font-medium">
                Identité vérifiée ✓
              </span>
            )}
            {profile.driver_license_verified && (
              <span className="text-xs px-2 py-0.5 rounded-full bg-blue-100 text-blue-700 font-medium">
                Permis vérifié ✓
              </span>
            )}
          </div>
        </div>
      </div>

      {/* Stats */}
      <StatsDashboard stats={stats} />

      {/* Phone + notifications */}
      <form onSubmit={handleSave} className="bg-white border border-gray-100 rounded-xl p-4 flex flex-col gap-3">
        <h2 className="font-semibold text-sm">Préférences</h2>
        <div>
          <label className="block text-xs text-gray-500 mb-1">Téléphone</label>
          <input
            type="tel"
            value={phone}
            onChange={(e) => setPhone(e.target.value)}
            placeholder="+33612345678"
            className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
          />
        </div>
        <label className="flex items-center gap-2 text-sm cursor-pointer">
          <input
            type="checkbox"
            checked={notifWhatsapp}
            onChange={(e) => setNotifWhatsapp(e.target.checked)}
            className="w-4 h-4 accent-brand-600"
          />
          Recevoir les notifications WhatsApp
        </label>
        {saveMsg && <p className="text-xs text-green-600">{saveMsg}</p>}
        <button
          type="submit"
          disabled={saving}
          className="bg-brand-600 hover:bg-brand-700 text-white rounded-lg py-2 text-sm font-medium disabled:opacity-60"
        >
          {saving ? "Sauvegarde…" : "Enregistrer"}
        </button>
      </form>

      {/* My vehicles */}
      <div className="flex items-center justify-between">
        <h2 className="font-semibold text-sm">Mes véhicules</h2>
        <Link
          to="/vehicles/new"
          className="text-xs text-brand-600 border border-brand-300 rounded-lg px-3 py-1 hover:bg-brand-50"
        >
          + Ajouter
        </Link>
      </div>

      {/* Booking history tabs */}
      <div>
        <div className="flex border-b border-gray-200 mb-3">
          {["renter", "owner"].map((t) => (
            <button
              key={t}
              onClick={() => setTab(t)}
              className={`px-4 py-2 text-sm font-medium border-b-2 -mb-px transition-colors ${
                tab === t
                  ? "border-brand-600 text-brand-600"
                  : "border-transparent text-gray-500 hover:text-gray-700"
              }`}
            >
              {t === "renter" ? "En tant que locataire" : "En tant que proprio"}
            </button>
          ))}
        </div>
        <BookingHistoryTable bookings={tab === "renter" ? renterBookings : ownerBookings} />
      </div>

      <button
        onClick={() => { logout(); navigate("/"); }}
        className="text-sm text-gray-400 hover:text-red-500 text-center"
      >
        Déconnexion
      </button>
    </div>
  );
}
