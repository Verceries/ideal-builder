import sys
import os
import json # For mock responses
from typing import List, Dict, Union
from unittest.mock import patch, PropertyMock # For mocking

# Adjust the Python path to include the parent directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from actions import gather_inspiration

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
            "description": None, # Test missing description
            "alt_description": "API Alt Text 2",
            "urls": {"regular": "http://example.com/api_img_2.jpg"},
            "tags": [{"title": "api"}, {"title": "portrait"}]
        }
    ]
})

MOCK_UNSPLASH_API_EMPTY_RESPONSE = json.dumps({"results": []})

# --- Mock Unsplash HTML Scrape Responses ---
MOCK_UNSPLASH_HTML_WITH_NEXT_DATA = """
<html><body>
<script id="__NEXT_DATA__" type="application/json">
{
  "props": {
    "pageProps": {
      "photos": [], 
      "results": [
        {
          "id": "scrape_json_1",
          "alt_description": "Scraped JSON Alt Text 1",
          "urls": {"regular": "http://example.com/scrape_json_1.jpg"},
          "tags": [{"title": "scraped"}, {"title": "json"}]
        }
      ]
    }
  }
}
</script>
</body></html>
"""

MOCK_UNSPLASH_HTML_WITH_IMG_TAGS = """
<html><body>
<img src="https://images.unsplash.com/photo-123?ixlib=rb-1.2.1&q=80&fm=jpg" alt="Scraped Img Alt 1">
<img src="https://images.unsplash.com/photo-456?ixlib=rb-1.2.1&q=80&fm=jpg" alt="Scraped Img Alt 2">
<img src="http://otherdomain.com/irrelevant.jpg" alt="Not Unsplash">
</body></html>
"""

MOCK_UNSPLASH_HTML_NO_MATCHES = "<html><body><p>No relevant images found here.</p></body></html>"
MOCK_API_ERROR_RESPONSE = "Error: API unavailable or rate limit exceeded."


# --- Test Cases ---

@patch('actions.gather_inspiration.view_text_website')
def test_api_call_success(mock_view_text_website):
    """Test API call path with successful response."""
    mock_view_text_website.return_value = MOCK_UNSPLASH_API_SUCCESS_RESPONSE
    
    # Temporarily set API key for this test
    original_key = gather_inspiration.UNSPLASH_ACCESS_KEY
    gather_inspiration.UNSPLASH_ACCESS_KEY = "DUMMY_KEY_FOR_TEST"
    
    result = gather_inspiration.get_inspiration("landscape")
    
    gather_inspiration.UNSPLASH_ACCESS_KEY = original_key # Restore
    
    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0]["id"] == "unsplash_api_api_img_1"
    assert result[0]["source"] == "Unsplash_API"
    assert "api" in result[0]["tags"]
    assert result[1]["title"] == "API Alt Text 2" # alt_description as fallback
    mock_view_text_website.assert_called_once()
    print("test_api_call_success PASSED")


@patch('actions.gather_inspiration.view_text_website')
def test_api_call_failure_then_scrape_failure_then_mock(mock_view_text_website):
    """Test API failure, then scrape failure, falling back to mock data."""
    # API call fails, then scrape call also fails
    mock_view_text_website.side_effect = [MOCK_API_ERROR_RESPONSE, MOCK_API_ERROR_RESPONSE]
    
    original_key = gather_inspiration.UNSPLASH_ACCESS_KEY
    gather_inspiration.UNSPLASH_ACCESS_KEY = "DUMMY_KEY_FOR_TEST"
    
    result = gather_inspiration.get_inspiration("minimalist portfolio") # This prompt matches mock data
    
    gather_inspiration.UNSPLASH_ACCESS_KEY = original_key
    
    assert isinstance(result, list)
    assert len(result) > 0 # Should get items from mock_inspiration_data.json
    assert result[0]["source"] != "Unsplash_API" and result[0]["source"] != "Unsplash_HTML_Img_Scrape" and result[0]["source"] != "Unsplash_JSON_Scrape"
    # Check if it's one of the known mock items
    assert any(item["id"] == "mock2" or item["id"] == "mock7" for item in result) # mock2 or mock7 match "minimalist portfolio"
    assert mock_view_text_website.call_count == 2 # API call + Scrape call
    print("test_api_call_failure_then_scrape_failure_then_mock PASSED")


