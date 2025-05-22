import sys
import os
import json # For mock responses
from typing import List, Dict
from unittest.mock import patch # For mocking

# Adjust the Python path to include the parent directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from actions import suggest_assets

# --- Mock Google Fonts API Responses ---
MOCK_GOOGLE_FONTS_API_SUCCESS_RESPONSE_SERIF = json.dumps({
    "items": [
        {"family": "Merriweather", "category": "serif"},
        {"family": "Playfair Display", "category": "serif"}, # Also in mock_asset_data
        {"family": "Lora", "category": "serif"}
    ]
})

MOCK_GOOGLE_FONTS_API_SUCCESS_RESPONSE_SANS_SERIF = json.dumps({
    "items": [
        {"family": "Roboto", "category": "sans-serif"}, # Also in mock_asset_data
        {"family": "Open Sans", "category": "sans-serif"},
        {"family": "Lato", "category": "sans-serif"}
    ]
})

MOCK_GOOGLE_FONTS_API_EMPTY_RESPONSE = json.dumps({"items": []})
MOCK_API_ERROR_RESPONSE = "Error: API unavailable or rate limit exceeded for fonts."


# --- Test Cases ---

@patch('actions.suggest_assets.view_text_website') # Target view_text_website where it's used
def test_google_fonts_api_success_serif(mock_view_text_website):
    """Test Google Fonts API success for serif fonts, plus mock icons/images."""
    mock_view_text_website.return_value = MOCK_GOOGLE_FONTS_API_SUCCESS_RESPONSE_SERIF
    
    original_key = suggest_assets.GOOGLE_FONTS_API_KEY
    suggest_assets.GOOGLE_FONTS_API_KEY = "DUMMY_FONT_KEY"
    
    summary = "Elegant blog design"
    trends = ["serif_fonts", "modern_ui"] # modern_ui for icons/images
    
    result = suggest_assets.get_asset_suggestions(summary, trends)
    
    suggest_assets.GOOGLE_FONTS_API_KEY = original_key # Restore
    
    assert isinstance(result, list)
    api_fonts_found = [item for item in result if item.get("source") == "GoogleFonts_API"]
    mock_assets_found = [item for item in result if item.get("source") != "GoogleFonts_API"]

    assert len(api_fonts_found) >= 1 # Should get at least one serif font from API
    assert any(font["name"] == "Merriweather" for font in api_fonts_found)
    # Playfair Display might be from API or mock, depending on deduplication logic (name match)
    
    assert len(mock_assets_found) > 0 # Should still get icons/images from mock
    assert any(asset["type"] == "icon" for asset in mock_assets_found)
    
    mock_view_text_website.assert_called_once() # Called for serif
    print("test_google_fonts_api_success_serif PASSED")


@patch('actions.suggest_assets.view_text_website')
def test_google_fonts_api_success_sans_serif_and_mock_icons(mock_view_text_website):
    """Test Google Fonts API for sans-serif and ensure mock icons are also present."""
    mock_view_text_website.return_value = MOCK_GOOGLE_FONTS_API_SUCCESS_RESPONSE_SANS_SERIF
    
    original_key = suggest_assets.GOOGLE_FONTS_API_KEY
    suggest_assets.GOOGLE_FONTS_API_KEY = "DUMMY_FONT_KEY"

    summary = "Modern dashboard app"
    trends = ["modern_ui", "data_visualization"] # modern_ui implies sans-serif for fonts
    
    result = suggest_assets.get_asset_suggestions(summary, trends)
    suggest_assets.GOOGLE_FONTS_API_KEY = original_key

    api_fonts = [r for r in result if r.get("source") == "GoogleFonts_API"]
    other_assets = [r for r in result if r.get("source") != "GoogleFonts_API"]

    assert len(api_fonts) > 0, "Should fetch sans-serif fonts from API"
    assert any(f["name"] == "Open Sans" for f in api_fonts)
    assert len(other_assets) > 0, "Should also fetch icons/images from mock data"
    assert any(a["type"] == "icon" and "data_visualization" in a["tags"] for a in other_assets)
    print("test_google_fonts_api_success_sans_serif_and_mock_icons PASSED")


@patch('actions.suggest_assets.view_text_website')
def test_google_fonts_api_failure_fallback_to_mock_fonts(mock_view_text_website):
    """Test API failure, then fallback to mock data for fonts."""
    mock_view_text_website.return_value = MOCK_API_ERROR_RESPONSE # Simulate API error
    
    original_key = suggest_assets.GOOGLE_FONTS_API_KEY
    suggest_assets.GOOGLE_FONTS_API_KEY = "DUMMY_FONT_KEY"
    
    summary = "A design needing a serif font"
    trends = ["serif_fonts", "minimalism"] # minimalism for other assets
    
    result = suggest_assets.get_asset_suggestions(summary, trends)
    
    suggest_assets.GOOGLE_FONTS_API_KEY = original_key
    
    assert isinstance(result, list)
    api_fonts_found = [item for item in result if item.get("source") == "GoogleFonts_API"]
    mock_fonts_found = [item for item in result if item.get("type") == "font" and item.get("source") != "GoogleFonts_API"]
    
    assert len(api_fonts_found) == 0, "No fonts should come from API on failure"
    assert len(mock_fonts_found) > 0, "Should get serif fonts from mock data"
    assert any(font["name"] == "Playfair Display" for font in mock_fonts_found) # Mock serif
    
    # Check if icons/images are still fetched
    assert any(item["type"] == "icon" for item in result)
    mock_view_text_website.assert_called_once() # API was attempted
    print("test_google_fonts_api_failure_fallback_to_mock_fonts PASSED")


