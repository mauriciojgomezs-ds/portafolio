"use strict";
(() => {
  const buttons = [...document.querySelectorAll("[data-report-family]")];
  const groups = [...document.querySelectorAll("[data-report-group]")];
  const info = document.getElementById("report-results");
  buttons.forEach(button => button.addEventListener("click", () => {
    const family = button.dataset.reportFamily;
    let count = 0;
    groups.forEach(group => {
      group.hidden = family !== "all" && group.dataset.reportGroup !== family;
      if (!group.hidden) count += Number(group.dataset.reportCount);
    });
    buttons.forEach(tab => tab.setAttribute("aria-pressed", String(tab === button)));
    info.textContent = `${count} ${count === 1 ? "informe disponible" : "informes disponibles"}`;
  }));
})();
