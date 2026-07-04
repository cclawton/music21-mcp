"""Tests for parse_midi_file tool following TDD."""

import pytest
from music21_mcp.tools.parse_midi import parse_midi_file


def test_parse_valid_midi(tmp_path):
    """Test parsing a simple MIDI file."""
    # Minimal test MIDI will be created in fixture or here
    midi_path = tmp_path / "test.mid"
    # For now, this will fail until we have a real MIDI or mock
    # Use a known good approach: music21 can create one
    from music21 import stream, note
    s = stream.Stream()
    s.append(note.Note('C4'))
    s.write('midi', fp=str(midi_path))

    result = parse_midi_file(str(midi_path))
    assert result is not None
    assert hasattr(result, 'parts') or hasattr(result, 'flat')  # music21 stream


def test_parse_invalid_file():
    """Test error handling for bad path."""
    with pytest.raises(FileNotFoundError):
        parse_midi_file("/nonexistent/path.mid")