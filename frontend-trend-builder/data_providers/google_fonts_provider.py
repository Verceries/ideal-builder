import logging
import json
from typing import List, Dict, Optional

from ..config import GOOGLE_FONTS_API_KEY # Adjusted import path
from .http_client import fetch_url_text, DataProviderError

logger = logging.getLogger(__name__)

# Store the placeholder to check against
CONFIG_GOOGLE_FONTS_KEY_PLACEHOLDER = "YOUR_GOOGLE_FONTS_API_KEY_HERE" # Or whatever was in .env.example


def _parse_google_fonts_api_response(json_string: str, category_filter: Optional[str] = None) -> List[Dict]:
    """Parses the JSON response from Google Fonts API."""
    fonts = []
    try:
        data = json.loads(json_string)
        font_items = data.get("items", [])
        
        for item in font_items:
            family = item.get("family")
            category = item.get("category")
            
            if family and category:
                # If the API call itself included a category filter, this client-side filter
                # might be redundant but acts as a safeguard or for broader queries.
                if category_filter and category_filter != category:
                    continue 
                
                fonts.append({
                    "type": "font",
                    "name": family,
                    "category": category, # Store the category from API
                    "source": "GoogleFonts_API"
                })
        # The API sorts by popularity by default if `sort=popularity` is used.
        # If we fetched a large list and needed to limit, we could slice here, e.g., fonts = fonts[:desired_limit]
    except json.JSONDecodeError:
        logger.exception("Failed to decode JSON from Google Fonts API response.") # Use .exception
    except Exception: # Catch any other exception during parsing
        logger.exception(f"Error parsing Google Fonts API response.") 
    return fonts

def fetch_google_fonts(category: Optional[str] = None, sort_by: str = "popularity") -> List[Dict]:
    """
    Fetches font suggestions from Google Fonts API if key is available.
    Can filter by category (e.g., "serif", "sans-serif") and sort.
    Returns a list of font items or an empty list.
    """
    if not GOOGLE_FONTS_API_KEY or GOOGLE_FONTS_API_KEY == CONFIG_GOOGLE_FONTS_KEY_PLACEHOLDER:
        logger.info("Google Fonts API key not configured or is placeholder. API call will be skipped.")
        return []

    api_url = f"https://www.googleapis.com/webfonts/v1/webfonts?key={GOOGLE_FONTS_API_KEY}"
    if sort_by:
        api_url += f"&sort={sort_by}"
    
    # According to Google Fonts API documentation, category filtering is supported.
    # Example: https://developers.google.com/fonts/docs/developer_api#Querying_for_Font_Families
    # It lists `category` as a request parameter.
    if category:
        api_url += f"&category={category}"

    try:
        logger.info(f"Attempting Google Fonts API call. Category: '{category or 'all'}', Sort: '{sort_by}', URL: {api_url}")
        json_string = fetch_url_text(api_url)
        if json_string:
            # Since the API is queried with a category, we don't need to re-filter in the parser.
            # Pass category_filter=None to _parse_google_fonts_api_response.
            return _parse_google_fonts_api_response(json_string, category_filter=None)
    except DataProviderError as e:
        logger.warning(f"Google Fonts API call failed: {e}")
    return []

