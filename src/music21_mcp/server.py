"""
music21 MCP Server — exposes music21 tools via Model Context Protocol.

The MCP tools accept JSON-serializable inputs (file paths, strings, ints)
and internally handle conversion to/from music21 streams.
"""

from __future__ import annotations

import json
from mcp.server.fastmcp import FastMCP

from .tools.parse_midi import parse_midi_file
from .tools.analyze_key import analyze_key
from .tools.export_midi import export_midi
from .tools.transpose_midi import transpose_midi
from .tools.change_velocity import change_velocity
from .tools.modify_notes import modify_notes
from .tools.replace_chord_at import replace_chord_at
from .tools.merge_midi import merge_midi
from .tools.quantize_midi import quantize_midi
from .tools.reharmonize import reharmonize
from .tools.harmonize_melody import harmonize_melody
from .tools.analyze_chord_progression import analyze_chord_progression
from .tools.extract_melody import extract_melody
from .tools.detect_modulations import detect_modulations
from .tools.analyze_form import analyze_form
from .tools.search_pattern import search_pattern

mcp = FastMCP("music21-mcp")

# Tool registry: maps tool name -> {description, fn}
# fn here is the raw tool function (not the MCP wrapper)
_tool_registry: dict[str, dict] = {
    "parse_midi_file": {
        "description": "Load a MIDI file and return a music21 stream for further processing.",
        "fn": parse_midi_file,
    },
    "analyze_key": {
        "description": "Analyze the key of a music21 stream. Returns key, mode, and confidence.",
        "fn": analyze_key,
    },
    "export_midi": {
        "description": "Export a music21 stream to a MIDI file.",
        "fn": export_midi,
    },
    "transpose_midi": {
        "description": "Transpose a stream by semitones or to a target key.",
        "fn": transpose_midi,
    },
    "change_velocity": {
        "description": "Adjust MIDI velocity (dynamics) of notes: scale, absolute, or offset.",
        "fn": change_velocity,
    },
    "modify_notes": {
        "description": "Filter/remove/select/shift notes by pitch criteria.",
        "fn": modify_notes,
    },
    "replace_chord_at": {
        "description": "Replace a chord at a specific bar/beat position.",
        "fn": replace_chord_at,
    },
    "merge_midi": {
        "description": "Overlay two streams into a single stream or multi-part score.",
        "fn": merge_midi,
    },
    "quantize_midi": {
        "description": "Snap note timings to a rhythmic grid (quarter, eighth, sixteenth).",
        "fn": quantize_midi,
    },
    "reharmonize": {
        "description": "Replace chords with harmonic alternatives (diatonic or jazz substitutions).",
        "fn": reharmonize,
    },
    "harmonize_melody": {
        "description": "Generate chord accompaniment for a melody line.",
        "fn": harmonize_melody,
    },
    "analyze_chord_progression": {
        "description": "Identify chords and Roman numerals in a progression.",
        "fn": analyze_chord_progression,
    },
    "extract_melody": {
        "description": "Extract the melody line (highest pitch) from a multi-part score.",
        "fn": extract_melody,
    },
    "detect_modulations": {
        "description": "Detect key changes (modulations) within a piece.",
        "fn": detect_modulations,
    },
    "analyze_form": {
        "description": "Analyze song structure — identify sections (A, B, A', etc.).",
        "fn": analyze_form,
    },
    "search_pattern": {
        "description": "Search for melodic patterns by exact pitch or interval sequence.",
        "fn": search_pattern,
    },
}


# --- MCP Tool Wrappers ---
# These accept file paths and JSON-serializable args, convert to streams,
# call the underlying tool, and return JSON strings.


@mcp.tool()
def mcp_parse_midi_file(file_path: str) -> str:
    """Parse a MIDI file into a music21 stream.

    Args:
        file_path: Path to the .mid file

    Returns:
        JSON with success status and basic stream info (note count, duration)
    """
    try:
        stream_obj = parse_midi_file(file_path)
        notes = list(stream_obj.flatten().notes)
        return json.dumps({
            "success": True,
            "file_path": file_path,
            "note_count": len(notes),
            "summary": f"Parsed {len(notes)} notes from {file_path}",
        })
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


