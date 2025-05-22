import sys
import os
from typing import List

# Adjust the Python path to include the parent directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from actions import suggest_assets

def test_get_asset_suggestions():
    """
    Tests if get_asset_suggestions returns a non-empty list of strings.
    """
    inspiration_summary = "test summary"
    trend_tags = ["trend1", "trend2"]

    result = suggest_assets.get_asset_suggestions(inspiration_summary, trend_tags)
    assert isinstance(result, list), "Output should be a list"
    assert len(result) > 0, "Output list should not be empty"
    for item in result:
        assert isinstance(item, str), "All items in the list should be strings"
    # Check for placeholder values (optional, but good for these mock functions)
    assert "icon_placeholder.svg" in result
    print("test_get_asset_suggestions PASSED")

if __name__ == "__main__":
    test_get_asset_suggestions()
