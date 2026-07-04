"""Tests for modify_notes tool following TDD."""

import pytest
from music21_mcp.tools.modify_notes import modify_notes


def _make_multi_octave_stream():
    """Helper: stream with notes across multiple octaves."""
    from music21 import stream, note
    s = stream.Stream()
    for n in ["C3", "E3", "G3", "C4", "E4", "G4", "C5", "E5", "G5"]:
        s.append(note.Note(n))
    return s


def _note_names(s):
    from music21 import note, chord
    names = []
    for n in s.flatten().notes:
        if isinstance(n, note.Note):
            names.append(n.nameWithOctave)
        elif isinstance(n, chord.Chord):
            names.extend([p.nameWithOctave for p in n.pitches])
    return names


def test_remove_notes_below_pitch():
    """Remove all notes below C4."""
    s = _make_multi_octave_stream()
    result = modify_notes(s, action="remove", filter_below="C4")
    names = _note_names(result)
    assert all(n not in names for n in ["C3", "E3", "G3"])
    assert "C4" in names
    assert "C5" in names


def test_remove_notes_above_pitch():
    """Remove all notes above C5."""
    s = _make_multi_octave_stream()
    result = modify_notes(s, action="remove", filter_above="C5")
    names = _note_names(result)
    assert "E5" not in names
    assert "G5" not in names
    assert "C3" in names


def test_select_notes_in_range():
    """Select only notes between C4 and G4."""
    s = _make_multi_octave_stream()
    result = modify_notes(s, action="select", filter_below="C4", filter_above="G4")
    names = _note_names(result)
    assert "C4" in names
    assert "E4" in names
    assert "G4" in names
    assert "C3" not in names
    assert "C5" not in names


def test_change_octave_shift():
    """Shift all notes up an octave."""
    s = _make_multi_octave_stream()
    result = modify_notes(s, action="shift_octave", octave_shift=1)
    names = _note_names(result)
    assert "C4" in names  # was C3
    assert "C6" in names  # was C5
    assert "C3" not in names


def test_modify_notes_empty_stream():
    """Empty stream should return empty stream."""
    from music21 import stream
    s = stream.Stream()
    result = modify_notes(s, action="remove", filter_below="C4")
    assert len(list(result.flatten().notes)) == 0


def test_modify_notes_invalid_input():
    """Should raise TypeError for non-stream input."""
    with pytest.raises(TypeError):
        modify_notes("not a stream", action="remove", filter_below="C4")


def test_modify_notes_invalid_action():
    """Should raise ValueError for invalid action."""
    from music21 import stream
    s = stream.Stream()
    with pytest.raises(ValueError):
        modify_notes(s, action="explode")