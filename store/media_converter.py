import subprocess
import logging
import os
from pathlib import Path
import mimetypes
import magic  # plus fiable que mimetypes seul

# Configuration des logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Dossier de sortie temporaire (sur Render)
OUTPUT_DIR = Path("converted")
OUTPUT_DIR.mkdir(exist_ok=True)

def run_ffmpeg(cmd, output_path):
    """Exécute FFmpeg avec gestion des erreurs et logs."""
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        logger.info(f"✅ Conversion réussie : {output_path}")
        return str(output_path)
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Erreur FFmpeg : {e.stderr.decode()}")
        return None

def get_output_path(input_path, suffix):
    """Construit le chemin de sortie dans le dossier converted/."""
    return OUTPUT_DIR / (Path(input_path).stem + suffix)

# =========================
# AUDIO
# =========================
def convert_audio_to_opus(input_path, bitrate="96k"):
    output_path = get_output_path(input_path, ".opus")
    cmd = ["ffmpeg", "-y", "-i", str(input_path), "-c:a", "libopus", "-b:a", bitrate, str(output_path)]
    return run_ffmpeg(cmd, output_path)

def convert_audio_to_aac(input_path, bitrate="128k"):
    output_path = get_output_path(input_path, ".m4a")
    cmd = ["ffmpeg", "-y", "-i", str(input_path), "-c:a", "aac", "-b:a", bitrate, str(output_path)]
    return run_ffmpeg(cmd, output_path)

# =========================
# VIDEO
# =========================
def convert_video_to_mp4(input_path, crf="22", preset="slow", audio_bitrate="128k"):
    output_path = get_output_path(input_path, ".mp4")
    cmd = [
        "ffmpeg", "-y", "-i", str(input_path),
        "-c:v", "libx264", "-preset", preset, "-crf", str(crf),
        "-pix_fmt", "yuv420p",  # ✅ compatibilité Safari/iOS
        "-movflags", "+faststart",
        "-c:a", "aac", "-b:a", audio_bitrate,
        str(output_path)
    ]
    return run_ffmpeg(cmd, output_path)

def convert_video_to_webm(input_path, crf="32", audio_bitrate="96k"):
    output_path = get_output_path(input_path, ".webm")
    cmd = [
        "ffmpeg", "-y", "-i", str(input_path),
        "-c:v", "libvpx-vp9", "-crf", str(crf), "-b:v", "0",
        "-c:a", "libopus", "-b:a", audio_bitrate,
        str(output_path)
    ]
    return run_ffmpeg(cmd, output_path)

# =========================
# THUMBNAILS
# =========================
def generate_video_thumbnail(input_path, time_position="00:00:01"):
    output_path = get_output_path(input_path, ".jpg")
    cmd = ["ffmpeg", "-y", "-i", str(input_path), "-ss", time_position, "-vframes", "1", str(output_path)]
    return run_ffmpeg(cmd, output_path)

def generate_thumbnails(input_path, positions=["00:00:01", "00:00:05", "00:00:10"]):
    thumbs = []
    for pos in positions:
        output_path = OUTPUT_DIR / f"{Path(input_path).stem}_{pos.replace(':','-')}.jpg"
        cmd = ["ffmpeg", "-y", "-i", str(input_path), "-ss", pos, "-vframes", "1", str(output_path)]
        result = run_ffmpeg(cmd, output_path)
        if result:
            thumbs.append(result)
    return thumbs

# =========================
# PIPELINE UNIFIÉE
# =========================
def detect_mime(input_path):
    """Détection MIME fiable avec python-magic."""
    with open(input_path, "rb") as f:
        return magic.from_buffer(f.read(2048), mime=True)

def process_media(input_path):
    """Pipeline complète : audio, vidéo, thumbnails."""
    mime = detect_mime(input_path)
    results = {}
    try:
        if mime.startswith("audio"):
            results["opus"] = convert_audio_to_opus(input_path)
            results["aac"] = convert_audio_to_aac(input_path)
        elif mime.startswith("video"):
            results["mp4"] = convert_video_to_mp4(input_path)
            results["webm"] = convert_video_to_webm(input_path)
            results["thumbs"] = generate_thumbnails(input_path)
        logger.info(f"✅ Pipeline terminée pour {input_path}")
        return results   # ✅ plus simple pour tasks.py
    except Exception as e:
        logger.error(f"❌ Erreur pipeline {input_path}: {e}")
        raise


