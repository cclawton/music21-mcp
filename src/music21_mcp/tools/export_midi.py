"""export_midi tool - Phase 1a core.

Writes a music21 stream to a MIDI file.
"""

from pathlib import Path
from music21 import stream


def export_midi(score: stream.Stream, filepath: str) -> dict:
    """Export a music21 stream to a MIDI file.

    Args:
        score: A music21 Stream or Score
        filepath: Output path for .mid file

    Returns:
        dict with 'success' (bool) and 'path' (str)
    """
    if not isinstance(score, stream.Stream):
        raise TypeError(f"Expected music21 Stream, got {type(score).__name__}")

    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)

    score.write("midi", fp=str(path))

    return {"success": True, "path": str(path)}