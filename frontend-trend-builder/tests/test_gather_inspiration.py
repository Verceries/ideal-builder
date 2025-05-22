import sys
import os
import json # For mock responses
from typing import List, Dict, Union # Not strictly needed for this file after changes, but good practice
from unittest.mock import patch 

# Adjust the Python path to include the parent directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from actions import gather_inspiration # Module under test

# --- Mock Unsplash API Responses ---
MOCK_UNSPLASH_API_SUCCESS_RESPONSE = json.dumps({
    "results": [
        {
            "id": "api_img_1",
            "description": "A beautiful API image",
            "alt_description": "API Alt Text 1",
            "urls": {"regular": "http://example.com/api_img_1.jpg", "small": "http://example.com/api_img_1_small.jpg"},
            "tags": [{"title": "api"}, {"title": "landscape"}]
        },
        {
            "id": "api_img_2",
            "description": None, 
            "alt_description": "API Alt Text 2",
            "urls": {"regular": "http://example.com/api_img_2.jpg"},
            "tags": [{"title": "api"}, {"title": "portrait"}]
        }
    ]
})
MOCK_UNSPLASH_API_EMPTY_RESPONSE = json.dumps({"results": []})

# --- Mock Unsplash HTML Scrape Responses ---
MOCK_UNSPLASH_HTML_WITH_NEXT_DATA = """
<html><body><script id="__NEXT_DATA__" type="application/json">{ "props": { "pageProps": { "results": [ { "id": "scrape_json_1", "alt_description": "Scraped JSON Alt Text 1", "urls": {"regular": "http://example.com/scrape_json_1.jpg"}, "tags": [{"title": "scraped"}, {"title": "json"}] } ] } } }</script></body></html>
"""
MOCK_UNSPLASH_HTML_WITH_IMG_TAGS = """
<html><body><img src="https://images.unsplash.com/photo-123?ixlib=rb-1.2.1&q=80&fm=jpg" alt="Scraped Img Alt 1"><img src="https://images.unsplash.com/photo-456?ixlib=rb-1.2.1&q=80&fm=jpg" alt="Scraped Img Alt 2"></body></html>
"""
MOCK_UNSPLASH_HTML_NO_MATCHES = "<html><body><p>No relevant images found here.</p></body></html>"
MOCK_API_ERROR_RESPONSE = "Error: API unavailable or rate limit exceeded."


# --- Test Cases ---

@patch('actions.gather_inspiration.view_text_website')
@patch('frontend_trend_builder.actions.gather_inspiration.UNSPLASH_API_KEY', 'DUMMY_KEY_FOR_TESTING')
def test_api_call_success_with_key_from_config(mock_view_text_website):
    """Test API call success when UNSPLASH_API_KEY is patched from config."""
    mock_view_text_website.return_value = MOCK_UNSPLASH_API_SUCCESS_RESPONSE
    
    result = gather_inspiration.get_inspiration("landscape")
    
    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0]["id"] == "unsplash_api_api_img_1"
    assert result[0]["source"] == "Unsplash_API"
    mock_view_text_website.assert_called_once()
    print("test_api_call_success_with_key_from_config PASSED")


@patch('actions.gather_inspiration.view_text_website')
@patch('frontend_trend_builder.actions.gather_inspiration.UNSPLASH_API_KEY', 'DUMMY_KEY_FOR_TESTING')
def test_api_failure_scrape_failure_mock_with_key_from_config(mock_view_text_website):
    """Test API failure, scrape failure, then mock, when key is from config."""
    mock_view_text_website.side_effect = [MOCK_API_ERROR_RESPONSE, MOCK_API_ERROR_RESPONSE]
    
    result = gather_inspiration.get_inspiration("minimalist portfolio") 
    
    assert isinstance(result, list)
    assert len(result) > 0 
    assert result[0]["source"] != "Unsplash_API" and result[0]["source"] != "Unsplash_HTML_Img_Scrape"
    assert any(item["id"] == "mock2" or item["id"] == "mock7" for item in result)
    assert mock_view_text_website.call_count == 2
    print("test_api_failure_scrape_failure_mock_with_key_from_config PASSED")


@patch('actions.gather_inspiration.view_text_website')
@patch('frontend_trend_builder.actions.gather_inspiration.UNSPLASH_API_KEY', None) # Simulate no key from config
def test_html_scrape_next_data_success_no_key(mock_view_text_website):
    """Test HTML __NEXT_DATA__ scrape success when key is None from config."""
    mock_view_text_website.return_value = MOCK_UNSPLASH_HTML_WITH_NEXT_DATA
    
    result = gather_inspiration.get_inspiration("any prompt")
    
    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0]["id"] == "unsplash_scrape_json_scrape_json_1"
    assert result[0]["source"] == "Unsplash_JSON_Scrape"
    mock_view_text_website.assert_called_once() 
    print("test_html_scrape_next_data_success_no_key PASSED")


@patch('actions.gather_inspiration.view_text_website')
@patch('frontend_trend_builder.actions.gather_inspiration.UNSPLASH_API_KEY', None)
def test_html_scrape_img_tags_success_no_key(mock_view_text_website):
    """Test HTML img tag scrape success when key is None and __NEXT_DATA__ fails."""
    # Simulate that the HTML content does not yield results for __NEXT_DATA__ but has img tags
    mock_view_text_website.return_value = MOCK_UNSPLASH_HTML_WITH_IMG_TAGS 
                                         # (and internally, _fetch_from_unsplash_scrape will try JSON parse first)
    
    result = gather_inspiration.get_inspiration("any prompt")
    
    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0]["id"] == "unsplash_scrape_img_0"
    assert result[0]["source"] == "Unsplash_HTML_Img_Scrape"
    mock_view_text_website.assert_called_once()
    print("test_html_scrape_img_tags_success_no_key PASSED")

