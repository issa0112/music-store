// ==============================
// PROFILE / MEDIA / INTERACTIONS
// ==============================

let profileInitialized = false;

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
    document.getElementById(tab.dataset.tab)?.classList.add("active");
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
    });
  });

  // ==========================
  // MEDIA CLICK → GLOBAL PLAYER
  // ==========================
  document.addEventListener("click", e => {
    const item = e.target.closest(".media-item");
    if (!item) return;

    playMediaGlobal({
      type: item.dataset.type,
      url: item.dataset.url,
      cover: item.dataset.cover,
      title: item.dataset.title,
      artist: item.dataset.artist
    });
  });

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
// GLOBAL PLAYER (1 seule fois)
// ==============================

function playMediaGlobal({ type, url, cover, title, artist }) {
  const miniPlayer = document.getElementById("mini-player");
  const audio = document.getElementById("mini-audio");
  const video = document.getElementById("mini-video");

  if (!miniPlayer) return;

  audio?.pause();
  video?.pause();

  document.getElementById("mini-title").textContent = title;
  document.getElementById("mini-artist").textContent = artist;
  document.getElementById("mini-cover").src = cover || "/static/img/trackdefault.png";

  if (type === "audio" && audio) {
    audio.src = url;
    audio.style.display = "block";
    video.style.display = "none";
    audio.play().catch(()=>{});
  }

  if (type === "video" && video) {
    video.src = url;
    video.style.display = "block";
    audio.style.display = "none";
    video.play().catch(()=>{});
  }

  miniPlayer.style.display = "flex";
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