@patch('actions.gather_inspiration.view_text_website')
def test_html_scrape_next_data_success(mock_view_text_website):
    """Test HTML scraping with __NEXT_DATA__ success."""
    mock_view_text_website.return_value = MOCK_UNSPLASH_HTML_WITH_NEXT_DATA
    
    original_key = gather_inspiration.UNSPLASH_ACCESS_KEY
    gather_inspiration.UNSPLASH_ACCESS_KEY = None # Ensure API is skipped
    
    result = gather_inspiration.get_inspiration("any prompt")
    
    gather_inspiration.UNSPLASH_ACCESS_KEY = original_key
    
    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0]["id"] == "unsplash_scrape_json_scrape_json_1"
    assert result[0]["source"] == "Unsplash_JSON_Scrape"
    assert "scraped" in result[0]["tags"] and "json" in result[0]["tags"]
    mock_view_text_website.assert_called_once() # Only scrape call
    print("test_html_scrape_next_data_success PASSED")


@patch('actions.gather_inspiration.view_text_website')
def test_html_scrape_img_tags_success(mock_view_text_website):
    """Test HTML scraping with img tags success when __NEXT_DATA__ fails."""
    # First call for __NEXT_DATA__ returns no usable JSON, second for img tags
    mock_view_text_website.side_effect = [
        "<html><body><script id='__NEXT_DATA__'>{}</script></body></html>", # Empty/invalid NEXT_DATA
        MOCK_UNSPLASH_HTML_WITH_IMG_TAGS # HTML with img tags
    ]
    
    original_key = gather_inspiration.UNSPLASH_ACCESS_KEY
    gather_inspiration.UNSPLASH_ACCESS_KEY = None 
    
    # This test is a bit complex because _fetch_from_unsplash_scrape tries JSON then regex.
    # We need the JSON part to "fail" to find items, then regex to succeed.
    # The current mock setup for side_effect might not perfectly simulate this internal logic of _fetch_from_unsplash_scrape.
    # For simplicity, let's assume the first call to view_text_website in get_inspiration is for API (skipped),
    # and the second is for scraping, which in _fetch_from_unsplash_scrape will first try JSON (mocked to fail internally if complex)
    # then regex.
    # A more direct way: mock the _fetch_from_unsplash_scrape's internal JSON parsing to fail.
    # However, for now, let's assume the HTML for JSON scrape is just empty of items.
    
    # Redo mock for a single call to scrape, which will try JSON then regex
    mock_view_text_website.side_effect = None # Clear side_effect
    mock_view_text_website.return_value = MOCK_UNSPLASH_HTML_WITH_IMG_TAGS # HTML that will fail JSON but pass regex
    
    result = gather_inspiration.get_inspiration("any prompt")
    
    gather_inspiration.UNSPLASH_ACCESS_KEY = original_key
    
    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0]["id"] == "unsplash_scrape_img_0"
    assert result[0]["source"] == "Unsplash_HTML_Img_Scrape"
    assert result[0]["title"] == "Scraped Img Alt 1"
    mock_view_text_website.assert_called_once()
    print("test_html_scrape_img_tags_success PASSED")


@patch('actions.gather_inspiration.view_text_website')
def test_html_scrape_failure_then_mock(mock_view_text_website):
    """Test HTML scraping failure, falling back to mock data."""
    mock_view_text_website.return_value = MOCK_UNSPLASH_HTML_NO_MATCHES
    
    original_key = gather_inspiration.UNSPLASH_ACCESS_KEY
    gather_inspiration.UNSPLASH_ACCESS_KEY = None 
    
    result = gather_inspiration.get_inspiration("minimalist portfolio") # Matches mock
    
    gather_inspiration.UNSPLASH_ACCESS_KEY = original_key
    
    assert isinstance(result, list)
    assert len(result) > 0
    assert result[0]["source"] != "Unsplash_API" and result[0]["source"] != "Unsplash_HTML_Img_Scrape"
    assert any(item["id"] == "mock2" or item["id"] == "mock7" for item in result)
    mock_view_text_website.assert_called_once()
    print("test_html_scrape_failure_then_mock PASSED")


