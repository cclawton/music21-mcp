# music21-mcp

MCP server exposing 16 music21 MIDI analysis and editing tools to AI agents. Built spec-driven with TDD — 120 tests, all green.

## What it does

Give an AI agent a MIDI file and it can:

- **Read** — parse MIDI, detect key, analyze chord progressions
- **Edit** — transpose, change velocity, filter notes, replace chords, merge files, quantize timings
- **Generate** — reharmonize progressions, harmonize melodies
- **Analyze** — detect modulations, extract melody, identify song form, search for patterns

## Tools

| Phase | Tool | What it does |
|-------|------|-------------|
| 1a | `parse_midi_file` | Load a .mid file into a music21 stream |
| 1a | `analyze_key` | Detect key, mode, and confidence |
| 1a | `export_midi` | Write a stream to a .mid file |
| 1c | `transpose_midi` | Transpose by semitones or to a target key |
| 1c | `change_velocity` | Scale, set, or offset note velocities (clamped 1–127) |
| 1c | `modify_notes` | Remove/select notes by pitch range, shift octaves |
| 1c | `replace_chord_at` | Replace a chord at a specific bar/beat |
| 1c | `merge_midi` | Overlay two streams (flat or multi-part score) |
| 1c | `quantize_midi` | Snap note timings to quarter/eighth/sixteenth grid |
| 2 | `reharmonize` | Replace chords with diatonic or jazz substitutions |
| 2 | `harmonize_melody` | Generate block chord accompaniment from a melody |
| 3 | `analyze_chord_progression` | Identify chords + Roman numerals in a progression |
| 3 | `extract_melody` | Isolate the melody line (highest pitch per offset) |
| 3 | `detect_modulations` | Find key changes via sliding window analysis |
| 3 | `analyze_form` | Identify song sections (A, B, A') by register changes |
| 3 | `search_pattern` | Find melodic patterns by exact pitch or interval sequence |

## Getting started

### Prerequisites

- Python 3.11+
- A virtual environment (recommended)

### Install

```bash
cd ~/Hacking/music21-mcp

# Create and activate venv
python3 -m venv venv
source venv/bin/activate

# Install the package in editable mode
pip install -e .

# Install MCP server dependency
pip install mcp
```

### Run tests

```bash
# All 120 tests
pytest -v

# Just one tool's tests
pytest tests/test_transpose_midi.py -v
```

### Use as MCP server

The server runs over stdio, compatible with any MCP-aware client (Claude Desktop, Cursor, etc).

```bash
# Start the server
python -m music21_mcp.server
```

To configure in an MCP client, add to your client's MCP config:

```json
{
  "mcpServers": {
    "music21-mcp": {
      "command": "python",
      "args": ["-m", "music21_mcp.server"],
      "cwd": "/Users/craiglawton/Hacking/music21-mcp"
    }
  }
}
```

Or if using the project venv:

```json
{
  "mcpServers": {
    "music21-mcp": {
      "command": "/Users/craiglawton/Hacking/music21-mcp/venv/bin/python",
      "args": ["-m", "music21_mcp.server"]
    }
  }
}
```

### Use directly in Python

Every tool is a pure function you can call without the MCP layer:

```python
from music21_mcp.tools.parse_midi import parse_midi_file
from music21_mcp.tools.analyze_key import analyze_key
from music21_mcp.tools.transpose_midi import transpose_midi
from music21_mcp.tools.export_midi import export_midi

# Load a MIDI file
stream = parse_midi_file("song.mid")

# Detect the key
key_info = analyze_key(stream)
print(key_info)
# {'key': 'C major', 'mode': 'major', 'confidence': 0.797}

# Transpose to F major
transposed = transpose_midi(stream, target_key="F")

# Save the result
export_midi(transposed, "song_in_f.mid")
```

### Example: the full pipeline

```python
from music21_mcp.tools import (
    parse_midi_file, analyze_key, transpose_midi,
    change_velocity, quantize_midi, export_midi,
)

# Load
s = parse_midi_file("input.mid")

# Detect key
print(analyze_key(s))

# Transpose up 2 semitones, make 20% louder, quantize to 16th notes
s = transpose_midi(s, semitones=2)
s = change_velocity(s, scale=1.2)
s = quantize_midi(s, grid="sixteenth")

# Save
export_midi(s, "output.mid")
```

## Architecture

```
src/music21_mcp/
  __init__.py          # Package entry
  server.py            # FastMCP server — 16 tool wrappers returning JSON
  tools/
    parse_midi.py      # Phase 1a
    analyze_key.py
    export_midi.py
    transpose_midi.py  # Phase 1c
    change_velocity.py
    modify_notes.py
    replace_chord_at.py
    merge_midi.py
    quantize_midi.py
    reharmonize.py     # Phase 2
    harmonize_melody.py
    analyze_chord_progression.py  # Phase 3
    extract_melody.py
    detect_modulations.py
    analyze_form.py
    search_pattern.py

tests/
    test_*.py          # One test file per tool, plus server + e2e tests
```

Each tool is a pure function that takes a music21 Stream and returns a Stream or dict. The MCP server layer handles file-path-to-stream conversion and JSON serialization. This separation means tools are testable without the MCP protocol and usable as a plain Python library.

## Tech

- [music21](https://web.mit.edu/music21/) — MIT's music theory and analysis toolkit
- [MCP](https://modelcontextprotocol.io/) — Model Context Protocol for AI agent tool calling
- Python 3.11+, pytest, strict TDD

## License

MIT
