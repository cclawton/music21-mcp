"""detect_modulations tool - Phase 3 advanced analysis.

Detects key changes (modulations) within a piece by analyzing
the key of successive windows of notes.

Uses music21's windowed key analysis to find where the key changes.
"""

from music21 import stream, analysis, key as m21key


def detect_modulations(
    score: stream.Stream,
    window_size: int = 8,
) -> dict:
    """Detect modulations (key changes) in a music21 stream.

    Args:
        score: A music21 Stream
        window_size: Number of notes per analysis window (default: 8)

    Returns:
        dict with:
            'modulations': list of dicts, each with:
                - 'from_key': str
                - 'to_key': str
                - 'offset': float (where the new key starts)
            'summary': str

    Raises:
        TypeError: If score is not a Stream
    """
    if not isinstance(score, stream.Stream):
        raise TypeError(f"Expected music21 Stream, got {type(score).__name__}")

    # Collect all notes from the flattened stream
    all_notes = list(score.flatten().notes)

    if len(all_notes) < window_size:
        return {
            "modulations": [],
            "summary": "Not enough notes for modulation analysis",
        }

    # Analyze key in sliding windows
    keys_by_window = []
    step = max(1, window_size // 2)  # 50% overlap

    for i in range(0, len(all_notes) - window_size + 1, step):
        window_notes = all_notes[i : i + window_size]
        window_stream = stream.Stream()
        for n in window_notes:
            window_stream.append(n.__class__())  # Create same type
            # Copy pitch info
            if hasattr(n, "pitch"):
                window_stream[-1].pitch = n.pitch
            elif hasattr(n, "pitches"):
                window_stream[-1].pitches = n.pitches

        try:
            detected = window_stream.analyze("key")
            keys_by_window.append({
                "key": f"{detected.tonic.name} {detected.mode}",
                "offset": float(all_notes[i].offset),
                "note_index": i,
            })
        except Exception:
            continue

    if not keys_by_window:
        return {
            "modulations": [],
            "summary": "Could not analyze key in any window",
        }

    # Find points where the key changes
    modulations = []
    prev_key = keys_by_window[0]["key"]

    for entry in keys_by_window[1:]:
        if entry["key"] != prev_key:
            modulations.append({
                "from_key": prev_key,
                "to_key": entry["key"],
                "offset": entry["offset"],
            })
            prev_key = entry["key"]

    summary = f"Found {len(modulations)} modulation(s)"
    if modulations:
        mod_strs = [f"{m['from_key']} → {m['to_key']} at offset {m['offset']}" for m in modulations]
        summary += ": " + "; ".join(mod_strs)

    return {
        "modulations": modulations,
        "summary": summary,
    }