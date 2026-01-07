// =====================================================
// PANIER / PAIEMENTS — compatible AJAX
// =====================================================
window.initCart = function () {
  console.log("🛒 initCart");

  const config = window.PAYMENT_CONFIG || null;

  // ===============================
  // UTILITAIRES
  // ===============================
  function showSection(type) {
    document.getElementById("section-stripe")
      ?.style.setProperty("display", type === "stripe" ? "block" : "none");

    document.getElementById("section-orange")
      ?.style.setProperty("display", type === "orange" ? "block" : "none");
  }

  function payMobileMoney(operateur) {
    const input = document.querySelector(
      `#section-${operateur} input[name="${operateur}_numero"]`
    );
    if (!input || !input.value) {
      alert("Veuillez entrer votre numéro de téléphone");
      return;
    }
    window.location.href =
      `/paiement_mobile/${operateur}/?numero=${encodeURIComponent(input.value)}`;
  }

  // ===============================
  // MENU MOBILE
  // ===============================
  // const toggle = document.querySelector(".menu-toggle");
  // const menu = document.querySelector(".nav-menu");
  // toggle && menu && toggle.addEventListener("click", () =>
  //   menu.classList.toggle("active")
  // );

  // ===============================
  // BOUTONS STRIPE / ORANGE
  // ===============================
  document.getElementById("btn-stripe")
    ?.addEventListener("click", () => showSection("stripe"));

  document.getElementById("btn-orange")
    ?.addEventListener("click", () => showSection("orange"));

  document.getElementById("pay-orange")
    ?.addEventListener("click", () => payMobileMoney("orange"));

  // ===============================
  // STRIPE
  // ===============================
  if (config && window.Stripe) {
    const form = document.getElementById("stripe-payment-form");

    if (form && !form.dataset.initialized) {
      form.dataset.initialized = "true";

      const stripe = Stripe(config.stripePublicKey);
      const elements = stripe.elements();
      const card = elements.create("card");
      card.mount("#card-element");

      const errors = document.getElementById("card-errors");

      card.on("change", e => {
        errors && (errors.textContent = e.error ? e.error.message : "");
      });

      document.getElementById("submit-payment")
        ?.addEventListener("click", async (e) => {
          e.preventDefault();

          const { error, paymentMethod } =
            await stripe.createPaymentMethod({ type: "card", card });

          if (error) {
            errors.textContent = error.message;
            return;
          }

          const res = await fetch(config.createPaymentIntentUrl, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ payment_method_id: paymentMethod.id }),
          });

          const data = await res.json();
          if (data.error) {
            errors.textContent = data.error;
            return;
          }

          const { error: confirmError } =
            await stripe.confirmCardPayment(data.client_secret, {
              payment_method: paymentMethod.id,
            });

          confirmError
            ? (errors.textContent = confirmError.message)
            : (window.location.href = config.redirectSuccessUrl);
        });
    }
  }

  // ===============================
  // PAYPAL
  // ===============================
  if (config && window.paypal) {
    const container = document.getElementById("paypal-button-container");

    if (container && !container.dataset.rendered) {
      container.dataset.rendered = "true";

      paypal.Buttons({
        createOrder: (_, actions) =>
          actions.order.create({
            purchase_units: [{ amount: { value: config.totalGeneral } }],
          }),
        onApprove: (_, actions) =>
          actions.order.capture().then(() => window.location.reload()),
      }).render("#paypal-button-container");
    }
  }
};


// =====================================================
// LISTENER GLOBAL — SUPPRESSION PANIER (UNE SEULE FOIS)
// =====================================================
if (!window.__cartRemoveBound) {
  window.__cartRemoveBound = true;

  document.addEventListener("click", async (e) => {
    const btn = e.target.closest(".retirer-btn");
    if (!btn) return;

    e.preventDefault();

    const albumId = btn.dataset.id;
    if (!albumId || !confirm("Retirer cet album du panier ?")) return;

    btn.disabled = true;

    try {
      const csrftoken = document.cookie
        .split("; ")
        .find(c => c.startsWith("csrftoken="))
        ?.split("=")[1];

      const res = await fetch(`/panier/retirer/${albumId}/`, {
        method: "POST",
        credentials: "same-origin",
        headers: {
          "X-CSRFToken": csrftoken,
          "Accept": "application/json",
        },
      });

      const data = await res.json();
      if (!data.success) throw new Error(data.error);

      // Suppression ligne
      btn.closest("tr")?.remove();

      // Mise à jour total
      const totalEl = document.querySelector(".total-panier h3");
      if (totalEl) {
        totalEl.textContent = `Total général : ${data.total}`;
      }

      // Panier vide / non vide
      const hasRows =
        document.querySelectorAll(".table-panier tbody tr").length > 0;

      document.getElementById("cart-content")
        ?.style.setProperty("display", hasRows ? "block" : "none");

      document.getElementById("empty-cart")
        ?.style.setProperty("display", hasRows ? "none" : "block");

      window.updateCartCount?.();
    } catch (err) {
      console.error(err);
      alert("Erreur lors de la suppression");
    } finally {
      btn.disabled = false;
    }
  });
}
