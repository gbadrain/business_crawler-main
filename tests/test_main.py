import pytest
import os
from main import sanitize_filename, get_file_size_human_readable


def test_sanitize_filename():
    assert sanitize_filename("AI in healthcare") == "AI_in_healthcare"
    assert (
        sanitize_filename("Natural Language Processing")
        == "Natural_Language_Processing"
    )
    assert (
        sanitize_filename("file with!@#$%^&*()special chars")
        == "file_with_special_chars"
    )
    assert sanitize_filename("another_file-with_dashes") == "another_file_with_dashes"


def test_get_file_size_human_readable(tmp_path):
    # Create a dummy file for testing
    file_path = tmp_path / "test_file.txt"

    # Test with 0 bytes
    file_path.write_text("")
    assert get_file_size_human_readable(str(file_path)) == "0 B"

    # Test with bytes
    file_path.write_text("a" * 500)
    assert get_file_size_human_readable(str(file_path)) == "500 B"

    # Test with KB
    file_path.write_text("a" * 1500)
    assert get_file_size_human_readable(str(file_path)) == "1.46 KB"

    # Test with MB
    file_path.write_text("a" * (1024 * 1024 * 2))
    assert get_file_size_human_readable(str(file_path)) == "2.00 MB"

    # Test non-existent file
    assert get_file_size_human_readable("non_existent_file.txt") == "N/A"
