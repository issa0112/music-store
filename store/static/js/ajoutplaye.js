addToPlaylistBtn?.addEventListener("click", async (e) => {
  if (typeof userIsLoggedIn === "undefined" || !userIsLoggedIn) {
    showToast("Veuillez vous connecter pour ajouter à une playlist !", "error");
    return;
  }

  const itemId = audio.dataset.trackId || audio.dataset.videoId;
  const itemType = audio.dataset.trackId ? "track" : "video";
  if (!itemId) return;

  // Supprime ancien menu s'il existe
  const oldMenu = document.getElementById("playlist-menu");
  if (oldMenu) oldMenu.remove();

  try {
  const res = await fetch("/playlists/user_playlists/", { credentials: 'same-origin' });
    if (!res.ok) throw new Error("Impossible de récupérer vos playlists.");
    const playlists = await res.json();

    // Crée le menu
    const menu = document.createElement("div");
    menu.id = "playlist-menu";
    menu.style.position = "fixed";
    menu.style.background = "#fff";
    menu.style.border = "1px solid #ccc";
    menu.style.padding = "12px";
    menu.style.boxShadow = "0 4px 10px rgba(0,0,0,0.15)";
    menu.style.borderRadius = "8px";
    menu.style.zIndex = 10000;
    menu.style.minWidth = "220px";
    menu.style.fontFamily = "sans-serif";
    menu.style.maxHeight = "280px";
    menu.style.overflowY = "auto";
    menu.style.transition = "opacity 0.2s ease";
    menu.style.opacity = "0";

    // Titre
    const title = document.createElement("div");
    title.textContent = "Ajouter à une playlist";
    title.style.fontWeight = "bold";
    title.style.marginBottom = "10px";
    title.style.cursor = "move";
    menu.appendChild(title);

    // Liste des playlists
    if (playlists.length > 0) {
      playlists.forEach(pl => {
        const btn = document.createElement("button");
        btn.textContent = pl.name;
        btn.style.display = "block";
        btn.style.width = "100%";
        btn.style.margin = "4px 0";
        btn.style.cursor = "pointer";
        btn.style.padding = "6px 8px";
        btn.style.border = "none";
        btn.style.background = "#f0f0f0";
        btn.style.borderRadius = "4px";
        btn.onmouseover = () => btn.style.background = "#e0e0e0";
        btn.onmouseout = () => btn.style.background = "#f0f0f0";
        btn.onclick = async () => {
          await addToPlaylist(itemType, itemId, pl.id);
          menu.remove();
        };
        menu.appendChild(btn);
      });
    } else {
      const noPl = document.createElement("div");
      noPl.textContent = "Vous n'avez pas encore de playlist.";
      noPl.style.marginBottom = "10px";
      menu.appendChild(noPl);
    }

    // Formulaire de création
    const formDiv = document.createElement("div");
    formDiv.style.marginTop = "10px";
    formDiv.style.display = "flex";
    formDiv.style.gap = "5px";

    const input = document.createElement("input");
    input.type = "text";
    input.placeholder = "Nouvelle playlist";
    input.style.flex = "1";
    input.style.padding = "6px 8px";
    input.style.borderRadius = "4px";
    input.style.border = "1px solid #ccc";

    const saveBtn = document.createElement("button");
    saveBtn.textContent = "Créer";
    saveBtn.style.cursor = "pointer";
    saveBtn.style.padding = "6px 10px";
    saveBtn.style.border = "none";
    saveBtn.style.background = "#00bfff";
    saveBtn.style.color = "#fff";
    saveBtn.style.borderRadius = "4px";
    saveBtn.onmouseover = () => saveBtn.style.background = "#00a3e0";
    saveBtn.onmouseout = () => saveBtn.style.background = "#00bfff";

    saveBtn.onclick = async () => {
      const name = input.value.trim();
      if (!name) return;
      try {
        const res = await fetch("/playlists/create/", {
          method: "POST",
          credentials: 'same-origin',
          headers: {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-CSRFToken": getCookie("csrftoken")
          },
          body: JSON.stringify({ name })
        });
        const data = await res.json().catch(() => null);
        if (res.ok && data && data.status === "success") {
          showToast("Playlist créée !");
          await addToPlaylist(itemType, itemId, data.id);
          menu.remove();
        } else {
          const msg = data && data.message ? data.message : `Erreur lors de la création de la playlist (code ${res.status})`;
          showToast(msg, "error");
        }
      } catch (err) {
        console.error(err);
        showToast("Erreur réseau", "error");
      }
    };

    formDiv.appendChild(input);
    formDiv.appendChild(saveBtn);
    menu.appendChild(formDiv);

    // Ajoute le menu dans le DOM
    document.body.appendChild(menu);

    // Position : collé à côté du bouton
    requestAnimationFrame(() => {
      const rect = addToPlaylistBtn.getBoundingClientRect();

      // Par défaut, à droite du bouton
      let left = rect.right + 6;
      let top = rect.top;

      // Si le popup dépasse à droite, le placer à gauche du bouton
      if (left + menu.offsetWidth > window.innerWidth) {
        left = rect.left - menu.offsetWidth - 6;
      }

      // Ajuster si dépasse en haut/bas
      if (top + menu.offsetHeight > window.innerHeight) {
        top = window.innerHeight - menu.offsetHeight - 10;
      }
      if (top < 10) top = 10;

      menu.style.left = left + "px";
      menu.style.top = top + "px";
      menu.style.opacity = "1";
    });

    // Fermer si clic extérieur
    const closeMenu = (event) => {
      if (!menu.contains(event.target) && event.target !== addToPlaylistBtn) {
        menu.remove();
        document.removeEventListener("click", closeMenu);
      }
    };
    document.addEventListener("click", closeMenu);

    // --- Déplacement manuel ---
    let isDragging = false;
    let offsetX, offsetY;

    title.addEventListener("mousedown", (e) => {
      isDragging = true;
      offsetX = e.clientX - menu.offsetLeft;
      offsetY = e.clientY - menu.offsetTop;
      menu.style.cursor = "move";
    });

    document.addEventListener("mouseup", () => {
      isDragging = false;
      menu.style.cursor = "default";
    });

    document.addEventListener("mousemove", (e) => {
      if (isDragging) {
        menu.style.left = e.clientX - offsetX + "px";
        menu.style.top = e.clientY - offsetY + "px";
      }
    });

  } catch (err) {
    console.error(err);
    showToast("Erreur lors de la récupération des playlists", "error");
  }
});


