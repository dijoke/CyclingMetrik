import { useEffect, useRef, useState } from "react";
import { useNavigate, useParams, useSearchParams } from "react-router-dom";
import Card from "../components/Card";
import { type Plateforme, api } from "../services/api_client";

export default function ConnexionCallback() {
  const { plateforme } = useParams<{ plateforme: Plateforme }>();
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [erreur, setErreur] = useState<string | null>(null);
  const appelEnCours = useRef(false);

  useEffect(() => {
    if (appelEnCours.current || !plateforme) return;
    appelEnCours.current = true;

    const code = searchParams.get("code");
    const erreurAutorisation = searchParams.get("error");

    if (erreurAutorisation) {
      setErreur(`Autorisation refusée par ${plateforme} (${erreurAutorisation}).`);
      return;
    }
    if (!code) {
      setErreur("Code d'autorisation manquant dans la réponse.");
      return;
    }

    api.connexions
      .callback(plateforme, code)
      .then(() => navigate("/connexions", { replace: true }))
      .catch((err: Error) => setErreur(err.message));
  }, [plateforme, searchParams, navigate]);

  return (
    <section>
      <h2 style={{ color: "var(--text-primary)" }}>Connexion en cours…</h2>
      {erreur ? (
        <Card tone="muted">{erreur}</Card>
      ) : (
        <p style={{ color: "var(--text-secondary)" }}>Finalisation de la connexion à {plateforme}…</p>
      )}
    </section>
  );
}
