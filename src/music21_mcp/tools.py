"""
music21 MCP Server — Tool implementations

Phase 1a: analyze_key, parse_midi_file, export_midi
Phase 1c: transpose_midi, modify_notes, change_velocity, replace_chord_at, merge_midi, quantize_midi
"""

from __future__ import annotations
import json
from pathlib import Path
from typing import Any

from music21 import converter, note, stream, chord, key, roman, interval, pitch, meter, tempo


# ─── Helpers ───────────────────────────────────────────────────────────────


def _parse_source(source: str) -> stream.Stream:
    """Parse a MIDI file path or inline note sequence into a music21 Stream."""
    if source.endswith('.mid') or source.endswith('.midi') or source.endswith('.xml') or source.endswith('.musicxml'):
        return converter.parse(source)
    # Treat as inline note sequence: "C4:q,E4:q,G4:q"
    s = stream.Stream()
    for token in source.split(','):
        token = token.strip()
        if not token:
            continue
        if ':' in token:
            name, dur_str = token.split(':', 1)
        else:
            name, dur_str = token, 'q'
        n = note.Note(name.strip())
        n.quarterLength = _parse_duration(dur_str.strip())
        s.append(n)
    return s


def _parse_duration(dur_str: str) -> float:
    """Parse a duration string like 'q', 'h', 'e', '1', '0.5' into quarter length."""
    dur_map = {'w': 4.0, 'h': 2.0, 'q': 1.0, 'e': 0.5, 's': 0.25, 't': 0.125}
    if dur_str in dur_map:
        return dur_map[dur_str]
    try:
        return float(dur_str)
    except ValueError:
        return 1.0


def _notes_to_json(notes_list) -> list[dict]:
    """Convert music21 notes to JSON-serializable dicts."""
    return [
        {
            'pitch': n.nameWithOctave,
            'midi': n.pitch.midi,
            'start_time': float(n.offset),
            'duration': float(n.quarterLength),
            'velocity': n.volume.velocity if hasattr(n, 'volume') and n.volume is not None else 64,
        }
        for n in notes_list
    ]


# ─── Phase 1a: Analysis + MIDI I/O ────────────────────────────────────────


def analyze_key(source: str, detail: bool = False) -> dict:
    """Detect the most likely key of a MIDI file or note sequence."""
    score = _parse_source(source)
    k = score.analyze('key')

    result: dict[str, Any] = {
        'key': f'{k.tonic.name} {k.mode}',
        'confidence': round(k.correlationCoefficient, 4),
        'alternatives': [
            {'key': f'{alt.tonic.name} {alt.mode}', 'confidence': round(alt.correlationCoefficient, 4)}
            for alt in k.alternateInterpretations[:5]
        ],
    }

    if detail:
        pcs = {}
        for n in score.flatten().notes:
            pc = n.pitch.pitchClass
            pcs[pc] = pcs.get(pc, 0) + 1
        result['pitch_class_distribution'] = pcs

    result['summary'] = f"Key: {k.tonic.name} {k.mode} (confidence: {k.correlationCoefficient:.2%})"
    return result


def parse_midi_file(file_path: str, extract_notes: bool = False, part_index: int | None = None) -> dict:
    """Parse a MIDI file and return its structure."""
    score = converter.parse(file_path)

    parts_data = []
    parts = score.parts if hasattr(score, 'parts') and score.parts else [score]

    if part_index is not None and part_index < len(parts):
        parts = [parts[part_index]]

    for i, part in enumerate(parts):
        notes = list(part.flatten().notesAndRests)
        part_data: dict[str, Any] = {
            'index': i,
            'name': part.partName or f'Part {i}',
            'note_count': len([n for n in notes if isinstance(n, note.Note)]),
        }
        if notes:
            pitches = [n.pitch for n in notes if isinstance(n, note.Note)]
            if pitches:
                part_data['pitch_range'] = f'{min(p.ps for p in pitches):.0f} to {max(p.ps for p in pitches):.0f}'
        if extract_notes:
            part_data['notes'] = _notes_to_json([n for n in notes if isinstance(n, note.Note)])
        parts_data.append(part_data)

    # Get tempo and time signature
    tempos = list(score.flatten().getElementsByClass(tempo.MetronomeMark))
    time_sigs = list(score.flatten().getElementsByClass(meter.TimeSignature))

    result = {
        'tempo': tempos[0].number if tempos else 120,
        'time_signature': str(time_sigs[0]) if time_sigs else '4/4',
        'duration': float(score.duration.quarterLength),
        'parts': parts_data,
    }
    result['summary'] = f"{len(parts_data)} part(s), {result['tempo']} BPM, {result['time_signature']}"
    return result


