"""search_pattern tool - Phase 3 advanced analysis.

Searches for melodic patterns in a music21 stream. Supports two modes:
  - 'pitches': exact pitch matching (e.g. ["C4", "D4", "E4"])
  - 'intervals': interval sequence matching (e.g. [2, 2] for two whole steps)
"""

from music21 import stream, note as m21note, pitch as m21pitch


def search_pattern(
    score: stream.Stream,
    pattern: list,
    pattern_type: str = "pitches",
) -> dict:
    """Search for a melodic pattern in a music21 stream.

    Args:
        score: A music21 Stream
        pattern: Pattern to search for. For 'pitches' mode, list of note names
                 (e.g. ["C4", "D4"]). For 'intervals' mode, list of semitone
                 intervals (e.g. [2, 2] for two whole steps up).
        pattern_type: 'pitches' or 'intervals'

    Returns:
        dict with:
            'matches': list of dicts, each with:
                - 'offset': float
                - 'notes': list of pitch names
            'summary': str

    Raises:
        TypeError: If score is not a Stream
        ValueError: If pattern is empty
    """
    if not isinstance(score, stream.Stream):
        raise TypeError(f"Expected music21 Stream, got {type(score).__name__}")

    if not pattern:
        raise ValueError("Pattern must not be empty")

    # Collect all notes with offsets
    all_notes = []
    for elem in score.flatten().notes:
        if isinstance(elem, m21note.Note):
            all_notes.append(elem)

    if len(all_notes) < len(pattern):
        return {"matches": [], "summary": "Pattern longer than stream"}

    matches = []

    if pattern_type == "pitches":
        # Exact pitch matching
        target_pitches = [m21pitch.Pitch(p).nameWithOctave for p in pattern]

        for i in range(len(all_notes) - len(pattern) + 1):
            window = all_notes[i : i + len(pattern)]
            window_names = [n.nameWithOctave for n in window]
            if window_names == target_pitches:
                matches.append({
                    "offset": float(window[0].offset),
                    "notes": window_names,
                })

    elif pattern_type == "intervals":
        # Interval sequence matching
        # Convert pattern to list of ints (semitone intervals)
        target_intervals = [int(x) for x in pattern]

        for i in range(len(all_notes) - len(target_intervals)):
            window = all_notes[i : i + len(target_intervals) + 1]
            intervals = [
                window[j + 1].pitch.ps - window[j].pitch.ps
                for j in range(len(target_intervals))
            ]
            # Compare as integers
            if [int(round(iv)) for iv in intervals] == target_intervals:
                matches.append({
                    "offset": float(window[0].offset),
                    "notes": [n.nameWithOctave for n in window],
                })
    else:
        raise ValueError(
            f"Invalid pattern_type '{pattern_type}'. Must be 'pitches' or 'intervals'"
        )

    summary = f"Found {len(matches)} match(es) for pattern {pattern}"
    if matches:
        match_strs = [f"at offset {m['offset']}" for m in matches]
        summary += ": " + ", ".join(match_strs)

    return {"matches": matches, "summary": summary}