document.addEventListener("DOMContentLoaded", () => {

    /*** TABS ***/
    const tabs = document.querySelectorAll(".profile-nav li");
    const contents = document.querySelectorAll(".tab-content");
    if(tabs.length && contents.length) {
        tabs.forEach(tab => {
            tab.addEventListener("click", () => {
                tabs.forEach(t => t.classList.remove("active"));
                tab.classList.add("active");
                contents.forEach(c => c.classList.remove("active"));
                const target = document.getElementById(tab.dataset.tab);
                if(target) target.classList.add("active");
            });
        });
    }

    /*** FOLLOW BUTTON ***/
    const followBtn = document.getElementById("follow-btn");
    if(followBtn) {
        followBtn.addEventListener("click", function() {
            const userId = this.dataset.user;
            const isFollowed = this.classList.contains("followed");
            const url = isFollowed ? `/unfollow/${userId}/` : `/follow/${userId}/`;

            fetch(url, {
                method: "POST",
                headers: {
                    "X-CSRFToken": getCookie("csrftoken"),
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ user_id: userId })
            })
            .then(response => response.json())
            .then(data => {
                if(data.status === "ok") {
                    followBtn.classList.toggle("followed");
                    followBtn.textContent = isFollowed ? "Suivre" : "Suivi";
                }
            })
            .catch(err => console.error("Follow error:", err));
        });
    }

    /*** MINI PLAYER ***/
    const miniPlayer = document.getElementById("mini-player");
    const miniAudio = document.getElementById("mini-audio");
    const miniVideo = document.getElementById("mini-video");
    const miniCover = document.getElementById("mini-cover");
    const miniTitle = document.getElementById("mini-title");
    const miniArtist = document.getElementById("mini-artist");
    const miniClose = document.getElementById("mini-close");
    const pipBtn = document.getElementById("pip-btn");

    function playMedia(type, url, cover, title, artist) {
        if(!miniPlayer) return;

        // Pause tous les médias
        if(miniAudio) miniAudio.pause();
        if(miniVideo) miniVideo.pause();

        // Mise à jour infos
        if(miniTitle) miniTitle.textContent = title;
        if(miniArtist) miniArtist.textContent = artist;
        if(miniCover) miniCover.src = cover || "/static/img/trackdefault.png";

        if(type === "audio" && miniAudio) {
            miniAudio.src = url;
            miniAudio.style.display = "block";
            if(miniVideo) miniVideo.style.display = "none";
            miniAudio.play().catch(e => console.log("Lecture audio bloquée:", e));
        } else if(type === "video" && miniVideo) {
            miniVideo.src = url;
            miniVideo.style.display = "block";
            if(miniAudio) miniAudio.style.display = "none";
            miniVideo.play().catch(e => console.log("Lecture vidéo bloquée:", e));
        }

        miniPlayer.style.display = "flex";
    }

    // Media items click
    const mediaItems = document.querySelectorAll(".media-item");
    if(mediaItems.length) {
        mediaItems.forEach(item => {
            item.addEventListener("click", () => {
                const type = item.dataset.type;
                const url = item.dataset.url;
                const cover = item.dataset.cover;
                const title = item.dataset.title;
                const artist = item.dataset.artist;
                playMedia(type, url, cover, title, artist);
            });
        });
    }

    // Mini player close
    if(miniClose) {
        miniClose.addEventListener("click", () => {
            if(miniVideo && miniVideo !== document.pictureInPictureElement) {
                miniVideo.pause();
            } else {
                document.exitPictureInPicture().catch(()=>{});
            }
            if(miniAudio) miniAudio.pause();
            if(miniPlayer) miniPlayer.style.display = "none";
        });
    }

    // Picture-in-Picture
    if(pipBtn && miniVideo) {
        pipBtn.addEventListener("click", async () => {
            if(miniVideo.style.display === "block" && 'pictureInPictureEnabled' in document) {
                try {
                    if(miniVideo !== document.pictureInPictureElement) {
                        await miniVideo.requestPictureInPicture();
                    } else {
                        await document.exitPictureInPicture();
                    }
                } catch(e) {
                    console.error("PiP error:", e);
                }
            }
        });
    }

    /*** HORIZONTAL SCROLL CONTAINER ***/
    const container = document.getElementById('artistContainer');
    if(container) {
        let isDown = false, startX, scrollLeft;
        container.addEventListener('mousedown', e => {
            isDown = true;
            container.classList.add('active');
            startX = e.pageX - container.offsetLeft;
            scrollLeft = container.scrollLeft;
        });
        container.addEventListener('mouseleave', () => { isDown = false; container.classList.remove('active'); });
        container.addEventListener('mouseup', () => { isDown = false; container.classList.remove('active'); });
        container.addEventListener('mousemove', e => {
            if(!isDown) return;
            e.preventDefault();
            const x = e.pageX - container.offsetLeft;
            const walk = (x - startX) * 2; // vitesse scroll
            container.scrollLeft = scrollLeft - walk;
        });
    }

    /*** UTILITAIRES ***/
    function getCookie(name) {
        let cookieValue = null;
        if(document.cookie && document.cookie !== "") {
            const cookies = document.cookie.split(";");
            for(let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if(cookie.substring(0, name.length + 1) === (name + "=")) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

});