def export_midi(
    notes: str,
    key_str: str | None = None,
    tempo_bpm: int = 120,
    time_signature: str = '4/4',
    output_path: str = 'output.mid',
) -> dict:
    """Create a MIDI file from a note sequence."""
    s = stream.Stream()

    # Add tempo and time signature
    s.append(tempo.MetronomeMark(number=tempo_bpm))
    s.append(meter.TimeSignature(time_signature))

    # Add key if provided
    if key_str:
        s.append(key.Key(key_str))

    # Parse notes
    for token in notes.split(','):
        token = token.strip()
        if not token:
            continue
        if ':' in token:
            name, dur_str = token.split(':', 1)
        else:
            name, dur_str = token, 'q'
        n = note.Note(name.strip())
        n.quarterLength = _parse_duration(dur_str.strip())
        s.append(n)

    s.write('midi', fp=output_path)

    note_count = len([n for n in s.flatten().notes if isinstance(n, note.Note)])
    duration = float(s.duration.quarterLength)

    return {
        'file_path': str(Path(output_path).resolve()),
        'note_count': note_count,
        'duration': duration,
        'summary': f'Exported {note_count} notes to {output_path} ({duration} beats, {tempo_bpm} BPM)',
    }


# ─── Phase 1c: MIDI Editing ─────────────────────────────────────────────────


def transpose_midi(
    file_path: str,
    semitones: int | None = None,
    target_key: str | None = None,
    output_path: str = 'transposed.mid',
) -> dict:
    """Transpose an existing MIDI file."""
    score = converter.parse(file_path)

    if target_key and semitones is None:
        current_key = score.analyze('key')
        target = key.Key(target_key)
        # Calculate interval
        iv = interval.Interval(current_key.tonic, target.tonic)
        semitones = iv.semitones

    if semitones is None:
        return {'error': 'Either semitones or target_key must be provided'}

    transposed = score.transpose(semitones)
    transposed.write('midi', fp=output_path)

    original_key = score.analyze('key')
    new_key = transposed.analyze('key')

    return {
        'file_path': str(Path(output_path).resolve()),
        'original_key': f'{original_key.tonic.name} {original_key.mode}',
        'new_key': f'{new_key.tonic.name} {new_key.mode}',
        'semitones': semitones,
        'summary': f'Transposed {semitones} semitones from {original_key.tonic.name} {original_key.mode} to {new_key.tonic.name} {new_key.mode}',
    }


def modify_notes(
    file_path: str,
    operations: list[dict],
    output_path: str = 'modified.mid',
    part_index: int | None = None,
) -> dict:
    """Modify notes in a MIDI file by criteria."""
    score = converter.parse(file_path)

    # Get parts to work with
    if part_index is not None and hasattr(score, 'parts') and part_index < len(score.parts):
        target = score.parts[part_index]
    else:
        target = score

    changes = 0

    for op in operations:
        op_type = op.get('type')

        if op_type == 'remove_below':
            cutoff = pitch.Pitch(op['pitch']).midi
            to_remove = [n for n in target.flatten().notes if isinstance(n, note.Note) and n.pitch.midi < cutoff]
            for n in to_remove:
                target.remove(n)
            changes += len(to_remove)

        elif op_type == 'remove_above':
            cutoff = pitch.Pitch(op['pitch']).midi
            to_remove = [n for n in target.flatten().notes if isinstance(n, note.Note) and n.pitch.midi > cutoff]
            for n in to_remove:
                target.remove(n)
            changes += len(to_remove)

        elif op_type == 'scale_velocity':
            factor = op.get('factor', 1.0)
            for n in target.flatten().notes:
                if isinstance(n, note.Note):
                    n.volume.velocity = min(127, max(1, int(n.volume.velocity * factor)))
            changes += 1

        elif op_type == 'set_velocity':
            val = op.get('value', 80)
            min_v = op.get('min', 0)
            max_v = op.get('max', 127)
            for n in target.flatten().notes:
                if isinstance(n, note.Note):
                    if min_v <= n.volume.velocity <= max_v:
                        n.volume.velocity = val
            changes += 1

        elif op_type == 'add_note':
            n = note.Note(op['pitch'])
            n.quarterLength = op.get('duration', 1.0)
            n.volume.velocity = op.get('velocity', 80)
            # TODO: bar/beat to offset conversion
            target.append(n)
            changes += 1

    score.write('midi', fp=output_path)

    return {
        'file_path': str(Path(output_path).resolve()),
        'changes_made': changes,
        'summary': f'Applied {len(operations)} operation(s), {changes} change(s) made',
    }


