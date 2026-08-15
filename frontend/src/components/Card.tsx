import type { CSSProperties, PropsWithChildren } from "react";

interface CardProps {
  style?: CSSProperties;
  tone?: "default" | "muted";
}

export default function Card({ children, style, tone = "default" }: PropsWithChildren<CardProps>) {
  return (
    <div
      style={{
        background: "var(--surface-1)",
        border: tone === "muted" ? "1px dashed var(--border)" : "1px solid var(--border)",
        borderRadius: "var(--radius-card)",
        padding: "1rem",
        color: tone === "muted" ? "var(--text-secondary)" : "var(--text-primary)",
        ...style,
      }}
    >
      {children}
    </div>
  );
}
