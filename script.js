const root = document.documentElement;
const nav = document.getElementById("nav");
const menuBtn = document.getElementById("menuBtn");
const modeBtn = document.getElementById("modeBtn");

/* Theme: saved choice first, otherwise the visitor's system setting */
function applyTheme(theme) {
  root.setAttribute("data-theme", theme);
  modeBtn.textContent = theme === "dark" ? "Light" : "Dark";
}

let saved = null;
try { saved = localStorage.getItem("theme"); } catch (e) {}
applyTheme(saved || (matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light"));

modeBtn.addEventListener("click", () => {
  const next = root.getAttribute("data-theme") === "dark" ? "light" : "dark";
  applyTheme(next);
  try { localStorage.setItem("theme", next); } catch (e) {}
});

/* Mobile menu */
menuBtn.addEventListener("click", () => {
  const open = nav.classList.toggle("open");
  menuBtn.setAttribute("aria-expanded", open);
});
nav.querySelectorAll("a").forEach(a =>
  a.addEventListener("click", () => {
    nav.classList.remove("open");
    menuBtn.setAttribute("aria-expanded", "false");
  })
);