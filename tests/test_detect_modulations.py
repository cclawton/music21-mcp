"""Tests for detect_modulations tool following TDD."""

import pytest
from music21_mcp.tools.detect_modulations import detect_modulations


def _make_modulating_stream():
    """Helper: stream that starts in C major then modulates to G major.

    Bars 1-4: C major scale + cadence
    Bars 5-8: G major scale + cadence
    """
    from music21 import stream, note, chord
    s = stream.Stream()

    # C major section
    for _ in range(2):
        for n in ["C4", "E4", "G4", "C5"]:
            s.append(note.Note(n))
    s.append(chord.Chord(["F4", "A4", "C5"]))
    s.append(chord.Chord(["G4", "B4", "D5"]))
    s.append(chord.Chord(["C4", "E4", "G4", "C5"]))

    # G major section
    for _ in range(2):
        for n in ["G4", "B4", "D5", "G5"]:
            s.append(note.Note(n))
    s.append(chord.Chord(["C4", "E4", "G4"]))
    s.append(chord.Chord(["D4", "F#4", "A4"]))
    s.append(chord.Chord(["G4", "B4", "D5", "G5"]))

    return s


def _make_no_modulation_stream():
    """Helper: stream that stays in C major throughout."""
    from music21 import stream, note, chord
    s = stream.Stream()
    for _ in range(3):
        for n in ["C4", "E4", "G4", "C5"]:
            s.append(note.Note(n))
        s.append(chord.Chord(["F4", "A4", "C5"]))
        s.append(chord.Chord(["G4", "B4", "D5"]))
        s.append(chord.Chord(["C4", "E4", "G4", "C5"]))
    return s


def test_detect_modulations_returns_dict():
    """Should return a dict with modulation info."""
    s = _make_modulating_stream()
    result = detect_modulations(s)
    assert isinstance(result, dict)


def test_detect_modulations_finds_modulation():
    """Should find at least one modulation point in the modulating stream."""
    s = _make_modulating_stream()
    result = detect_modulations(s)
    assert "modulations" in result
    assert isinstance(result["modulations"], list)
    assert len(result["modulations"]) >= 1


def test_detect_modulations_returns_key_info():
    """Each modulation should include source and target keys."""
    s = _make_modulating_stream()
    result = detect_modulations(s)
    if result["modulations"]:
        mod = result["modulations"][0]
        assert "from_key" in mod
        assert "to_key" in mod
        assert "offset" in mod


def test_detect_modulations_no_modulation():
    """Stream with no modulation should return empty modulations list."""
    s = _make_no_modulation_stream()
    result = detect_modulations(s)
    assert result["modulations"] == []


def test_detect_modulations_returns_summary():
    """Should include a human-readable summary."""
    s = _make_modulating_stream()
    result = detect_modulations(s)
    assert "summary" in result


def test_detect_modulations_invalid_input():
    """Should raise TypeError for non-stream input."""
    with pytest.raises(TypeError):
        detect_modulations("not a stream")


def test_detect_modulations_empty_stream():
    """Empty stream should return empty modulations."""
    from music21 import stream
    s = stream.Stream()
    result = detect_modulations(s)
    assert result["modulations"] == []