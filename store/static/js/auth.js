
document.addEventListener("DOMContentLoaded", function () {
    const signupForm = document.getElementById("signupForm");
    const signupMessages = document.getElementById("signupMessages");
    const signupFields = document.getElementById("signupFields");

    signupForm.addEventListener("submit", function (e) {
        e.preventDefault();

        const formData = new FormData(signupForm);

        fetch(signupForm.action, {
        method: "POST",
        body: formData,
        credentials: "same-origin", // important pour CSRF
        headers: {
            "X-Requested-With": "XMLHttpRequest"
        }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
            signupMessages.innerHTML = `<p class='success-message'>${data.message}</p>`;
            signupFields.style.display = "none";

            // Après inscription, afficher le login
            setTimeout(() => {
                document.getElementById("popupSignupForm").style.display = "none";
                document.getElementById("popupLoginForm").style.display = "block";
            }, 1500);
            } else {
            signupMessages.innerHTML = `<p class='error-message'>${data.message}</p>`;
            }
        })
        .catch(error => {
            console.error("Erreur : ", error);
            signupMessages.innerHTML = `<p class='error-message'>Erreur technique. Veuillez réessayer.</p>`;
        });
    });

});