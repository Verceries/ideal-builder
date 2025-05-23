import logging
import json
import re
from typing import List, Dict, Optional
from urllib.parse import quote_plus

from ..config import UNSPLASH_API_KEY # Adjusted import path
from .http_client import fetch_url_text, DataProviderError

logger = logging.getLogger(__name__)

# Store the placeholder to check against, to avoid using "YOUR_KEY..." as a real key
CONFIG_UNSPLASH_KEY_PLACEHOLDER = "YOUR_UNSPLASH_ACCESS_KEY_HERE" # From .env.example

_MOCK_UNSPLASH_DATA = [
    {
        "id": "unsplash_mock_1",
        "title": "Mock Image 1: Serene Landscape",
        "description": "A beautiful mock landscape image.",
        "tags": ["mock", "landscape", "nature"],
        "image_url_mock": "https://images.unsplash.com/photo-1506744038136-46273834b3fb?ixlib=rb-1.2.1&q=80&fm=jpg&crop=entropy&cs=tinysrgb&w=1080&fit=max&ixid=eyJhcHBfaWQiOjEyMDd9",
        "source": "Unsplash_Mock_Fallback"
    },
    {
        "id": "unsplash_mock_2",
        "title": "Mock Image 2: Abstract Design",
        "description": "An interesting abstract mock design.",
        "tags": ["mock", "abstract", "design"],
        "image_url_mock": "https://images.unsplash.com/photo-1550684376-efcbd6e3f031?ixlib=rb-1.2.1&q=80&fm=jpg&crop=entropy&cs=tinysrgb&w=1080&fit=max&ixid=eyJhcHBfaWQiOjEyMDd9",
        "source": "Unsplash_Mock_Fallback"
    }
]

def _parse_unsplash_api_response(json_string: str) -> List[Dict]:
    """Parses the JSON response from Unsplash API's /search/photos endpoint."""
    inspirations = []
    try:
        data = json.loads(json_string)
        results = data.get("results", [])
        for photo in results[:5]: # Limit to 5 results
            title = photo.get("alt_description") or photo.get("description", "Unsplash Image")
            photo_id = photo.get("id", "")
            tags = [tag.get("title") for tag in photo.get("tags", []) if tag.get("title")]
            image_url = photo.get("urls", {}).get("regular") or photo.get("urls", {}).get("small")
            
            if image_url:
                inspirations.append({
                    "id": f"unsplash_api_{photo_id}",
                    "title": title,
                    "description": photo.get("description", title),
                    "tags": tags,
                    "image_url_mock": image_url,
                    "source": "Unsplash_API"
                })
    except json.JSONDecodeError:
        logger.error("Failed to decode JSON from Unsplash API response.")
    except Exception as e:
        logger.exception(f"Error parsing Unsplash API response.") # Use .exception for stack trace
    return inspirations

