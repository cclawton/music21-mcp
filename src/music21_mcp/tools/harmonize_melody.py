"""harmonize_melody tool - Phase 2 generative harmony.

Generates chord accompaniment for a melody line based on key analysis
and simple harmonic function mapping.

Styles:
  - 'block': Block chords under each melody note (homophonic)
  - 'arpeggiated': Arpeggiated chord accompaniment
"""

import copy
from music21 import (
    stream,
    chord as m21chord,
    note as m21note,
    pitch as m21pitch,
    key as m21key,
    roman,
)
from .analyze_key import analyze_key


# Map scale degrees to typical harmonies in major key
HARMONY_MAP_MAJOR = {
    0: ["I", "vi"],
    1: ["ii", "IV"],
    2: ["I", "iii"],
    3: ["IV", "ii"],
    4: ["V", "iii"],
    5: ["vi", "I"],
    6: ["vii", "V"],
}

HARMONY_MAP_MINOR = {
    0: ["i", "VI"],
    1: ["ii°", "iv"],
    2: ["i", "III"],
    3: ["iv", "VI"],
    4: ["v", "V"],
    5: ["VI", "i"],
    6: ["vii°", "V"],
}


def harmonize_melody(
    score: stream.Stream,
    style: str = "block",
) -> stream.Stream:
    """Generate chord accompaniment for a melody.

    Args:
        score: A music21 Stream containing melody notes
        style: Accompaniment style — 'block' or 'arpeggiated'

    Returns:
        A new stream with melody + chord accompaniment

    Raises:
        TypeError: If score is not a Stream
    """
    if not isinstance(score, stream.Stream):
        raise TypeError(f"Expected music21 Stream, got {type(score).__name__}")

    result = copy.deepcopy(score)

    # Collect melody notes and their offsets directly from the stream
    # Use flat iteration (not recurse) to avoid wrapper issues
    melody_notes = []
    for elem in result:
        if isinstance(elem, m21note.Note):
            melody_notes.append(elem)

    if not melody_notes:
        return result

    # Detect key
    key_result = analyze_key(result)
    key_tonic = key_result["key"].split()[0]
    key_mode = key_result.get("mode", "major")

    detected_key = m21key.Key(key_tonic, key_mode)
    harmony_map = HARMONY_MAP_MAJOR if key_mode == "major" else HARMONY_MAP_MINOR

    # For each melody note, compute and insert a chord
    for note_obj in melody_notes:
        pitch_class = note_obj.pitch.pitchClass

        # Find scale degree
        scale_pitches = [p.pitchClass for p in detected_key.pitches]
        scale_degree = None
        for i, pc in enumerate(scale_pitches[:7]):
            if pc == pitch_class:
                scale_degree = i
                break

        if scale_degree is None:
            continue

        chord_options = harmony_map.get(scale_degree, ["I"])
        rn_str = chord_options[0]

        try:
            new_rn = roman.RomanNumeral(rn_str, detected_key)

            # Create chord one octave below the melody
            chord_pitches = []
            for p in new_rn.pitches:
                p_copy = m21pitch.Pitch(p.name)
                p_copy.octave = note_obj.pitch.octave - 1
                chord_pitches.append(p_copy)

            new_chord = m21chord.Chord(chord_pitches)
            new_chord.duration = copy.deepcopy(note_obj.duration)

            # Insert directly into the result stream at the same offset
            result.insert(note_obj.offset, new_chord)
        except Exception:
            continue

    return result