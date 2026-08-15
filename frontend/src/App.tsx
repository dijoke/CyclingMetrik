import { HashRouter as Router, NavLink, Route, Routes } from "react-router-dom";
import ThemeToggle from "./components/ThemeToggle";
import ConnexionCallback from "./pages/ConnexionCallback";
import Connexions from "./pages/Connexions";
import Dashboard from "./pages/Dashboard";
import HistoriqueSeances from "./pages/HistoriqueSeances";
import Profil from "./pages/Profil";
import Recommandations from "./pages/Recommandations";
import Statistiques from "./pages/Statistiques";

const liens = [
  { to: "/", label: "Tableau de bord" },
  { to: "/seances", label: "Historique" },
  { to: "/statistiques", label: "Statistiques" },
  { to: "/recommandations", label: "Recommandations" },
  { to: "/connexions", label: "Connexions" },
  { to: "/profil", label: "Profil" },
];

export default function App() {
  return (
    <Router>
      <div
        style={{
          minHeight: "100vh",
          fontFamily: "system-ui, -apple-system, 'Segoe UI', sans-serif",
          background: "var(--page-plane)",
          color: "var(--text-primary)",
        }}
      >
        <header
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            flexWrap: "wrap",
            gap: "1rem",
            padding: "0.85rem 1.5rem",
            borderBottom: "1px solid var(--border)",
            background: "var(--surface-1)",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: "2rem", flexWrap: "wrap" }}>
            <h1 style={{ fontSize: "1.1rem", margin: 0, color: "var(--text-primary)" }}>Coaching vélo</h1>
            <nav>
              <ul
                style={{
                  listStyle: "none",
                  padding: 0,
                  margin: 0,
                  display: "flex",
                  flexWrap: "wrap",
                  gap: "0.25rem",
                }}
              >
                {liens.map((lien) => (
                  <li key={lien.to}>
                    <NavLink
                      to={lien.to}
                      end={lien.to === "/"}
                      style={({ isActive }) => ({
                        display: "block",
                        padding: "0.5rem 0.75rem",
                        borderRadius: 6,
                        textDecoration: "none",
                        color: isActive ? "var(--selection-text)" : "var(--text-secondary)",
                        background: isActive ? "var(--selection-bg)" : "transparent",
                        fontWeight: isActive ? 600 : 400,
                      })}
                    >
                      {lien.label}
                    </NavLink>
                  </li>
                ))}
              </ul>
            </nav>
          </div>
          <ThemeToggle />
        </header>
        <main style={{ padding: "2rem" }}>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/seances" element={<HistoriqueSeances />} />
            <Route path="/statistiques" element={<Statistiques />} />
            <Route path="/recommandations" element={<Recommandations />} />
            <Route path="/connexions" element={<Connexions />} />
            <Route path="/connexions/:plateforme/callback" element={<ConnexionCallback />} />
            <Route path="/profil" element={<Profil />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}
