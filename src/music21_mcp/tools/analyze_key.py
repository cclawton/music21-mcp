"""analyze_key tool - Phase 1a core.

Uses music21's key analysis to determine the key of a stream.
"""

from music21 import stream, key


def analyze_key(score: stream.Stream) -> dict:
    """Analyze the key of a music21 stream.

    Args:
        score: A music21 Stream or Score

    Returns:
        dict with keys: 'key' (str), 'mode' (str), 'confidence' (float)
    """
    if not isinstance(score, stream.Stream):
        raise TypeError(f"Expected music21 Stream, got {type(score).__name__}")

    detected = score.analyze("key")

    # music21 Key object: .tonic.name gives note name, .mode gives 'major'/'minor'
    tonic_name = detected.tonic.name if detected.tonic else "Unknown"
    mode = detected.mode if detected.mode else "unknown"

    # Confidence: correlation coefficient from the analysis
    # music21 stores this on the Key object's alternateInterpretations
    confidence = 0.0
    if hasattr(detected, "correlationCoefficient"):
        confidence = round(detected.correlationCoefficient, 3)

    return {
        "key": f"{tonic_name} {mode}",
        "mode": mode,
        "confidence": confidence,
    }