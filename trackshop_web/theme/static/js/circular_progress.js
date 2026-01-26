function animateCircle(circle, duration = 1000) {
    const value = Number(circle.dataset.progress);
    const radius = circle.r.baseVal.value;
    const circumference = 2 * Math.PI * radius;

    // Cercle complet
    circle.style.strokeDasharray = circumference;
    circle.style.strokeDashoffset = circumference;

    // Animation horlogique
    requestAnimationFrame(() => {
        const offset = circumference * (1 - value / 100); // réduit dashoffset pour avancer
        circle.style.transition = `stroke-dashoffset ${duration}ms ease-out`;
        circle.style.strokeDashoffset = offset;
    });

    // Compteur central
    const counter = circle.parentElement.querySelector("[data-counter]");
    if (counter) animateCounter(counter, duration);
}

// Compteur commun
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

// Initialisation
document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll(".progress-circle").forEach(circle => animateCircle(circle));
});
