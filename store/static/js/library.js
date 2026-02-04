document.addEventListener("DOMContentLoaded", () => {
  const sidebar = document.getElementById("library-sidebar");
  const openBtn = document.getElementById("open-library-btn");
  const closeBtn = document.getElementById("library-close");
  const expandBtn = document.getElementById("library-expand");
  const mainContent = document.getElementById("main-content");

  let isExpanded = false;

  // Fonction pour charger la bibliothèque depuis l'API
  function loadLibrary() {
    fetch(libraryDataUrl)
      .then(res => res.json())
      .then(data => {
        // Playlists
        const playlistsUl = document.getElementById("lib-playlists");
        playlistsUl.innerHTML = "";
        if (data.playlists.length) {
          data.playlists.forEach(p => {
            const li = document.createElement("li");
            li.className = "library-playlist-item";
            li.dataset.playlistId = p.id;
            li.innerHTML = `
              <a href="#" data-playlist-id="${p.id}">${p.name}</a>
              <div class="playlist-tracks" data-playlist-id="${p.id}" style="display:none;"></div>
            `;
            playlistsUl.appendChild(li);
          });
        } else {
          playlistsUl.innerHTML = "<li><em>Aucune playlist trouvée.</em></li>";
        }

        // Artistes
        const artistsUl = document.getElementById("lib-artists");
        artistsUl.innerHTML = "";
        if (data.artists.length) {
          data.artists.forEach(a => {
            const li = document.createElement("li");
            const imageUrl = a.image || "/static/img/artistedefault.png";
            li.innerHTML = `
              <a href="/artist/${a.id}/">
                <img src="${imageUrl}" width="40" height="40" style="border-radius:50%; margin-right:8px;">
                ${a.name}
              </a>`;
            artistsUl.appendChild(li);
          });
        } else {
          artistsUl.innerHTML = "<li><em>Aucun artiste suivi.</em></li>";
        }

        // Albums
        const albumsUl = document.getElementById("lib-albums");
        albumsUl.innerHTML = "";
        if (data.albums.length) {
          data.albums.forEach(alb => {
            const li = document.createElement("li");
            const cover = alb.cover_image || "/static/img/default-album.png";
            li.innerHTML = `
              <a href="/album/${alb.id}/">
                <img src="${cover}" width="40" height="40" style="border-radius:6px; margin-right:8px;">
                ${alb.title} – <small>${alb.artist__name}</small>
              </a>`;
            albumsUl.appendChild(li);
          });
        } else {
          albumsUl.innerHTML = "<li><em>Aucun album acheté.</em></li>";
        }
      })
      .catch(err => console.error("Erreur bibliothèque :", err));
  }

  function renderPlaylistTracks(container, tracks) {
    if (!container) return;
    if (!tracks || !tracks.length) {
      container.innerHTML = "<div><em>Aucun titre dans cette playlist.</em></div>";
      return;
    }

    const items = tracks.map(t => {
      const cover = t.cover || "/static/img/trackdefault.png";
      const duration = t.duration ? ` <small>${t.duration}</small>` : "";
      return `
        <div class="playlist-track-item" data-track-id="${t.id}">
          <img src="${cover}" width="32" height="32" style="border-radius:6px; margin-right:8px;">
          <span>${t.title} - <small>${t.artist}</small>${duration}</span>
        </div>
      `;
    }).join("");

    container.innerHTML = items;
  }

  // Charger au départ
  loadLibrary();

  // === Clic playlist: afficher contenu juste en dessous ===
  document.addEventListener("click", e => {
    const link = e.target.closest("#lib-playlists a[data-playlist-id]");
    if (!link) return;
    e.preventDefault();

    const playlistId = link.dataset.playlistId;
    const container = document.querySelector(`.playlist-tracks[data-playlist-id="${playlistId}"]`);
    if (!container) return;

    if (container.style.display === "block") {
      container.style.display = "none";
      return;
    }

    container.style.display = "block";
    container.innerHTML = "<div><em>Chargement...</em></div>";

    fetch(`/playlists/${playlistId}/tracks/`)
      .then(res => res.json())
      .then(data => renderPlaylistTracks(container, data.tracks))
      .catch(() => {
        container.innerHTML = "<div><em>Erreur de chargement.</em></div>";
      });
  });

  // === Ouvrir la sidebar ===
  openBtn.addEventListener("click", () => {
    sidebar.classList.remove("library-collapsed");
    sidebar.classList.add("library-open");
    mainContent.classList.add("main-shifted");

    openBtn.classList.add("moved");
    openBtn.innerHTML = '<i class="bi bi-x-lg"></i> Fermer';
    console.log("Sidebar ouverte");
  });

  // === Fermer la sidebar ===
  closeBtn.addEventListener("click", () => {
    sidebar.classList.remove("library-open", "library-expanded");
    sidebar.classList.add("library-collapsed");
    mainContent.classList.remove("main-shifted", "main-expanded");

    openBtn.classList.remove("moved");
    openBtn.innerHTML = '<i class="bi bi-collection"></i> Bibliothèque';
    isExpanded = false;

    // reset la position du bouton
    openBtn.style.left = "";
  });

  // === Agrandir / Réduire la sidebar ===
  expandBtn.addEventListener("click", () => {
    isExpanded = !isExpanded;
    sidebar.classList.toggle("library-expanded", isExpanded);
    sidebar.classList.toggle("library-open", !isExpanded);
    mainContent.classList.toggle("main-expanded", isExpanded);
    mainContent.classList.toggle("main-shifted", !isExpanded);

    openBtn.style.left = isExpanded ? "510px" : "310px";
  });
});
