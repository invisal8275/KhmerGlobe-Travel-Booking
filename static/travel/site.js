(() => {
  const theme = localStorage.getItem("kg-theme");
  if (theme) document.documentElement.dataset.theme = theme;
  const toggle = document.getElementById("themeToggle");
  if (toggle) {
    toggle.textContent = document.documentElement.dataset.theme === "dark" ? "☀" : "☾";
    toggle.addEventListener("click", () => {
      const next = document.documentElement.dataset.theme === "dark" ? "light" : "dark";
      document.documentElement.dataset.theme = next;
      localStorage.setItem("kg-theme", next);
      toggle.textContent = next === "dark" ? "☀" : "☾";
    });
  }
  const menu = document.getElementById("menuToggle");
  const nav = document.getElementById("nav");
  if (menu && nav) menu.addEventListener("click", () => nav.classList.toggle("open"));
})();
