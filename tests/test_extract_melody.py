"""Tests for extract_melody tool following TDD."""

import pytest
from music21_mcp.tools.extract_melody import extract_melody


def _make_two_part_score():
    """Helper: a Score with two parts — melody (high) and bass (low).
    Both parts start at offset 0 (overlapping), not appended sequentially.
    """
    from music21 import stream, note
    score = stream.Score()

    melody = stream.Part()
    for n in ["C5", "E5", "G5", "C6"]:
        melody.append(note.Note(n))

    bass = stream.Part()
    for n in ["C3", "G3", "C4", "C3"]:
        bass.append(note.Note(n))

    score.insert(0, melody)
    score.insert(0, bass)
    return score


def _make_flat_stream_with_melody():
    """Helper: flat stream where higher notes are the melody."""
    from music21 import stream, note
    s = stream.Stream()
    # Interleaved melody (high) and accompaniment (low)
    for i, (melody_n, bass_n) in enumerate(
        zip(["C5", "E5", "G5", "C6"], ["C3", "G3", "E3", "C3"])
    ):
        s.insert(i, note.Note(melody_n))
        s.insert(i, note.Note(bass_n))
    return s


def test_extract_melody_from_score():
    """Should extract the highest part as melody from a Score."""
    s = _make_two_part_score()
    result = extract_melody(s)
    assert result is not None
    from music21 import stream
    assert isinstance(result, stream.Stream)
    notes = list(result.flatten().notes)
    assert len(notes) > 0


def test_extract_melody_pitch_content():
    """Extracted melody should contain the higher-pitched notes."""
    s = _make_two_part_score()
    result = extract_melody(s)
    note_names = [n.nameWithOctave for n in result.flatten().notes]
    # Should contain C5, E5, G5, C6 (the melody)
    assert "C5" in note_names
    assert "C6" in note_names
    # Should NOT contain C3, G3 (the bass)
    assert "C3" not in note_names


def test_extract_melody_from_flat_stream():
    """Should extract highest notes from a flat stream with interleaved parts."""
    s = _make_flat_stream_with_melody()
    result = extract_melody(s)
    note_names = [n.nameWithOctave for n in result.flatten().notes]
    assert "C5" in note_names
    assert "G5" in note_names


def test_extract_melody_returns_single_line():
    """Extracted melody should be a single-note line (no chords)."""
    s = _make_two_part_score()
    result = extract_melody(s)
    from music21 import chord
    chords = [e for e in result.flatten().notes if isinstance(e, chord.Chord)]
    assert len(chords) == 0


def test_extract_melody_invalid_input():
    """Should raise TypeError for non-stream input."""
    with pytest.raises(TypeError):
        extract_melody("not a stream")


def test_extract_melody_empty_stream():
    """Empty stream should return empty stream."""
    from music21 import stream
    s = stream.Stream()
    result = extract_melody(s)
    assert len(list(result.flatten().notes)) == 0