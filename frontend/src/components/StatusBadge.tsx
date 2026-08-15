export type StatusTone = "good" | "warning" | "serious" | "critical" | "neutral";

const STYLE_TONALITE: Record<StatusTone, { couleur: string; icone: string }> = {
  good: { couleur: "var(--status-good)", icone: "●" },
  warning: { couleur: "var(--status-warning)", icone: "▲" },
  serious: { couleur: "var(--status-serious)", icone: "▲" },
  critical: { couleur: "var(--status-critical)", icone: "■" },
  neutral: { couleur: "var(--text-secondary)", icone: "○" },
};

// Icône + label toujours ensemble : un statut ne repose jamais sur la seule couleur (FR-007).
export default function StatusBadge({ tone, label }: { tone: StatusTone; label: string }) {
  const { couleur, icone } = STYLE_TONALITE[tone];
  return (
    <span
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: "0.35rem",
        padding: "0.2rem 0.6rem",
        borderRadius: "var(--radius-badge)",
        border: `1px solid ${couleur}`,
        color: couleur,
        fontSize: "0.85rem",
        fontWeight: 600,
        whiteSpace: "nowrap",
      }}
    >
      <span aria-hidden="true">{icone}</span>
      {label}
    </span>
  );
}
