(function () {
  const stages = document.querySelectorAll("[data-auth-stage]");

  function syncHeight(stage, activePanel) {
    if (!stage || !activePanel) {
      return;
    }

    const host = stage.querySelector(".auth-panels");
    if (!host) {
      return;
    }

    window.requestAnimationFrame(function () {
      host.style.height = activePanel.offsetHeight + "px";
    });
  }

  function activateStage(stage, target) {
    stage.classList.remove("show-login", "show-signup", "show-forgot");
    stage.classList.add("show-" + target);

    const buttons = stage.querySelectorAll("[data-auth-switch]");
    buttons.forEach(function (button) {
      button.classList.toggle("active-btn", button.getAttribute("data-auth-switch") === target);
    });

    const activePanel = stage.querySelector('[data-auth-panel="' + target + '"]');
    if (activePanel) {
      syncHeight(stage, activePanel);
      const focusTarget = activePanel.querySelector("input, select, textarea");
      window.setTimeout(function () {
        if (focusTarget) {
          focusTarget.focus();
        }
      }, 180);
    }
  }

  window.setAuthPanel = function (target, scope) {
    const container = scope || document;
    const stage = container.querySelector("[data-auth-stage]");
    if (!stage) {
      return;
    }
    activateStage(stage, target || "login");
  };

  stages.forEach(function (stage) {
    const defaultPanel = document.body.getAttribute("data-auth-default") || "login";
    activateStage(stage, defaultPanel);

    stage.querySelectorAll("[data-auth-switch]").forEach(function (button) {
      button.addEventListener("click", function () {
        activateStage(stage, button.getAttribute("data-auth-switch"));
      });
    });

    if ("ResizeObserver" in window) {
      const observer = new ResizeObserver(function () {
        const activeTarget = stage.classList.contains("show-signup")
          ? "signup"
          : stage.classList.contains("show-forgot")
            ? "forgot"
            : "login";
        const activePanel = stage.querySelector('[data-auth-panel="' + activeTarget + '"]');
        syncHeight(stage, activePanel);
      });

      stage.querySelectorAll("[data-auth-panel]").forEach(function (panel) {
        observer.observe(panel);
      });
    }
  });
})();
