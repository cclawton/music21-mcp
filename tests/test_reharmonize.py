"""Tests for reharmonize tool following TDD."""

import pytest
from music21_mcp.tools.reharmonize import reharmonize


def _make_simple_progression():
    """Helper: simple I-IV-V-I in C major as chords."""
    from music21 import stream, chord
    s = stream.Stream()
    chords = [
        chord.Chord(["C4", "E4", "G4"]),    # I (C major)
        chord.Chord(["F4", "A4", "C5"]),    # IV (F major)
        chord.Chord(["G4", "B4", "D5"]),    # V (G major)
        chord.Chord(["C4", "E4", "G4"]),    # I (C major)
    ]
    for c in chords:
        c.duration.type = "whole"
        s.append(c)
    return s


def test_reharmonize_returns_stream():
    """Should return a music21 Stream."""
    s = _make_simple_progression()
    result = reharmonize(s, style="diatonic")
    assert result is not None
    from music21 import stream
    assert isinstance(result, stream.Stream)


def test_reharmonize_preserves_structure():
    """Should have same number of chord positions."""
    s = _make_simple_progression()
    result = reharmonize(s, style="diatonic")
    original_chords = [e for e in s if isinstance(e, type(list(s)[0]))]
    result_chords = list(result.recurse().notes)
    # Should have same number of chord/note elements
    assert len(result_chords) == 4


def test_reharmonize_diatonic_style():
    """Diatonic reharmonization should stay in key."""
    from music21_mcp.tools.analyze_key import analyze_key
    s = _make_simple_progression()
    result = reharmonize(s, style="diatonic")
    # Should still be in C major (or relative minor)
    key_result = analyze_key(result)
    assert "C" in key_result["key"] or "A" in key_result["key"]


def test_reharmonize_substitute_style():
    """Substitute style should use chord substitutions (e.g. tritone subs)."""
    s = _make_simple_progression()
    result = reharmonize(s, style="substitute")
    from music21 import stream
    assert isinstance(result, stream.Stream)
    # Should still have 4 chords
    result_chords = list(result.recurse().notes)
    assert len(result_chords) == 4


def test_reharmonize_invalid_input():
    """Should raise TypeError for non-stream input."""
    with pytest.raises(TypeError):
        reharmonize("not a stream", style="diatonic")


def test_reharmonize_invalid_style():
    """Should raise ValueError for invalid style."""
    from music21 import stream
    s = stream.Stream()
    with pytest.raises(ValueError):
        reharmonize(s, style="bogus")