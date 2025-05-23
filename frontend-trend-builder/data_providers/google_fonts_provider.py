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
    if 'view_text_website' not in globals():
        def view_text_website(url: str) -> Optional[str]:
            logger.debug(f"[Local Mock] view_text_website called for URL: {url}")
            if "googleapis.com/webfonts/v1/webfonts" in url:
                # Simulate key check behavior of the actual fetch_google_fonts function
                if not GOOGLE_FONTS_API_KEY or GOOGLE_FONTS_API_KEY == CONFIG_GOOGLE_FONTS_KEY_PLACEHOLDER:
                    logger.warning("[Local Mock] Google Fonts API key is placeholder or not set. Simulating API error/no call.")
                    # In reality, fetch_google_fonts would skip the call. Here, we simulate fetch_url_text returning None or error.
                    raise DataProviderError("Mock API Key Error: Key is placeholder or not set for this test.")

                mock_items = []
                if "category=serif" in url or ("sort=popularity" in url and "category=" not in url):
                    mock_items.extend([
                        {"family": "Lora", "category": "serif"},
                        {"family": "Merriweather", "category": "serif"}
                    ])
                if "category=sans-serif" in url or ("sort=popularity" in url and "category=" not in url):
                     mock_items.extend([
                        {"family": "Roboto", "category": "sans-serif"},
                        {"family": "Open Sans", "category": "sans-serif"}
                    ])
                # If no category specified, and sort=popularity, return a mix for testing _parse_google_fonts_api_response's own filtering
                if "category=" not in url and "sort=popularity" in url :
                     mock_items.extend([
                        {"family": "Display Font", "category": "display"}, # Add one non-matching for parse filter test
                     ])

                return json.dumps({"kind": "webfonts#webfontList", "items": mock_items[:5]}) # Limit items
            logger.error(f"[Local Mock] Unhandled URL: {url}")
            return None

    # Test 1: API call for serif fonts (simulating key is set)
    logger.info("\n--- Test 1: Fetch serif fonts via API (simulating valid key) ---")
    # Temporarily modify the global GOOGLE_FONTS_API_KEY for this test block
    # This approach is okay for __main__ but unittest.mock.patch is better for formal tests.
    original_key_state = GOOGLE_FONTS_API_KEY
    globals()['GOOGLE_FONTS_API_KEY'] = "DUMMY_VALID_KEY_FOR_TEST_IN_MAIN" 
    
    results_serif = fetch_google_fonts(category="serif")
    if results_serif:
        logger.info(f"Serif font results: {json.dumps(results_serif, indent=2)}")
        assert all(f['category'] == 'serif' for f in results_serif), "All fetched fonts should be serif"
    else:
        logger.info("API call (serif) did not return results (check mock or key).")
    
    globals()['GOOGLE_FONTS_API_KEY'] = original_key_state # Restore

    # Test 2: API call for sans-serif fonts (simulating key is set)
    logger.info("\n--- Test 2: Fetch sans-serif fonts via API (simulating valid key) ---")
    original_key_state = GOOGLE_FONTS_API_KEY
    globals()['GOOGLE_FONTS_API_KEY'] = "DUMMY_VALID_KEY_FOR_TEST_IN_MAIN"
    
    results_sans_serif = fetch_google_fonts(category="sans-serif")
    if results_sans_serif:
        logger.info(f"Sans-serif font results: {json.dumps(results_sans_serif, indent=2)}")
        assert all(f['category'] == 'sans-serif' for f in results_sans_serif), "All fetched fonts should be sans-serif"
    else:
        logger.info("API call (sans-serif) did not return results (check mock or key).")
        
    globals()['GOOGLE_FONTS_API_KEY'] = original_key_state

    # Test 3: API call (simulating key is placeholder/None)
    logger.info("\n--- Test 3: Fetch via API (simulating key as placeholder) ---")
    original_key_state = GOOGLE_FONTS_API_KEY
    globals()['GOOGLE_FONTS_API_KEY'] = CONFIG_GOOGLE_FONTS_KEY_PLACEHOLDER 
    
    results_no_key = fetch_google_fonts(category="serif")
    if not results_no_key:
        logger.info("API call correctly returned no results due to placeholder key.")
    else:
        logger.error(f"API call unexpectedly returned results with placeholder key: {results_no_key}")
        
    globals()['GOOGLE_FONTS_API_KEY'] = original_key_state
    
    # Test 4: API call for all popular fonts (simulating key is set)
    logger.info("\n--- Test 4: Fetch all popular fonts via API (simulating valid key) ---")
    original_key_state = GOOGLE_FONTS_API_KEY
    globals()['GOOGLE_FONTS_API_KEY'] = "DUMMY_VALID_KEY_FOR_TEST_IN_MAIN" 
    
    results_all_popular = fetch_google_fonts(sort_by="popularity") # No category filter
    if results_all_popular:
        logger.info(f"All popular font results (first 5): {json.dumps(results_all_popular[:5], indent=2)}")
        assert len(results_all_popular) > 0 
    else:
        logger.info("API call (all popular) did not return results (check mock or key).")
        
    globals()['GOOGLE_FONTS_API_KEY'] = original_key_state

    logger.info("--- End of google_fonts_provider.py tests ---")
