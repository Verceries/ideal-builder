import sys
import os
import json
import logging
from unittest import TestCase, mock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from data_providers.google_fonts_provider import (
    fetch_google_fonts,
    _parse_google_fonts_api_response, # For direct testing
    CONFIG_GOOGLE_FONTS_KEY_PLACEHOLDER
)
from data_providers.http_client import DataProviderError

if not logging.getLogger().hasHandlers() or logging.getLogger().level > logging.DEBUG:
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
logger = logging.getLogger(__name__)

# --- Mock Responses for Google Fonts ---
MOCK_GF_API_SUCCESS_SERIF = json.dumps({
    "items": [
        {"family": "Merriweather", "category": "serif"},
        {"family": "Playfair Display", "category": "serif"},
        {"family": "Lora", "category": "serif"}
    ]
})
MOCK_GF_API_SUCCESS_SANS_SERIF = json.dumps({
    "items": [
        {"family": "Roboto", "category": "sans-serif"},
        {"family": "Open Sans", "category": "sans-serif"}
    ]
})
MOCK_GF_API_SUCCESS_ALL_POPULAR = json.dumps({ # Simulates a broader, unfiltered popular list
    "items": [
        {"family": "Roboto", "category": "sans-serif"},
        {"family": "Open Sans", "category": "sans-serif"},
        {"family": "Lato", "category": "sans-serif"},
        {"family": "Merriweather", "category": "serif"},
        {"family": "Montserrat", "category": "sans-serif"},
        {"family": "Playfair Display", "category": "serif"},
        {"family": "Oswald", "category": "sans-serif"},
        {"family": "Source Sans Pro", "category": "sans-serif"},
        {"family": "Raleway", "category": "sans-serif"},
        {"family": "PT Sans", "category": "sans-serif"},
        {"family": "Lora", "category": "serif"}, # A serif font
        {"family": "Poppins", "category": "sans-serif"},
        {"family": "Nunito", "category": "sans-serif"},
        {"family": "Slabo 27px", "category": "serif"},
        {"family": "Rubik", "category": "sans-serif"},
        {"family": "Ubuntu", "category": "sans-serif"},
        {"family": "Noto Sans JP", "category": "sans-serif"},
        {"family": "PT Serif", "category": "serif"},
        {"family": "Work Sans", "category": "sans-serif"},
        {"family": "Nanum Gothic", "category": "sans-serif"}
    ]
})
MOCK_GF_API_EMPTY = json.dumps({"items": []})
MOCK_GF_API_MALFORMED = "This is not valid JSON for fonts"


