document.addEventListener('DOMContentLoaded', function () {

    window.videoPlay = function (video_id) {
        fetch(`/store/video/play/${video_id}/`)
            .then(response => response.json())
            .then(data => {
                console.log('Compteur de lecture mis à jour :', data.play_count);
            })
            .catch(error => {
                console.error('Erreur lors de la mise à jour du compteur de lecture:', error);
            });
    };

    window.removeSkeleton = function (videoElement) {
        videoElement.classList.remove('skeleton');
    };

});
