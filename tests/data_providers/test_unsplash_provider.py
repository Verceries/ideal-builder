import unittest
from unittest.mock import patch, MagicMock
import json

# Assuming the providers are in frontend-trend-builder/data_providers
# Adjust the import path based on how tests are run and the project structure.
# If tests are run from the root of the project, this might be:
# from frontend-trend-builder.data_providers.unsplash_provider import fetch_unsplash_images, _MOCK_UNSPLASH_DATA
# from frontend-trend-builder.data_providers.http_client import DataProviderError
# from frontend-trend-builder.config import UNSPLASH_API_KEY, CONFIG_UNSPLASH_KEY_PLACEHOLDER

# For now, let's assume a simpler structure or that PYTHONPATH is set up for tests
from frontend_trend_builder.data_providers.unsplash_provider import fetch_unsplash_images, _MOCK_UNSPLASH_DATA
from frontend_trend_builder.data_providers.http_client import DataProviderError
# We will patch 'frontend_trend_builder.config.UNSPLASH_API_KEY' and 
# 'frontend_trend_builder.data_providers.unsplash_provider.CONFIG_UNSPLASH_KEY_PLACEHOLDER' directly in tests.


# Mock data examples
MOCK_API_RESPONSE_SUCCESS = json.dumps({
    "results": [
        {"id": "api_123", "alt_description": "Mock API Image 1", "urls": {"regular": "http://api.example.com/img1.jpg"}, "tags": [{"title": "api_tag1"}]}
    ],
    "total": 1
})
MOCK_HTML_RESPONSE_SUCCESS = """
<html><body>
    <script id="__NEXT_DATA__" type="application/json">
    {
        "props": { "pageProps": {
            "photos": [
                {"id": "scrape_456", "alt_description": "Mock Scrape Image 1", "urls": {"regular": "http://scrape.example.com/img1.jpg"}, "tags": [{"title": "scrape_tag1"}]}
            ]
        }}
    }
    </script>
</body></html>
"""

