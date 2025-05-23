import sys
import os
import json 
from typing import List, Dict # Keep for type hints
from unittest import TestCase, mock # Changed to use TestCase for better structure

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from actions import suggest_assets # Module under test

# --- Mock Provider/API Responses ---
# These simulate what the fetch_google_fonts provider would return.
MOCK_PROVIDER_FONTS_SERIF = [
    {"type": "font", "name": "Merriweather", "category": "serif", "source": "GoogleFonts_API"},
    {"type": "font", "name": "Lora", "category": "serif", "source": "GoogleFonts_API"}
]
MOCK_PROVIDER_FONTS_SANS_SERIF = [
    {"type": "font", "name": "Roboto", "category": "sans-serif", "source": "GoogleFonts_API"},
    {"type": "font", "name": "Open Sans", "category": "sans-serif", "source": "GoogleFonts_API"}
]
MOCK_PROVIDER_FONTS_EMPTY = []

# Configure logging for tests if needed
import logging
if not logging.getLogger().hasHandlers() or logging.getLogger().level > logging.DEBUG:
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
logger = logging.getLogger(__name__)


class TestGetAssetSuggestionsWithProviderMocks(TestCase):

    @mock.patch('frontend_trend_builder.actions.suggest_assets.fetch_google_fonts')
    def test_provider_fonts_success_serif_plus_mock_assets(self, mock_fetch_fonts):
        logger.info("Running test_provider_fonts_success_serif_plus_mock_assets")
        mock_fetch_fonts.return_value = MOCK_PROVIDER_FONTS_SERIF
        
        summary = "Elegant blog design"
        trends = ["serif_fonts", "modern_ui"] # modern_ui for icons/images
        
        result = suggest_assets.get_asset_suggestions(summary, trends)
        
        self.assertIsInstance(result, list)
        api_fonts_found = [item for item in result if item.get("source") == "GoogleFonts_API"]
        mock_assets_found = [item for item in result if item.get("source") != "GoogleFonts_API"]

        self.assertEqual(len(api_fonts_found), 2) # Expecting 2 serif fonts from mock provider
        self.assertTrue(any(font["name"] == "Merriweather" for font in api_fonts_found))
        
        self.assertTrue(len(mock_assets_found) > 0) # Should still get icons/images from mock
        self.assertTrue(any(asset["type"] == "icon" for asset in mock_assets_found))
        
        # Check if fetch_google_fonts was called for "serif"
        # The provider is called for each category determined. "serif_fonts" trend maps to "serif" category.
        mock_fetch_fonts.assert_any_call(category="serif", sort_by="popularity")
        logger.info("test_provider_fonts_success_serif_plus_mock_assets PASSED")

    @mock.patch('frontend_trend_builder.actions.suggest_assets.fetch_google_fonts')
    def test_provider_fonts_success_sans_serif_and_mock_icons(self, mock_fetch_fonts):
        logger.info("Running test_provider_fonts_success_sans_serif_and_mock_icons")
        mock_fetch_fonts.return_value = MOCK_PROVIDER_FONTS_SANS_SERIF
        
        summary = "Modern dashboard app"
        # "modern_ui" implies "sans-serif" category for fonts in get_asset_suggestions logic
        trends = ["modern_ui", "data_visualization"] 
        
        result = suggest_assets.get_asset_suggestions(summary, trends)

        api_fonts = [r for r in result if r.get("source") == "GoogleFonts_API"]
        other_assets = [r for r in result if r.get("source") != "GoogleFonts_API"]

        self.assertTrue(len(api_fonts) > 0, "Should fetch sans-serif fonts from API provider")
        self.assertTrue(any(f["name"] == "Open Sans" for f in api_fonts))
        self.assertTrue(len(other_assets) > 0, "Should also fetch icons/images from mock data")
        self.assertTrue(any(a["type"] == "icon" and "data_visualization" in a.get("tags", []) for a in other_assets))
        mock_fetch_fonts.assert_any_call(category="sans-serif", sort_by="popularity")
        logger.info("test_provider_fonts_success_sans_serif_and_mock_icons PASSED")

    @mock.patch('frontend_trend_builder.actions.suggest_assets.fetch_google_fonts')
    def test_provider_fonts_failure_fallback_to_mock_fonts(self, mock_fetch_fonts):
        logger.info("Running test_provider_fonts_failure_fallback_to_mock_fonts")
        mock_fetch_fonts.return_value = MOCK_PROVIDER_FONTS_EMPTY # Simulate provider returning no fonts
        
        summary = "A design needing a serif font"
        trends = ["serif_fonts", "minimalism"] 
        
        result = suggest_assets.get_asset_suggestions(summary, trends)
        
        api_fonts_found = [item for item in result if item.get("source") == "GoogleFonts_API"]
        mock_fonts_found = [item for item in result if item.get("type") == "font" and item.get("source") != "GoogleFonts_API"]
        
        self.assertEqual(len(api_fonts_found), 0, "No fonts should come from API provider")
        self.assertTrue(len(mock_fonts_found) > 0, "Should get serif fonts from mock data")
        self.assertTrue(any(font["name"] == "Playfair Display" for font in mock_fonts_found)) # Mock serif
        
        self.assertTrue(any(item["type"] == "icon" for item in result))
        mock_fetch_fonts.assert_any_call(category="serif", sort_by="popularity")
        logger.info("test_provider_fonts_failure_fallback_to_mock_fonts PASSED")

    @mock.patch('frontend_trend_builder.actions.suggest_assets.fetch_google_fonts')
    def test_no_relevant_font_trends_uses_mock_fonts_and_assets(self, mock_fetch_fonts):
        logger.info("Running test_no_relevant_font_trends_uses_mock_fonts_and_assets")
        # No specific font trend, but "fonts" in summary might trigger a generic API call
        summary = "Dashboard with icons and nice fonts"
        trends = ["data_visualization", "dark_mode"] 
        
        # Simulate API returning nothing for default "sans-serif", "serif" calls triggered by "fonts"
        mock_fetch_fonts.return_value = MOCK_PROVIDER_FONTS_EMPTY 
        
        result = suggest_assets.get_asset_suggestions(summary, trends)
        
        api_fonts_found = [item for item in result if item.get("source") == "GoogleFonts_API"]
        mock_fonts_found = [item for item in result if item.get("type") == "font" and item.get("source") != "GoogleFonts_API"]
        icons_found = [item for item in result if item.get("type") == "icon"]
        
        self.assertEqual(len(api_fonts_found), 0)
        self.assertTrue(len(icons_found) > 0)
        self.assertTrue(any(icon["name"] == "Phosphor Icons - ChartLineUp" for icon in icons_found))
        # Check if mock fonts like JetBrains Mono (tagged with dashboard, dark_mode) are picked up
        self.assertTrue(any(font["name"] == "JetBrains Mono" for font in mock_fonts_found))
        
        # Check calls to fetch_google_fonts for "sans-serif" and "serif" due to "fonts" in summary
        calls = [mock.call(category="sans-serif", sort_by="popularity"), mock.call(category="serif", sort_by="popularity")]
        mock_fetch_fonts.assert_has_calls(calls, any_order=True)
        logger.info("test_no_relevant_font_trends_uses_mock_fonts_and_assets PASSED")

    # Test mock data path explicitly when no API call is expected (e.g. API key is None in provider)
    # This is now better tested in the provider's own tests. Here we assume provider handles key.
    @patch('frontend_trend_builder.actions.suggest_assets.fetch_google_fonts', return_value=[]) # Provider returns empty
    def test_get_asset_suggestions_mock_data_with_matches_provider_fails(self, mock_fetch_provider):
        logger.info("Running test_get_asset_suggestions_mock_data_with_matches_provider_fails")
        inspiration_summary = "A modern dashboard for crypto analytics. Dark theme preferred."
        trend_tags = ["dark_mode", "data_visualization", "modern_ui", "glassmorphism", "sans_serif_fonts"] # Add sans-serif
        result = suggest_assets.get_asset_suggestions(inspiration_summary, trend_tags)
        
        self.assertIsInstance(result, list)
        self.assertTrue(len(result) > 0)
        self.assertTrue(all(item.get("source") != "GoogleFonts_API" for item in result))
        expected_mock_font = "Roboto" # Mock sans-serif font
        expected_mock_icon = "Phosphor Icons - ChartLineUp"
        
        found_names = [item["name"] for item in result]
        self.assertIn(expected_mock_font, found_names)
        self.assertIn(expected_mock_icon, found_names)
        mock_fetch_provider.assert_any_call(category="sans-serif", sort_by="popularity")
        logger.info("test_get_asset_suggestions_mock_data_with_matches_provider_fails PASSED")

    # Test for file system errors for mock data loading path
    @patch('frontend_trend_builder.actions.suggest_assets.fetch_google_fonts', return_value=[])
    def test_get_asset_suggestions_mock_data_file_issues(self, mock_fetch_provider):
        logger.info("Running test_get_asset_suggestions_mock_data_file_issues")
        original_mock_path = suggest_assets.MOCK_ASSET_PATH
        
        # Test FileNotFoundError
        suggest_assets.MOCK_ASSET_PATH = "non_existent_asset_data.json"
        result_not_found = suggest_assets.get_asset_suggestions("test", ["test"])
        self.assertEqual(result_not_found, [])
        
        # Test JSONDecodeError
        temp_malformed_file = os.path.join(os.path.dirname(original_mock_path), "temp_malformed_asset.json")
        with open(temp_malformed_file, 'w') as f:
            f.write("[{'invalid_json': ]") 
        
        suggest_assets.MOCK_ASSET_PATH = temp_malformed_file
        result_decode_error = suggest_assets.get_asset_suggestions("test", ["test"])
        self.assertEqual(result_decode_error, [])
        
        os.remove(temp_malformed_file) 
        suggest_assets.MOCK_ASSET_PATH = original_mock_path 
        logger.info("test_get_asset_suggestions_mock_data_file_issues PASSED")


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger.info("Running tests for suggest_assets.py (refactored with provider mocks).")
    unittest.main()