@patch('actions.gather_inspiration.view_text_website')
@patch('frontend_trend_builder.actions.gather_inspiration.UNSPLASH_API_KEY', None)
def test_html_scrape_failure_then_mock_no_key(mock_view_text_website):
    """Test HTML scrape failure, then mock data, when key is None from config."""
    mock_view_text_website.return_value = MOCK_UNSPLASH_HTML_NO_MATCHES
    
    result = gather_inspiration.get_inspiration("minimalist portfolio") 
    
    assert isinstance(result, list)
    assert len(result) > 0
    assert result[0]["source"] != "Unsplash_API" and result[0]["source"] != "Unsplash_HTML_Img_Scrape"
    assert any(item["id"] == "mock2" or item["id"] == "mock7" for item in result)
    mock_view_text_website.assert_called_once()
    print("test_html_scrape_failure_then_mock_no_key PASSED")


# Test mock data paths explicitly when no API/Scraping attempts are expected to succeed
@patch('actions.gather_inspiration.view_text_website') # Still need to mock this as it's called by scrape path
@patch('frontend_trend_builder.actions.gather_inspiration.UNSPLASH_API_KEY', None)
def test_get_inspiration_mock_data_with_matches_no_key(mock_view_text_website):
    mock_view_text_website.return_value = MOCK_UNSPLASH_HTML_NO_MATCHES # Ensure scrape fails
    
    prompt = "glassmorphic crypto login" 
    result = gather_inspiration.get_inspiration(prompt)
    
    assert isinstance(result, list)
    assert len(result) >= 2
    found_ids = [item["id"] for item in result]
    assert "mock1" in found_ids and "mock6" in found_ids
    assert all(item["source"] != "Unsplash_API" for item in result)
    print("test_get_inspiration_mock_data_with_matches_no_key PASSED")

@patch('actions.gather_inspiration.view_text_website')
@patch('frontend_trend_builder.actions.gather_inspiration.UNSPLASH_API_KEY', None)
def test_get_inspiration_mock_data_no_matches_no_key(mock_view_text_website):
    mock_view_text_website.return_value = MOCK_UNSPLASH_HTML_NO_MATCHES
        
    prompt = "zyxw_unmatchable_keyword_12345"
    result = gather_inspiration.get_inspiration(prompt)
        
    assert isinstance(result, str)
    assert "No specific inspiration found in mock data" in result
    print("test_get_inspiration_mock_data_no_matches_no_key PASSED")

# Original test_get_inspiration_data_file_issues can remain as is.
# It tests file system errors for mock data, independent of API key logic.
def test_get_inspiration_data_file_issues():
    """
    Tests error handling if the mock data file is missing or corrupt.
    This requires temporarily altering the path or file.
    """
    original_mock_path = gather_inspiration.DATA_FILE_PATH
    
    # Test FileNotFoundError
    gather_inspiration.DATA_FILE_PATH = "non_existent_mock_data_file.json"
    # Patch API key and view_text_website to ensure we reach mock data loading attempt
    with patch('frontend_trend_builder.actions.gather_inspiration.UNSPLASH_API_KEY', None), \
         patch('actions.gather_inspiration.view_text_website', return_value=MOCK_UNSPLASH_HTML_NO_MATCHES):
        result_not_found = gather_inspiration.get_inspiration("test")
    assert isinstance(result_not_found, str)
    assert "Error: Mock inspiration data file not found" in result_not_found
    print("test_get_inspiration_data_file_not_found PASSED")

    # Test JSONDecodeError
    temp_malformed_file = os.path.join(os.path.dirname(original_mock_path), "temp_malformed_mock.json")
    with open(temp_malformed_file, 'w') as f:
        f.write("{'invalid_json': ") 
    
    gather_inspiration.DATA_FILE_PATH = temp_malformed_file
    with patch('frontend_trend_builder.actions.gather_inspiration.UNSPLASH_API_KEY', None), \
         patch('actions.gather_inspiration.view_text_website', return_value=MOCK_UNSPLASH_HTML_NO_MATCHES):
        result_decode_error = gather_inspiration.get_inspiration("test")
    assert isinstance(result_decode_error, str)
    assert "Error: Could not decode mock inspiration data" in result_decode_error
    print("test_get_inspiration_data_file_decode_error PASSED")
    
    os.remove(temp_malformed_file) 
    gather_inspiration.DATA_FILE_PATH = original_mock_path 
    print("test_get_inspiration_data_file_issues (overall) PASSED")


if __name__ == "__main__":
    print("--- Running test_gather_inspiration.py (with config mocks) ---")
    test_api_call_success_with_key_from_config()
    test_api_failure_scrape_failure_mock_with_key_from_config()
    test_html_scrape_next_data_success_no_key()
    test_html_scrape_img_tags_success_no_key()
    test_html_scrape_failure_then_mock_no_key()
    
    test_get_inspiration_mock_data_with_matches_no_key()
    test_get_inspiration_mock_data_no_matches_no_key()
    test_get_inspiration_data_file_issues()
    
    print("--- All gather_inspiration tests (with config mocks) completed ---")
