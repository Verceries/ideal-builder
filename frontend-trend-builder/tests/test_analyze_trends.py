import sys
import os
from typing import List

# Adjust the Python path to include the parent directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from actions import analyze_trends

def test_identify_trends():
    """
    Tests if identify_trends returns a non-empty list of strings.
    """
    prompt = "test prompt"
    inspiration_summary = "test summary"
    result = analyze_trends.identify_trends(prompt, inspiration_summary)
    assert isinstance(result, list), "Output should be a list"
    assert len(result) > 0, "Output list should not be empty"
    for item in result:
        assert isinstance(item, str), "All items in the list should be strings"
    # Check for placeholder values (optional, but good for these mock functions)
    assert "glassmorphism" in result
    print("test_identify_trends PASSED")

if __name__ == "__main__":
    test_identify_trends()