def _parse_unsplash_html_scrape(html_content: str, prompt: str) -> List[Dict]:
    """
    Parses HTML content from Unsplash search page.
    First tries to find __NEXT_DATA__ JSON blob, then falls back to img tag regex.
    """
    inspirations = []
    
    # 1. Try to parse __NEXT_DATA__
    try:
        script_tag_content = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html_content, re.DOTALL)
        if script_tag_content:
            next_data = json.loads(script_tag_content.group(1))
            # This path is a guess and needs verification against actual Unsplash structure.
            # Common paths might be:
            # - next_data.get("props", {}).get("pageProps", {}).get("photos", [])
            # - next_data.get("props", {}).get("pageProps", {}).get("results", [])
            # - next_data.get("props", {}).get("pageProps", {}).get("initialReduxState", {}).get("entities", {}).get("photos", {}).values()
            # Using a more generic search if possible, or specific known paths.
            photos_data = [] # Initialize photos_data
            page_props = next_data.get("props", {}).get("pageProps", {})

            # Try common paths for photo data within pageProps
            if "results" in page_props and isinstance(page_props["results"], list):
                 photos_data = page_props["results"]
            elif "photos" in page_props and isinstance(page_props["photos"], list):
                 photos_data = page_props["photos"]
            elif "initialData" in page_props and isinstance(page_props["initialData"], list) and len(page_props["initialData"]) > 0:
                # Example: initialData: [ { "type": "PHOTOGRAPHY", "entities": { "photos": { "some_id": {...} } } } ]
                # This path requires more specific parsing based on actual structure.
                # For now, let's assume a simpler structure or add a placeholder for more complex parsing.
                # This is a common pattern but specific keys might vary.
                if isinstance(page_props["initialData"][0], dict):
                    entities = page_props["initialData"][0].get("entities", {})
                    if "photos" in entities and isinstance(entities["photos"], dict):
                        photos_data = list(entities["photos"].values()) # if photos are dict values
                    elif "results" in entities and isinstance(entities["results"], list): # another possible path
                        photos_data = entities["results"]

            # Add more checks here based on observed Unsplash structure
            
            if not isinstance(photos_data, list): # Ensure photos_data is iterable list after attempts
                photos_data = []


            for photo in photos_data[:5]: 
                if not isinstance(photo, dict): continue # Skip if photo data is not a dict

                photo_id = photo.get("id")
                alt_description = photo.get("alt_description") or photo.get("description", "Unsplash Image")
                img_url = photo.get("urls", {}).get("regular") or photo.get("urls", {}).get("small")
                tags_data = photo.get("tags", [])
                tags = [tag.get("title") for tag in tags_data if isinstance(tag, dict) and tag.get("title")]


                if photo_id and alt_description and img_url:
                    inspirations.append({
                        "id": f"unsplash_scrape_{photo_id}", # Unified ID prefix
                        "title": alt_description,
                        "description": alt_description, # Use alt_description for description as well
                        "tags": tags if tags else [t.lower() for t in alt_description.split()[:3] if t],
                        "image_url_mock": img_url,
                        "source": "Unsplash_Scrape" # Unified source
                    })
            if inspirations:
                logger.info(f"Successfully parsed {len(inspirations)} items from __NEXT_DATA__ using JSON scrape.")
                return inspirations
    except Exception as e:
        logger.warning(f"Could not parse __NEXT_DATA__ from Unsplash HTML: {e}")

    # 2. Fallback to regex for <img> tags
    try:
        logger.info("Falling back to regex for <img> tags in Unsplash HTML.")
        found_images = re.findall(r'<img[^>]+src="([^"]+images\.unsplash\.com\/photo-[^"]+)"[^>]+alt="([^"]+)"', html_content)
        for i, (src, alt) in enumerate(found_images[:5]): 
            inspirations.append({
                "id": f"unsplash_html_scrape_{i}",
                "title": alt,
                "description": alt, # Use alt for description as well
                "tags": [t.lower() for t in alt.split()[:3] if t], 
                "image_url_mock": src.split('?')[0], # Clean basic URL
                "source": "Unsplash_Scrape" # Unified source
            })
        if inspirations:
             logger.info(f"Successfully parsed {len(inspirations)} items from HTML img tags using regex.")
    except Exception as e:
        logger.warning(f"Error during HTML img tag scraping for Unsplash: {e}")
        
    return inspirations


def fetch_unsplash_inspiration(prompt: str) -> List[Dict]:
    """
    Fetches inspiration from Unsplash API if key is available and not placeholder.
    Returns a list of inspiration items or an empty list.
    """
    if not UNSPLASH_API_KEY or UNSPLASH_API_KEY == CONFIG_UNSPLASH_KEY_PLACEHOLDER:
        logger.info("Unsplash API key not configured or is placeholder. API call will be skipped.")
        return []

    encoded_prompt = quote_plus(prompt)
    # Using a common endpoint, parameters might need adjustment based on Unsplash's current best practices
    api_url = f"https://api.unsplash.com/search/photos?query={encoded_prompt}&per_page=5&client_id={UNSPLASH_API_KEY}"
    
    try:
        logger.info(f"Attempting Unsplash API call for prompt: '{prompt}' to URL: {api_url}")
        json_string = fetch_url_text(api_url) # fetch_url_text already logs
        if json_string:
            return _parse_unsplash_api_response(json_string)
    except DataProviderError as e:
        logger.warning(f"Unsplash API call failed: {e}")
    return []