class TestGoogleFontsProvider(TestCase):

    # --- Tests for fetch_google_fonts ---
    @mock.patch('data_providers.google_fonts_provider.fetch_url_text')
    @mock.patch('frontend_trend_builder.data_providers.google_fonts_provider.GOOGLE_FONTS_API_KEY', 'VALID_DUMMY_KEY')
    def test_fetch_google_fonts_api_success_serif(self, mock_fetch_url):
        logger.info("Running test_fetch_google_fonts_api_success_serif")
        mock_fetch_url.return_value = MOCK_GF_API_SUCCESS_SERIF
        results = fetch_google_fonts(category="serif")
        self.assertEqual(len(results), 3)
        self.assertEqual(results[0]['name'], "Merriweather")
        self.assertEqual(results[0]['source'], "GoogleFonts_API")
        self.assertTrue(all(f['category'] == 'serif' for f in results))
        mock_fetch_url.assert_called_once()
        self.assertIn("category=serif", mock_fetch_url.call_args[0][0]) # Check if URL contains category
        logger.info("test_fetch_google_fonts_api_success_serif PASSED")

    @mock.patch('data_providers.google_fonts_provider.fetch_url_text')
    @mock.patch('frontend_trend_builder.data_providers.google_fonts_provider.GOOGLE_FONTS_API_KEY', 'VALID_DUMMY_KEY')
    def test_fetch_google_fonts_api_success_all_popular(self, mock_fetch_url):
        logger.info("Running test_fetch_google_fonts_api_success_all_popular")
        mock_fetch_url.return_value = MOCK_GF_API_SUCCESS_ALL_POPULAR
        results = fetch_google_fonts(sort_by="popularity") # No category
        self.assertTrue(len(results) > 5) # Expecting a larger list
        self.assertEqual(results[0]['name'], "Roboto")
        self.assertEqual(results[0]['source'], "GoogleFonts_API")
        self.assertNotIn("category=", mock_fetch_url.call_args[0][0]) # Ensure no category filter in URL
        logger.info("test_fetch_google_fonts_api_success_all_popular PASSED")


    @mock.patch('data_providers.google_fonts_provider.fetch_url_text')
    @mock.patch('frontend_trend_builder.data_providers.google_fonts_provider.GOOGLE_FONTS_API_KEY', None)
    def test_fetch_google_fonts_no_api_key(self, mock_fetch_url):
        logger.info("Running test_fetch_google_fonts_no_api_key")
        results = fetch_google_fonts(category="serif")
        self.assertEqual(len(results), 0)
        mock_fetch_url.assert_not_called()
        logger.info("test_fetch_google_fonts_no_api_key PASSED")

    @mock.patch('data_providers.google_fonts_provider.fetch_url_text')
    @mock.patch('frontend_trend_builder.data_providers.google_fonts_provider.GOOGLE_FONTS_API_KEY', CONFIG_GOOGLE_FONTS_KEY_PLACEHOLDER)
    def test_fetch_google_fonts_placeholder_key(self, mock_fetch_url):
        logger.info("Running test_fetch_google_fonts_placeholder_key")
        results = fetch_google_fonts(category="serif")
        self.assertEqual(len(results), 0)
        mock_fetch_url.assert_not_called()
        logger.info("test_fetch_google_fonts_placeholder_key PASSED")

    @mock.patch('data_providers.google_fonts_provider.fetch_url_text')
    @mock.patch('frontend_trend_builder.data_providers.google_fonts_provider.GOOGLE_FONTS_API_KEY', 'VALID_DUMMY_KEY')
    def test_fetch_google_fonts_api_returns_invalid_json(self, mock_fetch_url):
        logger.info("Running test_fetch_google_fonts_api_returns_invalid_json")
        mock_fetch_url.return_value = MOCK_GF_API_MALFORMED
        results = fetch_google_fonts(category="serif")
        self.assertEqual(len(results), 0)
        logger.info("test_fetch_google_fonts_api_returns_invalid_json PASSED")

    @mock.patch('data_providers.google_fonts_provider.fetch_url_text')
    @mock.patch('frontend_trend_builder.data_providers.google_fonts_provider.GOOGLE_FONTS_API_KEY', 'VALID_DUMMY_KEY')
    def test_fetch_google_fonts_api_fetch_raises_error(self, mock_fetch_url):
        logger.info("Running test_fetch_google_fonts_api_fetch_raises_error")
        mock_fetch_url.side_effect = DataProviderError("Simulated network error for fonts")
        results = fetch_google_fonts(category="sans-serif")
        self.assertEqual(len(results), 0)
        logger.info("test_fetch_google_fonts_api_fetch_raises_error PASSED")

    # --- Direct tests for parsing function ---
    def test_parse_google_fonts_api_response_direct_serif(self):
        logger.info("Running test_parse_google_fonts_api_response_direct_serif")
        results = _parse_google_fonts_api_response(MOCK_GF_API_SUCCESS_SERIF, category_filter="serif")
        self.assertEqual(len(results), 3)
        self.assertEqual(results[0]['name'], "Merriweather")
        self.assertTrue(all(f['category'] == 'serif' for f in results))
        logger.info("test_parse_google_fonts_api_response_direct_serif PASSED")
        
    def test_parse_google_fonts_api_response_direct_all_no_filter(self):
        logger.info("Running test_parse_google_fonts_api_response_direct_all_no_filter")
        # Test parsing when no client-side category filter is applied (API might have filtered or returned all)
        results = _parse_google_fonts_api_response(MOCK_GF_API_SUCCESS_ALL_POPULAR, category_filter=None)
        self.assertTrue(len(results) >= 10) # Should parse all items provided in this mock
        self.assertTrue(any(f['category'] == 'serif' for f in results))
        self.assertTrue(any(f['category'] == 'sans-serif' for f in results))
        logger.info("test_parse_google_fonts_api_response_direct_all_no_filter PASSED")

    def test_parse_google_fonts_api_response_direct_client_filter_miss(self):
        logger.info("Running test_parse_google_fonts_api_response_direct_client_filter_miss")
        # API returns serif, but client parser filters for display (should be empty)
        results = _parse_google_fonts_api_response(MOCK_GF_API_SUCCESS_SERIF, category_filter="display")
        self.assertEqual(len(results), 0)
        logger.info("test_parse_google_fonts_api_response_direct_client_filter_miss PASSED")


if __name__ == '__main__':
    logger.info("Running tests for google_fonts_provider.py. Use 'python -m unittest discover tests/data_providers'.")
    pass