@mcp.tool()
def mcp_analyze_key(file_path: str) -> str:
    """Detect the key of a MIDI file.

    Args:
        file_path: Path to the .mid file

    Returns:
        JSON with key, mode, confidence, and summary
    """
    try:
        stream_obj = parse_midi_file(file_path)
        result = analyze_key(stream_obj)
        result["success"] = True
        result["file_path"] = file_path
        result["summary"] = f"Key: {result['key']} (confidence: {result['confidence']})"
        return json.dumps(result)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


@mcp.tool()
def mcp_export_midi(file_path: str, output_path: str) -> str:
    """Export a parsed MIDI stream to a new file (use after modifications).

    Note: This is a placeholder — in practice, modifications return streams
    that can be saved. Use mcp_transpose_midi etc. which have output_path.

    Args:
        file_path: Source MIDI file to re-export
        output_path: Where to save the MIDI file

    Returns:
        JSON with success status and output path
    """
    try:
        stream_obj = parse_midi_file(file_path)
        result = export_midi(stream_obj, output_path)
        result["summary"] = f"Exported to {output_path}"
        return json.dumps(result)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


@mcp.tool()
def mcp_transpose_midi(
    file_path: str,
    semitones: int | None = None,
    target_key: str | None = None,
    output_path: str | None = None,
) -> str:
    """Transpose a MIDI file by semitones or to a target key.

    Args:
        file_path: Path to input MIDI file
        semitones: Number of semitones to transpose (can be negative)
        target_key: Target key name (e.g. "F", "Bb") — alternative to semitones
        output_path: Optional output path. If omitted, overwrites input.

    Returns:
        JSON with success status, original key, and new key
    """
    try:
        stream_obj = parse_midi_file(file_path)
        original_key = analyze_key(stream_obj)

        transposed = transpose_midi(stream_obj, semitones=semitones, target_key=target_key)
        new_key = analyze_key(transposed)

        if output_path is None:
            output_path = file_path.replace(".mid", "_transposed.mid")
        export_midi(transposed, output_path)

        return json.dumps({
            "success": True,
            "output_path": output_path,
            "original_key": original_key["key"],
            "new_key": new_key["key"],
            "summary": f"Transposed from {original_key['key']} to {new_key['key']}",
        })
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


@mcp.tool()
def mcp_change_velocity(
    file_path: str,
    scale: float | None = None,
    absolute: int | None = None,
    offset: int | None = None,
    output_path: str | None = None,
) -> str:
    """Adjust velocity (dynamics) of a MIDI file.

    Args:
        file_path: Path to input MIDI file
        scale: Multiply all velocities by this factor (e.g. 1.5 = 150%)
        absolute: Set all velocities to this exact value
        offset: Add this to all velocities (can be negative)
        output_path: Optional output path

    Returns:
        JSON with success status and notes changed
    """
    try:
        stream_obj = parse_midi_file(file_path)
        result_stream = change_velocity(stream_obj, scale=scale, absolute=absolute, offset=offset)

        if output_path is None:
            output_path = file_path.replace(".mid", "_velocity.mid")
        export_midi(result_stream, output_path)

        note_count = len(list(result_stream.flatten().notes))
        return json.dumps({
            "success": True,
            "output_path": output_path,
            "notes_changed": note_count,
            "summary": f"Adjusted velocity of {note_count} notes, saved to {output_path}",
        })
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


@mcp.tool()
def mcp_modify_notes(
    file_path: str,
    action: str = "remove",
    filter_below: str | None = None,
    filter_above: str | None = None,
    octave_shift: int | None = None,
    output_path: str | None = None,
) -> str:
    """Modify notes in a MIDI file by pitch criteria.

    Args:
        file_path: Path to input MIDI file
        action: 'remove', 'select', or 'shift_octave'
        filter_below: Remove/select notes below this pitch (e.g. "C4")
        filter_above: Remove/select notes above this pitch (e.g. "G5")
        octave_shift: Octaves to shift (for 'shift_octave' action)
        output_path: Optional output path

    Returns:
        JSON with success status and remaining note count
    """
    try:
        stream_obj = parse_midi_file(file_path)
        original_count = len(list(stream_obj.flatten().notes))

        result_stream = modify_notes(
            stream_obj,
            action=action,
            filter_below=filter_below,
            filter_above=filter_above,
            octave_shift=octave_shift,
        )

        new_count = len(list(result_stream.flatten().notes))

        if output_path is None:
            output_path = file_path.replace(".mid", "_modified.mid")
        export_midi(result_stream, output_path)

        return json.dumps({
            "success": True,
            "output_path": output_path,
            "original_notes": original_count,
            "remaining_notes": new_count,
            "summary": f"{action}: {original_count} → {new_count} notes, saved to {output_path}",
        })
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


