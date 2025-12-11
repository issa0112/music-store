
document.addEventListener('DOMContentLoaded', function () {
  // === SLIDER ARTISTES ===
  const artistContainer = document.getElementById('artistContainer');
  const scrollAmount = 300;

  window.scrollLeft = function () {
    artistContainer?.scrollBy({ left: -scrollAmount, behavior: 'smooth' });
  };

  window.scrollRight = function () {
    artistContainer?.scrollBy({ left: scrollAmount, behavior: 'smooth' });
  };

  // === FADE-IN AU SCROLL ===
  const faders = document.querySelectorAll('.fade-in-scroll');

  const appearOptions = {
    threshold: 0.1,
    rootMargin: "0px 0px -50px 0px"
  };

  const appearOnScroll = new IntersectionObserver(function(entries, observer) {
    entries.forEach(entry => {
      if (!entry.isIntersecting) return;
      entry.target.classList.add('visible');
      observer.unobserve(entry.target);
    });
  }, appearOptions);

  faders.forEach(fader => {
    appearOnScroll.observe(fader);
  });
});

