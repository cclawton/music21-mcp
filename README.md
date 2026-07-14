# music21-mcp

Symbolic music analysis and editing tools exposed through MCP, built on music21. The server works with user-supplied MIDI and supports analysis, transformation, and basic accompaniment generation.

The current implementation registers 16 MCP tools and has 120 automated tests.

## What it does

Give an AI agent a MIDI file and it can:

- **Read** — parse MIDI, detect key, analyze chord progressions
- **Edit** — transpose, change velocity, filter notes, replace chords, merge files, quantize timings
- **Generate** — reharmonize progressions, harmonize melodies
- **Analyze** — detect modulations, extract melody, identify song form, search for patterns

## Tools

The MCP-facing names currently use an `mcp_` prefix, such as `mcp_analyze_key` and `mcp_transpose_midi`. The underlying Python functions use the unprefixed names shown below.

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
cd music21-mcp

# Create and activate venv
python3 -m venv venv
source venv/bin/activate

# Install the package and test dependencies in editable mode
pip install -e ".[dev]"
```

### Run tests

```bash
# All 120 tests
pytest -v

# Just one tool's tests
pytest tests/test_transpose_midi.py -v
```

### Use as MCP server

The server runs over stdio and is intended for MCP clients that support local stdio servers.

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
      "cwd": "/path/to/music21-mcp"
    }
  }
}
```

Or if using the project venv:

```json
{
  "mcpServers": {
    "music21-mcp": {
      "command": "/path/to/music21-mcp/venv/bin/python",
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

## Example prompts for testing

Single-tool prompts to verify each tool works in isolation:

1. **Parse only** — "Load `song.mid` with parse_midi_file and tell me how many parts and measures it has."

2. **Key detection** — "Use parse_midi_file to load `song.mid`, then analyze_key to tell me the key, mode, and confidence."

3. **Export** — "Load `song.mid` with parse_midi_file and export it to `copy.mid` with export_midi. Report the output path."

4. **Transpose** — "Parse `song.mid` and transpose it down 3 semitones. Export to `song_down.mid`."

5. **Transpose to key** — "Load `song.mid`, detect its key, then transpose it to E minor. Export to `song_em.mid`."

6. **Velocity** — "Parse `song.mid`, set all velocities to a fixed value of 90. Export to `song_vel90.mid`."

7. **Velocity boost** — "Load `song.mid` and scale all velocities by 1.3 (clamped to 127). Export to `song_louder.mid`."

8. **Filter notes** — "Parse `song.mid` and remove all notes below C3. Export to `song_no_bass.mid`."

9. **Octave shift** — "Load `song.mid` and shift everything up 1 octave. Export to `song_oct_up.mid`."

10. **Replace chord** — "Parse `song.mid` and replace the chord at bar 2, beat 1 with a C major triad. Export to `song_newchord.mid`."

11. **Merge** — "Load `drums.mid` and `bass.mid`, merge them into a single file. Export to `drum_and_bass.mid`."

12. **Quantize** — "Parse `song.mid` and quantize all timings to a sixteenth-note grid. Export to `song_quantized.mid`."

13. **Reharmonize** — "Load `song.mid` and reharmonize the chord progression using jazz substitutions. Export to `song_jazz.mid`."

14. **Harmonize** — "Parse `melody.mid` and generate block chord accompaniment from the melody line. Export to `melody_with_chords.mid`."

15. **Chord analysis** — "Load `song.mid` and analyze the chord progression. Give me the chords and Roman numerals."

16. **Extract melody** — "Parse `song.mid` and extract just the melody line. Export to `melody_only.mid`."

17. **Detect modulations** — "Load `song.mid` and find all key changes. Tell me where each modulation happens."

18. **Analyze form** — "Parse `song.mid` and identify the song structure (A, B, A' sections)."

19. **Search pattern** — "Load `song.mid` and search for the pitch sequence C4-E4-G4. Tell me where it occurs."

Multi-tool chains to test tool composition:

20. **Full analysis** — "Load `song.mid`. Detect the key, analyze the chord progression, extract the melody, and analyze the song form. Give me a complete analysis report."

21. **Transpose and harmonize** — "Parse `song.mid`, transpose up 5 semitones, then reharmonize the result with jazz substitutions. Export to `song_jazz_up.mid`."

22. **Clean and quantize** — "Load `song.mid`, remove all notes below C2, quantize to an eighth-note grid, and scale velocities by 0.8. Export to `song_cleaned.mid`."

23. **Melody extraction pipeline** — "Parse `song.mid`, extract the melody, harmonize it with block chords, and export to `melody_harmonized.mid`."

24. **Key-aware reharm** — "Load `song.mid`, detect the key, then reharmonize using diatonic substitutions appropriate for that key. Export to `song_diatonic.mid`."

25. **Modulation-aware transpose** — "Parse `song.mid`, detect all modulations, then transpose the whole piece so the first key becomes A minor. Export to `song_am.mid`."

26. **Pattern search** — "Load `song.mid` and search for the interval sequence [2, 2] (two whole steps up). Report every matching offset."

27. **Form and melody analysis** — "Parse `song.mid`, analyze its form, then extract the full melody line and export it to `melody.mid`."

28. **Multi-file merge and clean** — "Merge `drums.mid` and `bass.mid`, then merge that result with `keys.mid`. Quantize the combined file to a sixteenth grid, set velocities to 100, and export to `full_band.mid`."

29. **End-to-end remix** — "Load `song.mid`. Detect key, transpose down 2 semitones, quantize to eighth notes, reharmonize with jazz substitutions, boost velocity by 1.4, and export to `song_remix.mid`."

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

Most editing and analysis functions operate on music21 streams. Parsing and export perform file I/O, while the MCP wrappers accept file paths and return JSON strings. This keeps the domain logic independently testable.

## Tech

- [music21](https://web.mit.edu/music21/) — MIT's music theory and analysis toolkit
- [MCP](https://modelcontextprotocol.io/) — Model Context Protocol for AI agent tool calling
- Python 3.11+, pytest, strict TDD

## License

MIT