@mcp.tool()
def mcp_replace_chord_at(
    file_path: str,
    bar: int,
    beat: int,
    new_chord: str,
    output_path: str | None = None,
) -> str:
    """Replace a chord at a specific bar/beat in a MIDI file.

    Args:
        file_path: Path to input MIDI file
        bar: Bar number (1-indexed)
        beat: Beat within the bar (1-indexed)
        new_chord: Comma-separated pitch names (e.g. "G3,B3,D4,F4")
        output_path: Optional output path

    Returns:
        JSON with success status and chord info
    """
    try:
        chord_pitches = [p.strip() for p in new_chord.split(",")]
        stream_obj = parse_midi_file(file_path)

        result_stream = replace_chord_at(stream_obj, bar=bar, beat=beat, new_chord=chord_pitches)

        if output_path is None:
            output_path = file_path.replace(".mid", "_replaced.mid")
        export_midi(result_stream, output_path)

        return json.dumps({
            "success": True,
            "output_path": output_path,
            "bar": bar,
            "beat": beat,
            "new_chord": new_chord,
            "summary": f"Replaced chord at bar {bar} beat {beat} with [{new_chord}]",
        })
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


@mcp.tool()
def mcp_merge_midi(
    file_a: str,
    file_b: str,
    output_parts: bool = False,
    output_path: str | None = None,
) -> str:
    """Merge (overlay) two MIDI files into one.

    Args:
        file_a: Path to first MIDI file (e.g. melody)
        file_b: Path to second MIDI file (e.g. bass)
        output_parts: If true, create multi-part score; if false, flat merge
        output_path: Optional output path

    Returns:
        JSON with success status and note count
    """
    try:
        stream_a = parse_midi_file(file_a)
        stream_b = parse_midi_file(file_b)

        result = merge_midi(stream_a, stream_b, output_parts=output_parts)

        if output_path is None:
            output_path = file_a.replace(".mid", "_merged.mid")
        export_midi(result, output_path)

        note_count = len(list(result.flatten().notes))
        return json.dumps({
            "success": True,
            "output_path": output_path,
            "total_notes": note_count,
            "summary": f"Merged {file_a} + {file_b} → {note_count} notes, saved to {output_path}",
        })
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


@mcp.tool()
def mcp_quantize_midi(
    file_path: str,
    grid: str = "sixteenth",
    output_path: str | None = None,
) -> str:
    """Quantize note timings in a MIDI file to a rhythmic grid.

    Args:
        file_path: Path to input MIDI file
        grid: Grid resolution: 'quarter', 'eighth', or 'sixteenth'
        output_path: Optional output path

    Returns:
        JSON with success status and notes quantized
    """
    try:
        stream_obj = parse_midi_file(file_path)
        result = quantize_midi(stream_obj, grid=grid)

        if output_path is None:
            output_path = file_path.replace(".mid", "_quantized.mid")
        export_midi(result, output_path)

        note_count = len(list(result.flatten().notes))
        return json.dumps({
            "success": True,
            "output_path": output_path,
            "notes_quantized": note_count,
            "grid": grid,
            "summary": f"Quantized {note_count} notes to {grid} grid, saved to {output_path}",
        })
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


@mcp.tool()
def mcp_reharmonize(
    file_path: str,
    style: str = "diatonic",
    output_path: str | None = None,
) -> str:
    """Reharmonize a chord progression in a MIDI file.

    Args:
        file_path: Path to input MIDI file
        style: 'diatonic' (in-key substitutions) or 'substitute' (jazz substitutions)
        output_path: Optional output path

    Returns:
        JSON with success status and chord changes
    """
    try:
        stream_obj = parse_midi_file(file_path)
        result = reharmonize(stream_obj, style=style)

        if output_path is None:
            output_path = file_path.replace(".mid", "_reharmonized.mid")
        export_midi(result, output_path)

        return json.dumps({
            "success": True,
            "output_path": output_path,
            "style": style,
            "summary": f"Reharmonized with {style} style, saved to {output_path}",
        })
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


