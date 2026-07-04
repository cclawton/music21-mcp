"""analyze_chord_progression tool - Phase 3 advanced analysis.

Identifies chords in a stream and labels them with Roman numerals
relative to the detected key.
"""

from music21 import stream, chord as m21chord, roman, key as m21key
from .analyze_key import analyze_key


def analyze_chord_progression(score: stream.Stream) -> dict:
    """Analyze a chord progression in a music21 stream.

    Args:
        score: A music21 Stream containing chords

    Returns:
        dict with:
            'key': detected key string
            'progression': list of dicts, each with:
                - 'roman_numeral': str (e.g. "I", "IV", "V")
                - 'chord_name': str (e.g. "C major", "F major")
                - 'offset': float (position in stream)
            'summary': str

    Raises:
        TypeError: If score is not a Stream
    """
    if not isinstance(score, stream.Stream):
        raise TypeError(f"Expected music21 Stream, got {type(score).__name__}")

    # Detect key — guard against empty streams
    try:
        key_result = analyze_key(score)
        key_tonic = key_result["key"].split()[0]
        key_mode = key_result.get("mode", "major")
        detected_key = m21key.Key(key_tonic, key_mode)
        key_str = key_result["key"]
    except Exception:
        return {
            "key": "Unknown",
            "progression": [],
            "summary": "Could not analyze key — stream may be empty",
        }

    # Find all chords via recurse (handles both flat and nested streams)
    chords = []
    for elem in score.recurse():
        if isinstance(elem, m21chord.Chord):
            chords.append(elem)

    if not chords:
        return {
            "key": key_str,
            "progression": [],
            "summary": f"Key: {key_str} — no chords found",
        }

    progression = []
    for chord_obj in chords:
        try:
            rn = roman.romanNumeralFromChord(chord_obj, detected_key)
            rn_str = rn.romanNumeral
            # Get chord name from pitches
            root_name = chord_obj.root().name
            quality = "major" if chord_obj.isMajorTriad() else (
                "minor" if chord_obj.isMinorTriad() else "other"
            )
            chord_name = f"{root_name} {quality}"

            progression.append({
                "roman_numeral": rn_str,
                "chord_name": chord_name,
                "offset": float(chord_obj.getOffsetInHierarchy(score)),
            })
        except Exception:
            progression.append({
                "roman_numeral": "?",
                "chord_name": str(chord_obj),
                "offset": float(chord_obj.getOffsetInHierarchy(score)),
            })

    rn_sequence = " - ".join(p["roman_numeral"] for p in progression)
    summary = f"Key: {key_str} | Progression: {rn_sequence}"

    return {
        "key": key_str,
        "progression": progression,
        "summary": summary,
    }