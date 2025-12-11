document.addEventListener('DOMContentLoaded', function () {

    const openLoginFormButton = document.getElementById('openLoginFormButton');
    const openLoginProfilButton = document.getElementById('openLoginProfilButton');
    const popupLoginForm = document.getElementById('popupLoginForm');
    const popupLoginProfil = document.getElementById('popupLoginProfil');
    const popupSignupForm = document.getElementById('popupSignupForm');
    const openSignupFormLink = document.getElementById('openSignupFormLink');
    const openLoginFormLink = document.getElementById('openLoginFormLink');
    const overlay = document.getElementById('overlay');

    function closeForms() {
        popupLoginForm?.classList.remove('show');
        popupSignupForm?.classList.remove('show');
        popupLoginProfil?.classList.remove('show');
        overlay?.classList.remove('show');
    }

    function openForm(form) {
        closeForms();
        form.classList.add('show');
        overlay.classList.add('show');
    }

    openLoginFormButton?.addEventListener('click', () => openForm(popupLoginForm));
    openLoginProfilButton?.addEventListener('click', () => openForm(popupLoginProfil));

    openSignupFormLink?.addEventListener('click', function (e) {
        e.preventDefault();
        openForm(popupSignupForm);
    });

    openLoginFormLink?.addEventListener('click', function (e) {
        e.preventDefault();
        openForm(popupLoginForm);
    });

    overlay?.addEventListener('click', closeForms);

});
