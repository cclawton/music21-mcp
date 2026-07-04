"""Tests for merge_midi tool following TDD."""

import pytest
from music21_mcp.tools.merge_midi import merge_midi


def _make_melody_stream():
    """Helper: simple melody."""
    from music21 import stream, note
    s = stream.Stream()
    for n in ["C5", "E5", "G5"]:
        s.append(note.Note(n))
    return s


def _make_bass_stream():
    """Helper: simple bass line."""
    from music21 import stream, note
    s = stream.Stream()
    for n in ["C2", "G2", "C3"]:
        s.append(note.Note(n))
    return s


def test_merge_two_streams():
    """Merging melody + bass should contain all notes from both."""
    melody = _make_melody_stream()
    bass = _make_bass_stream()
    result = merge_midi(melody, bass)
    assert result is not None
    notes = list(result.flatten().notes)
    assert len(notes) == 6  # 3 melody + 3 bass


def test_merge_preserves_pitch_content():
    """Merged stream should contain pitches from both streams."""
    melody = _make_melody_stream()
    bass = _make_bass_stream()
    result = merge_midi(melody, bass)
    all_pitches = []
    for n in result.flatten().notes:
        if hasattr(n, "pitch"):
            all_pitches.append(n.pitch.nameWithOctave)
        elif hasattr(n, "pitches"):
            all_pitches.extend([p.nameWithOctave for p in n.pitches])
    assert "C5" in all_pitches
    assert "E5" in all_pitches
    assert "G5" in all_pitches
    assert "C2" in all_pitches
    assert "G2" in all_pitches
    assert "C3" in all_pitches


def test_merge_into_parts():
    """Merging with output_parts=True should create a Score with 2 Parts."""
    from music21 import stream
    melody = _make_melody_stream()
    bass = _make_bass_stream()
    result = merge_midi(melody, bass, output_parts=True)
    assert hasattr(result, "parts")
    assert len(list(result.parts)) == 2


def test_merge_invalid_first_input():
    """Should raise TypeError for non-stream first input."""
    bass = _make_bass_stream()
    with pytest.raises(TypeError):
        merge_midi("not a stream", bass)


def test_merge_invalid_second_input():
    """Should raise TypeError for non-stream second input."""
    melody = _make_melody_stream()
    with pytest.raises(TypeError):
        merge_midi(melody, "not a stream")