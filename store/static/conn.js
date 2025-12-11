document.addEventListener("DOMContentLoaded", function () {
    const loginForm = document.getElementById("loginForm");
    const loginMessagesDiv = document.getElementById("loginMessages");
    const loginFields = document.getElementById("loginFields");

    // Récupération de l'URL via l'attribut data-url défini dans le HTML
    const actionUrl = loginForm.dataset.url;

    loginForm.addEventListener("submit", function (e) {
        e.preventDefault();  // Empêche la soumission normale

        const formData = new FormData(loginForm);

        fetch(actionUrl, {
            method: "POST",
            body: formData,
            credentials: "same-origin",
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                loginMessagesDiv.innerHTML = `<p class="success-message">${data.message}</p>`;
                loginFields.style.display = "none";
                setTimeout(() => {
                    location.reload();  // Recharge la page après connexion réussie
                }, 1000);
            } else {
                loginMessagesDiv.innerHTML = `<p class="error-message">${data.message}</p>`;
            }
        })
        .catch(error => {
            loginMessagesDiv.innerHTML = `<p class="error-message">Erreur réseau ou serveur.</p>`;
            console.error("Erreur :", error);
        });
    });
});
