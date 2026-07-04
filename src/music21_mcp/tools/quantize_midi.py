"""quantize_midi tool - Phase 1c editing.

Snaps note timings to a rhythmic grid (quarter, eighth, sixteenth notes).
"""

import copy
from music21 import stream


def quantize_midi(
    score: stream.Stream,
    grid: str = "sixteenth",
) -> stream.Stream:
    """Quantize note timings to a rhythmic grid.

    Args:
        score: A music21 Stream or Score
        grid: Grid resolution — 'quarter' (1.0), 'eighth' (0.5),
              'sixteenth' (0.25)

    Returns:
        A new stream with quantized note offsets

    Raises:
        TypeError: If score is not a Stream
        ValueError: If grid is not recognized
    """
    if not isinstance(score, stream.Stream):
        raise TypeError(f"Expected music21 Stream, got {type(score).__name__}")

    grid_values = {
        "quarter": 1.0,
        "eighth": 0.5,
        "sixteenth": 0.25,
    }

    if grid not in grid_values:
        raise ValueError(
            f"Invalid grid '{grid}'. Must be one of: {list(grid_values.keys())}"
        )

    grid_size = grid_values[grid]
    result = copy.deepcopy(score)

    # Iterate over all elements and snap their offsets
    for elem in result:
        offset = elem.offset
        snapped = round(offset / grid_size) * grid_size
        # Offset is relative to the containing stream
        elem.offset = snapped

    return result