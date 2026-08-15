import { useTheme } from "../hooks/useTheme";

export default function ThemeToggle() {
  const { theme, definirTheme } = useTheme();
  const estSombre = theme === "dark";

  return (
    <button
      type="button"
      onClick={() => definirTheme(estSombre ? "light" : "dark")}
      title={estSombre ? "Passer en thème clair" : "Passer en thème sombre"}
      aria-label={estSombre ? "Passer en thème clair" : "Passer en thème sombre"}
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: "0.4rem",
        background: "transparent",
        border: "1px solid var(--border)",
        borderRadius: "var(--radius-badge)",
        padding: "0.4rem 0.75rem",
        color: "var(--text-secondary)",
        cursor: "pointer",
      }}
    >
      <span aria-hidden="true">{estSombre ? "🌙" : "☀️"}</span>
      {estSombre ? "Sombre" : "Clair"}
    </button>
  );
}
