(function () {
  const modal = document.querySelector("[data-auth-modal]");
  const navToggle = document.querySelector("[data-nav-toggle]");
  const navPanel = document.querySelector("[data-nav-panel]");

  if (navToggle && navPanel) {
    navToggle.addEventListener("click", function () {
      const isOpen = navPanel.classList.toggle("active");
      navToggle.setAttribute("aria-expanded", String(isOpen));
    });
  }

  if (!modal) {
    return;
  }

  const openers = document.querySelectorAll("[data-auth-open]");
  const closers = modal.querySelectorAll("[data-auth-close]");

  function openModal(panelName) {
    modal.classList.add("active");
    modal.setAttribute("aria-hidden", "false");
    document.body.classList.add("ui-modal-open");
    if (typeof window.setAuthPanel === "function") {
      window.setAuthPanel(panelName || "login", modal);
    }
  }

  function closeModal() {
    modal.classList.remove("active");
    modal.setAttribute("aria-hidden", "true");
    document.body.classList.remove("ui-modal-open");
  }

  openers.forEach(function (trigger) {
    trigger.addEventListener("click", function (event) {
      if (trigger.closest(".ui-auth-modal") || trigger.id === "loginBtn" || trigger.id === "signupBtn" || trigger.id === "forgotBtn" || trigger.hasAttribute("data-auth-open")) {
        event.preventDefault();
        openModal(trigger.getAttribute("data-auth-open") || "login");
      }
    });
  });

  closers.forEach(function (closer) {
    closer.addEventListener("click", closeModal);
  });

  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape" && modal.classList.contains("active")) {
      closeModal();
    }
  });
})();
