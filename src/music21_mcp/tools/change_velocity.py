"""change_velocity tool - Phase 1c editing.

Adjusts MIDI velocity (dynamics) of notes in a music21 stream.
Supports three modes: scale (multiply), absolute (set), offset (add/subtract).
"""

from music21 import stream, volume


def change_velocity(
    score: stream.Stream,
    scale: float | None = None,
    absolute: int | None = None,
    offset: int | None = None,
) -> stream.Stream:
    """Change velocity of all notes in a stream.

    Args:
        score: A music21 Stream or Score
        scale: Multiply all velocities by this factor (e.g. 1.5 = 150%)
        absolute: Set all velocities to this exact value
        offset: Add this to all velocities (can be negative)

    Returns:
        A new stream with adjusted velocities (velocities clamped to 1-127)

    Raises:
        TypeError: If score is not a Stream
        ValueError: If no velocity parameter is provided
    """
    if not isinstance(score, stream.Stream):
        raise TypeError(f"Expected music21 Stream, got {type(score).__name__}")

    if scale is None and absolute is None and offset is None:
        raise ValueError(
            "Must provide one of: 'scale', 'absolute', or 'offset'"
        )

    import copy
    result = copy.deepcopy(score)

    for n in result.flatten().notes:
        # Get current velocity, defaulting to 64 if none set
        current_vel = 64
        if n.volume is not None and n.volume.velocity is not None:
            current_vel = n.volume.velocity

        if absolute is not None:
            new_vel = int(absolute)
        elif scale is not None:
            new_vel = int(round(current_vel * scale))
        elif offset is not None:
            new_vel = current_vel + int(offset)

        # Clamp to MIDI range [1, 127]
        new_vel = max(1, min(127, new_vel))

        n.volume = volume.Volume(velocity=new_vel)

    return result