// --- Notifications ---
function showToast(message, type = "info") {
  const toast = document.createElement("div");
  toast.textContent = message;
  toast.style.position = "fixed";
  toast.style.bottom = "20px";
  toast.style.right = "20px";
  toast.style.background = type === "error" ? "#ff4d4f" : "#333";
  toast.style.color = "#fff";
  toast.style.padding = "10px 15px";
  toast.style.borderRadius = "6px";
  toast.style.zIndex = 10000;
  toast.style.fontFamily = "sans-serif";
  toast.style.fontSize = "14px";
  toast.style.boxShadow = "0 2px 6px rgba(0,0,0,0.3)";
  toast.style.opacity = "0";
  toast.style.transition = "opacity 0.3s ease";
  document.body.appendChild(toast);
  setTimeout(() => toast.style.opacity = "1", 10);
  setTimeout(() => {
    toast.style.opacity = "0";
    setTimeout(() => toast.remove(), 400);
  }, 2500);
}

// --- Fonction pour ajouter ---
async function addToPlaylist(type, itemId, playlistId) {
  try {
    const res = await fetch(`/playlists/${playlistId}/add/${itemId}/`, {
      method: "POST",
      credentials: 'same-origin',
      headers: { "X-CSRFToken": getCookie("csrftoken") }
    });
    const data = await res.json();
    if (data.status === "success") {
      showToast(`${type === "track" ? "Track" : "Vidéo"} ajouté à la playlist !`);
    } else {
      showToast("Erreur lors de l'ajout à la playlist", "error");
    }
  } catch (err) {
    console.error(err);
    showToast("Erreur réseau", "error");
  }
}