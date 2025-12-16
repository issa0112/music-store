document.addEventListener("DOMContentLoaded", () => {
    // Tabs
    const tabs = document.querySelectorAll(".profile-nav ul li");
    const contents = document.querySelectorAll(".tab-content");

    tabs.forEach(tab => {
        tab.addEventListener("click", () => {
            tabs.forEach(t => t.classList.remove("active"));
            tab.classList.add("active");

            contents.forEach(c => c.classList.remove("active"));
            const target = document.getElementById(tab.dataset.tab);
            if(target) target.classList.add("active");
        });
    });

    // Follow button
    document.addEventListener("DOMContentLoaded", function() {
    const followBtn = document.getElementById("follow-btn");

    if (followBtn) {
        followBtn.addEventListener("click", function() {
            const userId = this.dataset.user;
            const isFollowed = this.classList.contains("followed");

            // Choix de l’URL selon l’état
            const url = isFollowed 
                ? `/unfollow/${userId}/` 
                : `/follow/${userId}/`;

            fetch(url, {
                method: "POST",
                headers: {
                    "X-CSRFToken": getCookie("csrftoken"), // récupère le token CSRF
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ user_id: userId })
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === "ok") {
                    // Toggle état du bouton
                    if (isFollowed) {
                        followBtn.classList.remove("followed");
                        followBtn.textContent = "Suivre";
                    } else {
                        followBtn.classList.add("followed");
                        followBtn.textContent = "Suivi";
                    }
                }
            });
        });
    }
});

// Fonction utilitaire pour récupérer le CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + "=")) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

});

document.addEventListener("DOMContentLoaded", () => {
    const miniPlayer = document.getElementById("mini-player");
    const miniAudio = document.getElementById("mini-audio");
    const miniVideo = document.getElementById("mini-video");
    const miniCover = document.getElementById("mini-cover");
    const miniTitle = document.getElementById("mini-title");
    const miniArtist = document.getElementById("mini-artist");
    const miniClose = document.getElementById("mini-close");
    const pipBtn = document.getElementById("pip-btn");

    function playMedia(type, url, cover, title, artist){
    // Pause tous les médias existants
    miniAudio.pause();
    miniVideo.pause();

    // Met à jour les infos du mini-player
    miniTitle.textContent = title;
    miniArtist.textContent = artist;
    miniCover.src = cover || "/static/img/trackdefault.png";

    if(type === "audio"){
        miniAudio.src = url;
        miniAudio.style.display = "block";
        miniVideo.style.display = "none";
        miniAudio.play().catch(e => console.log("Lecture audio bloquée:", e));
    } else {
        miniVideo.src = url;
        miniVideo.style.display = "block";
        miniAudio.style.display = "none";
        miniVideo.play().catch(e => console.log("Lecture vidéo bloquée:", e));
    }

    // Affiche le mini-player
    miniPlayer.style.display = "flex";
}
        document.querySelectorAll(".tab-content.active .media-item").forEach(item=>{
            item.addEventListener("click", ()=>{ /* déjà géré */ });
        });


    document.querySelectorAll(".media-item").forEach(item=>{
        item.addEventListener("click", ()=>{
            const type = item.dataset.type;
            const url = item.dataset.url;
            const cover = item.dataset.cover;
            const title = item.dataset.title;
            const artist = item.dataset.artist;
            playMedia(type,url,cover,title,artist);
        });
    });

        miniClose.addEventListener("click", ()=>{
            if(miniVideo!==document.pictureInPictureElement){
                miniVideo.pause();
            } else {
                document.exitPictureInPicture().catch(()=>{});
            }
            miniAudio.pause();
            miniPlayer.style.display="none";
        });


    // Picture-in-Picture pour les vidéos
    pipBtn.addEventListener("click", async ()=>{
        if(miniVideo.style.display==="block" && 'pictureInPictureEnabled' in document){
            try{
                if(miniVideo!==document.pictureInPictureElement){
                    await miniVideo.requestPictureInPicture();
                } else {
                    await document.exitPictureInPicture();
                }
            }catch(e){ console.error("PiP error:", e); }
        }
    });

    // Onglets
    document.querySelectorAll(".profile-nav li").forEach(tab=>{
        tab.addEventListener("click", ()=>{
            document.querySelectorAll(".tab-content").forEach(tc=>tc.classList.remove("active"));
            document.querySelectorAll(".profile-nav li").forEach(t=>t.classList.remove("active"));
            tab.classList.add("active");
            document.getElementById(tab.dataset.tab).classList.add("active");
        });
    });
});


// function scrollLeft() {
//     const container = document.getElementById("artistContainer");
//     container.scrollBy({
//         left: -150,
//         behavior: "smooth"
//     });
// }

// function scrollRight() {
//     const container = document.getElementById("artistContainer");
//     container.scrollBy({
//         left: 150,
//         behavior: "smooth"
//     });
// }




document.addEventListener('DOMContentLoaded', () => {
    const container = document.getElementById('artistContainer');

    let isDown = false;
    let startX;
    let scrollLeft;

    container.addEventListener('mousedown', (e) => {
        isDown = true;
        container.classList.add('active');
        startX = e.pageX - container.offsetLeft;
        scrollLeft = container.scrollLeft;
    });

    container.addEventListener('mouseleave', () => {
        isDown = false;
        container.classList.remove('active');
    });

    container.addEventListener('mouseup', () => {
        isDown = false;
        container.classList.remove('active');
    });

    container.addEventListener('mousemove', (e) => {
        if (!isDown) return;
        e.preventDefault();
        const x = e.pageX - container.offsetLeft;
        const walk = (x - startX) * 2; // vitesse du scroll
        container.scrollLeft = scrollLeft - walk;
    });
});
