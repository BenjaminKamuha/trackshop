function animateKpi(el, duration = 900) {
  const target = Number(el.dataset.value);
  const suffix = el.dataset.suffix || "";
  const startTime = performance.now();

  function update(now) {
    const progress = Math.min((now - startTime) / duration, 1);
    const eased = 1 - Math.pow(1 - progress, 3); // ease-out cubic
    const current = Math.round(eased * target);

    el.textContent = current.toLocaleString() + suffix;

    if (progress < 1) requestAnimationFrame(update);
  }

  requestAnimationFrame(update);
}

function initKpis(root = document) {
  root.querySelectorAll(".kpi-counter").forEach(el => {
    // éviter double animation
    if (el.dataset.animated) return;
    el.dataset.animated = "true";

    animateKpi(el);
  });
}

/* Initialisation */
document.addEventListener("DOMContentLoaded", () => {
  initKpis();
});

/* Support HTMX */
document.body.addEventListener("htmx:afterSwap", e => {
  initKpis(e.target);
});