def change_velocity(
    file_path: str,
    mode: str = 'scale',
    factor: float = 1.0,
    min_velocity: int = 1,
    max_velocity: int = 127,
    fade_from: int = 80,
    fade_to: int = 100,
    output_path: str = 'velocity_changed.mid',
) -> dict:
    """Adjust note velocities in a MIDI file."""
    score = converter.parse(file_path)
    notes = [n for n in score.flatten().notes if isinstance(n, note.Note)]
    changed = 0

    if mode == 'scale':
        for n in notes:
            new_vel = min(127, max(1, int(n.volume.velocity * factor)))
            if new_vel != n.volume.velocity:
                n.volume.velocity = new_vel
                changed += 1
    elif mode == 'set_range':
        for n in notes:
            new_vel = max(min_velocity, min(max_velocity, n.volume.velocity))
            if new_vel != n.volume.velocity:
                n.volume.velocity = new_vel
                changed += 1
    elif mode == 'fade':
        total = len(notes)
        for i, n in enumerate(notes):
            t = i / max(total - 1, 1)
            new_vel = int(fade_from + (fade_to - fade_from) * t)
            n.volume.velocity = new_vel
            changed += 1

    score.write('midi', fp=output_path)

    return {
        'file_path': str(Path(output_path).resolve()),
        'notes_changed': changed,
        'summary': f'Changed velocity of {changed} notes (mode: {mode})',
    }


def replace_chord_at(
    file_path: str,
    bar: int,
    beat: int,
    new_chord: str,
    duration: float = 1.0,
    output_path: str = 'chord_replaced.mid',
) -> dict:
    """Replace a chord at a specific bar and beat in a MIDI file."""
    score = converter.parse(file_path)

    # Convert bar/beat to offset
    ts = score.flatten().getElementsByClass(meter.TimeSignature)
    beats_per_bar = ts[0].numerator if ts else 4
    offset = (bar - 1) * beats_per_bar + (beat - 1)

    # Chordify to find existing chord at that position
    chordified = score.chordify()
    original_chord = None
    for c in chordified.flatten().getElementsByClass('Chord'):
        if abs(c.offset - offset) < 0.1:
            original_chord = c
            break

    # Create new chord
    if ',' in new_chord and any(c.isalpha() for c in new_chord.split(',')[0]):
        # Note names: "G4,B4,D5,F5"
        new_c = chord.Chord(new_chord.split(','))
    else:
        # Chord name: "G7", "Cmaj7"
        new_c = roman.RomanNumeral(new_chord, score.analyze('key')).pitches
        new_c = chord.Chord(new_c)
    new_c.quarterLength = duration

    # Remove notes near the target offset and insert new chord
    for n in list(score.flatten().notes):
        if isinstance(n, note.Note) and abs(n.offset - offset) < 0.5:
            score.remove(n)

    score.insert(offset, new_c)
    score.write('midi', fp=output_path)

    orig_str = str(original_chord.pitchNames) if original_chord else 'None'

    return {
        'file_path': str(Path(output_path).resolve()),
        'original_chord': orig_str,
        'new_chord': str(new_c.pitchNames),
        'summary': f'Replaced chord at bar {bar} beat {beat} with {new_c.pitchNames}',
    }


def merge_midi(
    file_a: str,
    file_b: str,
    output_path: str = 'merged.mid',
    offset_beats: float = 0.0,
) -> dict:
    """Merge two MIDI files into one."""
    score_a = converter.parse(file_a)
    score_b = converter.parse(file_b)

    # Insert parts from B into A
    if hasattr(score_b, 'parts'):
        for part in score_b.parts:
            part.offset = offset_beats
            score_a.insert(offset_beats, part)
    else:
        score_b.offset = offset_beats
        score_a.insert(offset_beats, score_b)

    score_a.write('midi', fp=output_path)

    parts_a = len(score_a.parts) if hasattr(score_a, 'parts') else 1
    parts_b = len(score_b.parts) if hasattr(score_b, 'parts') else 1

    return {
        'file_path': str(Path(output_path).resolve()),
        'tracks_a': parts_a,
        'tracks_b': parts_b,
        'total_tracks': parts_a + parts_b,
        'summary': f'Merged {parts_b} track(s) from B into {parts_a} track(s) from A',
    }


def quantize_midi(
    file_path: str,
    grid: str = '16th',
    swing: float = 0.0,
    output_path: str = 'quantized.mid',
) -> dict:
    """Quantize note timings to a rhythmic grid."""
    score = converter.parse(file_path)

    grid_values = {
        '32nd': 0.125,
        '16th': 0.25,
        '8th': 0.5,
        'quarter': 1.0,
        'half': 2.0,
    }
    grid_val = grid_values.get(grid, 0.25)

    adjusted = 0
    max_adj = 0.0

    for n in score.flatten().notes:
        if isinstance(n, note.Note):
            original_offset = n.offset
            # Snap to grid
            grid_pos = round(original_offset / grid_val) * grid_val

            # Apply swing (delay every other grid position)
            if swing > 0 and (grid_pos / grid_val) % 2 == 1:
                grid_pos += grid_val * swing

            adj = abs(grid_pos - original_offset)
            if adj > 0.001:
                n.offset = grid_pos
                adjusted += 1
                max_adj = max(max_adj, adj)

    score.write('midi', fp=output_path)

    return {
        'file_path': str(Path(output_path).resolve()),
        'notes_adjusted': adjusted,
        'max_adjustment': round(max_adj, 4),
        'summary': f'Quantized {adjusted} notes to {grid} grid (swing: {swing})',
    }
