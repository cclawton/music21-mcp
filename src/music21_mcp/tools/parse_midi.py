"""parse_midi_file tool - Phase 1a core."""

from pathlib import Path
from music21 import converter


def parse_midi_file(filepath: str):
    """Load a MIDI file and return a music21 stream.

    Args:
        filepath: Path to .mid file

    Returns:
        music21.stream.Score or Stream
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"MIDI file not found: {filepath}")
    return converter.parse(str(path))