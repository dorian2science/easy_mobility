import { createContext, useContext, useState, useCallback } from "react";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem("club_token"));
  const [user, setUser] = useState(() => {
    const raw = localStorage.getItem("club_user");
    return raw ? JSON.parse(raw) : null;
  });

  const login = useCallback((accessToken, userData) => {
    localStorage.setItem("club_token", accessToken);
    localStorage.setItem("club_user", JSON.stringify(userData));
    setToken(accessToken);
    setUser(userData);
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem("club_token");
    localStorage.removeItem("club_user");
    setToken(null);
    setUser(null);
  }, []);

  return (
    <AuthContext.Provider value={{ token, user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used inside <AuthProvider>");
  return ctx;
}
