import sys
import os
import json
import logging
from unittest import TestCase, mock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from data_providers.unsplash_provider import (
    fetch_unsplash_inspiration,
    scrape_unsplash_inspiration,
    _parse_unsplash_api_response, # For direct testing if needed
    _parse_unsplash_html_scrape,  # For direct testing if needed
    CONFIG_UNSPLASH_KEY_PLACEHOLDER
)
from data_providers.http_client import DataProviderError # To simulate fetch_url_text raising it

if not logging.getLogger().hasHandlers() or logging.getLogger().level > logging.DEBUG:
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
logger = logging.getLogger(__name__)

# --- Mock Responses for Unsplash ---
MOCK_API_JSON_SUCCESS = json.dumps({
    "results": [
        {"id": "api1", "alt_description": "API Image 1", "urls": {"regular": "api_url1.jpg"}, "tags": [{"title":"api_tag"}]},
        {"id": "api2", "alt_description": "API Image 2", "urls": {"small": "api_url2_small.jpg"}, "tags": []}
    ]
})
MOCK_API_JSON_EMPTY = json.dumps({"results": []})
MOCK_API_JSON_MALFORMED = "This is not valid JSON"

MOCK_HTML_NEXT_DATA_SUCCESS = '<html><script id="__NEXT_DATA__" type="application/json">{ "props": { "pageProps": { "results": [{"id": "next1", "alt_description": "Next Image 1", "urls": {"regular": "next_url1.jpg"}, "tags": [{"title":"next_tag"}]}] } } }</script></html>'
MOCK_HTML_IMG_TAGS_SUCCESS = '<html><body><img src="https://images.unsplash.com/photo-img1?auto=format" alt="Img Tag 1"><img src="https://images.unsplash.com/photo-img2?auto=format" alt="Img Tag 2"></body></html>'
MOCK_HTML_EMPTY = "<html><body>No images here.</body></html>"


