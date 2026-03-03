"""
Speech Processing Module
Handles audio transcription using OpenAI Whisper (local model).
"""

import whisper
import os
import tempfile

# Ensure ffmpeg is available on PATH (bundled via imageio-ffmpeg)
try:
    import imageio_ffmpeg
    import shutil
    _ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    _ffmpeg_dir = os.path.dirname(_ffmpeg_exe)
    
    # Whisper hardcodes the "ffmpeg" command name, 
    # but imageio-ffmpeg provides something like "ffmpeg-win-x86_64-v7.1.exe".
    # We create a copy as "ffmpeg.exe" if it doesn't already exist.
    _standard_exe = os.path.join(_ffmpeg_dir, "ffmpeg.exe")
    if not os.path.exists(_standard_exe):
        shutil.copy2(_ffmpeg_exe, _standard_exe)
        
    if _ffmpeg_dir not in os.environ.get("PATH", ""):
        os.environ["PATH"] = _ffmpeg_dir + os.pathsep + os.environ.get("PATH", "")
except ImportError:
    pass  # ffmpeg must be installed system-wide if imageio-ffmpeg is not available


# Load the Whisper model once at module level for efficiency
_model = None


def _get_model():
    """Lazy-load the Whisper model (small) on first use."""
    global _model
    if _model is None:
        _model = whisper.load_model("small")
    return _model


def transcribe_audio(file_path: str) -> dict:
    """
    Transcribe an audio file using OpenAI Whisper.

    Args:
        file_path: Path to the audio file (.wav or .mp3)

    Returns:
        dict with keys:
            - text: Full transcript string
            - segments: List of segment dicts from Whisper
            - language: Detected language code
            - duration: Audio duration in seconds
    """
    model = _get_model()
    result = model.transcribe(file_path)

    # Calculate total duration from segments
    duration = 0.0
    if result.get("segments"):
        duration = result["segments"][-1]["end"]

    return {
        "text": result.get("text", "").strip(),
        "segments": result.get("segments", []),
        "language": result.get("language", "en"),
        "duration": duration,
    }
