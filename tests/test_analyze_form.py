"""Tests for analyze_form tool following TDD."""

import pytest
from music21_mcp.tools.analyze_form import analyze_form


def _make_aba_stream():
    """Helper: A-B-A form stream (3 sections with different material).

    Section A: C major arpeggios (4 bars)
    Section B: A minor arpeggios (4 bars)
    Section A: C major arpeggios (4 bars, same as first A)
    """
    from music21 import stream, note
    s = stream.Stream()

    # Section A (C major)
    for _ in range(4):
        for n in ["C4", "E4", "G4", "C5"]:
            s.append(note.Note(n))

    # Section B (A minor)
    for _ in range(4):
        for n in ["A4", "C5", "E5", "A5"]:
            s.append(note.Note(n))

    # Section A' (C major again)
    for _ in range(4):
        for n in ["C4", "E4", "G4", "C5"]:
            s.append(note.Note(n))

    return s


def _make_verse_chorus_stream():
    """Helper: verse-chorus-verse form."""
    from music21 import stream, note
    s = stream.Stream()

    # Verse 1 (low register, stepwise)
    for n in ["C4", "D4", "E4", "F4", "G4", "F4", "E4", "D4"]:
        s.append(note.Note(n))

    # Chorus (high register, leaps)
    for n in ["C5", "G5", "E5", "C5", "G5", "E5", "C5", "G5"]:
        s.append(note.Note(n))

    # Verse 2 (same as verse 1)
    for n in ["C4", "D4", "E4", "F4", "G4", "F4", "E4", "D4"]:
        s.append(note.Note(n))

    return s


def test_analyze_form_returns_dict():
    """Should return a dict with form info."""
    s = _make_aba_stream()
    result = analyze_form(s)
    assert isinstance(result, dict)


def test_analyze_form_returns_sections():
    """Should return a list of sections."""
    s = _make_aba_stream()
    result = analyze_form(s)
    assert "sections" in result
    assert isinstance(result["sections"], list)


def test_analyze_form_finds_multiple_sections():
    """Should find at least 2 sections in ABA form."""
    s = _make_aba_stream()
    result = analyze_form(s)
    assert len(result["sections"]) >= 2


def test_analyze_form_section_has_label_and_offset():
    """Each section should have a label and start offset."""
    s = _make_aba_stream()
    result = analyze_form(s)
    for section in result["sections"]:
        assert "label" in section
        assert "start_offset" in section
        assert "end_offset" in section


def test_analyze_form_returns_summary():
    """Should include a human-readable summary."""
    s = _make_aba_stream()
    result = analyze_form(s)
    assert "summary" in result
    assert isinstance(result["summary"], str)


def test_analyze_form_invalid_input():
    """Should raise TypeError for non-stream input."""
    with pytest.raises(TypeError):
        analyze_form("not a stream")


def test_analyze_form_empty_stream():
    """Empty stream should return single empty section."""
    from music21 import stream
    s = stream.Stream()
    result = analyze_form(s)
    assert result["sections"] == []


def test_analyze_form_verse_chorus():
    """Should find distinct sections in verse-chorus-verse form."""
    s = _make_verse_chorus_stream()
    result = analyze_form(s)
    assert len(result["sections"]) >= 2