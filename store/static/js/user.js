// Récupère le cookie CSRF (obligatoire pour les requêtes POST)
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const trimmed = cookie.trim();
            if (trimmed.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(trimmed.slice(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Connexion utilisateur
document.getElementById('loginForm')?.addEventListener('submit', function(event) {
    event.preventDefault();
    
    const formData = new FormData(this);
    
    fetch("/connexion_compte/", {
        method: "POST",
        body: formData,
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            closeForms(); // si tu as une fonction pour fermer le popup
            location.reload();
        } else {
            alert(data.message);
        }
    });
});

// Inscription utilisateur
document.getElementById('registerForm')?.addEventListener('submit', function(event) {
    event.preventDefault();
    
    const formData = new FormData(this);
    
    fetch("/creation_compte/", {
        method: "POST",
        body: formData,
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert(data.message);
            closeForms();
            document.getElementById('loginPopup').style.display = 'block';
        } else {
            alert(data.message);
        }
    });
});

// Déconnexion
document.getElementById('logoutButton')?.addEventListener('click', function(event) {
    event.preventDefault();

    fetch("/deconnexion_compte/", {
        method: "POST",
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload();
        } else {
            alert('Erreur lors de la déconnexion.');
        }
    });
});
// if (data.success) {
//     closeForms();
//     window.location.href = "/";  // ou "/homepage/" selon ta route d’accueil
// }

document.getElementById("logoutForm")?.addEventListener("submit", function () {
    this.querySelector("button[type='submit']").disabled = true;
});