if __name__ == '__main__':
    # Basic logging setup for standalone execution
    # This ensures logs are visible if this script is run directly,
    # independent of whether main.py (which also sets up logging) is run.
    if not logging.getLogger().hasHandlers() or logging.getLogger().level > logging.DEBUG:
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
    
    logger.info("--- Testing google_fonts_provider.py ---")

    # This global mock for view_text_website is for standalone testing of this script.
    # It simulates the behavior of the actual tool.
    
    # Global state for mock_view_text_website to control API responses for tests
    _mock_api_configs = {} 

    if 'view_text_website' not in globals():
        def view_text_website(url: str) -> Optional[str]:
            global _mock_api_configs
            logger.debug(f"[Local Mock] view_text_website called for URL: {url}. Current mock config: {_mock_api_configs}")

            if "googleapis.com/webfonts/v1/webfonts" in url:
                # Simulate key check behavior of the actual fetch_google_fonts function
                # This check is done *before* fetch_url_text is called in the real function.
                # So, if the key is bad, fetch_url_text (and thus this mock) shouldn't even be called.
                # However, for testing the provider's internal call to fetch_url_text, we can simulate errors here.

                if _mock_api_configs.get("force_error"):
                    logger.warning("[Local Mock] Simulating forced API error.")
                    raise DataProviderError("Mock API Error: Forced error for testing.")
                
                if _mock_api_configs.get("return_empty_items"):
                    logger.info("[Local Mock] Simulating API returning empty list of items.")
                    return json.dumps({"kind": "webfonts#webfontList", "items": []})

                # Default mock response if no specific config matches
                mock_items = []
                # Determine category from URL for more dynamic mocking if needed
                url_category = None
                if "category=" in url:
                    try:
                        url_category = url.split("category=")[1].split("&")[0]
                    except IndexError:
                        pass
                
                logger.info(f"[Local Mock] Detected category from URL: {url_category}")

                if url_category == "serif" or not url_category: # also provide if no category (general query)
                    mock_items.extend([
                        {"family": "Mock Serif 1", "category": "serif", "variants": ["regular", "italic", "700"], "subsets": ["latin"], "version": "v1", "lastModified": "2023-01-01", "files": {"regular": "http://example.com/mockserif1.ttf"}},
                        {"family": "Mock Serif 2", "category": "serif", "variants": ["regular"], "subsets": ["latin"], "version": "v1", "lastModified": "2023-01-01", "files": {"regular": "http://example.com/mockserif2.ttf"}}
                    ])
                if url_category == "sans-serif" or not url_category:
                     mock_items.extend([
                        {"family": "Mock Sans-Serif 1", "category": "sans-serif", "variants": ["regular", "italic", "700"], "subsets": ["latin"], "version": "v1", "lastModified": "2023-01-01", "files": {"regular": "http://example.com/mocksans1.ttf"}},
                        {"family": "Mock Sans-Serif 2", "category": "sans-serif", "variants": ["regular"], "subsets": ["latin"], "version": "v1", "lastModified": "2023-01-01", "files": {"regular": "http://example.com/mocksans2.ttf"}}
                    ])
                if url_category == "display" or not url_category:
                     mock_items.extend([
                        {"family": "Mock Display", "category": "display", "variants": ["regular"], "subsets": ["latin"], "version": "v1", "lastModified": "2023-01-01", "files": {"regular": "http://example.com/mockdisplay.ttf"}}
                     ])
                if url_category == "handwriting" or not url_category: # Added for future tests
                     mock_items.extend([
                        {"family": "Mock Handwriting", "category": "handwriting", "variants": ["regular"], "subsets": ["latin"], "version": "v1", "lastModified": "2023-01-01", "files": {"regular": "http://example.com/mockhandwriting.ttf"}}
                     ])
                
                # Filter by the specific category requested if the mock has it, otherwise the parser will handle it.
                # The actual API does filtering server-side.
                # This mock simply provides a broad set if no category, or specific if category matches.
                
                final_mock_items = []
                if url_category:
                    final_mock_items = [item for item in mock_items if item["category"] == url_category]
                else: # if no category in url, return all for general popularity sort
                    final_mock_items = mock_items

                logger.info(f"[Local Mock] Returning {len(final_mock_items)} items for category '{url_category or 'any'}'.")
                return json.dumps({"kind": "webfonts#webfontList", "items": final_mock_items[:5]}) # Limit items

            logger.error(f"[Local Mock] Unhandled URL: {url}")
            return None

    # Backup original API key and mock config
    original_key_for_tests = GOOGLE_FONTS_API_KEY
    original_mock_api_configs = _mock_api_configs.copy()

    def set_test_conditions(api_key_value, mock_config=None):
        """Helper to set API key and mock configuration for a test."""
        global GOOGLE_FONTS_API_KEY, _mock_api_configs
        GOOGLE_FONTS_API_KEY = api_key_value
        _mock_api_configs = mock_config if mock_config is not None else {}

    # Test 1: Valid key, fetch serif fonts
    logger.info("\n--- Test 1: Valid key, Fetch serif fonts ---")
    set_test_conditions("DUMMY_VALID_KEY")
    results_serif = fetch_google_fonts(category="serif")
    assert results_serif and all(f['category'] == 'serif' for f in results_serif), "Test 1 Failed: Serif fonts not fetched correctly."
    logger.info(f"Test 1 OK: Fetched {len(results_serif)} serif fonts: {json.dumps(results_serif, indent=2)}")

    # Test 2: Valid key, fetch all popular fonts (no category)
    logger.info("\n--- Test 2: Valid key, Fetch all popular fonts ---")
    set_test_conditions("DUMMY_VALID_KEY")
    results_all_popular = fetch_google_fonts(sort_by="popularity")
    assert results_all_popular and len(results_all_popular) > 0, "Test 2 Failed: Popular fonts not fetched."
    # Check if it contains a mix of categories as per mock
    categories_in_results = {f['category'] for f in results_all_popular}
    assert "serif" in categories_in_results and "sans-serif" in categories_in_results, "Test 2 Failed: Expected multiple categories."
    logger.info(f"Test 2 OK: Fetched {len(results_all_popular)} popular fonts with mixed categories.")

    # Test 3: API key is placeholder
    logger.info("\n--- Test 3: API key is placeholder ---")
    set_test_conditions(CONFIG_GOOGLE_FONTS_KEY_PLACEHOLDER)
    results_placeholder = fetch_google_fonts(category="serif")
    assert results_placeholder == [], f"Test 3 Failed: Expected empty list for placeholder key, got {results_placeholder}"
    logger.info("Test 3 OK: Correctly returned empty list for placeholder key.")

    # Test 4: API key is None
    logger.info("\n--- Test 4: API key is None ---")
    set_test_conditions(None)
    results_none_key = fetch_google_fonts(category="serif")
    assert results_none_key == [], f"Test 4 Failed: Expected empty list for None key, got {results_none_key}"
    logger.info("Test 4 OK: Correctly returned empty list for None key.")

    # Test 5: Valid key, but API returns an error (simulated)
    logger.info("\n--- Test 5: Valid key, API returns error ---")
    set_test_conditions("DUMMY_VALID_KEY", mock_config={"force_error": True})
    results_api_error = fetch_google_fonts(category="serif")
    assert results_api_error == [], f"Test 5 Failed: Expected empty list on API error, got {results_api_error}"
    logger.info("Test 5 OK: Correctly returned empty list on simulated API error.")

    # Test 6: Valid key, but API returns no items for a valid query
    logger.info("\n--- Test 6: Valid key, API returns no items ---")
    set_test_conditions("DUMMY_VALID_KEY", mock_config={"return_empty_items": True})
    results_empty_items = fetch_google_fonts(category="serif")
    assert results_empty_items == [], f"Test 6 Failed: Expected empty list when API returns no items, got {results_empty_items}"
    logger.info("Test 6 OK: Correctly returned empty list when API returns no items.")
    
    # Test 7: Valid key, fetch for a category that mock might not have explicitly, ensure it's empty or parser handles it.
    logger.info("\n--- Test 7: Valid key, Fetch 'monospace' fonts (mock may not have this category explicitly) ---")
    set_test_conditions("DUMMY_VALID_KEY") # Mock returns specific categories or all if no category given.
                                       # If "monospace" is requested, mock returns empty for that category.
    results_monospace = fetch_google_fonts(category="monospace")
    # The mock for view_text_website, if category is specified, filters by it. If 'monospace' is not in mock_items, it will be empty.
    assert results_monospace == [], f"Test 7 Failed: Expected empty list for 'monospace' if not in mock, got {results_monospace}"
    logger.info(f"Test 7 OK: Fetched {len(results_monospace)} monospace fonts (expected empty if not in specific mock).")


    # Restore original API key and mock config
    GOOGLE_FONTS_API_KEY = original_key_for_tests
    _mock_api_configs = original_mock_api_configs

    logger.info("--- End of google_fonts_provider.py tests ---")
