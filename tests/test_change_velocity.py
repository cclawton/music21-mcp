"""Tests for change_velocity tool following TDD."""

import pytest
from music21_mcp.tools.change_velocity import change_velocity


def _make_stream_with_velocity():
    """Helper: stream with notes at velocity 64."""
    from music21 import stream, note, volume
    s = stream.Stream()
    for n in ["C4", "E4", "G4"]:
        note_obj = note.Note(n)
        note_obj.volume = volume.Volume(velocity=64)
        s.append(note_obj)
    return s


def _get_velocities(s):
    """Extract velocities from all notes in stream."""
    vels = []
    for n in s.flatten().notes:
        if hasattr(n, "volume") and n.volume:
            vels.append(n.volume.velocity)
    return vels


def test_scale_velocity_by_percentage():
    """Scaling velocity by 150% should multiply all velocities by 1.5."""
    s = _make_stream_with_velocity()
    result = change_velocity(s, scale=1.5)
    vels = _get_velocities(result)
    assert all(v == 96 for v in vels)  # 64 * 1.5 = 96


def test_scale_velocity_clamped_to_127():
    """Velocity should never exceed 127."""
    s = _make_stream_with_velocity()
    result = change_velocity(s, scale=3.0)
    vels = _get_velocities(result)
    assert all(v <= 127 for v in vels)
    assert all(v == 127 for v in vels)  # 64*3=192 → clamped to 127


def test_scale_velocity_clamped_to_1():
    """Velocity should never go below 1."""
    s = _make_stream_with_velocity()
    result = change_velocity(s, scale=0.001)
    vels = _get_velocities(result)
    assert all(v >= 1 for v in vels)


def test_set_absolute_velocity():
    """Setting velocity=100 should override all to 100."""
    s = _make_stream_with_velocity()
    result = change_velocity(s, absolute=100)
    vels = _get_velocities(result)
    assert all(v == 100 for v in vels)


def test_adjust_velocity_by_offset():
    """Adding offset=20 should add 20 to each velocity."""
    s = _make_stream_with_velocity()
    result = change_velocity(s, offset=20)
    vels = _get_velocities(result)
    assert all(v == 84 for v in vels)  # 64 + 20


def test_adjust_velocity_negative_offset_clamped():
    """Negative offset should clamp to minimum 1."""
    s = _make_stream_with_velocity()
    result = change_velocity(s, offset=-100)
    vels = _get_velocities(result)
    assert all(v == 1 for v in vels)


def test_change_velocity_invalid_input():
    """Should raise TypeError for non-stream input."""
    with pytest.raises(TypeError):
        change_velocity("not a stream", scale=1.0)


def test_change_velocity_requires_parameter():
    """Should raise ValueError if no velocity parameter given."""
    s = _make_stream_with_velocity()
    with pytest.raises(ValueError):
        change_velocity(s)