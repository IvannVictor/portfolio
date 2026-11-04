// Animações progressivas sem dependências. Sem JS, conteúdo permanece visível.
(() => {
  const motion = window.matchMedia("(prefers-reduced-motion: reduce)");
  if (!("IntersectionObserver" in window) || motion.matches) return;
  const selectors = [
    ".section-heading", ".projects-intro", ".project",
    ".study-divider", ".expertise-grid > *", ".about > *",
    ".career-heading", ".career-timeline li", ".contact-grid > *",
    ".case-journey > div"
  ];
  const elements = [...new Set(document.querySelectorAll(selectors.join(", ")))];
  if (!elements.length) return;
  const observer = new IntersectionObserver((entries) => {
    for (const entry of entries) {
      if (!entry.isIntersecting) continue;
      entry.target.classList.add("is-visible");
      observer.unobserve(entry.target);
    }
  }, { threshold: 0.08, rootMargin: "0px 0px -24px 0px" });
  elements.forEach((element) => {
    // Não anima conteúdo já visível ao abrir a página.
    if (element.getBoundingClientRect().top < window.innerHeight) return;
    element.dataset.reveal = "";
    if (element.matches(".case-journey > div")) {
      const position = [...element.parentElement.children].indexOf(element);
      element.style.setProperty("--reveal-delay", `${position * 80}ms`);
    }
    observer.observe(element);
  });
  document.documentElement.classList.add("reveal-ready");
  const disableReveal = (event) => {
    if (!event.matches) return;
    observer.disconnect();
    elements.forEach((element) => {
      element.classList.add("is-visible");
      element.removeAttribute("data-reveal");
      element.style.removeProperty("--reveal-delay");
    });
    document.documentElement.classList.remove("reveal-ready");
    motion.removeEventListener("change", disableReveal);
  };
  motion.addEventListener("change", disableReveal);
})();