def scrape_unsplash_inspiration(prompt: str) -> List[Dict]:
    """
    Fetches inspiration by scraping Unsplash HTML.
    Returns a list of inspiration items or an empty list.
    """
    encoded_prompt = quote_plus(prompt)
    scrape_url = f"https://unsplash.com/s/photos/{encoded_prompt}"
    
    try:
        logger.info(f"Attempting Unsplash HTML scrape for prompt: '{prompt}' from URL: {scrape_url}")
        html_content = fetch_url_text(scrape_url) # fetch_url_text already logs
        if html_content:
            return _parse_unsplash_html_scrape(html_content, prompt)
    except DataProviderError as e:
        logger.warning(f"Unsplash HTML scraping failed: {e}")
    return []

def fetch_unsplash_images(prompt: str) -> List[Dict]:
    """
    Fetches images from Unsplash for a given prompt.
    1. Tries Unsplash API.
    2. Falls back to Unsplash HTML scraping if API fails or returns no results.
    3. Falls back to predefined mock data if both API and scraping fail or return no results.
    """
    logger.info(f"Fetching Unsplash images for prompt: '{prompt}'")

    # 1. Try API
    api_results = fetch_unsplash_inspiration(prompt)
    if api_results:
        logger.info(f"Successfully fetched {len(api_results)} images from Unsplash API for prompt: '{prompt}'")
        return api_results

    logger.warning(f"Unsplash API did not return results for prompt: '{prompt}'. Falling back to scrape.")

    # 2. Try Scrape
    scrape_results = scrape_unsplash_inspiration(prompt)
    if scrape_results:
        logger.info(f"Successfully fetched {len(scrape_results)} images by scraping Unsplash for prompt: '{prompt}'")
        return scrape_results
    
    logger.warning(f"Unsplash scraping did not return results for prompt: '{prompt}'. Falling back to mock data.")
    
    # 3. Fallback to Mock Data
    logger.info(f"Using mock Unsplash data for prompt: '{prompt}'")
    return _MOCK_UNSPLASH_DATA


