"""transpose_midi tool - Phase 1c editing.

Transposes a music21 stream by semitones or to a target key.
"""

from music21 import stream, pitch, interval


def transpose_midi(
    score: stream.Stream,
    semitones: int | None = None,
    target_key: str | None = None,
) -> stream.Stream:
    """Transpose a music21 stream.

    Args:
        score: A music21 Stream or Score
        semitones: Number of semitones to transpose (can be negative)
        target_key: Target key name (e.g. "F", "Bb") — alternative to semitones

    Returns:
        A new transposed music21 Stream

    Raises:
        TypeError: If score is not a Stream
        ValueError: If neither semitones nor target_key is provided
    """
    if not isinstance(score, stream.Stream):
        raise TypeError(f"Expected music21 Stream, got {type(score).__name__}")

    if semitones is None and target_key is None:
        raise ValueError("Must provide either 'semitones' or 'target_key'")

    if semitones is not None:
        # Transpose by semitones directly
        return score.transpose(semitones)

    # Transpose to target key
    # Detect current key, compute interval to target
    current_key = score.analyze("key")
    current_tonic = current_key.tonic

    target_pitch = pitch.Pitch(target_key)
    interval_distance = interval.Interval(current_tonic, target_pitch)

    return score.transpose(interval_distance)