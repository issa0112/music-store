async function loadPage(url, addToHistory = true) {
  try {
    const res = await fetch(url, {
      headers: { "X-Requested-With": "XMLHttpRequest" }
    });

    const html = await res.text();
    const doc = new DOMParser().parseFromString(html, "text/html");
    const newContent = doc.querySelector("#main-content");

    if (!newContent) {
      window.location.href = url;
      return;
    }

    const main = document.querySelector("#main-content");
    main.innerHTML = newContent.innerHTML;

    console.log("AJAX OK - main-content remplacé");

    // 🔹 Assurer que le footer reste visible, sauf pour panier
    const footer = document.querySelector("footer");
    if (footer) {
      if (url.includes('/panier/')) {
        footer.style.display = "none";
      } else {
        footer.style.display = "block";
      }
    }

    if (addToHistory) history.pushState({}, "", url);

    window.refreshPage?.();
    window.updateActiveNav?.();

  } catch (err) {
    console.error("AJAX ERROR", err);
    window.location.href = url;
  }
}
