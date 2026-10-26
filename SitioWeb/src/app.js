"use strict";
(() => {
  if (window.location.hash === "#demos") {
    window.location.replace("demos/index.html");
    return;
  }
  const data = JSON.parse(document.getElementById("portfolio-data").textContent);
  const grid = document.getElementById("project-grid");
  const search = document.getElementById("project-search");
  const area = document.getElementById("project-area");
  const more = document.getElementById("load-more");
  const info = document.getElementById("results-info");
  const empty = document.getElementById("empty-results");
  const tabs = [...document.querySelectorAll("[data-family]")];
  let family = "all", limit = 12;
  const normalize = value => value.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase();
  function updateAreas() {
    const selected = area.value;
    const available = [...new Set(data.projects
      .filter(project => family === "all" || project.family === family)
      .map(project => project.area))].sort((a, b) => a.localeCompare(b, "es"));
    area.replaceChildren(new Option("Todas las áreas", "all"),
      ...available.map(value => new Option(value, value)));
    area.value = available.includes(selected) ? selected : "all";
  }
  function update() {
    const query = normalize(search.value.trim());
    const matching = data.projects.filter(project =>
      (family === "all" || project.family === family) &&
      (!area.value || area.value === "all" || project.area === area.value) &&
      normalize([project.name, project.area, project.question, project.techniques, project.status].join(" ")).includes(query));
    const visible = new Set(matching.slice(0, limit).map(project => project.id));
    for (const card of grid.children) card.hidden = !visible.has(card.dataset.project);
    empty.hidden = matching.length !== 0;
    more.hidden = matching.length <= limit;
    info.textContent = matching.length ? `Mostrando ${Math.min(limit, matching.length)} de ${matching.length} proyectos` : "0 proyectos encontrados";
    tabs.forEach(button => button.setAttribute("aria-pressed", String(button.dataset.family === family)));
  }
  function resetLimit() { limit = 12; update(); }
  search.addEventListener("input", resetLimit);
  area.addEventListener("change", resetLimit);
  tabs.forEach(button => button.addEventListener("click", () => {
    family = button.dataset.family; updateAreas(); resetLimit();
  }));
  more.addEventListener("click", () => { limit += 12; update(); });
  document.getElementById("reset-filters").addEventListener("click", () => {
    search.value = ""; family = "all"; updateAreas(); area.value = "all"; resetLimit(); search.focus();
  });
  updateAreas(); update();
  // Align deep links after the initial catalog has hidden its extra cards.
  if (window.location.hash) {
    requestAnimationFrame(() => {
      document.getElementById(window.location.hash.slice(1))?.scrollIntoView({block: "start", behavior: "instant"});
    });
  }
})();