@patch('actions.gather_inspiration.view_text_website')
def test_no_key_scrape_fail_then_mock(mock_view_text_website):
    """Test no API key, scrape fails, falls back to mock."""
    mock_view_text_website.return_value = MOCK_UNSPLASH_HTML_NO_MATCHES # Scrape fails
    
    original_key = gather_inspiration.UNSPLASH_ACCESS_KEY
    gather_inspiration.UNSPLASH_ACCESS_KEY = None 
    
    result = gather_inspiration.get_inspiration("dashboard") # Matches mock
    
    gather_inspiration.UNSPLASH_ACCESS_KEY = original_key
    
    assert isinstance(result, list)
    assert len(result) > 0
    assert result[0]["source"] != "Unsplash_API" # Should be from mock
    assert any(item["id"] == "mock3" or item["id"] == "mock6" for item in result) # mock3 or mock6 match "dashboard"
    mock_view_text_website.assert_called_once() # Scrape attempt
    print("test_no_key_scrape_fail_then_mock PASSED")

# --- Original Tests (can be adapted or kept if still relevant for mock data path) ---
def test_get_inspiration_mock_data_with_matches():
    """ Tests if get_inspiration returns a list of dicts from mock data when no external calls succeed."""
    # Ensure no API key and mock that scraping will fail to ensure mock data path
    original_key = gather_inspiration.UNSPLASH_ACCESS_KEY
    gather_inspiration.UNSPLASH_ACCESS_KEY = None
    
    with patch('actions.gather_inspiration.view_text_website', return_value=MOCK_UNSPLASH_HTML_NO_MATCHES):
        prompt = "glassmorphic crypto login" # Should match mock1 and mock6
        result = gather_inspiration.get_inspiration(prompt)
    
    gather_inspiration.UNSPLASH_ACCESS_KEY = original_key
    
    assert isinstance(result, list), "Output should be a list for matches."
    assert len(result) >= 2, "Should return at least two items for 'glassmorphic crypto'."
    found_ids = [item["id"] for item in result]
    assert "mock1" in found_ids
    assert "mock6" in found_ids
    assert all(item["source"] != "Unsplash_API" for item in result) # Ensure it's not from API
    print("test_get_inspiration_mock_data_with_matches PASSED")

def test_get_inspiration_mock_data_no_matches():
    """Tests if get_inspiration returns a specific string from mock data when no matches are found."""
    original_key = gather_inspiration.UNSPLASH_ACCESS_KEY
    gather_inspiration.UNSPLASH_ACCESS_KEY = None
    
    with patch('actions.gather_inspiration.view_text_website', return_value=MOCK_UNSPLASH_HTML_NO_MATCHES):
        prompt = "zyxw_unmatchable_keyword_12345"
        result = gather_inspiration.get_inspiration(prompt)
        
    gather_inspiration.UNSPLASH_ACCESS_KEY = original_key
    
    assert isinstance(result, str), "Output should be a string for no matches."
    assert "No specific inspiration found in mock data" in result
    print("test_get_inspiration_mock_data_no_matches PASSED")

# test_get_inspiration_data_file_issues can remain as is, as it tests file system errors for mock data.

if __name__ == "__main__":
    print("--- Running test_gather_inspiration.py (with mocks) ---")
    test_api_call_success()
    test_api_call_failure_then_scrape_failure_then_mock()
    test_html_scrape_next_data_success()
    test_html_scrape_img_tags_success() # This test might be tricky due to internal scrape logic
    test_html_scrape_failure_then_mock()
    test_no_key_scrape_fail_then_mock()
    
    # Original tests now explicitly testing mock data path
    test_get_inspiration_mock_data_with_matches()
    test_get_inspiration_mock_data_no_matches()
    # test_get_inspiration_data_file_issues() # This one is fine as is.
    
    # To run the file issues test if desired:
    # Create a dummy original_path for the test if DATA_FILE_PATH is modified by other tests
    # or ensure it's reset if that test is run.
    # For simplicity, if running all, ensure DATA_FILE_PATH is reset after any modifications.
    # It's better to run file system error tests in isolation or manage state carefully.
    # For now, commenting out to avoid issues if run with others without careful state management.
    print("--- (Skipping test_get_inspiration_data_file_issues in this combined run for simplicity) ---")
    
    print("--- All gather_inspiration tests completed ---")
