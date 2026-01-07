// ==============================
// VIDEO UTILITIES (GLOBAL)
// ==============================
window.videoPlay ??= function (video_id) {
  fetch(`/store/video/play/${video_id}/`)
    .then(r => r.json())
    .then(data => console.log("Lecture vidéo :", data.play_count))
    .catch(err => console.error("Video play error:", err));
};

window.removeSkeleton ??= function (el) {
  el?.classList.remove("skeleton");
};

// =====================================================
// PLAYER PRINCIPAL
// =====================================================
window.initVideo = function () {
  console.log("🎬 initVideo");

  const video = document.getElementById("mainVideo");
  const player = document.querySelector(".main-player");
  if (!video || !player) return;

  // ===============================
  // APPARITION DU PLAYER
  // ===============================
  if (!player.dataset.visibleInit) {
    player.dataset.visibleInit = "true";

    const showPlayer = () => player.classList.add("in-view");

    if (!("IntersectionObserver" in window)) {
      showPlayer();
    } else {
      const obs = new IntersectionObserver(entries => {
        entries.forEach(e => {
          if (e.isIntersecting) {
            showPlayer();
            obs.disconnect();
          }
        });
      });
      obs.observe(player);
      setTimeout(showPlayer, 800);
    }
  }

  // ===============================
  // AUTOPLAY / PAUSE AU SCROLL
  // ===============================
  if (!video.dataset.scrollObserver) {
    video.dataset.scrollObserver = "true";

    const obs = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          video.play().catch(() => {});
        } else if (video.muted) {
          video.pause();
        }
      });
    }, { threshold: 0.5 });

    obs.observe(video);
  }

  // ===============================
  // MUTE / UNMUTE
  // ===============================
  const muteBtn = document.getElementById("ytMuteBtn");
  if (muteBtn && !muteBtn.dataset.bound) {
    muteBtn.dataset.bound = "true";

    const icon = muteBtn.querySelector("i");

    const updateMuteIcon = () => {
      if (video.muted) {
        muteBtn.classList.remove("hidden");
        icon.className = "bi bi-volume-mute-fill";
      } else {
        muteBtn.classList.add("hidden");
      }
    };

    muteBtn.addEventListener("click", () => {
      video.muted = false;
      video.volume = 1;
      localStorage.setItem("videoUnmuted", "true");
      updateMuteIcon();
      window.handleUnmute?.(video);
    });

    updateMuteIcon();
  }

  // ===============================
  // PICTURE IN PICTURE
  // ===============================
  const pipBtn = document.getElementById("pipBtn");
  if (pipBtn && !pipBtn.dataset.bound) {
    pipBtn.dataset.bound = "true";
    let pipActive = false;

    pipBtn.addEventListener("click", async () => {
      try {
        if (video !== document.pictureInPictureElement) {
          await video.requestPictureInPicture();
          pipActive = true;
        } else {
          await document.exitPictureInPicture();
          pipActive = false;
        }
      } catch (e) {
        console.error("PiP error:", e);
      }
    });
  }

  // ===============================
  // MINI PLAYER FLOTTANT
  // ===============================
  const miniContainer = document.getElementById("miniPlayerContainer");

  if (miniContainer && !miniContainer.dataset.initialized) {
    miniContainer.dataset.initialized = "true";

    const miniPlayer = document.createElement("div");
    miniPlayer.className = "mini-player";
    const miniVideo = video.cloneNode(true);
    miniVideo.muted = video.muted;

    miniPlayer.appendChild(miniVideo);
    miniContainer.appendChild(miniPlayer);

    let miniVisible = false;

    window.addEventListener("scroll", () => {
      const unmuted = localStorage.getItem("videoUnmuted") === "true";

      if (window.scrollY > 300 && unmuted && !miniVisible) {
        miniPlayer.style.display = "block";
        miniVideo.play();
        miniVisible = true;
      } else if (window.scrollY < 300 && miniVisible) {
        miniPlayer.style.display = "none";
        miniVideo.pause();
        miniVisible = false;
      }
    });

    miniPlayer.addEventListener("click", () => {
      window.scrollTo({ top: video.offsetTop - 20, behavior: "smooth" });
      miniPlayer.style.display = "none";
      miniVisible = false;
    });
  }

  // ===============================
  // SWAP VIDÉO (CAROUSEL)
  // ===============================
  document.addEventListener("click", e => {
    const link = e.target.closest(".video-link");
    if (!link) return;

    e.preventDefault();

    const mainTitle = document.querySelector(".main-player h3");
    const mainStats = document.querySelector(".video-stats");
    const mainThumb = document.getElementById("mainThumbnail");
    if (!mainTitle || !mainStats || !mainThumb) return;

    const swap = {
      src: video.currentSrc,
      title: mainTitle.textContent,
      views: mainStats.children[0].textContent.replace(/\D/g, ""),
      downloads: mainStats.children[1].textContent.replace(/\D/g, ""),
      likes: mainStats.children[2].textContent.replace(/\D/g, ""),
      thumb: mainThumb.src
    };

    video.src = link.dataset.src;
    video.load();
    video.play().catch(() => {});
    mainTitle.textContent = link.dataset.title;
    mainThumb.src = link.querySelector("img").src;

    mainStats.innerHTML = `
      <span><i class="fa-regular fa-eye"></i> ${link.dataset.views}</span>
      <span><i class="fa-solid fa-download"></i> ${link.dataset.downloads}</span>
      <span><i class="fa-regular fa-heart"></i> ${link.dataset.likes}</span>
    `;

    link.dataset.src = swap.src;
    link.dataset.title = swap.title;
    link.dataset.views = swap.views;
    link.dataset.downloads = swap.downloads;
    link.dataset.likes = swap.likes;

    link.querySelector("h3").textContent = swap.title;
    link.querySelector(".stats").innerHTML = `
      <span><i class="fa-regular fa-eye"></i> ${swap.views}</span>
      <span><i class="fa-solid fa-download"></i> ${swap.downloads}</span>
      <span><i class="fa-regular fa-heart"></i> ${swap.likes}</span>
    `;
    link.querySelector("img").src = swap.thumb;

    document.querySelector(".mini-player video")?.setAttribute("src", video.src);
  });
};
