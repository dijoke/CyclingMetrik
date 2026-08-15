import { HashRouter as Router, NavLink, Route, Routes } from "react-router-dom";
import Connexions from "./pages/Connexions";
import Dashboard from "./pages/Dashboard";
import HistoriqueSeances from "./pages/HistoriqueSeances";
import Profil from "./pages/Profil";
import Recommandations from "./pages/Recommandations";

const liens = [
  { to: "/", label: "Tableau de bord" },
  { to: "/seances", label: "Historique" },
  { to: "/recommandations", label: "Recommandations" },
  { to: "/connexions", label: "Connexions" },
  { to: "/profil", label: "Profil" },
];

export default function App() {
  return (
    <Router>
      <div style={{ display: "flex", minHeight: "100vh", fontFamily: "system-ui, sans-serif" }}>
        <nav style={{ width: 220, borderRight: "1px solid #e2e2e2", padding: "1.5rem 1rem" }}>
          <h1 style={{ fontSize: "1.1rem", marginBottom: "1.5rem" }}>Coaching vélo</h1>
          <ul
            style={{
              listStyle: "none",
              padding: 0,
              display: "flex",
              flexDirection: "column",
              gap: "0.5rem",
            }}
          >
            {liens.map((lien) => (
              <li key={lien.to}>
                <NavLink
                  to={lien.to}
                  end={lien.to === "/"}
                  style={({ isActive }) => ({
                    textDecoration: "none",
                    color: isActive ? "#0b5fff" : "#333",
                    fontWeight: isActive ? 600 : 400,
                  })}
                >
                  {lien.label}
                </NavLink>
              </li>
            ))}
          </ul>
        </nav>
        <main style={{ flex: 1, padding: "2rem" }}>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/seances" element={<HistoriqueSeances />} />
            <Route path="/recommandations" element={<Recommandations />} />
            <Route path="/connexions" element={<Connexions />} />
            <Route path="/profil" element={<Profil />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}
