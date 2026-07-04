"""Tests for analyze_chord_progression tool following TDD."""

import pytest
from music21_mcp.tools.analyze_chord_progression import analyze_chord_progression


def _make_i_iv_v_i():
    """Helper: I-IV-V-I in C major as whole-note chords."""
    from music21 import stream, chord
    s = stream.Stream()
    chords = [
        chord.Chord(["C4", "E4", "G4"]),
        chord.Chord(["F4", "A4", "C5"]),
        chord.Chord(["G4", "B4", "D5"]),
        chord.Chord(["C4", "E4", "G4"]),
    ]
    for c in chords:
        c.duration.type = "whole"
        s.append(c)
    return s


def test_returns_dict():
    """Should return a dict with progression info."""
    s = _make_i_iv_v_i()
    result = analyze_chord_progression(s)
    assert isinstance(result, dict)


def test_returns_roman_numerals():
    """Should identify Roman numerals for each chord."""
    s = _make_i_iv_v_i()
    result = analyze_chord_progression(s)
    assert "progression" in result
    assert isinstance(result["progression"], list)
    assert len(result["progression"]) == 4
    # First chord should be I
    assert result["progression"][0]["roman_numeral"] == "I"
    # Second should be IV
    assert result["progression"][1]["roman_numeral"] == "IV"
    # Third should be V
    assert result["progression"][2]["roman_numeral"] == "V"


def test_returns_chord_names():
    """Should include chord names (e.g. 'C major', 'F major')."""
    s = _make_i_iv_v_i()
    result = analyze_chord_progression(s)
    assert "chord_name" in result["progression"][0]
    assert "C" in result["progression"][0]["chord_name"]


def test_returns_key():
    """Should include the detected key."""
    s = _make_i_iv_v_i()
    result = analyze_chord_progression(s)
    assert "key" in result
    assert "C" in result["key"]


def test_returns_summary():
    """Should include a human-readable summary."""
    s = _make_i_iv_v_i()
    result = analyze_chord_progression(s)
    assert "summary" in result
    assert isinstance(result["summary"], str)


def test_invalid_input():
    """Should raise TypeError for non-stream input."""
    with pytest.raises(TypeError):
        analyze_chord_progression("not a stream")


def test_empty_stream():
    """Empty stream should return empty progression."""
    from music21 import stream
    s = stream.Stream()
    result = analyze_chord_progression(s)
    assert result["progression"] == []