"""Tests for analyze_key tool following TDD."""

import pytest
from music21_mcp.tools.analyze_key import analyze_key


def _make_c_major_stream():
    """Helper: create a C major stream with strong tonal centre.

    Uses tonic triad arpeggios + V-I cadence to give the key
    detector enough harmonic context.
    """
    from music21 import stream, note, chord
    s = stream.Stream()
    # Tonic triad arpeggio x2
    for _ in range(2):
        for n in ["C4", "E4", "G4", "C5"]:
            s.append(note.Note(n))
    # F major (IV) then G major (V) then C major (I) cadence
    s.append(chord.Chord(["F4", "A4", "C5"]))
    s.append(chord.Chord(["G4", "B4", "D5"]))
    s.append(chord.Chord(["C4", "E4", "G4", "C5"]))
    return s


def _make_g_major_stream():
    """Helper: create a G major stream with strong tonal centre."""
    from music21 import stream, note, chord
    s = stream.Stream()
    for _ in range(2):
        for n in ["G4", "B4", "D5", "G5"]:
            s.append(note.Note(n))
    # C major (IV) then D major (V) then G major (I) cadence
    s.append(chord.Chord(["C4", "E4", "G4"]))
    s.append(chord.Chord(["D4", "F#4", "A4"]))
    s.append(chord.Chord(["G4", "B4", "D5", "G5"]))
    return s


def test_analyze_key_c_major():
    """Should detect C major from a C major progression."""
    s = _make_c_major_stream()
    result = analyze_key(s)
    assert result is not None
    assert isinstance(result, dict)
    assert "key" in result
    assert result["key"] in ("C major", "C")
    assert "confidence" in result


def test_analyze_key_g_major():
    """Should detect G major from a G major progression."""
    s = _make_g_major_stream()
    result = analyze_key(s)
    assert result["key"] in ("G major", "G")


def test_analyze_key_returns_mode():
    """Result should include major/minor mode."""
    s = _make_c_major_stream()
    result = analyze_key(s)
    assert "mode" in result
    assert result["mode"] == "major"


def test_analyze_key_invalid_input():
    """Should raise TypeError for non-stream input."""
    with pytest.raises(TypeError):
        analyze_key("not a stream")