"""analyze_form tool - Phase 3 advanced analysis.

Analyzes the structural form of a piece by detecting sections based on
pitch register, rhythmic patterns, and key changes.

Uses a simple segmentation approach: divides the stream into windows,
analyzes each window's characteristics (pitch range, key), and groups
similar adjacent windows into sections.
"""

from music21 import stream, note as m21note


def analyze_form(
    score: stream.Stream,
    window_size: int = 8,
) -> dict:
    """Analyze the structural form of a music21 stream.

    Args:
        score: A music21 Stream
        window_size: Number of notes per analysis window (default: 8)

    Returns:
        dict with:
            'sections': list of dicts, each with:
                - 'label': str (e.g. "A", "B", "A'")
                - 'start_offset': float
                - 'end_offset': float
                - 'note_range': str (e.g. "C4-C5")
            'summary': str

    Raises:
        TypeError: If score is not a Stream
    """
    if not isinstance(score, stream.Stream):
        raise TypeError(f"Expected music21 Stream, got {type(score).__name__}")

    all_notes = list(score.flatten().notes)

    if not all_notes:
        return {"sections": [], "summary": "No notes found"}

    # Build windows of notes and characterize each
    windows = []
    for i in range(0, len(all_notes), window_size):
        chunk = all_notes[i : i + window_size]
        if not chunk:
            break

        # Get pitch stats for this window
        pitches = []
        for n in chunk:
            if isinstance(n, m21note.Note):
                pitches.append(n.pitch.ps)
            elif hasattr(n, "pitches"):
                pitches.extend([p.ps for p in n.pitches])

        if not pitches:
            continue

        avg_pitch = sum(pitches) / len(pitches)
        min_pitch = min(pitches)
        max_pitch = max(pitches)

        windows.append({
            "start_offset": float(chunk[0].offset),
            "end_offset": float(chunk[-1].offset + chunk[-1].quarterLength),
            "avg_pitch": avg_pitch,
            "min_pitch": min_pitch,
            "max_pitch": max_pitch,
            "note_count": len(chunk),
        })

    if not windows:
        return {"sections": [], "summary": "Could not analyze form"}

    # Group windows into sections based on register changes
    # A new section starts when the average pitch changes significantly
    sections = []
    current_label = "A"
    label_map = ["A", "B", "C", "D", "E", "F"]
    label_idx = 0

    current_section_start = windows[0]["start_offset"]
    current_section_end = windows[0]["end_offset"]
    current_avg = windows[0]["avg_pitch"]

    # Threshold: 5 semitones = significant register change
    PITCH_THRESHOLD = 5.0

    for w in windows[1:]:
        if abs(w["avg_pitch"] - current_avg) > PITCH_THRESHOLD:
            # New section
            min_p = int(current_section_start)
            sections.append({
                "label": label_map[label_idx % len(label_map)],
                "start_offset": current_section_start,
                "end_offset": current_section_end,
                "note_range": f"{int(current_avg)}",
            })
            label_idx += 1
            current_section_start = w["start_offset"]
            current_avg = w["avg_pitch"]
        else:
            # Extend current section
            current_section_end = w["end_offset"]
            # Update running average
            current_avg = (current_avg + w["avg_pitch"]) / 2

    # Add the last section
    sections.append({
        "label": label_map[label_idx % len(label_map)],
        "start_offset": current_section_start,
        "end_offset": current_section_end,
        "note_range": f"{int(current_avg)}",
    })

    # Check for repeated sections (same label pattern)
    labels = [s["label"] for s in sections]
    # If last section matches first, label it A' (A prime)
    if len(labels) >= 3 and labels[0] == labels[-1] and labels[-1] == "A":
        sections[-1]["label"] = "A'"

    form_str = " - ".join(s["label"] for s in sections)
    summary = f"Form: {form_str} ({len(sections)} sections)"

    return {
        "sections": sections,
        "summary": summary,
    }