class TestUnsplashProvider(TestCase):

    # --- Tests for fetch_unsplash_inspiration ---
    @mock.patch('data_providers.unsplash_provider.fetch_url_text')
    @mock.patch('frontend_trend_builder.data_providers.unsplash_provider.UNSPLASH_API_KEY', 'VALID_DUMMY_KEY')
    def test_fetch_unsplash_inspiration_api_success(self, mock_fetch_url):
        logger.info("Running test_fetch_unsplash_inspiration_api_success")
        mock_fetch_url.return_value = MOCK_API_JSON_SUCCESS
        results = fetch_unsplash_inspiration("test prompt")
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]['id'], "unsplash_api_api1")
        self.assertEqual(results[0]['source'], "Unsplash_API")
        mock_fetch_url.assert_called_once()
        logger.info("test_fetch_unsplash_inspiration_api_success PASSED")

    @mock.patch('data_providers.unsplash_provider.fetch_url_text')
    @mock.patch('frontend_trend_builder.data_providers.unsplash_provider.UNSPLASH_API_KEY', None)
    def test_fetch_unsplash_inspiration_no_api_key(self, mock_fetch_url):
        logger.info("Running test_fetch_unsplash_inspiration_no_api_key")
        results = fetch_unsplash_inspiration("test prompt")
        self.assertEqual(len(results), 0)
        mock_fetch_url.assert_not_called()
        logger.info("test_fetch_unsplash_inspiration_no_api_key PASSED")

    @mock.patch('data_providers.unsplash_provider.fetch_url_text')
    @mock.patch('frontend_trend_builder.data_providers.unsplash_provider.UNSPLASH_API_KEY', CONFIG_UNSPLASH_KEY_PLACEHOLDER)
    def test_fetch_unsplash_inspiration_placeholder_key(self, mock_fetch_url):
        logger.info("Running test_fetch_unsplash_inspiration_placeholder_key")
        results = fetch_unsplash_inspiration("test prompt")
        self.assertEqual(len(results), 0)
        mock_fetch_url.assert_not_called()
        logger.info("test_fetch_unsplash_inspiration_placeholder_key PASSED")


    @mock.patch('data_providers.unsplash_provider.fetch_url_text')
    @mock.patch('frontend_trend_builder.data_providers.unsplash_provider.UNSPLASH_API_KEY', 'VALID_DUMMY_KEY')
    def test_fetch_unsplash_inspiration_api_returns_invalid_json(self, mock_fetch_url):
        logger.info("Running test_fetch_unsplash_inspiration_api_returns_invalid_json")
        mock_fetch_url.return_value = MOCK_API_JSON_MALFORMED
        results = fetch_unsplash_inspiration("test prompt")
        self.assertEqual(len(results), 0)
        logger.info("test_fetch_unsplash_inspiration_api_returns_invalid_json PASSED")

    @mock.patch('data_providers.unsplash_provider.fetch_url_text')
    @mock.patch('frontend_trend_builder.data_providers.unsplash_provider.UNSPLASH_API_KEY', 'VALID_DUMMY_KEY')
    def test_fetch_unsplash_inspiration_api_fetch_raises_error(self, mock_fetch_url):
        logger.info("Running test_fetch_unsplash_inspiration_api_fetch_raises_error")
        mock_fetch_url.side_effect = DataProviderError("Simulated network error")
        results = fetch_unsplash_inspiration("test prompt")
        self.assertEqual(len(results), 0)
        logger.info("test_fetch_unsplash_inspiration_api_fetch_raises_error PASSED")

    # --- Tests for scrape_unsplash_inspiration ---
    @mock.patch('data_providers.unsplash_provider.fetch_url_text')
    def test_scrape_unsplash_inspiration_next_data_success(self, mock_fetch_url):
        logger.info("Running test_scrape_unsplash_inspiration_next_data_success")
        mock_fetch_url.return_value = MOCK_HTML_NEXT_DATA_SUCCESS
        results = scrape_unsplash_inspiration("test prompt")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['id'], "unsplash_json_scrape_next1")
        self.assertEqual(results[0]['source'], "Unsplash_JSON_Scrape")
        logger.info("test_scrape_unsplash_inspiration_next_data_success PASSED")

    @mock.patch('data_providers.unsplash_provider.fetch_url_text')
    def test_scrape_unsplash_inspiration_img_tags_success(self, mock_fetch_url):
        logger.info("Running test_scrape_unsplash_inspiration_img_tags_success")
        # Simulate __NEXT_DATA__ parse returning empty or failing, then img tags work
        mock_fetch_url.return_value = MOCK_HTML_IMG_TAGS_SUCCESS 
        results = scrape_unsplash_inspiration("test prompt")
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]['id'], "unsplash_html_scrape_0")
        self.assertEqual(results[0]['source'], "Unsplash_HTML_Img_Scrape")
        logger.info("test_scrape_unsplash_inspiration_img_tags_success PASSED")

    @mock.patch('data_providers.unsplash_provider.fetch_url_text')
    def test_scrape_unsplash_inspiration_empty_html(self, mock_fetch_url):
        logger.info("Running test_scrape_unsplash_inspiration_empty_html")
        mock_fetch_url.return_value = MOCK_HTML_EMPTY
        results = scrape_unsplash_inspiration("test prompt")
        self.assertEqual(len(results), 0)
        logger.info("test_scrape_unsplash_inspiration_empty_html PASSED")

    @mock.patch('data_providers.unsplash_provider.fetch_url_text')
    def test_scrape_unsplash_inspiration_fetch_raises_error(self, mock_fetch_url):
        logger.info("Running test_scrape_unsplash_inspiration_fetch_raises_error")
        mock_fetch_url.side_effect = DataProviderError("Simulated network error")
        results = scrape_unsplash_inspiration("test prompt")
        self.assertEqual(len(results), 0)
        logger.info("test_scrape_unsplash_inspiration_fetch_raises_error PASSED")

    # --- Direct tests for parsing functions (optional, but good for granularity) ---
    def test_parse_unsplash_api_response_direct(self):
        logger.info("Running test_parse_unsplash_api_response_direct")
        results = _parse_unsplash_api_response(MOCK_API_JSON_SUCCESS)
        self.assertEqual(len(results), 2)
        self.assertEqual(results[1]['title'], "API Image 2") # alt_description was used
        logger.info("test_parse_unsplash_api_response_direct PASSED")

    def test_parse_unsplash_html_scrape_direct_next_data(self):
        logger.info("Running test_parse_unsplash_html_scrape_direct_next_data")
        results = _parse_unsplash_html_scrape(MOCK_HTML_NEXT_DATA_SUCCESS, "test")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], "Next Image 1")
        logger.info("test_parse_unsplash_html_scrape_direct_next_data PASSED")

    def test_parse_unsplash_html_scrape_direct_img_tags(self):
        logger.info("Running test_parse_unsplash_html_scrape_direct_img_tags")
        # Simulate __NEXT_DATA__ part failing by providing HTML that only has img tags
        results = _parse_unsplash_html_scrape(MOCK_HTML_IMG_TAGS_SUCCESS, "test")
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]['title'], "Img Tag 1")
        logger.info("test_parse_unsplash_html_scrape_direct_img_tags PASSED")

if __name__ == '__main__':
    # unittest.main() would typically be used here if running this file standalone
    logger.info("Running tests for unsplash_provider.py. Use 'python -m unittest discover tests/data_providers'.")
    pass
