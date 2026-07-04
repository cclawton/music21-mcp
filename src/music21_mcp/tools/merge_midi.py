"""merge_midi tool - Phase 1c editing.

Overlays two music21 streams into a single stream or multi-part score.
"""

import copy
from music21 import stream


def merge_midi(
    stream_a: stream.Stream,
    stream_b: stream.Stream,
    output_parts: bool = False,
) -> stream.Stream:
    """Merge (overlay) two streams into one.

    Args:
        stream_a: First stream (e.g. melody)
        stream_b: Second stream (e.g. bass line)
        output_parts: If True, return a Score with 2 Parts.
                      If False, return a single Stream with all elements merged.

    Returns:
        A merged stream or score

    Raises:
        TypeError: If either input is not a Stream
    """
    if not isinstance(stream_a, stream.Stream):
        raise TypeError(f"Expected music21 Stream for first arg, got {type(stream_a).__name__}")
    if not isinstance(stream_b, stream.Stream):
        raise TypeError(f"Expected music21 Stream for second arg, got {type(stream_b).__name__}")

    a_copy = copy.deepcopy(stream_a)
    b_copy = copy.deepcopy(stream_b)

    if output_parts:
        result = stream.Score()
        part_a = stream.Part()
        part_b = stream.Part()

        for elem in a_copy:
            part_a.append(copy.deepcopy(elem))
        for elem in b_copy:
            part_b.append(copy.deepcopy(elem))

        result.append(part_a)
        result.append(part_b)
        return result

    # Simple merge: append all elements from both into a single Part
    # Wrap in a Part so music21 can export to MIDI (flat streams fail)
    result = stream.Part()
    for elem in a_copy:
        result.append(copy.deepcopy(elem))
    for elem in b_copy:
        result.append(copy.deepcopy(elem))

    return result