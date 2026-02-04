document.addEventListener("DOMContentLoaded", function () {
    // Si le handler AJAX principal (menu.js) est deja initialise, on ne duplique pas.
    if (window._menuInitialized) return;

    const loginForm = document.getElementById("loginForm");
    const loginMessagesDiv = document.getElementById("loginMessages");
    const loginFields = document.getElementById("loginFields");

    if (!loginForm) return;

    // Utiliser l'action du form (pas de data-url requis)
    const actionUrl = loginForm.getAttribute("action");
    if (!actionUrl) return;

    loginForm.addEventListener("submit", function (e) {
        e.preventDefault();

        const formData = new FormData(loginForm);

        fetch(actionUrl, {
            method: "POST",
            body: formData,
            credentials: "same-origin",
            redirect: "manual",
            headers: {
                "X-Requested-With": "XMLHttpRequest"
            }
        })
        .then(async response => {
            // Si redirection, on recharge
            if (response.redirected || response.type === "opaqueredirect") {
                location.reload();
                return;
            }

            let data = {};
            try {
                data = await response.json();
            } catch {
                // Reponse non JSON -> rien a afficher
            }

            if (data.success) {
                loginMessagesDiv.innerHTML = `<p class="success-message">${data.message}</p>`;
                if (loginFields) loginFields.style.display = "none";
                setTimeout(() => {
                    location.reload();
                }, 1000);
            } else if (data.message) {
                loginMessagesDiv.innerHTML = `<p class="error-message">${data.message}</p>`;
            }
        })
        .catch(error => {
            loginMessagesDiv.innerHTML = `<p class="error-message">Erreur reseau ou serveur.</p>`;
            console.error("Erreur :", error);
        });
    });
});
