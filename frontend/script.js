/**
 * AI Public Speaking Confidence Analyzer — Frontend Logic
 * Handles file upload, API communication, and results rendering.
 */

(() => {
    "use strict";

    // ── Config ──────────────────────────────────────────────
    const API_URL = "http://localhost:5000/analyze";
    const MAX_FILE_SIZE = 25 * 1024 * 1024; // 25 MB

    // ── DOM References ──────────────────────────────────────
    const uploadSection = document.getElementById("upload-section");
    const resultsSection = document.getElementById("results-section");
    const uploadForm = document.getElementById("upload-form");
    const audioInput = document.getElementById("audio-input");
    const dropZone = document.getElementById("drop-zone");
    const fileInfo = document.getElementById("file-info");
    const fileName = document.getElementById("file-name");
    const clearFileBtn = document.getElementById("clear-file");
    const analyzeBtn = document.getElementById("analyze-btn");
    const btnLabel = analyzeBtn.querySelector(".btn__label");
    const btnLoader = analyzeBtn.querySelector(".btn__loader");
    const errorMsg = document.getElementById("error-msg");
    const backBtn = document.getElementById("back-btn");

    // Results
    const scoreNumber = document.getElementById("score-number");
    const scoreRingFill = document.getElementById("score-ring-fill");
    const valWpm = document.getElementById("val-wpm");
    const valFiller = document.getElementById("val-filler");
    const valPauses = document.getElementById("val-pauses");
    const barWpm = document.getElementById("bar-wpm");
    const barFiller = document.getElementById("bar-filler");
    const barPauses = document.getElementById("bar-pauses");
    const transcriptText = document.getElementById("transcript-text");

    let selectedFile = null;

    // ── Inject SVG gradient for the score ring ──────────────
    (() => {
        const svg = document.querySelector(".score-ring");
        if (!svg) return;
        const defs = document.createElementNS("http://www.w3.org/2000/svg", "defs");
        const grad = document.createElementNS("http://www.w3.org/2000/svg", "linearGradient");
        grad.setAttribute("id", "ring-gradient");
        grad.setAttribute("x1", "0%"); grad.setAttribute("y1", "0%");
        grad.setAttribute("x2", "100%"); grad.setAttribute("y2", "0%");
        const s1 = document.createElementNS("http://www.w3.org/2000/svg", "stop");
        s1.setAttribute("offset", "0%"); s1.setAttribute("stop-color", "#3b82f6");
        const s2 = document.createElementNS("http://www.w3.org/2000/svg", "stop");
        s2.setAttribute("offset", "100%"); s2.setAttribute("stop-color", "#a855f7");
        grad.appendChild(s1); grad.appendChild(s2);
        defs.appendChild(grad);
        svg.prepend(defs);
    })();

    // ── Helpers ─────────────────────────────────────────────
    function showError(msg) {
        errorMsg.textContent = msg;
        errorMsg.classList.remove("hidden");
    }
    function hideError() {
        errorMsg.classList.add("hidden");
    }
    function setLoading(loading) {
        analyzeBtn.disabled = loading;
        btnLabel.classList.toggle("hidden", loading);
        btnLoader.classList.toggle("hidden", !loading);
    }
    function selectFile(file) {
        if (!file) return;
        const ext = file.name.split(".").pop().toLowerCase();
        if (!["wav", "mp3"].includes(ext)) {
            showError("Invalid file type. Please upload a .wav or .mp3 file.");
            return;
        }
        if (file.size > MAX_FILE_SIZE) {
            showError("File is too large. Maximum size is 25 MB.");
            return;
        }
        hideError();
        selectedFile = file;
        fileName.textContent = file.name;
        fileInfo.classList.remove("hidden");
        dropZone.classList.add("hidden");
        analyzeBtn.disabled = false;
    }
    function clearFile() {
        selectedFile = null;
        audioInput.value = "";
        fileInfo.classList.add("hidden");
        dropZone.classList.remove("hidden");
        analyzeBtn.disabled = true;
        hideError();
    }

    // ── Drag & Drop ─────────────────────────────────────────
    ["dragenter", "dragover"].forEach(evt =>
        dropZone.addEventListener(evt, e => {
            e.preventDefault();
            dropZone.classList.add("drop-zone--active");
        })
    );
    ["dragleave", "drop"].forEach(evt =>
        dropZone.addEventListener(evt, e => {
            e.preventDefault();
            dropZone.classList.remove("drop-zone--active");
        })
    );
    dropZone.addEventListener("drop", e => {
        const file = e.dataTransfer?.files[0];
        if (file) selectFile(file);
    });

    // ── File Input Change ───────────────────────────────────
    audioInput.addEventListener("change", () => {
        if (audioInput.files[0]) selectFile(audioInput.files[0]);
    });

    // ── Clear File ──────────────────────────────────────────
    clearFileBtn.addEventListener("click", clearFile);

    // ── Form Submit ─────────────────────────────────────────
    uploadForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        if (!selectedFile) return;

        hideError();
        setLoading(true);

        try {
            const formData = new FormData();
            formData.append("audio", selectedFile);

            const res = await fetch(API_URL, {
                method: "POST",
                body: formData,
            });

            const data = await res.json();

            if (!res.ok) {
                throw new Error(data.error || "Server error");
            }

            renderResults(data);
        } catch (err) {
            showError(err.message || "Failed to connect to the server. Is the backend running?");
        } finally {
            setLoading(false);
        }
    });

    // ── Back Button ─────────────────────────────────────────
    backBtn.addEventListener("click", () => {
        resultsSection.classList.add("hidden");
        uploadSection.classList.remove("hidden");
        clearFile();
    });

    // ── Render Results ──────────────────────────────────────
    function renderResults(data) {
        uploadSection.classList.add("hidden");
        resultsSection.classList.remove("hidden");

        // Confidence score ring
        const score = Math.min(Math.max(data.confidence_score, 0), 100);
        const circumference = 2 * Math.PI * 60; // r = 60
        const offset = circumference - (score / 100) * circumference;
        scoreRingFill.style.strokeDashoffset = offset;
        animateCounter(scoreNumber, score);

        // WPM (scale: 0-250 wpm)
        valWpm.textContent = data.wpm;
        barWpm.style.width = Math.min((data.wpm / 250) * 100, 100) + "%";

        // Filler words (scale: 0-50)
        valFiller.textContent = data.filler_count;
        barFiller.style.width = Math.min((data.filler_count / 50) * 100, 100) + "%";

        // Pauses (scale: 0-30)
        valPauses.textContent = data.pause_count;
        barPauses.style.width = Math.min((data.pause_count / 30) * 100, 100) + "%";

        // Transcript
        transcriptText.textContent = data.transcript || "(No transcript available)";
    }

    // ── Animated Counter ────────────────────────────────────
    function animateCounter(el, target) {
        const duration = 1000;
        const start = performance.now();
        const from = 0;

        function tick(now) {
            const progress = Math.min((now - start) / duration, 1);
            const eased = 1 - Math.pow(1 - progress, 3); // ease-out cubic
            el.textContent = Math.round(from + (target - from) * eased);
            if (progress < 1) requestAnimationFrame(tick);
        }
        requestAnimationFrame(tick);
    }
})();
