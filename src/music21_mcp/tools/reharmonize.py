"""reharmonize tool - Phase 2 generative harmony.

Replaces chords in a progression with harmonic alternatives while
preserving the melodic/structural framework.

Styles:
  - 'diatonic': replace chords with diatonic alternatives (vi for I, ii for IV, etc.)
  - 'substitute': apply jazz chord substitutions (tritone subs, secondary dominants)
"""

import copy
from music21 import stream, chord as m21chord, pitch as m21pitch, roman
from .analyze_key import analyze_key


# Diatonic substitution map: Roman numeral → alternative Roman numerals
DIATONIC_SUBS = {
    "I": ["vi", "iii"],
    "IV": ["ii", "IV"],
    "V": ["vii", "V"],
    "vi": ["I", "iii"],
    "ii": ["IV", "ii"],
    "iii": ["I", "vi"],
    "vii": ["V", "vii"],
}

# Jazz substitution map: adds extended/alt chords
JAZZ_SUBS = {
    "I": ["Imaj7", "vi7"],
    "IV": ["IVmaj7", "ii7"],
    "V": ["V7", "bII7"],   # bII7 = tritone sub for V7
    "vi": ["vi7", "I7"],
    "ii": ["ii7", "IV7"],
}


def reharmonize(
    score: stream.Stream,
    style: str = "diatonic",
) -> stream.Stream:
    """Reharmonize a chord progression.

    Args:
        score: A music21 Stream containing chords
        style: Reharmonization style — 'diatonic' or 'substitute'

    Returns:
        A new stream with reharmonized chords

    Raises:
        TypeError: If score is not a Stream
        ValueError: If style is not recognized
    """
    if not isinstance(score, stream.Stream):
        raise TypeError(f"Expected music21 Stream, got {type(score).__name__}")

    valid_styles = {"diatonic", "substitute"}
    if style not in valid_styles:
        raise ValueError(
            f"Invalid style '{style}'. Must be one of: {valid_styles}"
        )

    result = copy.deepcopy(score)

    # Detect the key
    key_result = analyze_key(result)
    key_name = key_result["key"]
    key_tonic = key_name.split()[0]
    key_mode = key_result.get("mode", "major")

    from music21 import key as m21key
    detected_key = m21key.Key(key_tonic, key_mode)

    # Find all chords in the stream
    all_chords = []
    for elem in result.recurse():
        if isinstance(elem, m21chord.Chord):
            all_chords.append(elem)

    # Apply substitutions to each chord
    for chord_obj in all_chords:
        # Figure out the Roman numeral of this chord
        try:
            rn = roman.romanNumeralFromChord(chord_obj, detected_key)
            rn_str = rn.romanNumeral
        except Exception:
            continue  # Skip chords that can't be analyzed

        # Get substitution options
        if style == "diatonic":
            sub_options = DIATONIC_SUBS.get(rn_str, [])
        else:  # substitute
            sub_options = JAZZ_SUBS.get(rn_str, [])

        if not sub_options:
            continue

        # Pick the first alternative (deterministic for testing)
        replacement_rn = sub_options[0]

        # Convert Roman numeral to actual chord
        try:
            new_rn = roman.RomanNumeral(replacement_rn, detected_key)
            new_pitches = [p for p in new_rn.pitches]

            # Preserve octave range from original chord
            if chord_obj.pitches:
                orig_octave = chord_obj.pitches[0].octave
                new_pitches = []
                for p in new_rn.pitches:
                    p_copy = m21pitch.Pitch(p.name)
                    p_copy.octave = orig_octave
                    new_pitches.append(p_copy)

            chord_obj.pitches = new_pitches
        except Exception:
            continue  # Skip if substitution fails

    return result