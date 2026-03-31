(function () {
  const shell = document.querySelector("[data-lamp-shell]");
  if (!shell) {
    return;
  }

  const body = document.body;
  const toggle = shell.querySelector("[data-lamp-toggle]");
  const panel = shell.querySelector("[data-login-panel]");
  const storageKey = "elearning-lamp-light-on";
  let isLightOn = false;

  function playClickSound() {
    const AudioContextClass = window.AudioContext || window.webkitAudioContext;
    if (!AudioContextClass) {
      return;
    }

    try {
      const context = new AudioContextClass();
      const oscillator = context.createOscillator();
      const gain = context.createGain();
      oscillator.type = "triangle";
      oscillator.frequency.setValueAtTime(420, context.currentTime);
      oscillator.frequency.exponentialRampToValueAtTime(180, context.currentTime + 0.08);
      gain.gain.setValueAtTime(0.0001, context.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.035, context.currentTime + 0.01);
      gain.gain.exponentialRampToValueAtTime(0.0001, context.currentTime + 0.12);
      oscillator.connect(gain);
      gain.connect(context.destination);
      oscillator.start();
      oscillator.stop(context.currentTime + 0.13);
      oscillator.onended = function () {
        context.close().catch(function () {});
      };
    } catch (error) {
      console.debug("Lamp click sound skipped.", error);
    }
  }

  function persistState() {
    try {
      localStorage.setItem(storageKey, isLightOn ? "1" : "0");
    } catch (error) {
      console.debug("Lamp state persistence unavailable.", error);
    }
  }

  function updateUi(shouldFocusPanel) {
    body.classList.add("lamp-enabled");
    body.classList.toggle("lamp-on", isLightOn);
    panel.classList.toggle("is-visible", isLightOn);
    panel.setAttribute("aria-hidden", String(!isLightOn));
    toggle.setAttribute("aria-expanded", String(isLightOn));

    if (isLightOn && shouldFocusPanel) {
      const firstInput = panel.querySelector("input, button, a");
      if (firstInput) {
        window.setTimeout(function () {
          firstInput.focus();
        }, 180);
      }
    }

    persistState();
  }

  function animateCord() {
    toggle.classList.remove("is-pulling");
    window.requestAnimationFrame(function () {
      toggle.classList.add("is-pulling");
      window.setTimeout(function () {
        toggle.classList.remove("is-pulling");
      }, 260);
    });
  }

  function toggleLamp() {
    isLightOn = !isLightOn;
    animateCord();
    playClickSound();
    updateUi(true);
  }

  function restoreState() {
    try {
      isLightOn = localStorage.getItem(storageKey) === "1";
    } catch (error) {
      isLightOn = false;
    }
    updateUi(false);
  }

  toggle.addEventListener("click", toggleLamp);
  toggle.addEventListener("keydown", function (event) {
    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      toggleLamp();
    }
  });

  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape" && isLightOn) {
      isLightOn = false;
      updateUi(false);
    }
  });

  restoreState();
})();
