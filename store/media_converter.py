import subprocess
import logging
from pathlib import Path
import magic
import boto3
import os
import shutil
import multiprocessing
from django.conf import settings
import tempfile  # <-- ajoute ça

logger = logging.getLogger(__name__)

# =========================
# DOSSIER TEMPORAIRE LOCALE
# =========================
OUTPUT_DIR = Path(tempfile.gettempdir()) / "converted"
OUTPUT_DIR.mkdir(exist_ok=True)

# Nombre de threads pour FFmpeg
THREADS = str(max(1, multiprocessing.cpu_count() // 2))

# Client S3 (Backblaze B2)
s3 = boto3.client(
    "s3",
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    endpoint_url=settings.AWS_S3_ENDPOINT_URL,
)

# =========================
# FFmpeg SAFE RUNNER
# =========================
def run_ffmpeg(cmd, output_path, verbose=False):
    logger.info(f"▶️ Commande FFmpeg : {' '.join(cmd)}")
    try:
        subprocess.run(
            cmd,
            check=True,
            stdout=None if verbose else subprocess.DEVNULL,
            stderr=subprocess.PIPE
        )
        logger.info(f"✅ Conversion réussie : {output_path}")
        return str(output_path)
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Erreur FFmpeg : {e.stderr.decode(errors='ignore')}")
        return None

def get_output_path(input_path, suffix):
    return OUTPUT_DIR / (Path(input_path).stem + suffix)

# =========================
# AUDIO / VIDEO / THUMBNAILS
# =========================
def convert_audio_to_opus(input_path, bitrate="96k"):
    output_path = get_output_path(input_path, ".opus")
    cmd = [
        "ffmpeg", "-y", "-i", str(input_path),
        "-threads", THREADS,
        "-c:a", "libopus", "-b:a", bitrate,
        str(output_path)
    ]
    return run_ffmpeg(cmd, output_path)

def convert_audio_to_aac(input_path, bitrate="128k"):
    output_path = get_output_path(input_path, ".m4a")
    cmd = [
        "ffmpeg", "-y", "-i", str(input_path),
        "-threads", THREADS,
        "-c:a", "aac", "-b:a", bitrate,
        str(output_path)
    ]
    return run_ffmpeg(cmd, output_path)

def convert_video_to_mp4(input_path, crf="23", preset="veryfast", audio_bitrate="128k"):
    output_path = get_output_path(input_path, ".mp4")
    cmd = [
        "ffmpeg", "-y", "-i", str(input_path),
        "-threads", THREADS,
        "-c:v", "libx264",
        "-preset", preset,
        "-crf", str(crf),
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        "-c:a", "aac", "-b:a", audio_bitrate,
        str(output_path)
    ]
    return run_ffmpeg(cmd, output_path)

def generate_thumbnails(input_path, positions=("00:00:01",)):
    thumbs = []
    for pos in positions:
        output_path = OUTPUT_DIR / f"{Path(input_path).stem}_{pos.replace(':','-')}.jpg"
        cmd = [
            "ffmpeg", "-y", "-i", str(input_path),
            "-threads", THREADS,
            "-ss", pos,
            "-vframes", "1",
            str(output_path)
        ]
        result = run_ffmpeg(cmd, output_path)
        if result:
            thumbs.append(result)
    return thumbs

# =========================
# MIME DETECTION
# =========================
def detect_mime(input_path):
    if not Path(input_path).exists():
        logger.error(f"❌ Fichier introuvable : {input_path}")
        return None
    with open(input_path, "rb") as f:
        return magic.from_buffer(f.read(2048), mime=True)

# =========================
# UPLOAD DIRECT VERS B2
# =========================
def upload_to_b2(local_path, remote_name):
    try:
        with open(local_path, "rb") as f:
            s3.upload_fileobj(f, settings.AWS_STORAGE_BUCKET_NAME, remote_name)
        logger.info(f"☁️ Upload réussi : {remote_name}")
        return remote_name
    except Exception as e:
        logger.error(f"❌ Erreur upload B2 : {e}")
        return None

# =========================
# PIPELINE PRINCIPALE
# =========================
def process_media(input_path, remote_prefix="converted/"):
    """
    Pipeline média SAFE :
    - audio → opus + aac
    - video → mp4 + thumbnails
    - upload direct sur B2
    """
    mime = detect_mime(input_path)
    if not mime:
        return {"error": f"Fichier introuvable : {input_path}"}

    results = {}
    logger.info(f"🎬 Début pipeline pour {input_path} ({mime})")

    if mime.startswith("audio"):
        opus = convert_audio_to_opus(input_path)
        aac = convert_audio_to_aac(input_path)
        if opus: results["opus"] = upload_to_b2(opus, remote_prefix + Path(opus).name)
        if aac: results["aac"] = upload_to_b2(aac, remote_prefix + Path(aac).name)
    elif mime.startswith("video"):
        mp4 = convert_video_to_mp4(input_path)
        thumbs = generate_thumbnails(input_path)
        if mp4: results["mp4"] = upload_to_b2(mp4, remote_prefix + Path(mp4).name)
        if thumbs:
            results["thumbs"] = []
            for thumb in thumbs:
                uploaded = upload_to_b2(thumb, remote_prefix + Path(thumb).name)
                if uploaded:
                    results["thumbs"].append(uploaded)

    # Nettoyage des fichiers temporaires
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
        OUTPUT_DIR.mkdir(exist_ok=True)
        logger.info("🧹 Dossier converted nettoyé")

    logger.info(f"✅ Pipeline terminée pour {input_path}")
    return results
