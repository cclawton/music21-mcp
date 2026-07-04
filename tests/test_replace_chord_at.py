"""Tests for replace_chord_at tool following TDD."""

import pytest
from music21_mcp.tools.replace_chord_at import replace_chord_at


def _make_chord_progression():
    """Helper: 4-bar progression with one chord per bar in 4/4.

    Bar 1: C major, Bar 2: F major, Bar 3: G major, Bar 4: C major
    """
    from music21 import stream, chord, meter
    s = stream.Stream()
    s.append(meter.TimeSignature("4/4"))
    chords_data = [
        (["C4", "E4", "G4"], "C major"),
        (["F4", "A4", "C5"], "F major"),
        (["G4", "B4", "D5"], "G major"),
        (["C4", "E4", "G4"], "C major"),
    ]
    for pitches, _ in chords_data:
        c = chord.Chord(pitches)
        c.duration.type = "whole"
        s.append(c)
    return s


def test_replace_chord_at_bar_1():
    """Replace chord at bar 1 with G7."""
    s = _make_chord_progression()
    result = replace_chord_at(s, bar=1, beat=1, new_chord=["G3", "B3", "D4", "F4"])
    chords = list(result.flatten().notes)
    assert len(chords) == 4  # still 4 chords
    # First chord should now be G7
    first_pitches = [p.name for p in chords[0].pitches]
    assert set(first_pitches) == {"G", "B", "D", "F"}


def test_replace_chord_at_bar_3():
    """Replace chord at bar 3 with A minor."""
    s = _make_chord_progression()
    result = replace_chord_at(s, bar=3, beat=1, new_chord=["A3", "C4", "E4"])
    chords = list(result.flatten().notes)
    third_pitches = [p.name for p in chords[2].pitches]
    assert set(third_pitches) == {"A", "C", "E"}


def test_replace_preserves_other_chords():
    """Replacing one chord should leave others unchanged."""
    s = _make_chord_progression()
    result = replace_chord_at(s, bar=2, beat=1, new_chord=["D3", "F#3", "A3"])
    chords = list(result.flatten().notes)
    # Bar 1 should still be C major
    first_pitches = [p.name for p in chords[0].pitches]
    assert set(first_pitches) == {"C", "E", "G"}
    # Bar 4 should still be C major
    fourth_pitches = [p.name for p in chords[3].pitches]
    assert set(fourth_pitches) == {"C", "E", "G"}


def test_replace_chord_invalid_bar():
    """Should raise ValueError for bar that doesn't exist."""
    s = _make_chord_progression()
    with pytest.raises(ValueError):
        replace_chord_at(s, bar=99, beat=1, new_chord=["C4", "E4", "G4"])


def test_replace_chord_invalid_input():
    """Should raise TypeError for non-stream input."""
    with pytest.raises(TypeError):
        replace_chord_at("not a stream", bar=1, beat=1, new_chord=["C4"])


def test_replace_chord_empty_new_chord():
    """Should raise ValueError for empty chord list."""
    s = _make_chord_progression()
    with pytest.raises(ValueError):
        replace_chord_at(s, bar=1, beat=1, new_chord=[])