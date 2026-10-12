"""Verify word-error arithmetic independently from any transcription service."""

import pytest

from scripts.voice_score import word_error_rate


@pytest.mark.parametrize(("reference", "actual", "errors"), [
    ("Four boards.", "four boards", 0), ("four boards", "for boards", 1),
    ("four boards", "boards", 1), ("four boards", "four large boards", 1),
    ("four boards", "", 2), ("four", "4", 1), ("one", "one two three", 2),
])
def test_edit_distance(reference, actual, errors):
    """Verify edit distance."""
    result = word_error_rate(reference, actual)
    assert result["word_errors"] == errors
    assert result["word_error_rate"] == errors / result["reference_words"]


def test_empty_reference_has_no_defined_rate():
    """Verify empty reference has no defined rate."""
    with pytest.raises(ValueError, match="Reference"):
        word_error_rate("...", "anything")