class TestUnsplashProvider(unittest.TestCase):

    @patch('frontend_trend_builder.data_providers.unsplash_provider.fetch_url_text')
    @patch('frontend_trend_builder.data_providers.unsplash_provider.UNSPLASH_API_KEY', 'VALID_API_KEY')
    def test_fetch_unsplash_images_api_success(self, mock_fetch_url_text):
        mock_fetch_url_text.return_value = MOCK_API_RESPONSE_SUCCESS
        
        images = fetch_unsplash_images("test_prompt")
        
        self.assertEqual(len(images), 1)
        self.assertEqual(images[0]['id'], 'unsplash_api_api_123')
        self.assertEqual(images[0]['source'], 'Unsplash_API')
        self.assertEqual(images[0]['title'], 'Mock API Image 1')
        self.assertIn('api_tag1', images[0]['tags'])
        mock_fetch_url_text.assert_called_once()
        self.assertTrue("api.unsplash.com" in mock_fetch_url_text.call_args[0][0])

    @patch('frontend_trend_builder.data_providers.unsplash_provider.fetch_url_text')
    @patch('frontend_trend_builder.data_providers.unsplash_provider.CONFIG_UNSPLASH_KEY_PLACEHOLDER', 'KEY_IS_PLACEHOLDER')
    @patch('frontend_trend_builder.data_providers.unsplash_provider.UNSPLASH_API_KEY', 'KEY_IS_PLACEHOLDER')
    def test_fetch_unsplash_images_api_key_placeholder_falls_to_scrape(self, mock_fetch_url_text):
        # First call (API) will be skipped, second call (scrape) should return HTML
        mock_fetch_url_text.return_value = MOCK_HTML_RESPONSE_SUCCESS
        
        images = fetch_unsplash_images("test_prompt")
        
        self.assertEqual(len(images), 1)
        self.assertEqual(images[0]['id'], 'unsplash_scrape_scrape_456')
        self.assertEqual(images[0]['source'], 'Unsplash_Scrape')
        mock_fetch_url_text.assert_called_once() # Only called for scrape
        self.assertTrue("unsplash.com/s/photos/" in mock_fetch_url_text.call_args[0][0])

    @patch('frontend_trend_builder.data_providers.unsplash_provider.fetch_url_text')
    @patch('frontend_trend_builder.data_providers.unsplash_provider.UNSPLASH_API_KEY', None) # API Key is None
    def test_fetch_unsplash_images_api_key_none_falls_to_scrape(self, mock_fetch_url_text):
        mock_fetch_url_text.return_value = MOCK_HTML_RESPONSE_SUCCESS
        
        images = fetch_unsplash_images("test_prompt")
        
        self.assertEqual(len(images), 1)
        self.assertEqual(images[0]['id'], 'unsplash_scrape_scrape_456')
        self.assertEqual(images[0]['source'], 'Unsplash_Scrape')
        mock_fetch_url_text.assert_called_once()
        self.assertTrue("unsplash.com/s/photos/" in mock_fetch_url_text.call_args[0][0])

    @patch('frontend_trend_builder.data_providers.unsplash_provider.fetch_url_text')
    @patch('frontend_trend_builder.data_providers.unsplash_provider.UNSPLASH_API_KEY', 'VALID_API_KEY')
    def test_fetch_unsplash_images_api_fails_then_scrape_success(self, mock_fetch_url_text):
        # API call fails, Scrape call succeeds
        mock_fetch_url_text.side_effect = [
            DataProviderError("API Failed"),  # For API call
            MOCK_HTML_RESPONSE_SUCCESS        # For Scrape call
        ]
        
        images = fetch_unsplash_images("test_prompt")
        
        self.assertEqual(len(images), 1)
        self.assertEqual(images[0]['id'], 'unsplash_scrape_scrape_456')
        self.assertEqual(images[0]['source'], 'Unsplash_Scrape')
        self.assertEqual(mock_fetch_url_text.call_count, 2)
        self.assertTrue("api.unsplash.com" in mock_fetch_url_text.call_args_list[0][0][0])
        self.assertTrue("unsplash.com/s/photos/" in mock_fetch_url_text.call_args_list[1][0][0])

    @patch('frontend_trend_builder.data_providers.unsplash_provider.fetch_url_text')
    @patch('frontend_trend_builder.data_providers.unsplash_provider.UNSPLASH_API_KEY', 'VALID_API_KEY')
    def test_fetch_unsplash_images_api_returns_invalid_json_then_scrape_success(self, mock_fetch_url_text):
        mock_fetch_url_text.side_effect = [
            "This is not JSON",          # For API call
            MOCK_HTML_RESPONSE_SUCCESS   # For Scrape call
        ]
        
        images = fetch_unsplash_images("test_prompt")
        
        self.assertEqual(len(images), 1)
        self.assertEqual(images[0]['id'], 'unsplash_scrape_scrape_456')
        self.assertEqual(images[0]['source'], 'Unsplash_Scrape')
        self.assertEqual(mock_fetch_url_text.call_count, 2)

    @patch('frontend_trend_builder.data_providers.unsplash_provider.fetch_url_text')
    @patch('frontend_trend_builder.data_providers.unsplash_provider.UNSPLASH_API_KEY', 'VALID_API_KEY')
    def test_fetch_unsplash_images_api_and_scrape_fail_fallback_to_mock(self, mock_fetch_url_text):
        # Both API and Scrape calls fail
        mock_fetch_url_text.side_effect = [
            DataProviderError("API Failed"),
            DataProviderError("Scrape Failed")
        ]
        
        images = fetch_unsplash_images("test_prompt_for_fallback")
        
        self.assertEqual(len(images), len(_MOCK_UNSPLASH_DATA))
        self.assertEqual(images[0]['source'], 'Unsplash_Mock_Fallback')
        self.assertEqual(images[0]['id'], _MOCK_UNSPLASH_DATA[0]['id'])
        self.assertEqual(mock_fetch_url_text.call_count, 2)

    @patch('frontend_trend_builder.data_providers.unsplash_provider.fetch_url_text')
    @patch('frontend_trend_builder.data_providers.unsplash_provider.UNSPLASH_API_KEY', 'VALID_API_KEY')
    def test_fetch_unsplash_images_api_and_scrape_return_empty_fallback_to_mock(self, mock_fetch_url_text):
        # API returns empty results, Scrape returns empty/invalid HTML
        mock_fetch_url_text.side_effect = [
            json.dumps({"results": [], "total": 0}), # API returns no images
            "<html><body><p>No images here</p></body></html>"  # Scrape returns no parsable images
        ]
        
        images = fetch_unsplash_images("test_prompt_for_empty_fallback")
        
        self.assertEqual(len(images), len(_MOCK_UNSPLASH_DATA))
        self.assertEqual(images[0]['source'], 'Unsplash_Mock_Fallback')
        self.assertEqual(images[1]['id'], _MOCK_UNSPLASH_DATA[1]['id'])
        self.assertEqual(mock_fetch_url_text.call_count, 2)

    def test_returned_image_structure(self):
        # This test uses the _MOCK_UNSPLASH_DATA to check structure,
        # as it's the easiest to inspect directly without mocking calls.
        image = _MOCK_UNSPLASH_DATA[0]
        self.assertIn('id', image)
        self.assertIn('title', image)
        self.assertIn('description', image)
        self.assertIn('tags', image)
        self.assertIsInstance(image['tags'], list)
        self.assertIn('image_url_mock', image)
        self.assertIn('source', image)

if __name__ == '__main__':
    # This is to make tests runnable when the file is executed directly
    # For proper testing in a larger project, use a test runner (e.g. `python -m unittest discover`)
    # that handles package structures and PYTHONPATH correctly.
    # To run this file directly for quick checks, you might need to adjust sys.path:
    import sys
    import os
    # Assuming this test file is in tests/data_providers/ and the code is in frontend-trend-builder/
    # Add the project root to sys.path
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    
    # Need to re-import after sys.path modification if modules were not found initially
    # This is tricky. A better way is to run with `python -m unittest tests.data_providers.test_unsplash_provider`
    # from the project root.

    unittest.main()
