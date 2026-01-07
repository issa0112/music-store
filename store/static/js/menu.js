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

  function openForm(form) {
    if (!form) return;
    form.classList.add("show");
    overlay?.classList.add("show");
  }

  function closeForms() {
    popupLoginForm?.classList.remove("show");
    popupSignupForm?.classList.remove("show");
    popupLoginProfil?.classList.remove("show");
    overlay?.classList.remove("show");
  }

  document.addEventListener("click", e => {
    const btnLogin = e.target.closest("#openLoginFormButton");
    const btnProfil = e.target.closest("#openLoginProfilButton");
    const btnSignup = e.target.closest("#openSignupFormLink");
    const btnLoginLink = e.target.closest("#openLoginFormLink");

    if (btnLogin) {
      e.preventDefault();
      closeForms();
      openForm(popupLoginForm);
    }

    if (btnProfil) {
      e.preventDefault();
      closeForms();
      openForm(popupLoginProfil);
    }

    if (btnSignup) {
      e.preventDefault();
      closeForms();
      openForm(popupSignupForm);
    }

    if (btnLoginLink) {
      e.preventDefault();
      closeForms();
      openForm(popupLoginForm);
    }
  });

  overlay?.addEventListener("click", closeForms);

  // ==========================
  // SEARCH OPTIONS
  // ==========================
  document.addEventListener("click", e => {
    const option = e.target.closest(".search-option");
    if (!option) return;

    document.querySelectorAll(".search-option")
      .forEach(btn => btn.classList.remove("active"));

    option.classList.add("active");
    document.getElementById("search-type").value = option.dataset.type;
  });

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

    // 👉 navigation AJAX
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
