import sys
import os
import json 
from typing import List, Dict # Keep for type hints if needed
from unittest.mock import patch 

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from actions import gather_inspiration # Module under test

# --- Mock Provider Responses ---
# These simulate what the provider functions would return.
MOCK_PROVIDER_API_SUCCESS = [
    {"id": "api_img_1", "title": "API Image 1", "source": "Unsplash_API", "tags": ["api", "landscape"], "image_url_mock": "url1"}
]
MOCK_PROVIDER_SCRAPE_SUCCESS = [
    {"id": "scrape_img_1", "title": "Scraped Image 1", "source": "Unsplash_JSON_Scrape", "tags": ["scrape", "json"], "image_url_mock": "url2"}
]
MOCK_PROVIDER_EMPTY_LIST = []


class TestGetInspirationWithProviderMocks(unittest.TestCase): # Changed to use unittest.TestCase for better structure

    @patch('frontend_trend_builder.actions.gather_inspiration.fetch_unsplash_inspiration')
    @patch('frontend_trend_builder.actions.gather_inspiration.scrape_unsplash_inspiration')
    def test_api_provider_success(self, mock_scrape_unsplash, mock_fetch_unsplash):
        """Test get_inspiration when fetch_unsplash_inspiration (API) succeeds."""
        logger.info("Running test_api_provider_success")
        mock_fetch_unsplash.return_value = MOCK_PROVIDER_API_SUCCESS
        
        result = gather_inspiration.get_inspiration("landscape")
        
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "api_img_1")
        self.assertEqual(result[0]["source"], "Unsplash_API")
        mock_fetch_unsplash.assert_called_once_with("landscape")
        mock_scrape_unsplash.assert_not_called()
        logger.info("test_api_provider_success PASSED")

    @patch('frontend_trend_builder.actions.gather_inspiration.fetch_unsplash_inspiration')
    @patch('frontend_trend_builder.actions.gather_inspiration.scrape_unsplash_inspiration')
    def test_api_provider_fails_scrape_provider_success(self, mock_scrape_unsplash, mock_fetch_unsplash):
        """Test get_inspiration: API provider fails (empty list), scrape provider succeeds."""
        logger.info("Running test_api_provider_fails_scrape_provider_success")
        mock_fetch_unsplash.return_value = MOCK_PROVIDER_EMPTY_LIST # API returns no results
        mock_scrape_unsplash.return_value = MOCK_PROVIDER_SCRAPE_SUCCESS
        
        result = gather_inspiration.get_inspiration("abstract")
        
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "scrape_img_1")
        self.assertEqual(result[0]["source"], "Unsplash_JSON_Scrape")
        mock_fetch_unsplash.assert_called_once_with("abstract")
        mock_scrape_unsplash.assert_called_once_with("abstract")
        logger.info("test_api_provider_fails_scrape_provider_success PASSED")

    @patch('frontend_trend_builder.actions.gather_inspiration.fetch_unsplash_inspiration')
    @patch('frontend_trend_builder.actions.gather_inspiration.scrape_unsplash_inspiration')
    def test_api_and_scrape_providers_fail_fallback_to_mock(self, mock_scrape_unsplash, mock_fetch_unsplash):
        """Test get_inspiration: Both API and scrape providers fail (empty), fallback to mock."""
        logger.info("Running test_api_and_scrape_providers_fail_fallback_to_mock")
        mock_fetch_unsplash.return_value = MOCK_PROVIDER_EMPTY_LIST
        mock_scrape_unsplash.return_value = MOCK_PROVIDER_EMPTY_LIST
        
        # This prompt should match items in 'mock_inspiration_data.json'
        result = gather_inspiration.get_inspiration("minimalist portfolio") 
        
        self.assertIsInstance(result, list)
        self.assertTrue(len(result) > 0) # Expecting mock data
        # Check if source is NOT from API or scrape (i.e., it's from mock)
        self.assertTrue(all(item.get("source") not in ["Unsplash_API", "Unsplash_JSON_Scrape", "Unsplash_HTML_Img_Scrape"] for item in result))
        self.assertTrue(any(item["id"] == "mock2" or item["id"] == "mock7" for item in result)) # From mock data
        mock_fetch_unsplash.assert_called_once_with("minimalist portfolio")
        mock_scrape_unsplash.assert_called_once_with("minimalist portfolio")
        logger.info("test_api_and_scrape_providers_fail_fallback_to_mock PASSED")

    @patch('frontend_trend_builder.actions.gather_inspiration.fetch_unsplash_inspiration')
    @patch('frontend_trend_builder.actions.gather_inspiration.scrape_unsplash_inspiration')
    def test_mock_data_no_matches(self, mock_scrape_unsplash, mock_fetch_unsplash):
        """Test get_inspiration: API/scrape fail, and mock data also has no matches."""
        logger.info("Running test_mock_data_no_matches")
        mock_fetch_unsplash.return_value = MOCK_PROVIDER_EMPTY_LIST
        mock_scrape_unsplash.return_value = MOCK_PROVIDER_EMPTY_LIST
        
        # This prompt is unlikely to match anything in mock_inspiration_data.json
        result = gather_inspiration.get_inspiration("zyxw_unmatchable_keyword_12345_for_inspiration")
        
        self.assertIsInstance(result, list) # Function now always returns a list
        self.assertEqual(len(result), 0) # Expecting an empty list if no mock data matches
        logger.info("test_mock_data_no_matches PASSED")

    # Test for file system errors for mock data loading path
    # This test needs to ensure that the API and scrape paths are simulated to return empty,
    # so the code attempts to load the mock file.
    @patch('frontend_trend_builder.actions.gather_inspiration.fetch_unsplash_inspiration', return_value=[])
    @patch('frontend_trend_builder.actions.gather_inspiration.scrape_unsplash_inspiration', return_value=[])
    def test_get_inspiration_mock_data_file_issues(self, mock_scrape, mock_fetch_api):
        logger.info("Running test_get_inspiration_mock_data_file_issues")
        original_mock_path = gather_inspiration.MOCK_INSPIRATION_PATH
        
        # Test FileNotFoundError
        gather_inspiration.MOCK_INSPIRATION_PATH = "non_existent_mock_data_file.json"
        result_not_found = gather_inspiration.get_inspiration("test")
        self.assertEqual(result_not_found, []) # Should return empty list on file error
        
        # Test JSONDecodeError
        temp_malformed_file = os.path.join(os.path.dirname(original_mock_path), "temp_malformed_mock.json")
        with open(temp_malformed_file, 'w') as f:
            f.write("{'invalid_json': ") 
        
        gather_inspiration.MOCK_INSPIRATION_PATH = temp_malformed_file
        result_decode_error = gather_inspiration.get_inspiration("test")
        self.assertEqual(result_decode_error, []) # Should return empty list on decode error
        
        os.remove(temp_malformed_file) 
        gather_inspiration.MOCK_INSPIRATION_PATH = original_mock_path 
        logger.info("test_get_inspiration_mock_data_file_issues PASSED")


if __name__ == '__main__':
    # unittest.main() is the standard way to run tests in a file.
    # Ensure this script is run with `python -m unittest path_to_this_file` or similar.
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger.info("Running tests for gather_inspiration.py (refactored with provider mocks).")
    unittest.main()
