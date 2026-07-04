"""replace_chord_at tool - Phase 1c editing.

Replaces a chord at a specific bar/beat position in a music21 stream.
"""

import copy
from music21 import stream, chord as m21chord, note as m21note


def replace_chord_at(
    score: stream.Stream,
    bar: int,
    beat: int,
    new_chord: list[str],
) -> stream.Stream:
    """Replace the chord at a specific bar and beat position.

    Args:
        score: A music21 Stream or Score
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

    # Get chord/note elements directly from the stream (not via flatten())
    chords_only = [
        e for e in result
        if isinstance(e, (m21chord.Chord, m21note.Note))
    ]

    if bar < 1 or bar > len(chords_only):
        raise ValueError(f"Bar {bar} is out of range (1-{len(chords_only)})")

    target = chords_only[bar - 1]

    if not isinstance(target, m21chord.Chord):
        raise ValueError(f"Element at bar {bar} is not a chord (got {type(target).__name__})")

    # Modify the chord's pitches in place
    from music21 import pitch as m21pitch
    target.pitches = [m21pitch.Pitch(p) for p in new_chord]

    return result