const toggle = document.querySelector(".menu-toggle");
const navigation = document.getElementById("navegacao");
const mobile = window.matchMedia("(max-width: 760px)");

if (toggle && navigation) {
  // Without JavaScript, all navigation links remain visible.
  toggle.hidden = false;

  function closeMenu({ restoreFocus = false } = {}) {
    toggle.setAttribute("aria-expanded", "false");
    navigation.hidden = mobile.matches;
    if (restoreFocus) toggle.focus();
  }

  function syncViewport() {
    const focusWasInNavigation = navigation.contains(document.activeElement);
    closeMenu({ restoreFocus: mobile.matches && focusWasInNavigation });
  }

  toggle.addEventListener("click", () => {
    const opening = toggle.getAttribute("aria-expanded") !== "true";
    toggle.setAttribute("aria-expanded", String(opening));
    navigation.hidden = !opening;
  });

  navigation.addEventListener("click", (event) => {
    const link = event.target.closest("a");
    if (!link) return;
    closeMenu();
    const target = link.hash && link.hash.length > 1
      ? document.getElementById(decodeURIComponent(link.hash.slice(1)))
      : null;
    if (target) {
      target.setAttribute("tabindex", "-1");
      target.focus({ preventScroll: true });
    }
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && mobile.matches && !navigation.hidden) {
      closeMenu({ restoreFocus: true });
    }
  });

  document.addEventListener("click", (event) => {
    if (
      mobile.matches &&
      !navigation.hidden &&
      !navigation.contains(event.target) &&
      !toggle.contains(event.target)
    ) {
      closeMenu();
    }
  });

  navigation.addEventListener("focusout", (event) => {
    if (
      mobile.matches &&
      !navigation.contains(event.relatedTarget) &&
      event.relatedTarget !== toggle
    )
      closeMenu();
  });

  mobile.addEventListener("change", syncViewport);
  syncViewport();
}

const viewer = document.getElementById("image-viewer");
if (viewer && typeof viewer.showModal === "function") {
  const title = document.getElementById("viewer-title");
  const caption = document.getElementById("viewer-caption");
  const imageContainer = viewer.querySelector(".viewer-image");
  const original = viewer.querySelector(".viewer-original");

  document.querySelectorAll(".gallery-link").forEach((link) => {
    link.setAttribute("aria-haspopup", "dialog");
    link.addEventListener("click", (event) => {
      // Preserve the browser's open-in-new-tab/window gestures.
      if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey)
        return;
      event.preventDefault();
      const image = new Image();
      image.src = link.href;
      image.alt = link.querySelector("img").alt;
      imageContainer.replaceChildren(image);
      title.textContent = link.dataset.title;
      caption.textContent = link.dataset.caption;
      original.href = link.href;
      viewer.showModal();
    });
  });

  viewer
    .querySelector(".viewer-close")
    .addEventListener("click", () => viewer.close());
  viewer.addEventListener("click", (event) => {
    if (event.target !== viewer) return;
    const rect = viewer.getBoundingClientRect();
    if (
      event.clientX < rect.left ||
      event.clientX > rect.right ||
      event.clientY < rect.top ||
      event.clientY > rect.bottom
    )
      viewer.close();
  });
  viewer.addEventListener("keydown", (event) => {
    if (event.key !== "Tab") return;
    const controls = viewer.querySelectorAll("button, a[href]");
    const first = controls[0];
    const last = controls[controls.length - 1];
    if (event.shiftKey && document.activeElement === first) {
      event.preventDefault();
      last.focus();
    } else if (!event.shiftKey && document.activeElement === last) {
      event.preventDefault();
      first.focus();
    }
  });
  // Native <dialog> handles Escape, initial focus and focus restoration.
}
