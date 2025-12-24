import subprocess
import logging
from pathlib import Path
import magic  # python-magic

# =========================
# LOGGING
# =========================
logger = logging.getLogger(__name__)

# =========================
# DOSSIER DE SORTIE
# =========================
OUTPUT_DIR = Path("converted")
OUTPUT_DIR.mkdir(exist_ok=True)

# =========================
# FFMPEG SAFE RUNNER
# =========================
def run_ffmpeg(cmd, output_path):
    """
    Exécute FFmpeg de manière SAFE :
    - limite mémoire
    - évite stdout PIPE (trop gourmand)
    """
    try:
        subprocess.run(
            cmd,
            check=True,
            stdout=subprocess.DEVNULL,   # ⛔ évite explosion mémoire
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
# AUDIO
# =========================
def convert_audio_to_opus(input_path, bitrate="96k"):
    output_path = get_output_path(input_path, ".opus")
    cmd = [
        "ffmpeg", "-y", "-i", str(input_path),
        "-threads", "1",
        "-c:a", "libopus", "-b:a", bitrate,
        str(output_path)
    ]
    return run_ffmpeg(cmd, output_path)

def convert_audio_to_aac(input_path, bitrate="128k"):
    output_path = get_output_path(input_path, ".m4a")
    cmd = [
        "ffmpeg", "-y", "-i", str(input_path),
        "-threads", "1",
        "-c:a", "aac", "-b:a", bitrate,
        str(output_path)
    ]
    return run_ffmpeg(cmd, output_path)

# =========================
# VIDEO (SAFE SETTINGS)
# =========================
def convert_video_to_mp4(input_path, crf="23", preset="veryfast", audio_bitrate="128k"):
    output_path = get_output_path(input_path, ".mp4")
    cmd = [
        "ffmpeg", "-y", "-i", str(input_path),
        "-threads", "1",                 # ✅ limite CPU
        "-c:v", "libx264",
        "-preset", preset,               # ✅ veryfast
        "-crf", str(crf),
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        "-c:a", "aac", "-b:a", audio_bitrate,
        str(output_path)
    ]
    return run_ffmpeg(cmd, output_path)

# ❌ WEBM / VP9 SUPPRIMÉ (trop lourd pour Render)
# def convert_video_to_webm(...): SUPPRIMÉ

# =========================
# THUMBNAILS (SAFE)
# =========================
def generate_thumbnails(input_path, positions=("00:00:01",)):
    thumbs = []

    for pos in positions:
        output_path = OUTPUT_DIR / f"{Path(input_path).stem}_{pos.replace(':','-')}.jpg"
        cmd = [
            "ffmpeg", "-y", "-i", str(input_path),
            "-threads", "1",
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
    with open(input_path, "rb") as f:
        return magic.from_buffer(f.read(2048), mime=True)

# =========================
# PIPELINE PRINCIPALE
# =========================
def process_media(input_path):
    """
    Pipeline SAFE :
    - pas de VP9
    - CPU limité
    - mémoire contrôlée
    """
    mime = detect_mime(input_path)
    results = {}

    logger.info(f"🎬 Début pipeline pour {input_path} ({mime})")

    if mime.startswith("audio"):
        results["opus"] = convert_audio_to_opus(input_path)
        results["aac"] = convert_audio_to_aac(input_path)

    elif mime.startswith("video"):
        results["mp4"] = convert_video_to_mp4(input_path)
        results["thumbs"] = generate_thumbnails(input_path)

    logger.info(f"✅ Pipeline terminée pour {input_path}")
    return results
