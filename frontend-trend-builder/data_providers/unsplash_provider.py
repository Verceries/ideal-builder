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
                    "image_url_mock": image_url, # Name kept for consistency with existing schema
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
            photos_data = []
            page_props = next_data.get("props", {}).get("pageProps", {})
            if "results" in page_props: # Common for search result pages
                 photos_data = page_props["results"]
            elif "photos" in page_props: # Common for other photo list pages
                 photos_data = page_props["photos"]
            # Add more checks here based on observed Unsplash structure
            
            if not isinstance(photos_data, list): # Ensure photos_data is iterable list
                photos_data = []

            for photo in photos_data[:5]: 
                if not isinstance(photo, dict): continue # Skip if photo data is not a dict

                photo_id = photo.get("id")
                alt_description = photo.get("alt_description") or photo.get("description")
                img_url = photo.get("urls", {}).get("regular")
                tags_data = photo.get("tags", [])
                tags = [tag.get("title") for tag in tags_data if isinstance(tag, dict) and tag.get("title")]


                if photo_id and alt_description and img_url:
                    inspirations.append({
                        "id": f"unsplash_json_scrape_{photo_id}",
                        "title": alt_description,
                        "description": alt_description,
                        "tags": tags if tags else [t.lower() for t in alt_description.split()[:3]],
                        "image_url_mock": img_url,
                        "source": "Unsplash_JSON_Scrape"
                    })
            if inspirations:
                logger.info(f"Successfully parsed {len(inspirations)} items from __NEXT_DATA__.")
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
                "description": alt,
                "tags": [t.lower() for t in alt.split()[:3]], 
                "image_url_mock": src.split('?')[0], # Clean basic URL
                "source": "Unsplash_HTML_Img_Scrape"
            })
        if inspirations:
             logger.info(f"Successfully parsed {len(inspirations)} items from HTML img tags.")
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

    def local_mock_view_text_website(url: str) -> Optional[str]:
        logger.debug(f"[Local Mock] view_text_website called for URL: {url}")
        if "api.unsplash.com" in url:
            if UNSPLASH_API_KEY and UNSPLASH_API_KEY != CONFIG_UNSPLASH_KEY_PLACEHOLDER:
                logger.info("[Local Mock] Simulating successful Unsplash API response.")
                return MOCK_API_RESP_SUCCESS
            else:
                logger.warning("[Local Mock] Unsplash API key is placeholder or missing. Simulating API error.")
                raise DataProviderError("Mock API Key Error: Key is placeholder or not set.")
        elif "unsplash.com/s/photos/" in url:
            logger.info("[Local Mock] Simulating Unsplash HTML scrape response (with __NEXT_DATA__).")
            return MOCK_HTML_RESP_NEXT_DATA
            # To test img tag fallback: return MOCK_HTML_RESP_IMG_TAGS
            # To test scrape failure: return None or raise DataProviderError("Mock scrape error")
        logger.error(f"[Local Mock] Unhandled URL: {url}")
        return None

    # Replace fetch_url_text's internal call to view_text_website with our local mock for this test run
    # This is a bit more involved than patching directly if http_client itself is not easily patchable here.
    # A simpler way for __main__ is to just globally define view_text_website if not present.
    # For now, let's assume http_client.view_text_website can be patched or this script is run where the tool is available.
    # The original http_client.py already has a similar mock if view_text_website is not found globally.
    # We will rely on that for now for simplicity in this __main__ block.
    
    # Test 1: API call (simulating key is valid)
    logger.info("\n--- Test 1: Fetch via API (simulating valid key) ---")
    # To test this properly, you'd patch 'frontend_trend_builder.data_providers.unsplash_provider.UNSPLASH_API_KEY'
    # For this __main__ block, we assume it's set or we can temporarily set it if testing logic allows.
    # Let's assume the config.py will provide it. If not, it will log and skip.
    # For a direct test here, we might need a more complex setup or rely on .env for this test.
    # For now, we'll see what the imported UNSPLASH_API_KEY is.
    if UNSPLASH_API_KEY and UNSPLASH_API_KEY != CONFIG_UNSPLASH_KEY_PLACEHOLDER:
        logger.info(f"Using configured UNSPLASH_API_KEY: ...{UNSPLASH_API_KEY[-4:]}")
        # Temporarily replace http_client's view_text_website for this specific test case
        # This is tricky. A better way is to use unittest.mock.patch if running this as a formal test.
        # For this __main__ block, if we want to force the API path for testing, we'd need to ensure
        # `fetch_url_text` uses a mocked `view_text_website` that returns MOCK_API_RESP_SUCCESS.
        # This example will primarily test the parsing logic if `fetch_url_text` works.
        
        # To ensure this test path is hit, we'd ideally mock fetch_url_text itself,
        # or ensure UNSPLASH_API_KEY is set and view_text_website is globally mocked.
        # For this specific run, we'll rely on the global mock in http_client.py if view_text_website is not available.
        # If view_text_website IS available (e.g. in agent env), it will make a real call.
        
        # Let's assume for this test, we provide a mock response directly to parsing
        logger.info("Directly testing API response parsing:")
        parsed_api = _parse_unsplash_api_response(MOCK_API_RESP_SUCCESS)
        logger.info(f"Parsed API results: {json.dumps(parsed_api, indent=2)}")

    else:
        logger.info("UNSPLASH_API_KEY is placeholder or not set in config. Skipping direct API fetch test in __main__.")


    # Test 2: Scrape call (always attempted if API fails or key is missing)
    logger.info("\n--- Test 2: Fetch via HTML Scrape ---")
    # Similar to above, this relies on the environment's view_text_website or http_client's mock.
    logger.info("Directly testing HTML scrape parsing (__NEXT_DATA__):")
    parsed_scrape_next_data = _parse_unsplash_html_scrape(MOCK_HTML_RESP_NEXT_DATA, "test prompt")
    logger.info(f"Parsed HTML (__NEXT_DATA__) results: {json.dumps(parsed_scrape_next_data, indent=2)}")
    
    logger.info("Directly testing HTML scrape parsing (img tags):")
    parsed_scrape_img_tags = _parse_unsplash_html_scrape(MOCK_HTML_RESP_IMG_TAGS, "test prompt")
    logger.info(f"Parsed HTML (img tags) results: {json.dumps(parsed_scrape_img_tags, indent=2)}")

        
    # Test 3: fetch_unsplash_inspiration (which uses the key)
    logger.info("\n--- Test 3: fetch_unsplash_inspiration function call ---")
    # This will use the actual UNSPLASH_API_KEY from config.
    # If not set, it will log and return [].
    # If set, it depends on the global view_text_website tool.
    # To make this testable here, we need to ensure view_text_website is defined.
    if 'view_text_website' not in globals():
        globals()['view_text_website'] = local_mock_view_text_website # Use our local mock

    results_fetch_api = fetch_unsplash_inspiration("mountains")
    if results_fetch_api:
        logger.info(f"fetch_unsplash_inspiration results: {json.dumps(results_fetch_api, indent=2)}")
    else:
        logger.info("fetch_unsplash_inspiration did not return results (check API key and view_text_website mock).")

    logger.info("--- End of unsplash_provider.py tests ---")
