document.addEventListener("DOMContentLoaded", () => {
  
  // Si la page n'a pas le lecteur global (par ex. page "play_track" qui a son propre lecteur),
  // on quitte proprement pour éviter erreurs sur des éléments absents.
  const _globalPlayerEl = document.getElementById("global-audio-player");
  if (!_globalPlayerEl) return; // rien à initialiser ici
  // ---------------------
  // Sélection des éléments
  // ---------------------
  const audio = document.getElementById("audio-player");
  const audioSource = document.getElementById("audio-source");
  const playPauseBtn = document.getElementById("play-pause");
  const progressBar = document.getElementById("progress-bar");
  const volumeControl = document.getElementById("volume");
  const muteBtn = document.getElementById("mute-btn");
  const prevBtn = document.getElementById("prev");
  const nextBtn = document.getElementById("next");
  const shuffleBtn = document.getElementById("shuffle");
  const loopBtn = document.getElementById("loop");
  const titleEl = document.getElementById("audio-title");
  const artistEl = document.getElementById("audio-artist");
  const coverImg = document.getElementById("player-cover");
  const playerContainer = document.getElementById("global-audio-player");
  const currentTimeEl = document.getElementById("current-time");
  const totalTimeEl = document.getElementById("total-time");
  const expandBtn = document.getElementById("expand-player");
  const likeBtn = document.getElementById("like");
  const addToPlaylistBtn = document.getElementById("add-to-playlist");
  const shareBtn = document.getElementById("share");
  const closeBtn = document.getElementById("close-player");
  const mainContent = document.getElementById("main-content");
  const links = document.querySelectorAll("nav a"); // liens du menu

  // ---------------------
  // Variables
  // ---------------------
  window.currentTrackList = window.currentTrackList || [];
  window.currentTrackIndex = typeof window.currentTrackIndex === 'number' ? window.currentTrackIndex : -1;


  let isShuffle = false;
  let isLoop = false;
  let isLiked = false;
  let prevVolume = null;
  let isSeeking = false;
  let rafId = null;
  let audioContext = null;
  let analyser = null;
  let dataArray = null;
  let bufferLength = 0;
  let visualizerRaf = null;
  let mediaSource = null;
  let visualizerCanvas = document.getElementById("player-visualizer");
  let visualizerCtx = visualizerCanvas ? visualizerCanvas.getContext("2d") : null;

  // ---------------------
  // Fonctions utilitaires
  // ---------------------
  function formatTime(seconds) {
    if (isNaN(seconds)) return "0:00";
    const min = Math.floor(seconds / 60);
    const sec = Math.floor(seconds % 60);
    return `${min}:${sec < 10 ? "0" + sec : sec}`;
  }

  function startVisualizerIfPossible() {
    if (!visualizerCanvas) return;

    try {
      if (!audioContext) {
        audioContext = new (window.AudioContext || window.webkitAudioContext)();
      }

      if (audioContext.state === "suspended") {
        audioContext.resume();
      }

      if (!analyser) {
        analyser = audioContext.createAnalyser();
        analyser.fftSize = 256;
        bufferLength = analyser.frequencyBinCount;
        dataArray = new Uint8Array(bufferLength);
      }

      // 🔴 PROTECTION CRITIQUE
      if (!mediaSource && audio instanceof HTMLMediaElement) {
          mediaSource = audioContext.createMediaElementSource(audio);
          mediaSource.connect(analyser);
          analyser.connect(audioContext.destination);
        }

      if (!visualizerRaf) {
        const draw = () => {
          analyser.getByteFrequencyData(dataArray);
          visualizerCtx.clearRect(0, 0, visualizerCanvas.width, visualizerCanvas.height);

          const barWidth = (visualizerCanvas.width / bufferLength) * 2.5;
          let x = 0;

          for (let i = 0; i < bufferLength; i++) {
            const barHeight = (dataArray[i] / 255) * visualizerCanvas.height;
            visualizerCtx.fillStyle = `rgb(${barHeight + 100},50,50)`;
            visualizerCtx.fillRect(x, visualizerCanvas.height - barHeight, barWidth, barHeight);
            x += barWidth + 1;
          }

          visualizerRaf = requestAnimationFrame(draw);
        };
        draw();
      }
    } catch (e) {
      console.error("[player] visualizer error", e);
    }
  }


  function stopVisualizer() {
    if (visualizerRaf) {
      cancelAnimationFrame(visualizerRaf);
      visualizerRaf = null;
    }
    if (visualizerCtx) {
      visualizerCtx.clearRect(0, 0, visualizerCanvas.width, visualizerCanvas.height);
    }
  }

  // Inject small CSS for fade-in (used when restoring the player on back navigation)
  try {
    const styleId = 'global-audio-player-fade-style';
    if (!document.getElementById(styleId)) {
      const s = document.createElement('style');
      s.id = styleId;
      s.textContent = `#global-audio-player.fade-in { opacity: 0; animation: gplayer-fade-in 0.35s forwards; } @keyframes gplayer-fade-in { from { opacity: 0; } to { opacity: 1; } }`;
      document.head.appendChild(s);
    }
  } catch (e) {}

  function savePlayerState(trackId) {
    const playerData = {
      src: audio.src,
      currentTime: audio.currentTime,
      paused: audio.paused,
      volume: audio.volume,
      muted: audio.muted || false,
      prevVolume: (typeof prevVolume === 'number' ? prevVolume : (audio.volume || 0)),
      trackId: trackId,
      title: titleEl ? titleEl.textContent : '',
      artist: artistEl ? artistEl.textContent : '',
      cover: coverImg ? coverImg.src : '',
      shuffle: isShuffle,
      repeat: isLoop,
      // timestamp to avoid restoring very old states on simple reloads
      _ts: Date.now()
    };
    try {
      localStorage.setItem("currentPlayer", JSON.stringify(playerData));
    } catch (e) {}
    try {
      sessionStorage.setItem("currentPlayer", JSON.stringify(playerData));
    } catch (e) {}
  }

  function restorePlayerState() {
    // Respect user's choice to keep the player closed: if they previously closed
    // it, don't reopen on reload.
    try {
      if (sessionStorage.getItem('playerClosed') === '1') {
        return;
      }
    } catch (e) {}
    let raw = null;
    try { raw = sessionStorage.getItem('currentPlayer'); } catch(e) { raw = null; }
    if (!raw) {
      try { raw = localStorage.getItem('currentPlayer'); } catch(e) { raw = null; }
    }
    if (!raw) return;
    let saved = null;
    try { saved = JSON.parse(raw); } catch(e) { console.log('[player] invalid saved state', e); return; }

  // Only restore/show the global player if the saved state indicates active playback
  // (has a valid src AND either was not paused or had progressed beyond 1 second)
  // and the saved state is recent (avoid showing after long time or unrelated reloads).
    const hasSrc = !!saved.src;
    const wasPlaying = saved.paused === false;
    const progressed = typeof saved.currentTime === 'number' && saved.currentTime > 1;
  const age = saved._ts ? (Date.now() - saved._ts) : Infinity;
  const RECENT_MS = 2 * 60 * 1000; // 2 minutes
  const isRecent = age <= RECENT_MS;
  const shouldShow = hasSrc && (wasPlaying || progressed) && isRecent;

    if (!shouldShow) {
      // Do not reveal the player on simple page reloads when nothing was actively playing.
      return;
    }

    // Apply visual metadata (title/artist/cover) from saved state if available
    try {
      if (saved.title && titleEl) titleEl.textContent = saved.title;
    } catch (e) {}
    try {
      if (saved.artist && artistEl) artistEl.textContent = saved.artist;
    } catch (e) {}
    try {
      if (saved.cover && coverImg) coverImg.src = saved.cover;
    } catch (e) {}

    // Proceed to restore audio only when we decided to show the player
    try { audio.src = saved.src; } catch (e) {}
    try { audio.dataset.trackId = saved.trackId; } catch (e) {}
    try { if (expandBtn) expandBtn.dataset.trackId = saved.trackId; } catch (e) {}

    // Restore volume and muted UI control
    try { audio.volume = typeof saved.volume === 'number' ? saved.volume : (audio.volume || 1); } catch (e) {}
    try { audio.muted = !!saved.muted; } catch (e) {}
    try { if (volumeControl) volumeControl.value = (typeof saved.volume === 'number' ? saved.volume : audio.volume); } catch (e) {}
    try {
      if (muteBtn) {
        const ic = muteBtn.querySelector('i');
        if (audio.muted || audio.volume === 0) {
          if (ic) ic.className = 'bi bi-volume-mute';
        } else if (audio.volume < 0.5) {
          if (ic) ic.className = 'bi bi-volume-down';
        } else {
          if (ic) ic.className = 'bi bi-volume-up';
        }
      }
    } catch (e) {}

    isShuffle = saved.shuffle || false;
    isLoop = saved.repeat || false;
    audio.loop = isLoop;

    // Ensure the small/global player is visible when restoring state (e.g. after Back)
    try {
      if (playerContainer) {
        playerContainer.classList.remove('fade-out');
        playerContainer.style.display = playerContainer.style.display && playerContainer.style.display !== 'none' ? playerContainer.style.display : 'flex';
        try {
          playerContainer.classList.add('fade-in');
          // Force reflow to ensure animation runs
          // eslint-disable-next-line no-unused-expressions
          playerContainer.offsetHeight;
          setTimeout(() => playerContainer.classList.remove('fade-in'), 400);
        } catch (e) {}
      }
    } catch (e) {}

    // When metadata is ready, ensure we set currentTime, total time and progress UI
    const onMetaRestore = () => {
      try {
        if (typeof saved.currentTime === 'number') audio.currentTime = saved.currentTime;
      } catch (e) {}
      try {
        if (totalTimeEl) totalTimeEl.textContent = formatTime(audio.duration);
      } catch (e) {}
      try {
        if (!isNaN(audio.duration) && progressBar) progressBar.value = (audio.currentTime / audio.duration) * 100;
      } catch (e) {}
      audio.removeEventListener('loadedmetadata', onMetaRestore);
    };
    try {
      audio.addEventListener('loadedmetadata', onMetaRestore);
    } catch (e) {}

    // Start playback if it was playing. Use the play() promise to decide which
    // icon to show — browsers may block autoplay so saved.paused == false does
    // not guarantee the audio is actually playing.
    try {
      if (!saved.paused) {
        const playPromise = audio.play();
        if (playPromise && typeof playPromise.then === 'function') {
          playPromise.then(() => {
            try { playPauseBtn.innerHTML = '<i class="bi bi-pause-fill"></i>'; } catch (e) {}
          }).catch(() => {
            // Autoplay blocked or error -> keep audio paused and show Play icon
            try { playPauseBtn.innerHTML = '<i class="bi bi-play-fill"></i>'; } catch (e) {}
          });
        } else {
          // older browsers: assume play succeeded
          try { playPauseBtn.innerHTML = '<i class="bi bi-pause-fill"></i>'; } catch (e) {}
        }
      } else {
        try { playPauseBtn.innerHTML = '<i class="bi bi-play-fill"></i>'; } catch (e) {}
      }
    } catch (e) {
      try { playPauseBtn.innerHTML = '<i class="bi bi-play-fill"></i>'; } catch (ex) {}
    }

    // If the browser already has metadata loaded, trigger the onMetaRestore immediately
    try {
      if (!isNaN(audio.duration) && audio.duration > 0) {
        onMetaRestore();
      }
    } catch (e) {}
  }

  // ---------------------
  // Lecture depuis recherche
  // ---------------------
window.playAudioFromSearch = function (track) {
  if (!track || !track.file_url) return;

  const cover = track.cover || "/static/img/trackdefault.png";

  // Stop lecture précédente
  audio.pause();

  // Reset visual state
  isLiked = false;
  likeBtn.innerHTML = '<i class="bi bi-heart"></i>';

  // Load new track
  audio.src = track.file_url;
  audio.currentTime = 0;
  audio.muted = false;

  if (audio.volume === 0) {
    audio.volume = volumeControl?.value || 1;
  }

  audio.dataset.trackId = track.id;
  expandBtn.dataset.trackId = track.id;

  titleEl.textContent = track.title || "Sans titre";
  artistEl.textContent = track.artist || "Inconnu";
  coverImg.src = cover;

  playerContainer.style.display = "flex";
  try { sessionStorage.removeItem("playerClosed"); } catch {}

  const playPromise = audio.play();
  if (playPromise?.then) {
    playPromise
      .then(() => {
        playPauseBtn.innerHTML = '<i class="bi bi-pause-fill"></i>';
        startVisualizerIfPossible();
        savePlayerState(track.id); // ✅ IMPORTANT
      })
      .catch(() => {
        playPauseBtn.innerHTML = '<i class="bi bi-play-fill"></i>';
      });
  }

  if (Array.isArray(window.currentTrackList)) {
    window.currentTrackIndex =
      window.currentTrackList.findIndex(t => t.id === track.id);
  }
};

// Next bouton
nextBtn?.addEventListener("click", () => {
    if (window.location.pathname.includes('/track/play/')) {
        if (typeof nextTrack === 'function') nextTrack();
        return;
    }

    if (!window.currentTrackList || window.currentTrackList.length === 0) return;

    window.currentTrackIndex++;
    if (window.currentTrackIndex >= window.currentTrackList.length) {
        window.currentTrackIndex = 0; // boucle comme Spotify
    }

    const nextTrackItem = window.currentTrackList[window.currentTrackIndex];
    if (nextTrackItem) window.playAudioFromSearch(nextTrackItem);
});

// Prev bouton
prevBtn?.addEventListener("click", () => {
    if (window.location.pathname.includes('/track/play/')) {
        if (typeof prevTrack === 'function') prevTrack();
        return;
    }

    if (!window.currentTrackList || window.currentTrackList.length === 0) return;

    window.currentTrackIndex--;
    if (window.currentTrackIndex < 0) {
        window.currentTrackIndex = window.currentTrackList.length - 1; // boucle comme Spotify
    }

    const prevTrackItem = window.currentTrackList[window.currentTrackIndex];
    if (prevTrackItem) window.playAudioFromSearch(prevTrackItem);
});


  // ---------------------
  // Contrôles audio
  // ---------------------
  playPauseBtn?.addEventListener("click", () => {
    if (window.location.pathname.includes('/track/play/')) {
      // On play_track page, use the full player's play/pause functions
      if (typeof togglePlayPause === 'function') {
        togglePlayPause();
        return;
      }
    }

    if (audio.paused) {
      audio.play();
      playPauseBtn.innerHTML = '<i class="bi bi-pause-fill"></i>';
    } else {
      audio.pause();
      playPauseBtn.innerHTML = '<i class="bi bi-play-fill"></i>';
    }
  });

  audio.addEventListener("loadedmetadata", () => {
    totalTimeEl.textContent = formatTime(audio.duration);
  });

  audio.addEventListener("timeupdate", () => {
    if (!isNaN(audio.duration)) {
      progressBar.value = (audio.currentTime / audio.duration) * 100;
      currentTimeEl.textContent = formatTime(audio.currentTime);
    }
  });
  audio.addEventListener("volumechange", () => {
    if (!volumeControl) return;
    volumeControl.value = audio.muted ? 0 : audio.volume;
  });


  progressBar?.addEventListener("input", () => {
    audio.currentTime = (progressBar.value / 100) * audio.duration;
  });

  volumeControl?.addEventListener("input", e => {
    audio.volume = e.target.value;
    try {
      // remember last non-zero volume for unmute
      const v = Number(audio.volume);
      if (!isNaN(v) && v > 0) prevVolume = v;
    } catch (ee) {}
    try {
      if (muteBtn) {
        const ic = muteBtn.querySelector('i');
        if (audio.volume === 0) {
          audio.muted = true;
          if (ic) ic.className = 'bi bi-volume-mute';
        } else {
          audio.muted = false;
          if (ic) ic.className = audio.volume < 0.5 ? 'bi bi-volume-down' : 'bi bi-volume-up';
        }
      }
    } catch (e) {}
  });

    // -------------------------
  // Progress


  // Toggle mute/unmute
  muteBtn?.addEventListener('click', () => {
    try {
      if (!audio.muted) {
        // muting -> remember last non-zero volume
        try { if (audio.volume && audio.volume > 0) prevVolume = audio.volume; } catch (e) {}
        audio.muted = true;
        const ic = muteBtn.querySelector('i'); if (ic) ic.className = 'bi bi-volume-mute';
      } else {
        // unmute -> restore remembered volume if current is 0
        audio.muted = false;
        try {
          if (!audio.volume || audio.volume === 0) audio.volume = (typeof prevVolume === 'number' && prevVolume > 0) ? prevVolume : 0.5;
        } catch (e) {}
        const ic = muteBtn.querySelector('i'); if (ic) ic.className = audio.volume < 0.5 ? 'bi bi-volume-down' : 'bi bi-volume-up';
        if (volumeControl) volumeControl.value = audio.volume;
      }
    } catch (e) {}
  });

  shuffleBtn?.addEventListener("click", () => {
    isShuffle = !isShuffle;
    shuffleBtn.style.color = isShuffle ? "#00ffff" : "white";
  });

  loopBtn?.addEventListener("click", () => {
    isLoop = !isLoop;
    audio.loop = isLoop;
    loopBtn.style.color = isLoop ? "#00ffff" : "white";
  });

likeBtn?.addEventListener("click", async () => {
  if (typeof userIsLoggedIn === "undefined" || !userIsLoggedIn) { // userIsLoggedIn = true/false depuis Django
    alert("Veuillez vous connecter pour aimer ce contenu !");
    return;
  }

  // Toggle visuel immédiat
  isLiked = !isLiked;
  likeBtn.innerHTML = isLiked
    ? '<i class="bi bi-heart-fill" style="color:red;"></i>'
    : '<i class="bi bi-heart"></i>';

  // Envoi au serveur
  try {
    const model = audio.dataset.modelType; // "track" ou "video" ou "artist"
    const id = audio.dataset.trackId || audio.dataset.videoId || audio.dataset.artistId;
    if (!id || !model) return;

    const res = await fetch(`/action/${model}/${id}/`, {
      method: "POST",
      headers: { "X-CSRFToken": getCookie("csrftoken") }
    });
    const data = await res.json();
    if (!data.status) {
      // rollback visuel si erreur
      isLiked = !isLiked;
      likeBtn.innerHTML = isLiked
        ? '<i class="bi bi-heart-fill" style="color:red;"></i>'
        : '<i class="bi bi-heart"></i>';
      alert("Erreur lors de l'action Like/Follow");
    }
  } catch (err) {
    console.error(err);
  }
});


// --- Gestion du bouton ajouter à la playlist ---
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


  shareBtn?.addEventListener("click", async () => {
    if (!audio.src) return alert("Aucune piste en lecture !");
    const shareData = {
      title: titleEl.textContent,
      text: `🎶 Écoute ${titleEl.textContent} de ${artistEl.textContent}`,
      url: window.location.href,
    };
    if (navigator.share) {
      try { await navigator.share(shareData); } catch {}

    }
  })

closeBtn?.addEventListener("click", () => {
    // Ferme le mini-lecteur
    const player = document.getElementById("global-audio-player");
    if (player) player.style.display = "none";
    
    // Pause l'audio
    if (audio) audio.pause();
    
    // Marque le mini-lecteur comme fermé
    try { sessionStorage.setItem('playerClosed', '1'); } catch (e) {}

    // Ferme le fullscreen si ouvert
    const fs = document.getElementById("fullscreen-player");
    if (fs && fs.classList.contains("fs-visible")) {
        fs.classList.remove("fs-visible");
    }
});

  // ---------------------
  // Bouton agrandir
  // ---------------------
// ---------------------
// Bouton agrandir

// Événement clic pour agrandir

const fs = document.getElementById("fullscreen-player");
const fsClose = document.getElementById("fs-close");

const fsTitle = document.getElementById("fs-title");
const fsArtist = document.getElementById("fs-artist");
const fsCover = document.getElementById("fs-cover");
const fsBg = document.querySelector(".fs-bg");

expandBtn?.addEventListener("click", () => {
    if (!fs || !fsTitle || !fsArtist || !fsCover || !fsBg) return;

    // Récupère info du mini-lecteur
    const title = titleEl?.textContent || "";
    const artist = artistEl?.textContent || "";
    const cover = coverImg?.src || "/static/img/trackdefault.png";

    fsTitle.textContent = title;
    fsArtist.textContent = artist;
    fsCover.src = cover;
    fsBg.style.backgroundImage = `url('${cover}')`;

    fs.classList.add("fs-visible");
});

fsClose?.addEventListener("click", () => {
    fs?.classList.remove("fs-visible");
});



  // ---------------------
  // Navigation AJAX
  // ---------------------
  links.forEach(link => {
    link.addEventListener("click", async e => {
      if (e.ctrlKey || e.metaKey || e.button === 1) return;
      e.preventDefault();
      try {
        const res = await fetch(link.href);
        const text = await res.text();
        const doc = new DOMParser().parseFromString(text, "text/html");
        const newContent = doc.querySelector("#main-content");
        if (newContent) {
          mainContent.innerHTML = newContent.innerHTML;
          history.pushState(null, "", link.href);
          window.scrollTo(0, 0);
        }
      } catch {
        window.location.href = link.href;
      }
    });
  });

  window.addEventListener("popstate", async () => {
    const res = await fetch(location.href);
    const text = await res.text();
    const doc = new DOMParser().parseFromString(text, "text/html");
    const newContent = doc.querySelector("#main-content");
    if (newContent) {
      mainContent.innerHTML = newContent.innerHTML;
      window.scrollTo(0, 0);
    }
  });

  // Visualizer event listeners
  document.addEventListener("click", () => {
    if (audioContext && audioContext.state === "suspended") {
      try { audioContext.resume(); } catch {}
    }
  });
  audio.addEventListener('play', () => {
    startVisualizerIfPossible();
  });
  audio.addEventListener('pause', () => {
    stopVisualizer();
  });
  audio.addEventListener('ended', () => {
    stopVisualizer();
  });

  // ---------------------
  // Restaurer lecteur
  // ---------------------
  restorePlayerState();

  // Save current player state before the page is unloaded so the previous page
  // (small player) can restore it when the user navigates back.
  window.addEventListener('beforeunload', () => {
    try {
      // use dataset.trackId if available, else pass null
      const tid = audio.dataset.trackId || expandBtn?.dataset.trackId || null;
      savePlayerState(tid);
    } catch (e) {}
  });

  // Some browsers use the bfcache (back/forward cache) and don't fire
  // a full reload. Listen to pageshow (persisted) to restore state when
  // the page is being shown from cache.
  window.addEventListener('pageshow', (event) => {
    if (event.persisted) {
      try { restorePlayerState(); } catch (e) {}
    }
  });

});
