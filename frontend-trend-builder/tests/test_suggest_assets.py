import sys
import os
import json # For mock responses
from typing import List, Dict # Not strictly needed after changes, but good practice
from unittest.mock import patch # For mocking

# Adjust the Python path to include the parent directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from actions import suggest_assets # Module under test

# --- Mock Google Fonts API Responses ---
MOCK_GOOGLE_FONTS_API_SUCCESS_RESPONSE_SERIF = json.dumps({
    "items": [
        {"family": "Merriweather", "category": "serif"},
        {"family": "Playfair Display", "category": "serif"},
        {"family": "Lora", "category": "serif"}
    ]
})
MOCK_GOOGLE_FONTS_API_SUCCESS_RESPONSE_SANS_SERIF = json.dumps({
    "items": [
        {"family": "Roboto", "category": "sans-serif"},
        {"family": "Open Sans", "category": "sans-serif"},
        {"family": "Lato", "category": "sans-serif"}
    ]
})
MOCK_GOOGLE_FONTS_API_EMPTY_RESPONSE = json.dumps({"items": []})
MOCK_API_ERROR_RESPONSE_FONTS = "Error: API unavailable or rate limit exceeded for fonts." # More specific error


# --- Test Cases ---

@patch('actions.suggest_assets.view_text_website') 
@patch('frontend_trend_builder.actions.suggest_assets.GOOGLE_FONTS_API_KEY', 'DUMMY_FONT_KEY_FOR_TESTING')
def test_google_fonts_api_success_serif_with_key_from_config(mock_view_text_website):
    """Test Google Fonts API success for serif fonts with key from config."""
    mock_view_text_website.return_value = MOCK_GOOGLE_FONTS_API_SUCCESS_RESPONSE_SERIF
    
    summary = "Elegant blog design"
    trends = ["serif_fonts", "modern_ui"] 
    
    result = suggest_assets.get_asset_suggestions(summary, trends)
    
    assert isinstance(result, list)
    api_fonts_found = [item for item in result if item.get("source") == "GoogleFonts_API"]
    mock_assets_found = [item for item in result if item.get("source") != "GoogleFonts_API"]

    assert len(api_fonts_found) >= 1 
    assert any(font["name"] == "Merriweather" for font in api_fonts_found)
    assert len(mock_assets_found) > 0 
    assert any(asset["type"] == "icon" for asset in mock_assets_found)
    mock_view_text_website.assert_called_once() 
    print("test_google_fonts_api_success_serif_with_key_from_config PASSED")


@patch('actions.suggest_assets.view_text_website')
@patch('frontend_trend_builder.actions.suggest_assets.GOOGLE_FONTS_API_KEY', 'DUMMY_FONT_KEY_FOR_TESTING')
def test_google_fonts_api_sans_serif_with_key_from_config(mock_view_text_website):
    """Test Google Fonts API for sans-serif with key from config."""
    mock_view_text_website.return_value = MOCK_GOOGLE_FONTS_API_SUCCESS_RESPONSE_SANS_SERIF
    
    summary = "Modern dashboard app"
    trends = ["modern_ui", "data_visualization"] 
    
    result = suggest_assets.get_asset_suggestions(summary, trends)

    api_fonts = [r for r in result if r.get("source") == "GoogleFonts_API"]
    other_assets = [r for r in result if r.get("source") != "GoogleFonts_API"]

    assert len(api_fonts) > 0
    assert any(f["name"] == "Open Sans" for f in api_fonts)
    assert len(other_assets) > 0
    assert any(a["type"] == "icon" and "data_visualization" in a["tags"] for a in other_assets)
    print("test_google_fonts_api_sans_serif_with_key_from_config PASSED")


@patch('actions.suggest_assets.view_text_website')
@patch('frontend_trend_builder.actions.suggest_assets.GOOGLE_FONTS_API_KEY', 'DUMMY_FONT_KEY_FOR_TESTING')
def test_google_fonts_api_failure_fallback_with_key_from_config(mock_view_text_website):
    """Test API failure, fallback to mock fonts, with key from config."""
    mock_view_text_website.return_value = MOCK_API_ERROR_RESPONSE_FONTS
    
    summary = "A design needing a serif font"
    trends = ["serif_fonts", "minimalism"] 
    
    result = suggest_assets.get_asset_suggestions(summary, trends)
    
    api_fonts_found = [item for item in result if item.get("source") == "GoogleFonts_API"]
    mock_fonts_found = [item for item in result if item.get("type") == "font" and item.get("source") != "GoogleFonts_API"]
    
    assert len(api_fonts_found) == 0
    assert len(mock_fonts_found) > 0
    assert any(font["name"] == "Playfair Display" for font in mock_fonts_found) 
    assert any(item["type"] == "icon" for item in result)
    mock_view_text_website.assert_called_once() 
    print("test_google_fonts_api_failure_fallback_with_key_from_config PASSED")


