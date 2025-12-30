document.addEventListener("DOMContentLoaded", () => {
  // =====================================================
  // CONFIG DJANGO (optionnelle selon la page)
  // =====================================================
  const config = window.PAYMENT_CONFIG || null;

  // =====================================================
  // MENU MOBILE (safe pour toutes les pages)
  // =====================================================
  const toggle = document.querySelector(".menu-toggle");
  const menu = document.querySelector(".nav-menu");

  if (toggle && menu) {
    toggle.addEventListener("click", () => {
      menu.classList.toggle("active");
    });
  }

  // =====================================================
  // AFFICHAGE DES SECTIONS (utilisé par onclick HTML)
  // =====================================================
  window.showSection = function (type) {
    const carte = document.getElementById("section-carte");
    const mobile = document.getElementById("section-mobile");

    if (carte) carte.style.display = type === "carte" ? "block" : "none";
    if (mobile) mobile.style.display = type === "mobile" ? "block" : "none";
  };

  window.showMoneyForm = function (type) {
    ["orange", "moov", "wave"].forEach((t) => {
      const form = document.getElementById("form-" + t);
      if (form) {
        form.style.display = t === type ? "block" : "none";
      }
    });
  };

  window.payMobileMoney = function (operateur) {
    const input = document.querySelector(`input[name="${operateur}_numero"]`);
    if (!input || !input.value) {
      alert("Veuillez entrer votre numéro de téléphone");
      return;
    }

    window.location.href =
      `/paiement_mobile/${operateur}/?numero=` +
      encodeURIComponent(input.value);
  };

  // =====================================================
  // STRIPE (uniquement si présent sur la page)
  // =====================================================
  if (config && window.Stripe) {
    const stripe = Stripe(config.stripePublicKey);
    let cardElement;

    const stripeButton = document.getElementById("stripe-button");
    const stripeForm = document.getElementById("stripe-payment-form");
    const submitPayment = document.getElementById("submit-payment");
    const cardErrors = document.getElementById("card-errors");

    stripeButton?.addEventListener("click", () => {
      if (!stripeForm) return;

      stripeForm.style.display = "block";

      if (!cardElement) {
        const elements = stripe.elements();
        cardElement = elements.create("card");
        cardElement.mount("#card-element");

        cardElement.on("change", (event) => {
          if (cardErrors) {
            cardErrors.textContent = event.error ? event.error.message : "";
          }
        });
      }
    });

    document.addEventListener("click", (event) => {
      if (
        stripeForm &&
        stripeButton &&
        stripeForm.style.display === "block" &&
        !stripeForm.contains(event.target) &&
        !stripeButton.contains(event.target)
      ) {
        stripeForm.style.display = "none";
      }
    });

    submitPayment?.addEventListener("click", async (e) => {
      e.preventDefault();

      if (!cardElement) return;

      const { error, paymentMethod } = await stripe.createPaymentMethod({
        type: "card",
        card: cardElement,
      });

      if (error) {
        if (cardErrors) cardErrors.textContent = error.message;
        return;
      }

      const response = await fetch(config.createPaymentIntentUrl, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ payment_method_id: paymentMethod.id }),
      });

      const data = await response.json();

      if (data.error) {
        if (cardErrors) cardErrors.textContent = data.error;
        return;
      }

      const { error: confirmError } = await stripe.confirmCardPayment(
        data.client_secret,
        { payment_method: paymentMethod.id }
      );

      if (confirmError) {
        if (cardErrors) cardErrors.textContent = confirmError.message;
      } else {
        window.location.href = config.redirectSuccessUrl;
      }
    });
  }

  // =====================================================
  // PAYPAL (safe)
  // =====================================================
  if (config && window.paypal) {
    const container = document.getElementById("paypal-button-container");
    if (container) {
      paypal
        .Buttons({
          createOrder: (data, actions) => {
            return actions.order.create({
              purchase_units: [
                { amount: { value: config.totalGeneral } },
              ],
            });
          },
          onApprove: (data, actions) => {
            return actions.order.capture().then(() => {
              window.location.reload();
            });
          },
        })
        .render("#paypal-button-container");
    }
  }

  // =====================================================
  // PANIER - RETIRER UN ALBUM (AJAX)
  // =====================================================
  const csrftoken = getCookie("csrftoken");

  document.querySelectorAll(".retirer-btn").forEach((btn) => {
    btn.addEventListener("click", async (e) => {
      e.preventDefault();
      if (!confirm("Retirer cet album du panier ?")) return;

      const albumId = btn.dataset.id;

      try {
        const response = await fetch(`/panier/retirer/${albumId}/`, {
          method: "POST",
          headers: { "X-CSRFToken": csrftoken },
        });

        const data = await response.json();

        if (data.success) {
          btn.closest("tr")?.remove();

          const tbody = document.querySelector(".table-panier tbody");
          if (!tbody || tbody.children.length === 0) {
            document.getElementById("cart-content")?.style.setProperty("display", "none");
            document.getElementById("empty-cart")?.style.setProperty("display", "block");
          } else {
            const total = document.querySelector(".total-panier h3");
            if (total) total.textContent = `Total général : ${data.total}`;
          }

          window.updateCartCount?.();
        } else {
          alert(data.error || "Erreur lors de la suppression");
        }
      } catch (err) {
        console.error(err);
        alert("Erreur réseau");
      }
    });
  });

  // =====================================================
  // CSRF
  // =====================================================
  function getCookie(name) {
    let cookieValue = null;
    document.cookie.split(";").forEach((cookie) => {
      cookie = cookie.trim();
      if (cookie.startsWith(name + "=")) {
        cookieValue = decodeURIComponent(cookie.slice(name.length + 1));
      }
    });
    return cookieValue;
  }
});

