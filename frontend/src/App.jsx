import { BrowserRouter, Routes, Route, Link } from "react-router-dom";
import Home from "./pages/Home";
import Quote from "./pages/Quote";

export default function App() {
  return (
    <BrowserRouter>
      <header className="bg-brand-600 text-white px-4 py-3 flex items-center justify-between shadow">
        <Link to="/" className="text-lg font-bold tracking-tight">
          Club de Mobilité Pierrefontaine
        </Link>
        <span className="text-sm opacity-75">0% commission · Tarifs transparents</span>
      </header>

      <main className="max-w-2xl mx-auto px-4 py-6">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/quote/:vehicleId" element={<Quote />} />
        </Routes>
      </main>
    </BrowserRouter>
  );
}
