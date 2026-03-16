import { BrowserRouter, Routes, Route, Link } from "react-router-dom";
import { GoogleOAuthProvider } from "@react-oauth/google";
import { AuthProvider } from "./context/AuthContext";
import LoginButton from "./components/LoginButton";
import Home from "./pages/Home";
import Quote from "./pages/Quote";
import VehicleDetail from "./pages/VehicleDetail";
import Login from "./pages/Login";
import Profile from "./pages/Profile";
import AddVehicle from "./pages/AddVehicle";

export default function App() {
  const googleClientId = import.meta.env.VITE_GOOGLE_CLIENT_ID || "";

  return (
    <GoogleOAuthProvider clientId={googleClientId} locale="fr">
    <AuthProvider>
      <BrowserRouter>
        <header className="bg-brand-600 text-white px-4 py-3 flex items-center justify-between shadow">
          <Link to="/" className="text-lg font-bold tracking-tight">
            Club de Mobilité Pierrefontaine
          </Link>
          <div className="flex items-center gap-3">
            <span className="text-sm opacity-75 hidden sm:inline">0% commission · Tarifs transparents</span>
            <LoginButton />
          </div>
        </header>

        <main className="max-w-2xl mx-auto px-4 py-6">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/vehicles/:vehicleId" element={<VehicleDetail />} />
            <Route path="/vehicles/new" element={<AddVehicle />} />
            <Route path="/quote/:vehicleId" element={<Quote />} />
            <Route path="/login" element={<Login />} />
            <Route path="/profile" element={<Profile />} />
          </Routes>
        </main>
      </BrowserRouter>
    </AuthProvider>
    </GoogleOAuthProvider>
  );
}
