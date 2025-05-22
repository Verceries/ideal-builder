import sys
import os
from typing import List

# Adjust the Python path to include the parent directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from actions import generate_code

def test_create_code():
    """
    Tests if create_code returns a non-empty string.
    """
    inspiration_summary = "test summary"
    trend_tags = ["trend1", "trend2"]
    tech_stack = "react-tailwind"
    color_mode = "dark"
    layout_type = "full-page"

    result = generate_code.create_code(
        inspiration_summary,
        trend_tags,
        tech_stack,
        color_mode,
        layout_type
    )
    assert isinstance(result, str), "Output should be a string"
    assert len(result) > 0, "Output string should not be empty"
    assert tech_stack in result, f"Output string should contain tech_stack '{tech_stack}'"
    assert color_mode in result, f"Output string should contain color_mode '{color_mode}'"
    assert layout_type in result, f"Output string should contain layout_type '{layout_type}'"
    for tag in trend_tags:
        assert tag in result, f"Output string should contain trend_tag '{tag}'"
    print("test_create_code PASSED")

if __name__ == "__main__":
    test_create_code()
