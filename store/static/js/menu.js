// ==============================
// MENU / AUTH / SEARCH UI
// ==============================

function initMenu() {
  if (window._menuInitialized) return;
  window._menuInitialized = true;

  // ==========================
  // POPUPS AUTH
  // ==========================
  const overlay = document.getElementById("overlay");

  const popupLoginForm = document.getElementById("popupLoginForm");
  const popupSignupForm = document.getElementById("popupSignupForm");
  const popupLoginProfil = document.getElementById("popupLoginProfil");
  const popupForgotPassword = document.getElementById("popupForgotPassword");

  function openForm(form) {
    if (!form) return;
    form.classList.add("show");
    overlay?.classList.add("show");

    // reset login messages
    if (form === popupLoginForm) {
      const loginMessages = document.getElementById("loginMessages");
      if (loginMessages) loginMessages.innerHTML = "";
    }
  }

  function closeForms() {
    popupLoginForm?.classList.remove("show");
    popupSignupForm?.classList.remove("show");
    popupLoginProfil?.classList.remove("show");
    popupForgotPassword?.classList.remove("show");
    overlay?.classList.remove("show");
  }

  // ==========================
  // AUTH EVENTS
  // ==========================
  document.addEventListener("click", e => {
    const btnLogin = e.target.closest("#openLoginFormButton, #openLoginFormButtonMobile");
    const btnProfil = e.target.closest("#openLoginProfilButton");
    const btnSignup = e.target.closest("#openSignupFormLink");
    const btnLoginLink = e.target.closest("#openLoginFormLink");
    const btnForgotPassword = e.target.closest("#openForgotPasswordLink");

    if (btnLogin) { e.preventDefault(); closeForms(); openForm(popupLoginForm); return; }
    if (btnProfil) { e.preventDefault(); closeForms(); openForm(popupLoginProfil); return; }
    if (btnSignup) { e.preventDefault(); closeForms(); openForm(popupSignupForm); return; }
    if (btnForgotPassword) { e.preventDefault(); closeForms(); openForm(popupForgotPassword); return; }
    if (btnLoginLink) { e.preventDefault(); closeForms(); openForm(popupLoginForm); return; }
  });

  overlay?.addEventListener("click", closeForms);

  // ==========================
  // LOGIN AJAX
  // ==========================
// ==========================
// LOGIN AJAX SILENCIEUX
// ==========================
(function() {
  const loginForm = document.getElementById("loginForm");
  const overlay = document.getElementById("overlay");
  const popupLoginForm = document.getElementById("popupLoginForm");

  if (!loginForm) return;

  loginForm.addEventListener("submit", function(e) {
    e.preventDefault();

    const url = loginForm.getAttribute("action");
    const formData = new FormData(loginForm);
    const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]")?.value;

    fetch(url, {
      method: "POST",
      body: formData,
      redirect: "manual",  // pour détecter redirections
      headers: {
        "X-Requested-With": "XMLHttpRequest",
        "X-CSRFToken": csrfToken,
      },
    })
    .then(async res => {
      // Si le serveur redirige, reload la page
      if (res.redirected || res.type === "opaqueredirect") {
        window.location.reload();
        return;
      }

      // Sinon on essaie de parser JSON
      let data = {};
      try {
        data = await res.json();
      } catch {
        // réponse non JSON → on ignore
      }

      // Login réussi → reload
      if (data.success === true) {
        popupLoginForm?.classList.remove("show");
        overlay?.classList.remove("show");
        window.location.reload();  // 1 seule redirection/reload
      }

      // Sinon rien → silencieux
    })
    .catch(() => {
      // erreur réseau/serveur → silencieuse
    });
  });
})();



  // ==========================
  // SEARCH INPUT (AJAX)
  // ==========================
  const searchInput = document.getElementById("query");
  const searchToggle = document.getElementById("search-toggle");
  const searchUrlEl = document.getElementById("search-url");

  searchToggle?.addEventListener("click", () => {
    searchInput?.classList.toggle("show");
    searchInput?.focus();
  });

  searchInput?.addEventListener("keydown", e => {
    if (e.key !== "Enter") return;

    const query = searchInput.value.trim();
    if (!query) return;

    const url = `${searchUrlEl.dataset.url}?q=${encodeURIComponent(query)}&type=${encodeURIComponent(
      document.getElementById("search-type").value
    )}`;

    loadPage(url);
  });

  // ==========================
  // MENU MOBILE
  // ==========================
  document.addEventListener("click", e => {
    const toggleBtn = e.target.closest(".menu-toggle");
    if (!toggleBtn) return;

    document.querySelector(".nav-menu")?.classList.toggle("active");
  });
}
