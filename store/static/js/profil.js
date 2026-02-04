// ==============================
// PROFILE / MEDIA / INTERACTIONS
// ==============================

let profileInitialized = false;
let trackClickInitialized = false;

function initProfile() {
  if (profileInitialized) return;
  profileInitialized = true;

  // ==========================
  // TABS (delegation)
  // ==========================
  document.addEventListener("click", e => {
    const tab = e.target.closest(".profile-nav li");
    if (!tab) return;

    const tabs = document.querySelectorAll(".profile-nav li");
    const contents = document.querySelectorAll(".tab-content");

    tabs.forEach(t => t.classList.remove("active"));
    contents.forEach(c => c.classList.remove("active"));

    tab.classList.add("active");

    const content = document.getElementById(tab.dataset.tab);
    if (content) content.classList.add("active");
  });

  // ==========================
  // FOLLOW BUTTON
  // ==========================
  document.addEventListener("click", e => {
    const btn = e.target.closest("#follow-btn");
    if (!btn) return;

    const userId = btn.dataset.user;
    const isFollowed = btn.classList.contains("followed");
    const url = isFollowed ? `/unfollow/${userId}/` : `/follow/${userId}/`;

    fetch(url, {
      method: "POST",
      headers: {
        "X-CSRFToken": getCookie("csrftoken"),
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ user_id: userId })
    })
    .then(r => r.json())
    .then(data => {
      if (data.status === "ok") {
        btn.classList.toggle("followed");
        btn.textContent = isFollowed ? "Suivre" : "Suivi";
      }
    })
    .catch(err => console.error("Follow error:", err));
  });

  // ==========================
  // MEDIA CLICK → GLOBAL PLAYER
  // ==========================
  initTrackClick();

  // ==========================
  // HORIZONTAL DRAG SCROLL
  // ==========================
  let isDown = false, startX, scrollLeft;

  document.addEventListener("mousedown", e => {
    const container = e.target.closest("#artistContainer");
    if (!container) return;

    isDown = true;
    startX = e.pageX - container.offsetLeft;
    scrollLeft = container.scrollLeft;
    container.classList.add("active");

    const onMove = e => {
      if (!isDown) return;
      e.preventDefault();
      const x = e.pageX - container.offsetLeft;
      container.scrollLeft = scrollLeft - (x - startX) * 2;
    };

    const stop = () => {
      isDown = false;
      container.classList.remove("active");
      document.removeEventListener("mousemove", onMove);
      document.removeEventListener("mouseup", stop);
    };

    document.addEventListener("mousemove", onMove);
    document.addEventListener("mouseup", stop);
  });
}

// ==============================
// GLOBAL PLAYER
// ==============================
function playMediaGlobal({ type, url, cover, title, artist, id }) {
  const audioPlayer = document.getElementById("audio-player");
  const audioSource = document.getElementById("audio-source");
  const playerCover = document.getElementById("player-cover");
  const audioTitle = document.getElementById("audio-title");
  const audioArtist = document.getElementById("audio-artist");
  const playPauseBtn = document.getElementById("play-pause");

  if (type === "audio") {
    audioSource.src = url;
    audioPlayer.load();
    audioPlayer.play().catch(() => {});

    playerCover.src = cover || "/static/img/trackdefault.png";
    audioTitle.textContent = title;
    audioArtist.textContent = artist;

    playPauseBtn.innerHTML = '<i class="bi bi-pause-fill"></i>';
  }
}

// ==============================
// TRACK CLICK + PLAYLIST
// ==============================
function initTrackClick() {
  const tracks = document.querySelectorAll(".media-item");

  // Construire / rafraîchir la playlist globale
  window.currentTrackList = Array.from(tracks).map(t => ({
    id: t.dataset.id,
    title: t.dataset.title,
    artist: t.dataset.artist,
    cover: t.dataset.cover,
    file_url: t.dataset.url,
    type: t.dataset.type
  }));
  window.currentTrackIndex = -1;

  if (trackClickInitialized) return;
  trackClickInitialized = true;

  // Délégation pour supporter le contenu injecté via AJAX
  document.addEventListener("click", e => {
    const track = e.target.closest(".media-item");
    if (!track) return;

    const tracksNow = document.querySelectorAll(".media-item");
    window.currentTrackList = Array.from(tracksNow).map(t => ({
      id: t.dataset.id,
      title: t.dataset.title,
      artist: t.dataset.artist,
      cover: t.dataset.cover,
      file_url: t.dataset.url,
      type: t.dataset.type
    }));
    const index = Array.from(tracksNow).indexOf(track);
    window.currentTrackIndex = index;

    // ✅ Utiliser la fonction centrale qui gère le mini-player
    window.playAudioFromSearch({
      file_url: track.dataset.url,
      title: track.dataset.title,
      artist: track.dataset.artist,
      cover: track.dataset.cover,
      id: track.dataset.id
    });
  });
}


// ==============================
// UTIL
// ==============================
function getCookie(name) {
  return document.cookie
    .split("; ")
    .find(row => row.startsWith(name + "="))
    ?.split("=")[1];
}

// ==============================
// INIT
// ==============================
document.addEventListener("DOMContentLoaded", initProfile);

// Exposé à main.js (AJAX navigation)
window.initProfil = function () {
  initProfile();
  initTrackClick();
};
