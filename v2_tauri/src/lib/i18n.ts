import { derived, writable } from "svelte/store";

import en from "../locales/en.json";
import fr from "../locales/fr.json";

const translations = {
  fr,
  en,
};

export const currentLang = writable("fr");

export const t = derived(currentLang, ($lang) => (key: string) => {
  const lang = $lang as keyof typeof translations;
  return translations[lang]?.[key as keyof (typeof translations)["en"]] || key;
});
