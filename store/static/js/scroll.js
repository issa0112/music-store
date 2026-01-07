// =====================================================
// SCROLL / ANIMATIONS — compatible AJAX
// =====================================================
window.initScroll = function () {
  console.log("🟢 initScroll");

  // ===============================
  // FADE-IN AU SCROLL
  // ===============================
  document.querySelectorAll(".fade-in-scroll").forEach(el => {
    // Évite double observer
    if (el.dataset.fadeInit) return;
    el.dataset.fadeInit = "true";

    el.classList.remove("visible");

    const observer = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add("visible");
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.1 });

    observer.observe(el);
  });

  // ===============================
  // SWIPER (popular artists)
  // ===============================
  if (typeof Swiper === "undefined") {
    console.error("❌ Swiper non chargé");
    return;
  }

  const swiperEl = document.querySelector(".popular-swiper");
  if (!swiperEl) {
    console.warn("⚠️ .popular-swiper introuvable");
    return;
  }

  // Détruire proprement si déjà initialisé
  if (swiperEl.swiper) {
    swiperEl.swiper.destroy(true, true);
    swiperEl.swiper = null;
    console.log("🔁 Swiper détruit");
  }

  // Initialisation
  swiperEl.swiper = new Swiper(swiperEl, {
    slidesPerView: 4,
    spaceBetween: 30,
    grabCursor: true,
    navigation: {
      nextEl: ".popular-artists .swiper-button-next",
      prevEl: ".popular-artists .swiper-button-prev",
    },
    breakpoints: {
      0:   { slidesPerView: 1 },
      768: { slidesPerView: 3 },
      992: { slidesPerView: 4 },
    },
  });

  console.log("✅ Swiper initialisé");
};
