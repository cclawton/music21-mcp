"""Tests for export_midi tool following TDD."""

import pytest
from pathlib import Path
from music21_mcp.tools.export_midi import export_midi


def _make_simple_stream():
    """Helper: create a simple stream with a few notes."""
    from music21 import stream, note
    s = stream.Stream()
    for n in ["C4", "E4", "G4"]:
        s.append(note.Note(n))
    return s


def test_export_creates_midi_file(tmp_path):
    """Should create a .mid file from a stream."""
    s = _make_simple_stream()
    out_path = tmp_path / "output.mid"
    result = export_midi(s, str(out_path))
    assert Path(out_path).exists()
    assert Path(out_path).stat().st_size > 0
    assert result["path"] == str(out_path)
    assert result["success"] is True


def test_export_roundtrip(tmp_path):
    """Exported file should be re-parseable as MIDI."""
    from music21_mcp.tools.parse_midi import parse_midi_file
    s = _make_simple_stream()
    out_path = tmp_path / "roundtrip.mid"
    export_midi(s, str(out_path))
    reparsed = parse_midi_file(str(out_path))
    assert reparsed is not None
    # Should have at least 3 notes
    notes = list(reparsed.flatten().notes)
    assert len(notes) >= 3


def test_export_creates_parent_dirs(tmp_path):
    """Should create parent directories if they don't exist."""
    s = _make_simple_stream()
    out_path = tmp_path / "subdir" / "deeper" / "output.mid"
    result = export_midi(s, str(out_path))
    assert Path(out_path).exists()
    assert result["success"] is True


def test_export_invalid_input():
    """Should raise TypeError for non-stream input."""
    with pytest.raises(TypeError):
        export_midi("not a stream", "/tmp/out.mid")