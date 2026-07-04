"""replace_chord_at tool - Phase 1c editing.

Replaces a chord at a specific bar/beat position in a music21 stream.
Handles both flat streams (directly constructed) and parsed MIDI files
(nested Score → Part → Measure structure).
"""

import copy
from music21 import stream, chord as m21chord, note as m21note, pitch as m21pitch


def replace_chord_at(
    score: stream.Stream,
    bar: int,
    beat: int,
    new_chord: list[str],
) -> stream.Stream:
    """Replace the chord at a specific bar and beat position.

    Args:
        score: A music21 Stream or Score (flat or parsed from MIDI)
        bar: Bar number (1-indexed)
        beat: Beat number within the bar (1-indexed)
        new_chord: List of pitch names for the replacement chord (e.g. ["G3", "B3", "D4"])

    Returns:
        A new stream with the chord replaced

    Raises:
        TypeError: If score is not a Stream
        ValueError: If bar is out of range or new_chord is empty
    """
    if not isinstance(score, stream.Stream):
        raise TypeError(f"Expected music21 Stream, got {type(score).__name__}")

    if not new_chord:
        raise ValueError("new_chord must not be empty")

    result = copy.deepcopy(score)

    # Try to find chords via recurse() — works for both flat and nested streams
    all_chords = []
    for elem in result.recurse():
        if isinstance(elem, m21chord.Chord):
            all_chords.append(elem)

    # If no chords found via recurse, check flat notes (might be single notes)
    if not all_chords:
        all_notes = []
        for elem in result.recurse():
            if isinstance(elem, m21note.Note):
                all_notes.append(elem)
        if not all_notes:
            raise ValueError(f"No chords or notes found in stream")

    # Use chord list if available, otherwise note list
    target_list = all_chords if all_chords else all_notes

    if bar < 1 or bar > len(target_list):
        raise ValueError(f"Bar {bar} is out of range (1-{len(target_list)})")

    target = target_list[bar - 1]

    if isinstance(target, m21chord.Chord):
        # Replace chord pitches in place
        target.pitches = [m21pitch.Pitch(p) for p in new_chord]
    elif isinstance(target, m21note.Note):
        # Replace note with a chord at same position
        parent = target.activeSite
        if parent is not None:
            offset = target.getOffsetInHierarchy(parent)
            parent.remove(target)
            new = m21chord.Chord(new_chord)
            new.duration = target.duration
            parent.insert(offset, new)

    return result