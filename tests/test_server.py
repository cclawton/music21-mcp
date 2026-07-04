"""Tests for MCP server tool registration and dispatch."""

import pytest
from music21_mcp.server import mcp, _tool_registry


def test_server_imports():
    """Server module should import cleanly."""
    from music21_mcp import server
    assert server is not None


def test_tool_registry_has_all_phase_1a_tools():
    """Registry should contain all 3 Phase 1a tools."""
    expected_1a = ["parse_midi_file", "analyze_key", "export_midi"]
    for tool_name in expected_1a:
        assert tool_name in _tool_registry, f"Missing Phase 1a tool: {tool_name}"


def test_tool_registry_has_all_phase_1c_tools():
    """Registry should contain all 6 Phase 1c tools."""
    expected_1c = [
        "transpose_midi",
        "change_velocity",
        "modify_notes",
        "replace_chord_at",
        "merge_midi",
        "quantize_midi",
    ]
    for tool_name in expected_1c:
        assert tool_name in _tool_registry, f"Missing Phase 1c tool: {tool_name}"


def test_tool_registry_has_phase_2_tools():
    """Registry should contain both Phase 2 tools."""
    expected_p2 = ["reharmonize", "harmonize_melody"]
    for tool_name in expected_p2:
        assert tool_name in _tool_registry, f"Missing Phase 2 tool: {tool_name}"


def test_tool_registry_has_phase_3_tools():
    """Registry should contain all 5 Phase 3 tools."""
    expected_p3 = [
        "analyze_chord_progression",
        "extract_melody",
        "detect_modulations",
        "analyze_form",
        "search_pattern",
    ]
    for tool_name in expected_p3:
        assert tool_name in _tool_registry, f"Missing Phase 3 tool: {tool_name}"


def test_tool_registry_has_descriptions():
    """Each tool should have a description string."""
    for name, tool_def in _tool_registry.items():
        assert "description" in tool_def, f"Tool {name} missing description"
        assert isinstance(tool_def["description"], str)
        assert len(tool_def["description"]) > 0


def test_parse_midi_file_dispatch(tmp_path):
    """Dispatching parse_midi_file should return a music21 stream."""
    from music21 import stream, note
    s = stream.Stream()
    s.append(note.Note("C4"))
    midi_path = tmp_path / "test.mid"
    s.write("midi", fp=str(midi_path))

    result = _tool_registry["parse_midi_file"]["fn"](str(midi_path))
    assert result is not None


def test_analyze_key_dispatch():
    """Dispatching analyze_key should return a dict with key info."""
    from music21 import stream, note, chord
    s = stream.Stream()
    for _ in range(2):
        for n in ["C4", "E4", "G4", "C5"]:
            s.append(note.Note(n))
    s.append(chord.Chord(["F4", "A4", "C5"]))
    s.append(chord.Chord(["G4", "B4", "D5"]))
    s.append(chord.Chord(["C4", "E4", "G4", "C5"]))

    result = _tool_registry["analyze_key"]["fn"](s)
    assert isinstance(result, dict)
    assert "key" in result


def test_export_midi_dispatch(tmp_path):
    """Dispatching export_midi should create a file."""
    from music21 import stream, note
    s = stream.Stream()
    s.append(note.Note("C4"))
    out_path = tmp_path / "out.mid"

    result = _tool_registry["export_midi"]["fn"](s, str(out_path))
    assert result["success"] is True
    assert out_path.exists()


def test_transpose_midi_dispatch():
    """Dispatching transpose_midi should return a transposed stream."""
    from music21 import stream, note, chord
    s = stream.Stream()
    for _ in range(2):
        for n in ["C4", "E4", "G4", "C5"]:
            s.append(note.Note(n))
    s.append(chord.Chord(["F4", "A4", "C5"]))
    s.append(chord.Chord(["G4", "B4", "D5"]))
    s.append(chord.Chord(["C4", "E4", "G4", "C5"]))

    result = _tool_registry["transpose_midi"]["fn"](s, semitones=2)
    assert result is not None


def test_change_velocity_dispatch():
    """Dispatching change_velocity should return modified stream."""
    from music21 import stream, note, volume
    s = stream.Stream()
    n = note.Note("C4")
    n.volume = volume.Volume(velocity=64)
    s.append(n)

    result = _tool_registry["change_velocity"]["fn"](s, scale=1.5)
    assert result is not None


def test_mcp_server_object_exists():
    """The FastMCP server object should exist."""
    assert mcp is not None
    # FastMCP server should have a run method or similar
    assert hasattr(mcp, "run") or hasattr(mcp, "list_tools")