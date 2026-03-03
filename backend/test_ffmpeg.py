import os
import sys

# Add backend directory to path so we can import our module
sys.path.append(r"d:\pragna repose\main_project\backend")

from speech_processing import transcribe_audio

# Let's see if ffmpeg is found
import subprocess

try:
    subprocess.run(["ffmpeg", "-version"], check=True, capture_output=True)
    print("✅ ffmpeg is found on PATH!")
except Exception as e:
    print(f"❌ ffmpeg could not be run: {e}")

