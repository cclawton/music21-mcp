"""Tests for harmonize_melody tool following TDD."""

import pytest
from music21_mcp.tools.harmonize_melody import harmonize_melody


def _make_c_major_melody():
    """Helper: simple C major melody (C-E-G-C pattern)."""
    from music21 import stream, note
    s = stream.Stream()
    for n in ["C4", "E4", "G4", "C5"]:
        note_obj = note.Note(n)
        note_obj.quarterLength = 1.0
        s.append(note_obj)
    return s


def test_harmonize_returns_stream():
    """Should return a music21 Stream."""
    s = _make_c_major_melody()
    result = harmonize_melody(s)
    assert result is not None
    from music21 import stream
    assert isinstance(result, stream.Stream)


def test_harmonize_produces_chords():
    """Result should contain chords (not just the original melody notes)."""
    s = _make_c_major_melody()
    result = harmonize_melody(s)
    from music21 import chord
    chords_found = [e for e in result.recurse() if isinstance(e, chord.Chord)]
    assert len(chords_found) > 0


def test_harmonize_preserves_melody():
    """The original melody notes should still be present."""
    s = _make_c_major_melody()
    result = harmonize_melody(s)
    from music21 import note
    melody_notes = [e for e in result.recurse() if isinstance(e, note.Note)]
    # Should still have the 4 melody notes
    assert len(melody_notes) >= 4


def test_harmonize_chords_match_key():
    """Generated chords should be consistent with the melody's key."""
    from music21_mcp.tools.analyze_key import analyze_key
    s = _make_c_major_melody()
    result = harmonize_melody(s)
    key_result = analyze_key(result)
    # Should be in C major or A minor (relative minor)
    assert "C" in key_result["key"] or "A" in key_result["key"]


def test_harmonize_custom_style():
    """Should accept style parameter."""
    s = _make_c_major_melody()
    result = harmonize_melody(s, style="block")
    from music21 import stream
    assert isinstance(result, stream.Stream)


def test_harmonize_invalid_input():
    """Should raise TypeError for non-stream input."""
    with pytest.raises(TypeError):
        harmonize_melody("not a stream")


def test_harmonize_empty_stream():
    """Empty melody should return empty stream without error."""
    from music21 import stream
    s = stream.Stream()
    result = harmonize_melody(s)
    assert isinstance(result, stream.Stream)