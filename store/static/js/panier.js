// =====================================================
// FONCTIONS GLOBALES
// =====================================================

// Affiche la section Stripe ou Orange Money
function showSection(type) {
  const stripeSection = document.getElementById("section-stripe");
  const orangeSection = document.getElementById("section-orange");

  if (stripeSection) stripeSection.style.display = type === "stripe" ? "block" : "none";
  if (orangeSection) orangeSection.style.display = type === "orange" ? "block" : "none";
}

// Paiement mobile (Orange Money)
function payMobileMoney(operateur) {
  const input = document.querySelector(`#section-${operateur} input[name="${operateur}_numero"]`);
  if (!input || !input.value) {
    alert("Veuillez entrer votre numéro de téléphone");
    return;
  }
  window.location.href = `/paiement_mobile/${operateur}/?numero=` + encodeURIComponent(input.value);
}

// =====================================================
// DOMContentLoaded
// =====================================================
document.addEventListener("DOMContentLoaded", () => {
  const config = window.PAYMENT_CONFIG || null;

  // ===== Menu mobile =====
  const toggle = document.querySelector(".menu-toggle");
  const menu = document.querySelector(".nav-menu");
  if (toggle && menu) {
    toggle.addEventListener("click", () => menu.classList.toggle("active"));
  }

  // ===== Boutons Stripe / Orange =====
  const stripeBtn = document.getElementById("btn-stripe");
  const orangeBtn = document.getElementById("btn-orange");
  stripeBtn?.addEventListener("click", () => showSection("stripe"));
  orangeBtn?.addEventListener("click", () => showSection("orange"));

  const payOrangeBtn = document.getElementById("pay-orange");
  payOrangeBtn?.addEventListener("click", () => payMobileMoney("orange"));

  // ===== Stripe =====
  if (config && window.Stripe) {
    const stripe = Stripe(config.stripePublicKey);
    let cardElement;

    const stripeForm = document.getElementById("stripe-payment-form");
    const submitPayment = document.getElementById("submit-payment");
    const cardErrors = document.getElementById("card-errors");

    if (stripeForm) {
      const elements = stripe.elements();
      cardElement = elements.create("card");
      cardElement.mount("#card-element");

      cardElement.on("change", (event) => {
        if (cardErrors) cardErrors.textContent = event.error ? event.error.message : "";
      });
    }

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

  // ===== PayPal =====
  if (config && window.paypal) {
    const container = document.getElementById("paypal-button-container");
    if (container) {
      paypal.Buttons({
        createOrder: (data, actions) => actions.order.create({
          purchase_units: [{ amount: { value: config.totalGeneral } }],
        }),
        onApprove: (data, actions) => actions.order.capture().then(() => window.location.reload()),
      }).render("#paypal-button-container");
    }
  }

  // ===== Retirer un album du panier =====
  const csrftoken = getCookie("csrftoken");
  document.querySelectorAll(".retirer-btn").forEach((btn) => {
    btn.addEventListener("click", async (e) => {
      e.preventDefault();
      const albumId = btn.dataset.id;
      if (!albumId || !confirm("Retirer cet album du panier ?")) return;
      btn.disabled = true;

      try {
        const response = await fetch(`/panier/retirer/${albumId}/`, {
          method: "POST",
          credentials: "same-origin",
          headers: { "X-CSRFToken": csrftoken, "Accept": "application/json" },
        });

        if (!response.ok) throw new Error("Erreur serveur " + response.status);
        const data = await response.json();

        if (data.success) {
          btn.closest("tr")?.remove();
          const totalEl = document.querySelector(".total-panier h3");
          if (totalEl) totalEl.textContent = data.total ? `Total général : ${data.total}` : totalEl.innerHTML;
          const tbody = document.querySelector(".table-panier tbody");
          const hasRows = tbody && tbody.querySelectorAll("tr").length > 0;
          document.getElementById("cart-content")?.style.setProperty("display", hasRows ? "block" : "none");
          document.getElementById("empty-cart")?.style.setProperty("display", hasRows ? "none" : "block");
          window.updateCartCount?.();
        } else {
          alert(data.error || "Erreur lors de la suppression");
        }
      } catch (err) {
        console.error(err);
        alert("Erreur réseau");
      } finally {
        btn.disabled = false;
      }
    });
  });

  // ===== CSRF =====
  function getCookie(name) {
    let cookieValue = null;
    document.cookie.split(";").forEach((cookie) => {
      cookie = cookie.trim();
      if (cookie.startsWith(name + "=")) cookieValue = decodeURIComponent(cookie.slice(name.length + 1));
    });
    return cookieValue;
  }
});
