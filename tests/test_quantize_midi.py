"""Tests for quantize_midi tool following TDD."""

import pytest
from music21_mcp.tools.quantize_midi import quantize_midi


def _make_unquantized_stream():
    """Helper: stream with notes at slightly off-grid timings.

    Notes offset at roughly quarter-note positions but with
    small offsets that should be snapped to the grid.
    """
    from music21 import stream, note
    s = stream.Stream()
    notes = [
        (0.0, "C4"),     # on beat 1
        (1.02, "E4"),    # slightly after beat 2
        (2.01, "G4"),    # slightly after beat 3
        (2.98, "C5"),    # slightly before beat 4
    ]
    for offset, pitch in notes:
        n = note.Note(pitch)
        n.quarterLength = 1.0
        s.insert(offset, n)
    return s


def test_quantize_to_quarter_notes():
    """Quantizing to quarter notes should snap offsets to integers."""
    s = _make_unquantized_stream()
    result = quantize_midi(s, grid="quarter")
    notes = list(result.flatten().notes)
    for n in notes:
        # offset should be very close to an integer
        assert abs(n.offset - round(n.offset)) < 0.001, f"Note at {n.offset} not quantized"


def test_quantize_to_eighth_notes():
    """Quantizing to eighth notes should snap to 0.5 increments."""
    s = _make_unquantized_stream()
    result = quantize_midi(s, grid="eighth")
    notes = list(result.flatten().notes)
    for n in notes:
        snapped = round(n.offset * 2) / 2
        assert abs(n.offset - snapped) < 0.001, f"Note at {n.offset} not quantized to eighth"


def test_quantize_to_sixteenth_notes():
    """Quantizing to sixteenth notes should snap to 0.25 increments."""
    s = _make_unquantized_stream()
    result = quantize_midi(s, grid="sixteenth")
    notes = list(result.flatten().notes)
    for n in notes:
        snapped = round(n.offset * 4) / 4
        assert abs(n.offset - snapped) < 0.001, f"Note at {n.offset} not quantized to sixteenth"


def test_quantize_already_on_grid():
    """Notes already on grid should remain unchanged."""
    from music21 import stream, note
    s = stream.Stream()
    s.insert(0.0, note.Note("C4"))
    s.insert(1.0, note.Note("E4"))
    s.insert(2.0, note.Note("G4"))
    result = quantize_midi(s, grid="quarter")
    notes = list(result.flatten().notes)
    assert notes[0].offset == 0.0
    assert notes[1].offset == 1.0
    assert notes[2].offset == 2.0


def test_quantize_invalid_input():
    """Should raise TypeError for non-stream input."""
    with pytest.raises(TypeError):
        quantize_midi("not a stream", grid="quarter")


def test_quantize_invalid_grid():
    """Should raise ValueError for invalid grid name."""
    from music21 import stream
    s = stream.Stream()
    with pytest.raises(ValueError):
        quantize_midi(s, grid="thirtysecond")