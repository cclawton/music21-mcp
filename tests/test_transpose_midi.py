"""Tests for transpose_midi tool following TDD."""

import pytest
from music21_mcp.tools.transpose_midi import transpose_midi
from music21_mcp.tools.analyze_key import analyze_key


def _make_c_major_stream():
    """Helper: C major triad arpeggio with cadence."""
    from music21 import stream, note, chord
    s = stream.Stream()
    for _ in range(2):
        for n in ["C4", "E4", "G4", "C5"]:
            s.append(note.Note(n))
    s.append(chord.Chord(["F4", "A4", "C5"]))
    s.append(chord.Chord(["G4", "B4", "D5"]))
    s.append(chord.Chord(["C4", "E4", "G4", "C5"]))
    return s


def test_transpose_by_semitones():
    """Transposing C major by +2 semitones should yield D major."""
    s = _make_c_major_stream()
    result = transpose_midi(s, semitones=2)
    assert result is not None
    key_result = analyze_key(result)
    assert key_result["key"] in ("D major", "D")


def test_transpose_by_negative_semitones():
    """Transposing C major by -3 semitones should yield A major."""
    s = _make_c_major_stream()
    result = transpose_midi(s, semitones=-3)
    key_result = analyze_key(result)
    assert key_result["key"] in ("A major", "A")


def test_transpose_to_target_key():
    """Transposing C major to F major should work."""
    s = _make_c_major_stream()
    result = transpose_midi(s, target_key="F")
    key_result = analyze_key(result)
    assert key_result["key"] in ("F major", "F")


def _note_names(s):
    """Extract note names from a stream (handles Notes and Chords)."""
    from music21 import note, chord
    names = []
    for n in s.flatten().notes:
        if isinstance(n, note.Note):
            names.append(n.name)
        elif isinstance(n, chord.Chord):
            names.extend([p.name for p in n.pitches])
    return names


def test_transpose_zero_semitones():
    """Transposing by 0 should return equivalent stream."""
    s = _make_c_major_stream()
    result = transpose_midi(s, semitones=0)
    assert _note_names(s) == _note_names(result)


def test_transpose_invalid_input():
    """Should raise TypeError for non-stream input."""
    with pytest.raises(TypeError):
        transpose_midi("not a stream", semitones=2)


def test_transpose_requires_semitones_or_target():
    """Should raise ValueError if neither semitones nor target_key given."""
    s = _make_c_major_stream()
    with pytest.raises(ValueError):
        transpose_midi(s)