def test_no_api_key_fonts_from_mock():
    """Test no API key, fonts should come from mock data."""
    original_key = suggest_assets.GOOGLE_FONTS_API_KEY
    suggest_assets.GOOGLE_FONTS_API_KEY = None # Simulate no key
    
    summary = "Design needing a sans-serif font"
    trends = ["modern_ui"] # modern_ui implies sans-serif
    
    result = suggest_assets.get_asset_suggestions(summary, trends)
    
    suggest_assets.GOOGLE_FONTS_API_KEY = original_key
    
    api_fonts_found = [item for item in result if item.get("source") == "GoogleFonts_API"]
    mock_fonts_found = [item for item in result if item.get("type") == "font" and item.get("source") != "GoogleFonts_API"]
    
    assert len(api_fonts_found) == 0
    assert len(mock_fonts_found) > 0
    assert any(font["name"] == "Roboto" for font in mock_fonts_found) # Mock sans-serif
    print("test_no_api_key_fonts_from_mock PASSED")


def test_only_other_assets_no_font_trends():
    """Test when no specific font trends are given."""
    original_key = suggest_assets.GOOGLE_FONTS_API_KEY
    suggest_assets.GOOGLE_FONTS_API_KEY = None # Ensure no API call for fonts
    
    summary = "Dashboard with icons"
    trends = ["data_visualization", "dark_mode"] # No specific font type trends
    
    result = suggest_assets.get_asset_suggestions(summary, trends)
    
    suggest_assets.GOOGLE_FONTS_API_KEY = original_key
    
    fonts_found = [item for item in result if item.get("type") == "font"]
    icons_found = [item for item in result if item.get("type") == "icon"]
    
    # Depending on logic, default fonts from mock might be picked or not.
    # For now, let's assert that icons are found and not focus too much on default fonts without trends.
    # The current logic in get_asset_suggestions might pick up mock fonts if their general tags match.
    assert len(icons_found) > 0
    assert any(icon["name"] == "Phosphor Icons - ChartLineUp" for icon in icons_found)
    
    # If "modern_ui" or "minimalism" were in trends, they'd imply sans-serif.
    # Without them, only direct "font" keyword in summary or specific font trends trigger font search.
    # The prompt "Dashboard with icons" doesn't strongly imply font needs beyond defaults.
    # Check if "JetBrains Mono" is picked up due to "dashboard" and "dark_mode" tags.
    assert any(font["name"] == "JetBrains Mono" for font in fonts_found), "JetBrains Mono expected for dashboard/dark_mode"
    print("test_only_other_assets_no_font_trends PASSED")


# Original tests (can be adapted or kept if testing mock data paths specifically)
def test_get_asset_suggestions_mock_data_with_matches():
    """ Tests if get_asset_suggestions (mock path) returns a list of asset dicts when matches are found."""
    original_key = suggest_assets.GOOGLE_FONTS_API_KEY
    suggest_assets.GOOGLE_FONTS_API_KEY = None # Ensure API is skipped
    
    with patch('actions.suggest_assets.view_text_website', return_value=MOCK_API_ERROR_RESPONSE): # ensure API fails if accidentally called
        inspiration_summary = "A modern dashboard for crypto analytics. Dark theme preferred."
        trend_tags = ["dark_mode", "data_visualization", "modern_ui", "glassmorphism"]
        result = suggest_assets.get_asset_suggestions(inspiration_summary, trend_tags)
    
    suggest_assets.GOOGLE_FONTS_API_KEY = original_key
    
    assert isinstance(result, list)
    assert len(result) > 0
    # Check that all results are from mock (no "GoogleFonts_API" source)
    assert all(item.get("source") != "GoogleFonts_API" for item in result)
    # Check for specific mock items
    expected_names = ["Phosphor Icons - ChartLineUp", "JetBrains Mono", "Abstract Geometric Background"]
    found_names = [item["name"] for item in result]
    assert all(name in found_names for name in expected_names)
    print("test_get_asset_suggestions_mock_data_with_matches PASSED")


if __name__ == "__main__":
    print("--- Running test_suggest_assets.py (with mocks) ---")
    test_google_fonts_api_success_serif()
    test_google_fonts_api_success_sans_serif_and_mock_icons()
    test_google_fonts_api_failure_fallback_to_mock_fonts()
    test_no_api_key_fonts_from_mock()
    test_only_other_assets_no_font_trends()
    test_get_asset_suggestions_mock_data_with_matches() # Explicitly test mock data path
    # test_get_asset_suggestions_data_file_issues() # This can be run separately if needed
    print("--- All suggest_assets tests completed ---")
