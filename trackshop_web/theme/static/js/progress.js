/* ----------------------------- */
/* Animation compteur commun      */
/* ----------------------------- */
function animateCounter(el, duration = 1000) {
  const target = Number(el.dataset.counter);
  const startTime = performance.now();

  function update(now) {
    const progress = Math.min((now - startTime) / duration, 1);
    const eased = 1 - Math.pow(1 - progress, 3); // easing cubic
    el.textContent = Math.round(eased * target) + "%";

    if (progress < 1) requestAnimationFrame(update);
  }

  requestAnimationFrame(update);
}

/* ----------------------------- */
/* Animation barre linéaire       */
/* ----------------------------- */
function animateLinearProgress(bar, duration = 700) {
  if (!bar) return;

  const target = Number(bar.dataset.progress);
  const color = bar.dataset.color;

  if (color) bar.style.backgroundColor = color;

  bar.style.width = "0%";
  bar.style.transition = `width ${duration}ms ease-out`;

  requestAnimationFrame(() => {
    bar.style.width = target + "%";
  });

  const container = bar.closest(".progress-container");
  if (container) {
    const counter = container.querySelector("[data-counter]");
    if (counter) animateCounter(counter, duration);
  }
}

function initLinearProgress(root = document) {
  root.querySelectorAll(".progress-bar").forEach(bar => {
    animateLinearProgress(bar);
  });
}

/* ----------------------------- */
/* Animation cercle circulaire    */
/* ----------------------------- */
function animateCircle(circle, duration = 1000) {
  if (!circle) return;

  const radius = circle.r.baseVal.value;
  const circumference = 2 * Math.PI * radius;

  // Initialiser sans transition pour garantir le point de départ
  circle.style.strokeDasharray = circumference;
  circle.style.strokeDashoffset = circumference;
  circle.style.transition = "none";

  // Compteur
  const container = circle.closest(".circle-container");
  if (container) {
    const counter = container.querySelector("[data-counter]");
    if (counter) animateCounter(counter, duration);
  }

  // Forcer un "reflow" pour que le navigateur enregistre la valeur initiale
  circle.getBoundingClientRect();

  // Puis appliquer la transition et la valeur finale
  circle.style.transition = `stroke-dashoffset ${duration}ms ease-out`;
  const value = Number(circle.dataset.progress);
  const offset = circumference - (value / 100) * circumference;
  circle.style.strokeDashoffset = offset;
}


function initCircles(root = document) {
  root.querySelectorAll(".progress-circle").forEach(circle => {
    animateCircle(circle);
  });
}

/* ----------------------------- */
/* Initialisation globale         */
/* ----------------------------- */
document.addEventListener("DOMContentLoaded", () => {
  initLinearProgress();
  initCircles();
});

document.body.addEventListener("htmx:afterSwap", e => {
  initLinearProgress(e.target);
  initCircles(e.target);
});
