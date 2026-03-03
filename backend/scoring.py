"""
Scoring Module
Actual scoring logic for speech analysis.
"""

import re

def calculate_wpm(transcript: str, duration_seconds: float) -> int:
    """
    Calculate words per minute.

    Args:
        transcript: The full transcript text.
        duration_seconds: Total audio duration in seconds.

    Returns:
        Words per minute as an integer.
    """
    if duration_seconds <= 0:
        return 0
    words = transcript.split()
    wpm = (len(words) / duration_seconds) * 60
    return int(wpm)


def count_filler_words(transcript: str) -> int:
    """
    Count filler words (um, uh, like, you know, etc.) in the transcript.

    Args:
        transcript: The full transcript text.

    Returns:
        Total count of filler words.
    """
    filler_words_pattern = r'\b(um|uh|like|you know|basically|actually|right|so|well)\b'
    matches = re.findall(filler_words_pattern, transcript, flags=re.IGNORECASE)
    return len(matches)


def count_pauses(segments: list, threshold_seconds: float = 1.0) -> int:
    """
    Count significant pauses between speech segments.

    Args:
        segments: List of Whisper segment dicts with 'start' and 'end' keys.
        threshold_seconds: Minimum gap in seconds to be considered a pause.

    Returns:
        Number of significant pauses detected.
    """
    pause_count = 0
    if not segments:
        return 0
        
    for i in range(1, len(segments)):
        prev_end = segments[i-1].get("end", 0)
        curr_start = segments[i].get("start", 0)
        gap = curr_start - prev_end
        if gap >= threshold_seconds:
            pause_count += 1
            
    return pause_count


def calculate_confidence_score(
    wpm: int, filler_count: int, pause_count: int
) -> int:
    """
    Calculate an overall confidence score (0-100).

    Args:
        wpm: Words per minute.
        filler_count: Number of filler words.
        pause_count: Number of pauses.

    Returns:
        Confidence score from 0 to 100.
    """
    score = 100
    
    # 1. WPM Penalty
    # Optimal speaking rate is generally between 130 and 160 WPM.
    if wpm < 110:
        score -= min(20, (110 - wpm) // 2)  # Penalize slow
    elif wpm > 180:
        score -= min(20, (wpm - 180) // 2)  # Penalize fast
        
    # 2. Filler Word Penalty
    # We deduct 3 points for every filler word, max 30 point penalty
    score -= min(30, filler_count * 3)
    
    # 3. Pause Penalty
    # We deduct 4 points for every significant pause, max 30 point penalty
    score -= min(30, pause_count * 4)
    
    # Ensure score stays bounded [0, 100]
    return max(0, min(100, score))


def analyze(transcript: str, segments: list, duration_seconds: float) -> dict:
    """
    Run the full analysis pipeline and return all metrics.

    Args:
        transcript: The full transcript text.
        segments: List of Whisper segment dicts.
        duration_seconds: Total audio duration in seconds.

    Returns:
        dict with keys: wpm, filler_count, pause_count, confidence_score
    """
    wpm = calculate_wpm(transcript, duration_seconds)
    filler_count = count_filler_words(transcript)
    pause_count = count_pauses(segments)
    confidence_score = calculate_confidence_score(wpm, filler_count, pause_count)

    return {
        "wpm": wpm,
        "filler_count": filler_count,
        "pause_count": pause_count,
        "confidence_score": confidence_score,
    }
