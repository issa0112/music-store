document.addEventListener('DOMContentLoaded', function () {

    // --- RÉFÉRENCES AUX ÉLÉMENTS ---
    const openLoginFormButton = document.getElementById('openLoginFormButton');
    const openLoginProfilButton = document.getElementById('openLoginProfilButton');
    const popupLoginForm = document.getElementById('popupLoginForm');
    const popupLoginProfil = document.getElementById('popupLoginProfil');
    const popupSignupForm = document.getElementById('popupSignupForm');
    const openSignupFormLink = document.getElementById('openSignupFormLink');
    const openLoginFormLink = document.getElementById('openLoginFormLink');
    const overlay = document.getElementById('overlay');

    // --- GESTION DES POPUPS ---
    function openForm(form) {
        form.classList.add('show');
        overlay.classList.add('show');
    }

    function closeForms() {
        popupLoginForm?.classList.remove('show');
        popupSignupForm?.classList.remove('show');
        popupLoginProfil?.classList.remove('show');
        overlay?.classList.remove('show');
    }

    if (openLoginFormButton) {
        openLoginFormButton.addEventListener('click', function () {
            closeForms();
            openForm(popupLoginForm);
        });
    }

    if (openLoginProfilButton) {
        openLoginProfilButton.addEventListener('click', function () {
            closeForms();
            openForm(popupLoginProfil);
        });
    }

    if (openSignupFormLink) {
        openSignupFormLink.addEventListener('click', function (event) {
            event.preventDefault();
            closeForms();
            openForm(popupSignupForm);
        });
    }

    if (openLoginFormLink) {
        openLoginFormLink.addEventListener('click', function (event) {
            event.preventDefault();
            closeForms();
            openForm(popupLoginForm);
        });
    }

    overlay?.addEventListener('click', closeForms);

    // --- BARRE DE RECHERCHE ---
    document.querySelectorAll('.search-option').forEach(function (button) {
        button.addEventListener('click', function () {
            document.querySelectorAll('.search-option').forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');
            document.getElementById('search-type').value = this.getAttribute('data-type');
        });
    });

    // --- TOGGLE SEARCH INPUT ON MOBILE ---
    const searchToggle = document.getElementById('search-toggle');
    const searchInput = document.getElementById('query');
    if (searchToggle && searchInput) {
        searchToggle.addEventListener('click', function () {
            searchInput.classList.toggle('show');
            searchInput.focus(); // Focus on the input when shown
        });
    }
    if (searchInput) {
        searchInput.addEventListener('keydown', function (event) {
            if (event.key === 'Enter') {
                const query = this.value;
                const searchUrl = document.getElementById('search-url').getAttribute('data-url');
                const searchType = document.getElementById('search-type').value;

                if (query) {
                    window.location.href = `${searchUrl}?q=${encodeURIComponent(query)}&type=${encodeURIComponent(searchType)}`;
                }
            }
        });
    }

    // --- DÉFILEMENT HORIZONTAL DES ARTISTES ---
    const artistContainer = document.getElementById('artistContainer');
    const scrollAmount = 300;

    window.scrollLeft = function () {
        artistContainer?.scrollBy({ top: 0, left: -scrollAmount, behavior: 'smooth' });
    };

    window.scrollRight = function () {
        artistContainer?.scrollBy({ top: 0, left: scrollAmount, behavior: 'smooth' });
    };

    // --- MISE À JOUR DU COMPTEUR DE VIDÉO ---
    window.videoPlay = function (video_id) {
        fetch(`/store/video/play/${video_id}/`)
            .then(response => response.json())
            .then(data => {
                console.log('Compteur de lecture mis à jour :', data.play_count);
            })
            .catch(error => {
                console.error('Erreur lors de la mise à jour du compteur de lecture:', error);
            });
    };

    // --- SUPPRESSION DES CLASSES SKELETON ---
    window.removeSkeleton = function (videoElement) {
        videoElement.classList.remove('skeleton');
    };

});


document.addEventListener('DOMContentLoaded', function() {
    const popularSwiper = new Swiper(".popular-swiper", {
        slidesPerView: 4,        // 4 artistes visibles
        spaceBetween: 30,        // espace entre chaque artiste
        navigation: {
            nextEl: ".popular-artists .swiper-button-next",
            prevEl: ".popular-artists .swiper-button-prev",
        },
        loop: false,             // boucle infinie désactivée
        freeMode: true,          // <<< active la glissade libre
        grabCursor: true,        // change le curseur pour indiquer qu'on peut glisser
        breakpoints: {
            0:   { slidesPerView: 1, spaceBetween: 15 },
            480: { slidesPerView: 1, spaceBetween: 20 },
            768: { slidesPerView: 3, spaceBetween: 25 },
            992: { slidesPerView: 4, spaceBetween: 30 }
        }
    });
});


const toggleBtn = document.querySelector(".menu-toggle");
const navMenu  = document.querySelector(".nav-menu");

toggleBtn.addEventListener("click", () => {
    navMenu.classList.toggle("active");
});
