import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { GoogleLogin } from "@react-oauth/google";
import { useAuth } from "../context/AuthContext";

const GOOGLE_CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID;

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();

  const [mode, setMode] = useState("login"); // "login" | "register"
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setError(null);
    setLoading(true);

    const path = mode === "register" ? "/api/auth/register" : "/api/auth/login";
    const body = mode === "register"
      ? { email, password, name }
      : { email, password };

    try {
      const resp = await fetch(path, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      if (!resp.ok) {
        const err = await resp.json().catch(() => ({ detail: `Erreur serveur ${resp.status}` }));
        throw new Error(err.detail || `Erreur ${resp.status}`);
      }
      const data = await resp.json();
      login(data.access_token, data.user);
      navigate("/");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="max-w-sm mx-auto mt-8">
      <h1 className="text-xl font-bold mb-6 text-center">
        {mode === "login" ? "Connexion" : "Créer un compte"}
      </h1>

      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        {mode === "register" && (
          <div>
            <label className="block text-sm font-medium mb-1">Nom complet</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
            />
          </div>
        )}

        <div>
          <label className="block text-sm font-medium mb-1">Adresse e-mail</label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">Mot de passe</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            minLength={8}
            maxLength={72}
            className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
          />
        </div>

        {error && <p className="text-red-500 text-sm">{error}</p>}

        {GOOGLE_CLIENT_ID && (
          <>
            <div className="relative flex items-center my-1">
              <div className="flex-grow border-t border-gray-200" />
              <span className="px-3 text-xs text-gray-400">ou</span>
              <div className="flex-grow border-t border-gray-200" />
            </div>
            <div className="flex justify-center">
              <GoogleLogin
                onSuccess={async (credentialResponse) => {
                  setError(null);
                  setLoading(true);
                  try {
                    const resp = await fetch("/api/auth/google", {
                      method: "POST",
                      headers: { "Content-Type": "application/json" },
                      body: JSON.stringify({ id_token: credentialResponse.credential }),
                    });
                    if (!resp.ok) {
                      const err = await resp.json().catch(() => ({ detail: `Erreur serveur ${resp.status}` }));
                      throw new Error(err.detail || `Erreur ${resp.status}`);
                    }
                    const data = await resp.json();
                    login(data.access_token, data.user);
                    navigate("/");
                  } catch (err) {
                    setError(err.message);
                  } finally {
                    setLoading(false);
                  }
                }}
                onError={() => setError("Connexion Google échouée")}
                text={mode === "register" ? "signup_with" : "signin_with"}
                locale="fr"
              />
            </div>
          </>
        )}

        <button
          type="submit"
          disabled={loading}
          className="bg-brand-600 hover:bg-brand-700 text-white rounded-lg py-2 text-sm font-medium disabled:opacity-60"
        >
          {loading
            ? "Chargement…"
            : mode === "login"
            ? "Se connecter"
            : "Créer le compte"}
        </button>
      </form>

      <p className="text-center text-sm text-gray-500 mt-4">
        {mode === "login" ? (
          <>
            Pas encore de compte ?{" "}
            <button onClick={() => setMode("register")} className="text-brand-600 underline">
              S'inscrire
            </button>
          </>
        ) : (
          <>
            Déjà un compte ?{" "}
            <button onClick={() => setMode("login")} className="text-brand-600 underline">
              Se connecter
            </button>
          </>
        )}
      </p>

      <p className="text-center mt-4">
        <Link to="/" className="text-sm text-gray-400 hover:text-gray-600">
          ← Retour à l'accueil
        </Link>
      </p>
    </div>
  );
}
