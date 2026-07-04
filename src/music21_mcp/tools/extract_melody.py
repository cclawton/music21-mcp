"""extract_melody tool - Phase 3 advanced analysis.

Extracts the melody line from a multi-part score or interleaved stream.
Strategy: for each time offset, keep the highest-pitched note.

Handles:
  - Multi-part Scores: flattens and selects highest note at each offset
  - Flat streams with interleaved notes: keeps highest note at each offset
"""

import copy
from music21 import stream, note as m21note


def extract_melody(score: stream.Stream) -> stream.Stream:
    """Extract the melody line from a music21 stream.

    Args:
        score: A music21 Stream, Score, or Part

    Returns:
        A new Stream containing only the melody notes (highest pitch line)

    Raises:
        TypeError: If score is not a Stream
    """
    if not isinstance(score, stream.Stream):
        raise TypeError(f"Expected music21 Stream, got {type(score).__name__}")

    # Flatten the stream to get all notes at their absolute offsets
    flat = score.flatten()

    # Collect all notes with their offsets
    # Group by rounded offset to handle minor timing differences
    notes_at_offsets = {}  # rounded_offset -> list of (note, pitch_int)

    for elem in flat.notes:
        if isinstance(elem, m21note.Note):
            offset = round(float(elem.offset), 2)
            pitch_int = elem.pitch.ps  # MIDI note number
            if offset not in notes_at_offsets:
                notes_at_offsets[offset] = []
            notes_at_offsets[offset].append((copy.deepcopy(elem), pitch_int))

    if not notes_at_offsets:
        return stream.Stream()

    # For each time offset, pick the highest-pitched note
    melody = stream.Stream()
    for offset in sorted(notes_at_offsets.keys()):
        candidates = notes_at_offsets[offset]
        # Pick the note with the highest pitch
        best_note = max(candidates, key=lambda x: x[1])[0]
        melody.insert(offset, best_note)

    return melody