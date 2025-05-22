import sys
import os
from typing import List, Dict

# Adjust the Python path to include the parent directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from actions import suggest_assets

def test_get_asset_suggestions_with_matches():
    """
    Tests if get_asset_suggestions returns a list of asset dicts when matches are found.
    """
    inspiration_summary = "A modern dashboard for crypto analytics. Dark theme preferred."
    trend_tags = ["dark_mode", "data_visualization", "modern_ui", "glassmorphism"]
    # Expected assets:
    # - Phosphor Icons - ChartLineUp (data_visualization, modern_ui)
    # - Heroicons - Sparkles (modern_ui, glassmorphism)
    # - JetBrains Mono (modern_ui, dashboard, dark_mode)
    # - Abstract Geometric Background (glassmorphism, dark_mode, modern_ui)
    # - Material Icons - Dark Mode (dark_mode)
    result = suggest_assets.get_asset_suggestions(inspiration_summary, trend_tags)
    
    assert isinstance(result, list), "Output should be a list for matches."
    assert len(result) > 0, "Should return assets for the given input."
    
    found_asset_names = []
    for asset in result:
        assert isinstance(asset, dict), "Each item in the list should be a dictionary."
        assert "name" in asset and "type" in asset and "tags" in asset
        found_asset_names.append(asset["name"])

    expected_names = [
        "Phosphor Icons - ChartLineUp", "Heroicons - Sparkles", 
        "JetBrains Mono", "Abstract Geometric Background", "Material Icons - Dark Mode"
    ]
    for name in expected_names:
        assert name in found_asset_names, f"Expected asset '{name}' not found in {found_asset_names}."
    print("test_get_asset_suggestions_with_matches PASSED")

def test_get_asset_suggestions_no_matches():
    """
    Tests if get_asset_suggestions returns an empty list when no relevant assets are found.
    """
    inspiration_summary = "A website about ancient history and philosophy."
    trend_tags = ["parchment_scroll_effect", "stoicism_icons"] # Unlikely to be in mock data
    result = suggest_assets.get_asset_suggestions(inspiration_summary, trend_tags)
    
    assert isinstance(result, list), "Output should be a list."
    assert len(result) == 0, f"Should return an empty list for no matching assets, but got {len(result)} items."
    print("test_get_asset_suggestions_no_matches PASSED")

def test_get_asset_suggestions_minimal_input():
    """
    Tests with minimal input, relying on a single trend tag that should have matches.
    """
    inspiration_summary = "A basic page."
    trend_tags = ["minimalism"] # Should match "Feather Icons - User", "Roboto", "Minimalist Desk Setup", "Bootstrap Icons - Credit Card"
    result = suggest_assets.get_asset_suggestions(inspiration_summary, trend_tags)
    
    assert isinstance(result, list)
    assert len(result) >= 2, "Expected at least a couple of 'minimalism' tagged assets."
    
    found_minimal_icon = any(a["name"] == "Feather Icons - User" for a in result)
    found_minimal_font = any(a["name"] == "Roboto" for a in result) # Roboto also has 'minimalism'
    found_minimal_image = any(a["name"] == "Minimalist Desk Setup" for a in result)
    assert found_minimal_icon, "Did not find 'Feather Icons - User' for minimalism."
    assert found_minimal_font, "Did not find 'Roboto' for minimalism."
    assert found_minimal_image, "Did not find 'Minimalist Desk Setup' for minimalism."
    print("test_get_asset_suggestions_minimal_input PASSED")

def test_get_asset_suggestions_data_file_issues():
    """
    Tests error handling if the asset data file is missing or corrupt.
    """
    original_path = suggest_assets.ASSET_DATA_PATH
    
    # Test FileNotFoundError
    suggest_assets.ASSET_DATA_PATH = "non_existent_asset_data.json"
    result_not_found = suggest_assets.get_asset_suggestions("test", ["test"])
    assert isinstance(result_not_found, list)
    assert len(result_not_found) == 0 # Function should return empty list on error
    print("test_get_asset_suggestions_data_file_not_found (check console for error print) PASSED")

    # Test JSONDecodeError
    temp_malformed_file = os.path.join(os.path.dirname(original_path), "temp_malformed_asset.json")
    with open(temp_malformed_file, 'w') as f:
        f.write("[{'invalid_json': ]") # Malformed JSON
    
    suggest_assets.ASSET_DATA_PATH = temp_malformed_file
    result_decode_error = suggest_assets.get_asset_suggestions("test", ["test"])
    assert isinstance(result_decode_error, list)
    assert len(result_decode_error) == 0 # Function should return empty list on error
    print("test_get_asset_suggestions_data_file_decode_error (check console for error print) PASSED")
    
    os.remove(temp_malformed_file) # Clean up
    suggest_assets.ASSET_DATA_PATH = original_path # Restore original path
    print("test_get_asset_suggestions_data_file_issues (overall) PASSED")

if __name__ == "__main__":
    print("--- Running test_suggest_assets.py ---")
    test_get_asset_suggestions_with_matches()
    test_get_asset_suggestions_no_matches()
    test_get_asset_suggestions_minimal_input()
    test_get_asset_suggestions_data_file_issues()
    print("--- All suggest_assets tests completed ---")
