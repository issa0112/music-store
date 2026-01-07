// ==============================
// AUTH (SIGNUP AJAX)
// ==============================

let authInitialized = false;

function initAuth() {
  if (authInitialized) return;
  authInitialized = true;

  document.addEventListener("submit", e => {
    const form = e.target.closest("#signupForm");
    if (!form) return;

    e.preventDefault();

    const messages = document.getElementById("signupMessages");
    const fields = document.getElementById("signupFields");

    const formData = new FormData(form);

    fetch(form.action, {
      method: "POST",
      body: formData,
      credentials: "same-origin",
      headers: {
        "X-Requested-With": "XMLHttpRequest"
      }
    })
    .then(r => r.json())
    .then(data => {
      if (data.success) {
        messages.innerHTML = `<p class="success-message">${data.message}</p>`;
        fields.style.display = "none";

        setTimeout(() => {
          document.getElementById("popupSignupForm")?.classList.remove("show");
          document.getElementById("popupLoginForm")?.classList.add("show");
        }, 1200);
      } else {
        messages.innerHTML = `<p class="error-message">${data.message}</p>`;
      }
    })
    .catch(() => {
      messages.innerHTML = `<p class="error-message">Erreur technique.</p>`;
    });
  });
}