if __name__ == '__main__':
    # This block is for basic testing of unsplash_provider.py.
    # It requires 'view_text_website' to be available or mocked globally for fetch_url_text.
    
    logging.basicConfig(
        level=logging.DEBUG, # Set to DEBUG to see all logs from this module
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    logger.info("--- Testing unsplash_provider.py ---")

    # --- Mocking setup for standalone testing ---
    # This mock will be used by fetch_url_text when this script is run directly.
    MOCK_API_RESP_SUCCESS = json.dumps({ "results": [ {"id": "api_123", "alt_description": "API Mock Image", "description": "A test image via API.", "tags": [{"title":"mock"}, {"title":"api"}], "urls": {"regular": "http://mock.com/api.jpg"}} ]})
    MOCK_HTML_RESP_NEXT_DATA = '<html><script id="__NEXT_DATA__" type="application/json">{ "props": { "pageProps": { "photos": [{"id": "next_123", "alt_description": "Next Data Image", "urls": {"regular": "http://mock.com/next.jpg"}, "tags": [{"title":"next"}, {"title":"data"}] }] } } }</script></html>'
    MOCK_HTML_RESP_IMG_TAGS = '<html><body><img src="https://images.unsplash.com/photo-mock123?auto=format&fit=crop&w=800&q=60" alt="HTML Img Tag Image"></body></html>'
    MOCK_HTML_EMPTY_FOR_SCRAPE_TEST = '<html><body><p>No images found</p></body></html>'


    def local_mock_view_text_website(url: str) -> Optional[str]:
        logger.debug(f"[Local Mock] view_text_website called for URL: {url}")
        # Use a global variable to control the API key status for testing within this __main__ block
        current_test_api_key_state = globals().get("_TEST_API_KEY_STATE", "VALID") # Default to valid if not set by test

        if "api.unsplash.com" in url:
            if current_test_api_key_state == "VALID_KEY_BUT_API_ERROR": # Simulate API error even if key is 'valid'
                 logger.warning("[Local Mock] Simulating API error despite valid key configuration.")
                 raise DataProviderError("Mock API Error: Simulated API failure.")
            # Check the actual UNSPLASH_API_KEY value for other states
            elif UNSPLASH_API_KEY and UNSPLASH_API_KEY != CONFIG_UNSPLASH_KEY_PLACEHOLDER:
                logger.info(f"[Local Mock] Simulating successful Unsplash API response (key: ...{UNSPLASH_API_KEY[-4:]}).")
                return MOCK_API_RESP_SUCCESS
            else: # Key is placeholder, None, or explicitly set to fail for test
                logger.warning(f"[Local Mock] Unsplash API key is placeholder ('{CONFIG_UNSPLASH_KEY_PLACEHOLDER}'), None, or forced to fail. Simulating API key error.")
                raise DataProviderError("Mock API Key Error: Key is placeholder, not set, or forced fail.")
        
        # Scrape behavior based on prompt content for testing
        if "unsplash.com/s/photos/" in url:
            if "scrape_next_data_works" in url:
                logger.info("[Local Mock] Simulating Unsplash HTML scrape response (with __NEXT_DATA__).")
                return MOCK_HTML_RESP_NEXT_DATA
            elif "scrape_img_tags_works" in url:
                 logger.info("[Local Mock] Simulating Unsplash HTML scrape response (img tags fallback).")
                 return MOCK_HTML_RESP_IMG_TAGS
            elif "scrape_fails" in url:
                logger.warning("[Local Mock] Simulating Unsplash HTML scrape failure (empty/no results).")
                return MOCK_HTML_EMPTY_FOR_SCRAPE_TEST
            else: # Default scrape response if not specified by prompt for testing
                logger.info("[Local Mock] Simulating default Unsplash HTML scrape response (e.g. __NEXT_DATA__ for generic prompt).")
                return MOCK_HTML_RESP_NEXT_DATA

        logger.error(f"[Local Mock] Unhandled URL for local_mock_view_text_website: {url}")
        return None 

    if 'view_text_website' not in globals():
        globals()['view_text_website'] = local_mock_view_text_website
        logger.info("Defined local_mock_view_text_website for __main__ tests.")

    original_unsplash_api_key_for_tests = UNSPLASH_API_KEY # Save the original key from config.py
    
    def set_api_key_state_for_test(key_value, test_state_override=None):
        """Helper to set both the global UNSPLASH_API_KEY and the mock controller state."""
        globals()['UNSPLASH_API_KEY'] = key_value
        if test_state_override: # Explicitly set how the mock API call should behave
            globals()['_TEST_API_KEY_STATE'] = test_state_override
        elif key_value and key_value != CONFIG_UNSPLASH_KEY_PLACEHOLDER:
            globals()['_TEST_API_KEY_STATE'] = "VALID" # Default if key looks okay
        else: # If key is None or placeholder, the API call should fail due to key check
            globals()['_TEST_API_KEY_STATE'] = "FORCE_API_FAIL" 


    # Test 1: fetch_unsplash_images - API Success
    logger.info("\n--- Test 1: fetch_unsplash_images (API Success) ---")
    set_api_key_state_for_test("fake_valid_api_key_for_test_1") 
    results_api_success = fetch_unsplash_images("mountains api success")
    logger.info(f"Test 1 Results: {json.dumps(results_api_success, indent=2)}")
    assert results_api_success and results_api_success[0]["source"] == "Unsplash_API", "Test 1 Failed: Expected API success."


    # Test 2: fetch_unsplash_images - API Key is Placeholder, Scrape Success (__NEXT_DATA__)
    logger.info("\n--- Test 2: fetch_unsplash_images (API Key Placeholder, Scrape __NEXT_DATA__ Success) ---")
    set_api_key_state_for_test(CONFIG_UNSPLASH_KEY_PLACEHOLDER) 
    results_scrape_next_data = fetch_unsplash_images("scrape_next_data_works") # prompt for mock scrape behavior
    logger.info(f"Test 2 Results: {json.dumps(results_scrape_next_data, indent=2)}")
    assert results_scrape_next_data and results_scrape_next_data[0]["source"] == "Unsplash_Scrape", "Test 2 Failed: Expected Scrape success."


    # Test 3: fetch_unsplash_images - API Key Valid but API Call Fails (e.g. network error), Scrape Success (img tags)
    logger.info("\n--- Test 3: fetch_unsplash_images (API Call Fails, Scrape img tags Success) ---")
    set_api_key_state_for_test("fake_valid_key_for_test_3", test_state_override="VALID_KEY_BUT_API_ERROR")
    results_scrape_img_tags = fetch_unsplash_images("scrape_img_tags_works") # prompt for mock scrape behavior
    logger.info(f"Test 3 Results: {json.dumps(results_scrape_img_tags, indent=2)}")
    assert results_scrape_img_tags and results_scrape_img_tags[0]["source"] == "Unsplash_Scrape", "Test 3 Failed: Expected Scrape success after API error."
    

    # Test 4: fetch_unsplash_images - API Fail (no key), Scrape Fail, Mock Fallback
    logger.info("\n--- Test 4: fetch_unsplash_images (API Fail no key, Scrape Fail, Mock Fallback) ---")
    set_api_key_state_for_test(None) # Simulate no API key
    results_mock_fallback = fetch_unsplash_images("scrape_fails") # prompt for mock scrape behavior
    logger.info(f"Test 4 Results: {json.dumps(results_mock_fallback, indent=2)}")
    assert results_mock_fallback and results_mock_fallback[0]["source"] == "Unsplash_Mock_Fallback", "Test 4 Failed: Expected Mock Fallback."

    # Test 5: Direct call to fetch_unsplash_inspiration with placeholder key (should return [] and log)
    logger.info("\n--- Test 5: fetch_unsplash_inspiration (Placeholder Key) ---")
    set_api_key_state_for_test(CONFIG_UNSPLASH_KEY_PLACEHOLDER)
    results_placeholder = fetch_unsplash_inspiration("any_prompt_placeholder_test5")
    logger.info(f"Test 5 Results: {results_placeholder}")
    assert results_placeholder == [], "Test 5 Failed: Expected empty list for placeholder key."

    # Test 6: Direct call to fetch_unsplash_inspiration with NO key (should return [] and log)
    logger.info("\n--- Test 6: fetch_unsplash_inspiration (No Key) ---")
    set_api_key_state_for_test(None)
    results_no_key = fetch_unsplash_inspiration("any_prompt_no_key_test6")
    logger.info(f"Test 6 Results: {results_no_key}")
    assert results_no_key == [], "Test 6 Failed: Expected empty list for no key."

    # Restore original UNSPLASH_API_KEY from config.py and clear test state global
    globals()['UNSPLASH_API_KEY'] = original_unsplash_api_key_for_tests
    if "_TEST_API_KEY_STATE" in globals():
        del globals()['_TEST_API_KEY_STATE']
    
    logger.info("--- All tests in unsplash_provider.py completed ---")
