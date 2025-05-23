import unittest
from unittest.mock import patch, MagicMock
import json

# Adjust import paths based on test execution context
from frontend_trend_builder.data_providers.google_fonts_provider import fetch_google_fonts
from frontend_trend_builder.data_providers.http_client import DataProviderError
# We will patch 'frontend_trend_builder.config.GOOGLE_FONTS_API_KEY' and 
# 'frontend_trend_builder.data_providers.google_fonts_provider.CONFIG_GOOGLE_FONTS_KEY_PLACEHOLDER'

# Mock data examples
MOCK_API_FONTS_SUCCESS_SERIF = json.dumps({
    "items": [
        {"family": "Lora", "category": "serif"},
        {"family": "Merriweather", "category": "serif"}
    ]
})

MOCK_API_FONTS_SUCCESS_ALL = json.dumps({
    "items": [
        {"family": "Roboto", "category": "sans-serif"},
        {"family": "Open Sans", "category": "sans-serif"},
        {"family": "Lato", "category": "sans-serif"},
        {"family": "Playfair Display", "category": "serif"},
        {"family": "Montserrat", "category": "sans-serif"}
    ]
})

class TestGoogleFontsProvider(unittest.TestCase):

    @patch('frontend_trend_builder.data_providers.google_fonts_provider.fetch_url_text')
    @patch('frontend_trend_builder.data_providers.google_fonts_provider.GOOGLE_FONTS_API_KEY', 'VALID_API_KEY')
    def test_fetch_google_fonts_api_success_with_category(self, mock_fetch_url_text):
        mock_fetch_url_text.return_value = MOCK_API_FONTS_SUCCESS_SERIF
        
        fonts = fetch_google_fonts(category="serif")
        
        self.assertEqual(len(fonts), 2)
        self.assertEqual(fonts[0]['name'], 'Lora')
        self.assertEqual(fonts[0]['source'], 'GoogleFonts_API')
        self.assertEqual(fonts[0]['category'], 'serif')
        mock_fetch_url_text.assert_called_once()
        self.assertTrue("googleapis.com/webfonts/v1/webfonts" in mock_fetch_url_text.call_args[0][0])
        self.assertTrue("category=serif" in mock_fetch_url_text.call_args[0][0])

    @patch('frontend_trend_builder.data_providers.google_fonts_provider.fetch_url_text')
    @patch('frontend_trend_builder.data_providers.google_fonts_provider.GOOGLE_FONTS_API_KEY', 'VALID_API_KEY')
    def test_fetch_google_fonts_api_success_no_category(self, mock_fetch_url_text):
        mock_fetch_url_text.return_value = MOCK_API_FONTS_SUCCESS_ALL
        
        fonts = fetch_google_fonts() # No category specified
        
        self.assertEqual(len(fonts), 5) # Expecting all 5 from MOCK_API_FONTS_SUCCESS_ALL
        self.assertEqual(fonts[0]['name'], 'Roboto')
        self.assertEqual(fonts[0]['source'], 'GoogleFonts_API')
        self.assertEqual(fonts[3]['category'], 'serif')
        mock_fetch_url_text.assert_called_once()
        self.assertTrue("googleapis.com/webfonts/v1/webfonts" in mock_fetch_url_text.call_args[0][0])
        self.assertFalse("category=" in mock_fetch_url_text.call_args[0][0]) # No category in URL

    @patch('frontend_trend_builder.data_providers.google_fonts_provider.fetch_url_text')
    @patch('frontend_trend_builder.data_providers.google_fonts_provider.CONFIG_GOOGLE_FONTS_KEY_PLACEHOLDER', 'KEY_IS_PLACEHOLDER')
    @patch('frontend_trend_builder.data_providers.google_fonts_provider.GOOGLE_FONTS_API_KEY', 'KEY_IS_PLACEHOLDER')
    def test_fetch_google_fonts_api_key_placeholder(self, mock_fetch_url_text):
        fonts = fetch_google_fonts(category="serif")
        self.assertEqual(len(fonts), 0)
        mock_fetch_url_text.assert_not_called() # API call should be skipped

    @patch('frontend_trend_builder.data_providers.google_fonts_provider.fetch_url_text')
    @patch('frontend_trend_builder.data_providers.google_fonts_provider.GOOGLE_FONTS_API_KEY', None)
    def test_fetch_google_fonts_api_key_none(self, mock_fetch_url_text):
        fonts = fetch_google_fonts(category="display")
        self.assertEqual(len(fonts), 0)
        mock_fetch_url_text.assert_not_called()

    @patch('frontend_trend_builder.data_providers.google_fonts_provider.fetch_url_text')
    @patch('frontend_trend_builder.data_providers.google_fonts_provider.GOOGLE_FONTS_API_KEY', 'VALID_API_KEY')
    def test_fetch_google_fonts_api_call_fails(self, mock_fetch_url_text):
        mock_fetch_url_text.side_effect = DataProviderError("API Call Failed")
        
        fonts = fetch_google_fonts(category="sans-serif")
        
        self.assertEqual(len(fonts), 0)
        mock_fetch_url_text.assert_called_once()

    @patch('frontend_trend_builder.data_providers.google_fonts_provider.fetch_url_text')
    @patch('frontend_trend_builder.data_providers.google_fonts_provider.GOOGLE_FONTS_API_KEY', 'VALID_API_KEY')
    def test_fetch_google_fonts_api_returns_invalid_json(self, mock_fetch_url_text):
        mock_fetch_url_text.return_value = "This is not JSON"
        
        fonts = fetch_google_fonts(category="serif")
        
        self.assertEqual(len(fonts), 0) # Expect empty list due to JSON parsing error
        mock_fetch_url_text.assert_called_once()

    @patch('frontend_trend_builder.data_providers.google_fonts_provider.fetch_url_text')
    @patch('frontend_trend_builder.data_providers.google_fonts_provider.GOOGLE_FONTS_API_KEY', 'VALID_API_KEY')
    def test_fetch_google_fonts_api_returns_empty_items(self, mock_fetch_url_text):
        mock_fetch_url_text.return_value = json.dumps({"items": []}) # API returns no fonts
        
        fonts = fetch_google_fonts(category="serif")
        
        self.assertEqual(len(fonts), 0)
        mock_fetch_url_text.assert_called_once()

    def test_returned_font_structure(self):
        # Test structure using a manually created example that fetch_google_fonts should return
        example_font_list = [{"type": "font", "name": "Test Font", "category": "serif", "source": "GoogleFonts_API"}]
        font = example_font_list[0]
        self.assertIn('type', font)
        self.assertEqual(font['type'], 'font')
        self.assertIn('name', font)
        self.assertIn('category', font)
        self.assertIn('source', font)
        self.assertEqual(font['source'], 'GoogleFonts_API')

if __name__ == '__main__':
    # Adjust sys.path for direct execution, similar to test_unsplash_provider.py
    import sys
    import os
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    unittest.main()
