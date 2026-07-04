"""Tests for search_pattern tool following TDD."""

import pytest
from music21_mcp.tools.search_pattern import search_pattern


def _make_melody_stream():
    """Helper: melody with a known pattern repeated."""
    from music21 import stream, note
    s = stream.Stream()
    # Pattern: C-D-E (ascending stepwise)
    # Then some other notes, then C-D-E again
    notes = [
        ("C4", 0), ("D4", 1), ("E4", 2),  # pattern occurrence 1
        ("F4", 3), ("G4", 4), ("A4", 5),   # filler
        ("C5", 6), ("D5", 7), ("E5", 8),  # pattern occurrence 2 (transposed)
        ("G4", 9), ("F4", 10), ("E4", 11), # descending
    ]
    for pitch, offset in notes:
        n = note.Note(pitch)
        n.quarterLength = 1.0
        s.insert(offset, n)
    return s


def test_search_pattern_returns_dict():
    """Should return a dict with match info."""
    s = _make_melody_stream()
    result = search_pattern(s, pattern=["C4", "D4", "E4"])
    assert isinstance(result, dict)


def test_search_pattern_finds_exact_match():
    """Should find exact pitch pattern in the stream."""
    s = _make_melody_stream()
    result = search_pattern(s, pattern=["C4", "D4", "E4"])
    assert "matches" in result
    assert isinstance(result["matches"], list)
    assert len(result["matches"]) >= 1
    # First match should be at offset 0
    assert result["matches"][0]["offset"] == 0.0


def test_search_pattern_finds_intervals():
    """Should find interval pattern (ascending whole steps) regardless of key."""
    s = _make_melody_stream()
    # Search for the interval pattern [2, 2] (two whole steps up)
    result = search_pattern(s, pattern=[2, 2], pattern_type="intervals")
    assert "matches" in result
    # C-D-E is [+2, +2] semitones, C5-D5-E5 is also [+2, +2]
    assert len(result["matches"]) >= 2


def test_search_pattern_no_match():
    """Should return empty matches when pattern not found."""
    s = _make_melody_stream()
    result = search_pattern(s, pattern=["C2", "C#2", "D2"])
    assert result["matches"] == []


def test_search_pattern_returns_summary():
    """Should include a human-readable summary."""
    s = _make_melody_stream()
    result = search_pattern(s, pattern=["C4", "D4", "E4"])
    assert "summary" in result


def test_search_pattern_match_has_offset_and_notes():
    """Each match should include offset and matched notes."""
    s = _make_melody_stream()
    result = search_pattern(s, pattern=["C4", "D4", "E4"])
    if result["matches"]:
        match = result["matches"][0]
        assert "offset" in match
        assert "notes" in match


def test_search_pattern_invalid_input():
    """Should raise TypeError for non-stream input."""
    with pytest.raises(TypeError):
        search_pattern("not a stream", pattern=["C4"])


def test_search_pattern_empty_pattern():
    """Should raise ValueError for empty pattern."""
    from music21 import stream
    s = stream.Stream()
    with pytest.raises(ValueError):
        search_pattern(s, pattern=[])


def test_search_pattern_empty_stream():
    """Empty stream should return no matches."""
    from music21 import stream
    s = stream.Stream()
    result = search_pattern(s, pattern=["C4", "D4"])
    assert result["matches"] == []