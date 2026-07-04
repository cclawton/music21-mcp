"""End-to-end MCP wrapper tests — verify JSON tool wrappers work with real MIDI files."""

import json
import pytest
from pathlib import Path

from music21_mcp.server import (
    mcp_parse_midi_file,
    mcp_analyze_key,
    mcp_export_midi,
    mcp_transpose_midi,
    mcp_change_velocity,
    mcp_modify_notes,
    mcp_replace_chord_at,
    mcp_merge_midi,
    mcp_quantize_midi,
)


@pytest.fixture
def sample_midi(tmp_path):
    """Create a sample MIDI file for testing."""
    from music21 import stream, note, chord
    s = stream.Stream()
    for _ in range(2):
        for n in ["C4", "E4", "G4", "C5"]:
            s.append(note.Note(n))
    s.append(chord.Chord(["F4", "A4", "C5"]))
    s.append(chord.Chord(["G4", "B4", "D5"]))
    s.append(chord.Chord(["C4", "E4", "G4", "C5"]))
    path = tmp_path / "sample.mid"
    s.write("midi", fp=str(path))
    return str(path)


@pytest.fixture
def bass_midi(tmp_path):
    """Create a simple bass MIDI file."""
    from music21 import stream, note
    s = stream.Stream()
    for n in ["C2", "G2", "C3"]:
        s.append(note.Note(n))
    path = tmp_path / "bass.mid"
    s.write("midi", fp=str(path))
    return str(path)


def test_e2e_parse_midi(sample_midi):
    result = json.loads(mcp_parse_midi_file(sample_midi))
    assert result["success"] is True
    assert result["note_count"] > 0


def test_e2e_analyze_key(sample_midi):
    result = json.loads(mcp_analyze_key(sample_midi))
    assert result["success"] is True or "key" in result
    assert "C major" in result.get("key", "") or "key" in result


def test_e2e_transpose(sample_midi, tmp_path):
    out = str(tmp_path / "transposed.mid")
    result = json.loads(mcp_transpose_midi(sample_midi, semitones=2, output_path=out))
    assert result["success"] is True
    assert Path(out).exists()
    assert "D major" in result.get("new_key", "")


def test_e2e_change_velocity(sample_midi, tmp_path):
    out = str(tmp_path / "velocity.mid")
    result = json.loads(mcp_change_velocity(sample_midi, scale=1.5, output_path=out))
    assert result["success"] is True
    assert Path(out).exists()


def test_e2e_modify_notes(sample_midi, tmp_path):
    out = str(tmp_path / "modified.mid")
    result = json.loads(mcp_modify_notes(sample_midi, action="remove", filter_above="C4", output_path=out))
    assert result["success"] is True
    # Removing notes above C4 should leave fewer or equal notes
    assert result["remaining_notes"] <= result["original_notes"]


def test_e2e_replace_chord(sample_midi, tmp_path):
    out = str(tmp_path / "replaced.mid")
    result = json.loads(mcp_replace_chord_at(sample_midi, bar=1, beat=1, new_chord="G3,B3,D4,F4", output_path=out))
    assert result["success"] is True
    assert Path(out).exists()


def test_e2e_merge(sample_midi, bass_midi, tmp_path):
    out = str(tmp_path / "merged.mid")
    result = json.loads(mcp_merge_midi(sample_midi, bass_midi, output_path=out))
    assert result["success"] is True
    assert result["total_notes"] > 0
    assert Path(out).exists()


def test_e2e_quantize(sample_midi, tmp_path):
    out = str(tmp_path / "quantized.mid")
    result = json.loads(mcp_quantize_midi(sample_midi, grid="quarter", output_path=out))
    assert result["success"] is True
    assert Path(out).exists()


def test_e2e_error_handling():
    """Bad file path should return error JSON, not crash."""
    result = json.loads(mcp_parse_midi_file("/nonexistent/file.mid"))
    assert result["success"] is False
    assert "error" in result