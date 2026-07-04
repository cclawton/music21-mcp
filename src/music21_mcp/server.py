"""
music21 MCP Server — exposes music21 tools via Model Context Protocol
"""

from __future__ import annotations
import json
from mcp.server.fastmcp import FastMCP

from .tools import (
    analyze_key,
    parse_midi_file,
    export_midi,
    transpose_midi,
    modify_notes,
    change_velocity,
    replace_chord_at,
    merge_midi,
    quantize_midi,
)

mcp = FastMCP("music21-mcp")


@mcp.tool()
def tool_analyze_key(source: str, detail: bool = False) -> str:
    """Detect the most likely key of a MIDI file or note sequence.

    Args:
        source: MIDI file path OR comma-separated note names (e.g. 'C4,E4,G4,F4,A4,C5')
        detail: Include detailed pitch class distribution (default: false)

    Returns:
        JSON with key, confidence, alternatives, and summary
    """
    return json.dumps(analyze_key(source, detail))


@mcp.tool()
def tool_parse_midi_file(
    file_path: str, extract_notes: bool = False, part_index: int | None = None
) -> str:
    """Parse a MIDI file and return its structure: parts, tracks, tempo, time signature, key signatures, note count, duration.

    Args:
        file_path: Path to MIDI file
        extract_notes: Include note list per part (default: false, returns counts only)
        part_index: Optional, analyze specific part only

    Returns:
        JSON with tempo, time_signature, duration, parts, and summary
    """
    return json.dumps(parse_midi_file(file_path, extract_notes, part_index))


@mcp.tool()
def tool_export_midi(
    notes: str,
    key_str: str | None = None,
    tempo_bpm: int = 120,
    time_signature: str = "4/4",
    output_path: str = "output.mid",
) -> str:
    """Create a MIDI file from a note sequence, chord progression, or Roman numeral progression.

    Args:
        notes: Note names with optional durations (e.g. 'C4:q,E4:q,G4:q' or 'C4:1,E4:0.5,G4:0.5')
        key_str: Optional key for Roman numeral input (e.g. 'C major')
        tempo_bpm: BPM (default: 120)
        time_signature: e.g. '4/4' (default: '4/4')
        output_path: Where to save the MIDI file

    Returns:
        JSON with file_path, note_count, duration, and summary
    """
    return json.dumps(export_midi(notes, key_str, tempo_bpm, time_signature, output_path))


@mcp.tool()
def tool_transpose_midi(
    file_path: str,
    semitones: int | None = None,
    target_key: str | None = None,
    output_path: str = "transposed.mid",
) -> str:
    """Transpose an existing MIDI file by semitones or to a target key.

    Args:
        file_path: Path to input MIDI file
        semitones: Number of semitones (mutually exclusive with target_key)
        target_key: Target key (e.g. 'D major')
        output_path: Where to save transposed MIDI

    Returns:
        JSON with file_path, original_key, new_key, and summary
    """
    return json.dumps(transpose_midi(file_path, semitones, target_key, output_path))


@mcp.tool()
def tool_modify_notes(
    file_path: str,
    operations: str,
    output_path: str = "modified.mid",
    part_index: int | None = None,
) -> str:
    """Modify notes in a MIDI file by criteria: pitch range, velocity, timing, or specific bar/beat.

    Args:
        file_path: Path to input MIDI file
        operations: JSON array of modification operations. Each operation has a "type" field:
            - {"type": "remove_below", "pitch": "C3"}
            - {"type": "remove_above", "pitch": "C6"}
            - {"type": "scale_velocity", "factor": 1.2}
            - {"type": "set_velocity", "min": 40, "max": 100, "value": 80}
            - {"type": "add_note", "pitch": "G3", "duration": 1.0, "velocity": 90}
        output_path: Where to save modified MIDI
        part_index: Optional, apply to specific part only (default: all parts)

    Returns:
        JSON with file_path, changes_made, and summary
    """
    ops = json.loads(operations) if isinstance(operations, str) else operations
    return json.dumps(modify_notes(file_path, ops, output_path, part_index))


@mcp.tool()
def tool_change_velocity(
    file_path: str,
    mode: str = "scale",
    factor: float = 1.0,
    min_velocity: int = 1,
    max_velocity: int = 127,
    fade_from: int = 80,
    fade_to: int = 100,
    output_path: str = "velocity_changed.mid",
) -> str:
    """Adjust note velocities (dynamics) in a MIDI file.

    Args:
        file_path: Path to input MIDI file
        mode: 'scale' (multiply all by factor), 'set_range' (clamp to min/max), 'fade' (gradual change)
        factor: For 'scale' mode (e.g. 1.2 = 20% louder)
        min_velocity: For 'set_range' mode (0-127)
        max_velocity: For 'set_range' mode (0-127)
        fade_from: For 'fade' mode (start velocity)
        fade_to: For 'fade' mode (end velocity)
        output_path: Where to save modified MIDI

    Returns:
        JSON with file_path, notes_changed, and summary
    """
    return json.dumps(
        change_velocity(file_path, mode, factor, min_velocity, max_velocity, fade_from, fade_to, output_path)
    )


@mcp.tool()
def tool_replace_chord_at(
    file_path: str,
    bar: int,
    beat: int,
    new_chord: str,
    duration: float = 1.0,
    output_path: str = "chord_replaced.mid",
) -> str:
    """Replace the chord at a specific bar and beat in a MIDI file.

    Args:
        file_path: Path to input MIDI file
        bar: 1-indexed bar number
        beat: Beat within the bar (1-indexed)
        new_chord: Chord name (e.g. 'G7', 'Cmaj7', 'Am') or note names (e.g. 'G4,B4,D5,F5')
        duration: Duration in beats (default: 1.0)
        output_path: Where to save modified MIDI

    Returns:
        JSON with file_path, original_chord, new_chord, and summary
    """
    return json.dumps(replace_chord_at(file_path, bar, beat, new_chord, duration, output_path))


@mcp.tool()
def tool_merge_midi(
    file_a: str,
    file_b: str,
    output_path: str = "merged.mid",
    offset_beats: float = 0.0,
) -> str:
    """Merge two MIDI files into one. Overlays the second file's tracks onto the first.

    Args:
        file_a: Base MIDI file path
        file_b: MIDI file to overlay
        output_path: Where to save merged MIDI
        offset_beats: Shift file_b by this many beats (default: 0)

    Returns:
        JSON with file_path, tracks_a, tracks_b, total_tracks, and summary
    """
    return json.dumps(merge_midi(file_a, file_b, output_path, offset_beats))


@mcp.tool()
def tool_quantize_midi(
    file_path: str,
    grid: str = "16th",
    swing: float = 0.0,
    output_path: str = "quantized.mid",
) -> str:
    """Quantize note timings in a MIDI file to a rhythmic grid.

    Args:
        file_path: Path to input MIDI file
        grid: Quantization grid: '16th', '8th', 'quarter', '32nd' (default: '16th')
        swing: Swing amount 0-1 (0 = straight, 0.5 = triplet feel, default: 0)
        output_path: Where to save quantized MIDI

    Returns:
        JSON with file_path, notes_adjusted, max_adjustment, and summary
    """
    return json.dumps(quantize_midi(file_path, grid, swing, output_path))


if __name__ == "__main__":
    mcp.run(transport="stdio")