@mcp.tool()
def mcp_harmonize_melody(
    file_path: str,
    style: str = "block",
    output_path: str | None = None,
) -> str:
    """Generate chord accompaniment for a melody in a MIDI file.

    Args:
        file_path: Path to input MIDI file (melody)
        style: 'block' (homophonic chords) or 'arpeggiated'
        output_path: Optional output path

    Returns:
        JSON with success status and chords added
    """
    try:
        stream_obj = parse_midi_file(file_path)
        result = harmonize_melody(stream_obj, style=style)

        if output_path is None:
            output_path = file_path.replace(".mid", "_harmonized.mid")
        export_midi(result, output_path)

        from music21 import chord as m21chord
        chord_count = sum(
            1 for e in result.recurse() if isinstance(e, m21chord.Chord)
        )

        return json.dumps({
            "success": True,
            "output_path": output_path,
            "chords_added": chord_count,
            "style": style,
            "summary": f"Added {chord_count} chords ({style} style), saved to {output_path}",
        })
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


@mcp.tool()
def mcp_analyze_chord_progression(file_path: str) -> str:
    """Analyze the chord progression of a MIDI file.

    Args:
        file_path: Path to the .mid file

    Returns:
        JSON with key, progression (Roman numerals + chord names), and summary
    """
    try:
        stream_obj = parse_midi_file(file_path)
        result = analyze_chord_progression(stream_obj)
        result["file_path"] = file_path
        return json.dumps(result)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


@mcp.tool()
def mcp_extract_melody(file_path: str, output_path: str | None = None) -> str:
    """Extract the melody line from a MIDI file.

    Args:
        file_path: Path to the .mid file
        output_path: Optional path to save extracted melody as MIDI

    Returns:
        JSON with note count, pitch range, and summary
    """
    try:
        stream_obj = parse_midi_file(file_path)
        melody = extract_melody(stream_obj)
        note_count = len(list(melody.flatten().notes))

        if output_path and note_count > 0:
            export_midi(melody, output_path)

        return json.dumps({
            "success": True,
            "note_count": note_count,
            "output_path": output_path,
            "summary": f"Extracted {note_count} melody notes",
        })
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


@mcp.tool()
def mcp_detect_modulations(file_path: str, window_size: int = 8) -> str:
    """Detect key changes (modulations) in a MIDI file.

    Args:
        file_path: Path to the .mid file
        window_size: Notes per analysis window (default: 8)

    Returns:
        JSON with list of modulations (from_key, to_key, offset) and summary
    """
    try:
        stream_obj = parse_midi_file(file_path)
        result = detect_modulations(stream_obj, window_size=window_size)
        result["file_path"] = file_path
        return json.dumps(result)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


@mcp.tool()
def mcp_analyze_form(file_path: str, window_size: int = 8) -> str:
    """Analyze the structural form of a MIDI file.

    Args:
        file_path: Path to the .mid file
        window_size: Notes per analysis window (default: 8)

    Returns:
        JSON with sections (label, start/end offset) and summary
    """
    try:
        stream_obj = parse_midi_file(file_path)
        result = analyze_form(stream_obj, window_size=window_size)
        result["file_path"] = file_path
        return json.dumps(result)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


@mcp.tool()
def mcp_search_pattern(
    file_path: str,
    pattern: str,
    pattern_type: str = "pitches",
) -> str:
    """Search for a melodic pattern in a MIDI file.

    Args:
        file_path: Path to the .mid file
        pattern: Comma-separated pattern. For 'pitches' mode: note names (e.g. "C4,D4,E4").
                 For 'intervals' mode: semitone intervals (e.g. "2,2")
        pattern_type: 'pitches' or 'intervals'

    Returns:
        JSON with list of matches (offset, notes) and summary
    """
    try:
        stream_obj = parse_midi_file(file_path)

        if pattern_type == "pitches":
            pattern_list = [p.strip() for p in pattern.split(",")]
        else:
            pattern_list = [int(x.strip()) for x in pattern.split(",")]

        result = search_pattern(stream_obj, pattern=pattern_list, pattern_type=pattern_type)
        result["file_path"] = file_path
        return json.dumps(result)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


if __name__ == "__main__":
    mcp.run(transport="stdio")