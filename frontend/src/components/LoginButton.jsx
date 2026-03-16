import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function LoginButton() {
  const { user, logout } = useAuth();

  if (user) {
    return (
      <div className="flex items-center gap-2">
        {user.avatar_url && (
          <img src={user.avatar_url} alt="" className="w-7 h-7 rounded-full" />
        )}
        <Link to="/profile" className="text-sm font-medium hover:underline">
          {user.name}
        </Link>
        <button
          onClick={logout}
          className="text-xs text-white/70 hover:text-white ml-1"
        >
          Déconnexion
        </button>
      </div>
    );
  }

  return (
    <Link
      to="/login"
      className="text-sm font-medium border border-white/40 rounded-lg px-3 py-1 hover:bg-white/10 transition-colors"
    >
      Connexion
    </Link>
  );
}
