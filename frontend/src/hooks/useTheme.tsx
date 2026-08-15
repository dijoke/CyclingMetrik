import { type PropsWithChildren, createContext, useContext, useEffect, useState } from "react";

type ChoixTheme = "light" | "dark" | null; // null = suit la préférence système
type ThemeResolu = "light" | "dark";

interface ThemeContextValue {
  theme: ThemeResolu;
  choixExplicite: ChoixTheme;
  definirTheme: (choix: ChoixTheme) => void;
}

const ThemeContext = createContext<ThemeContextValue | null>(null);

const CLE_STOCKAGE = "cyclingmetrik-theme";

function lireChoixStocke(): ChoixTheme {
  const valeur = localStorage.getItem(CLE_STOCKAGE);
  return valeur === "light" || valeur === "dark" ? valeur : null;
}

function preferenceSystemeActuelle(): ThemeResolu {
  return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}

export function ThemeProvider({ children }: PropsWithChildren) {
  const [choixExplicite, setChoixExplicite] = useState<ChoixTheme>(lireChoixStocke);
  const [preferenceSysteme, setPreferenceSysteme] = useState<ThemeResolu>(preferenceSystemeActuelle);

  useEffect(() => {
    const media = window.matchMedia("(prefers-color-scheme: dark)");
    const ecouter = (evenement: MediaQueryListEvent) =>
      setPreferenceSysteme(evenement.matches ? "dark" : "light");
    media.addEventListener("change", ecouter);
    return () => media.removeEventListener("change", ecouter);
  }, []);

  const theme = choixExplicite ?? preferenceSysteme;

  useEffect(() => {
    if (choixExplicite) {
      document.documentElement.dataset.theme = choixExplicite;
    } else {
      delete document.documentElement.dataset.theme;
    }
  }, [choixExplicite]);

  function definirTheme(choix: ChoixTheme) {
    setChoixExplicite(choix);
    if (choix) {
      localStorage.setItem(CLE_STOCKAGE, choix);
    } else {
      localStorage.removeItem(CLE_STOCKAGE);
    }
  }

  return (
    <ThemeContext.Provider value={{ theme, choixExplicite, definirTheme }}>{children}</ThemeContext.Provider>
  );
}

export function useTheme(): ThemeContextValue {
  const contexte = useContext(ThemeContext);
  if (!contexte) throw new Error("useTheme doit être utilisé à l'intérieur d'un ThemeProvider");
  return contexte;
}
