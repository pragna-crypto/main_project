"""
AI Public Speaking Confidence Analyzer — Backend
Flask API server with a single POST /analyze endpoint.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import tempfile

from speech_processing import transcribe_audio
from scoring import analyze

app = Flask(__name__)
CORS(app)

ALLOWED_EXTENSIONS = {"wav", "mp3"}
MAX_CONTENT_LENGTH = 25 * 1024 * 1024  # 25 MB
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH


def _allowed_file(filename: str) -> bool:
    """Check if the uploaded file has an allowed extension."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/analyze", methods=["POST"])
def analyze_speech():
    """
    Analyze an uploaded audio file.

    Expects: multipart/form-data with an 'audio' file field (.wav or .mp3)

    Returns JSON:
        {
            "transcript": str,
            "wpm": int,
            "filler_count": int,
            "pause_count": int,
            "confidence_score": int
        }
    """
    # --- Validate upload ---
    if "audio" not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    file = request.files["audio"]

    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    if not _allowed_file(file.filename):
        return jsonify({"error": "Invalid file type. Only .wav and .mp3 are accepted"}), 400

    # --- Save to temp file ---
    try:
        suffix = os.path.splitext(secure_filename(file.filename))[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            file.save(tmp)
            tmp_path = tmp.name

        # --- Transcribe ---
        transcription = transcribe_audio(tmp_path)
        transcript = transcription["text"]
        segments = transcription["segments"]
        duration = transcription["duration"]

        # --- Score ---
        metrics = analyze(transcript, segments, duration)

        return jsonify({
            "transcript": transcript,
            "wpm": metrics["wpm"],
            "filler_count": metrics["filler_count"],
            "pause_count": metrics["pause_count"],
            "confidence_score": metrics["confidence_score"],
        })

    except Exception as e:
        return jsonify({"error": f"Processing failed: {str(e)}"}), 500

    finally:
        # Clean up temp file
        if "tmp_path" in locals() and os.path.exists(tmp_path):
            os.unlink(tmp_path)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
