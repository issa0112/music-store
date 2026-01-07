(function () {
  let persistentReady = false;

  function safeInit(fn, name) {
    if (typeof fn === "function") {
      fn();
    } else {
      // utile en debug, silencieux en prod si tu veux
      console.warn(`${name} non défini`);
    }
  }

  function initPersistent() {
    if (persistentReady) return;

    safeInit(window.initMenu, "initMenu");
    safeInit(window.initPlayer, "initPlayer");
    safeInit(window.initAuth, "initAuth");
    safeInit(window.initLibrary, "initLibrary");

    persistentReady = true;
  }

  function initDynamic() {
    safeInit(window.initSearch, "initSearch");
    safeInit(window.initCart, "initCart");
    safeInit(window.initScroll, "initScroll");
    safeInit(window.initPopup, "initPopup");
    safeInit(window.initProfil, "initProfil");
    safeInit(window.initVideo, "initVideo");
  }

  window.refreshPage = function () {
    console.log("🔄 refreshPage");
    initPersistent();
    initDynamic();
  };

  window.updateActiveNav = function () {
    const path = location.pathname;
    document.querySelectorAll(".main-nav a, .bottom-nav a").forEach(a => {
      a.classList.remove("active");
      const href = a.getAttribute("href");
      if (href && (href === path || path.startsWith(href))) {
        a.classList.add("active");
      }
    });
  };

  document.addEventListener("DOMContentLoaded", () => {
    refreshPage();
    updateActiveNav();
  });
})();
