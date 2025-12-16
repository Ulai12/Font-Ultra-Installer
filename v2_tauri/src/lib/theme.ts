import { writable } from "svelte/store";

const initialTheme =
  localStorage.getItem("theme") ||
  (window.matchMedia("(prefers-color-scheme: dark)").matches
    ? "dark"
    : "light");

export const theme = writable(initialTheme);

theme.subscribe((value) => {
  localStorage.setItem("theme", value);
  document.documentElement.setAttribute("data-theme", value);
});
