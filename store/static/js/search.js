// === Attendre que le DOM soit chargé ===
document.addEventListener("DOMContentLoaded", () => {
  // === Recherche ===
  const input = document.getElementById("query");
  const resultBox = document.getElementById("search-results");
  const searchUrlEl = document.getElementById("search-url");

  if (!input || !resultBox || !searchUrlEl) return;

  const searchUrl = searchUrlEl.dataset.url;
  let debounceTimer;

  input.addEventListener("input", function () {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => {
      const q = this.value.trim();
      if (!q) {
        resultBox.style.display = "none";
        resultBox.innerHTML = "";
        return;
      }

      fetch(`${searchUrl}?q=${encodeURIComponent(q)}`)
        .then(resp => resp.json())
        .then(showResults)
        .catch(err => console.error(err));
    }, 150);
  });

  function showResults(data) {
    resultBox.innerHTML = "";

    function createResultItem(imgSrc, title, subtitle, iconClass, onClick, imgRadius = "5px") {
      const item = document.createElement("div");
      item.style.display = "flex";
      item.style.alignItems = "center";
      item.style.cursor = "pointer";
      item.style.padding = "4px 8px";
      item.style.borderRadius = "6px";
      item.style.boxSizing = "border-box";
      item.style.overflow = "hidden";

      item.innerHTML = `
        <img src="${imgSrc}" style="width:40px;height:40px;object-fit:cover;border-radius:${imgRadius};margin-right:10px;">
        <div style="flex:1;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">
          <strong>${title}</strong><br>
          <small>${subtitle || ""}</small>
        </div>
        ${iconClass ? `<i class="${iconClass}" style="font-size:24px;color:#47918b;margin-left:8px;"></i>` : ""}
      `;
      item.onclick = onClick;
      return item;
    }

    // --- Tracks ---
    if (data.tracks) {
      // 🔁 Mettre à jour la playlist globale uniquement pour les tracks
      window.currentTrackList = data.tracks.map(t => ({
        id: t.id,
        title: t.title,
        artist: t.artist,
        cover: t.cover_image,
        file_url: t.audio_url
      }));
      window.currentTrackIndex = -1;

      data.tracks.forEach(track => {
        resultBox.appendChild(
          createResultItem(
            track.cover_image || "/static/img/trackdefault.png",
            track.title,
            track.artist,
            "bi bi-play-circle",
            () => {
              // Lecture via le lecteur global
              playAudioFromSearch({
                file_url: track.audio_url,
                title: track.title,
                artist: track.artist,
                cover: track.cover_image,
                id: track.id
              });
            }
          )
        );
      });
    }

    // --- Videos ---
    if (data.videos) {
      data.videos.forEach(video => {
        resultBox.appendChild(
          createResultItem(
            video.thumbnail || "/static/img/videodefault.png",
            video.title,
            video.artist,
            "bi bi-play-circle",
            () => (window.location.href = video.url)
          )
        );
      });
    }

    // --- Artists ---
    if (data.artists) {
      data.artists.forEach(artist => {
        resultBox.appendChild(
          createResultItem(
            artist.image || "/static/img/artistedefault.png",
            artist.name,
            "",
            "bi bi-info-circle",
            () => (window.location.href = artist.url),
            "50%" // image ronde
          )
        );
      });
    }

    // --- Albums ---
    if (data.albums) {
      data.albums.forEach(alb => {
        resultBox.appendChild(
          createResultItem(
            alb.cover_image || "/static/img/default-album.png",
            alb.title,
            alb.artist,
            "bi bi-collection-play-fill",
            () => (window.location.href = alb.url)
          )
        );
      });
    }

    resultBox.style.display = "block";
  }

  // Cacher les résultats si clic en dehors
  document.addEventListener("click", e => {
    if (!e.target.closest(".search-container")) {
      resultBox.style.display = "none";
    }
  });
});
