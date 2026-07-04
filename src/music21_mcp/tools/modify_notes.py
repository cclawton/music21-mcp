"""modify_notes tool - Phase 1c editing.

Filter, remove, select, or octave-shift notes in a music21 stream
by pitch criteria.
"""

import copy
from music21 import stream, note as m21note, pitch as m21pitch


def modify_notes(
    score: stream.Stream,
    action: str = "remove",
    filter_below: str | None = None,
    filter_above: str | None = None,
    octave_shift: int | None = None,
) -> stream.Stream:
    """Modify notes in a stream based on pitch criteria.

    Args:
        score: A music21 Stream or Score
        action: One of 'remove', 'select', 'shift_octave'
        filter_below: Remove/select notes below this pitch (e.g. "C4")
        filter_above: Remove/select notes above this pitch (e.g. "G5")
        octave_shift: Number of octaves to shift (for 'shift_octave' action)

    Returns:
        A new modified stream

    Raises:
        TypeError: If score is not a Stream
        ValueError: If action is not recognized
    """
    if not isinstance(score, stream.Stream):
        raise TypeError(f"Expected music21 Stream, got {type(score).__name__}")

    valid_actions = {"remove", "select", "shift_octave"}
    if action not in valid_actions:
        raise ValueError(
            f"Invalid action '{action}'. Must be one of: {valid_actions}"
        )

    result = copy.deepcopy(score)

    if action == "shift_octave":
        if octave_shift is None:
            octave_shift = 0
        for n in result.flatten().notes:
            if isinstance(n, m21note.Note):
                n.octave += octave_shift
            elif hasattr(n, "pitches"):
                for p in n.pitches:
                    p.octave += octave_shift
        return result

    # For remove and select, we need filter boundaries
    low_pitch = m21pitch.Pitch(filter_below) if filter_below else None
    high_pitch = m21pitch.Pitch(filter_above) if filter_above else None

    # Collect elements to keep or remove
    elements_to_keep = []
    flat = result.flatten()

    for elem in flat.notes:
        keep = True

        # Get the pitches of this element
        if isinstance(elem, m21note.Note):
            elem_pitches = [elem.pitch]
        elif hasattr(elem, "pitches"):
            elem_pitches = elem.pitches
        else:
            elem_pitches = []

        for p in elem_pitches:
            if low_pitch and p < low_pitch:
                keep = False
                break
            if high_pitch and p > high_pitch:
                keep = False
                break

        if action == "remove":
            if keep:
                elements_to_keep.append(elem)
        elif action == "select":
            if keep:
                elements_to_keep.append(elem)

    # Build a new stream with the kept elements
    new_stream = stream.Stream()
    for elem in elements_to_keep:
        new_stream.append(copy.deepcopy(elem))

    return new_stream