@patch('actions.suggest_assets.view_text_website') # Still mock view_text_website in case of unexpected calls
@patch('frontend_trend_builder.actions.suggest_assets.GOOGLE_FONTS_API_KEY', None) # Simulate no key from config
def test_no_api_key_fonts_from_mock_no_key(mock_view_text_website):
    """Test no API key from config, fonts from mock."""
    summary = "Design needing a sans-serif font"
    trends = ["modern_ui"] 
    
    result = suggest_assets.get_asset_suggestions(summary, trends)
    
    api_fonts_found = [item for item in result if item.get("source") == "GoogleFonts_API"]
    mock_fonts_found = [item for item in result if item.get("type") == "font" and item.get("source") != "GoogleFonts_API"]
    
    assert len(api_fonts_found) == 0
    assert len(mock_fonts_found) > 0
    assert any(font["name"] == "Roboto" for font in mock_fonts_found) 
    mock_view_text_website.assert_not_called() # API should not be called
    print("test_no_api_key_fonts_from_mock_no_key PASSED")


@patch('actions.suggest_assets.view_text_website')
@patch('frontend_trend_builder.actions.suggest_assets.GOOGLE_FONTS_API_KEY', None)
def test_only_other_assets_no_font_trends_no_key(mock_view_text_website):
    """Test no font trends, no API key, only mock assets."""
    summary = "Dashboard with icons"
    trends = ["data_visualization", "dark_mode"] 
    
    result = suggest_assets.get_asset_suggestions(summary, trends)
    
    fonts_found = [item for item in result if item.get("type") == "font"]
    icons_found = [item for item in result if item.get("type") == "icon"]
    
    assert len(icons_found) > 0
    assert any(icon["name"] == "Phosphor Icons - ChartLineUp" for icon in icons_found)
    assert any(font["name"] == "JetBrains Mono" for font in fonts_found)
    mock_view_text_website.assert_not_called()
    print("test_only_other_assets_no_font_trends_no_key PASSED")

# Test mock data path explicitly when no API call is expected
@patch('frontend_trend_builder.actions.suggest_assets.GOOGLE_FONTS_API_KEY', None)
def test_get_asset_suggestions_mock_data_with_matches_no_key(mock_vtw_not_used): # mock_vtw_not_used as API won't be called
    inspiration_summary = "A modern dashboard for crypto analytics. Dark theme preferred."
    trend_tags = ["dark_mode", "data_visualization", "modern_ui", "glassmorphism"]
    result = suggest_assets.get_asset_suggestions(inspiration_summary, trend_tags)
    
    assert isinstance(result, list) and len(result) > 0
    assert all(item.get("source") != "GoogleFonts_API" for item in result)
    expected_names = ["Phosphor Icons - ChartLineUp", "JetBrains Mono", "Abstract Geometric Background"]
    found_names = [item["name"] for item in result]
    assert all(name in found_names for name in expected_names)
    print("test_get_asset_suggestions_mock_data_with_matches_no_key PASSED")

# Original test_get_asset_suggestions_data_file_issues can remain,
# but ensure it also mocks the API key to None to isolate testing of mock file issues.
@patch('frontend_trend_builder.actions.suggest_assets.GOOGLE_FONTS_API_KEY', None)
@patch('actions.suggest_assets.view_text_website') # Mock this even if not called, for consistency
def test_get_asset_suggestions_data_file_issues(mock_vtw, mock_api_key_val):
    """ Tests error handling if the mock asset data file is missing or corrupt. """
    original_mock_path = suggest_assets.ASSET_DATA_PATH
    
    # Test FileNotFoundError
    suggest_assets.ASSET_DATA_PATH = "non_existent_asset_data.json"
    result_not_found = suggest_assets.get_asset_suggestions("test", ["test"])
    assert isinstance(result_not_found, list) and len(result_not_found) == 0
    print("test_get_asset_suggestions_data_file_not_found PASSED")

    # Test JSONDecodeError
    temp_malformed_file = os.path.join(os.path.dirname(original_mock_path), "temp_malformed_asset.json")
    with open(temp_malformed_file, 'w') as f:
        f.write("[{'invalid_json': ]") 
    
    suggest_assets.ASSET_DATA_PATH = temp_malformed_file
    result_decode_error = suggest_assets.get_asset_suggestions("test", ["test"])
    assert isinstance(result_decode_error, list) and len(result_decode_error) == 0
    print("test_get_asset_suggestions_data_file_decode_error PASSED")
    
    os.remove(temp_malformed_file) 
    suggest_assets.ASSET_DATA_PATH = original_mock_path 
    print("test_get_asset_suggestions_data_file_issues (overall) PASSED")


if __name__ == "__main__":
    print("--- Running test_suggest_assets.py (with config mocks) ---")
    test_google_fonts_api_success_serif_with_key_from_config()
    test_google_fonts_api_sans_serif_with_key_from_config()
    test_google_fonts_api_failure_fallback_with_key_from_config()
    test_no_api_key_fonts_from_mock_no_key()
    test_only_other_assets_no_font_trends_no_key()
    test_get_asset_suggestions_mock_data_with_matches_no_key() 
    test_get_asset_suggestions_data_file_issues()
    print("--- All suggest_assets tests (with config mocks) completed ---")
