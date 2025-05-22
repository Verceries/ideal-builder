import json
import os
import urllib.parse
import logging 
import re 
from typing import List, Dict, Union

from ..config import UNSPLASH_API_KEY 

# Get a logger instance for this module
logger = logging.getLogger(__name__)

# Determine the absolute path to the mock data file
DATA_FILE_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'mock_inspiration_data.json')

# Removed the standalone basicConfig as the root logger is configured in main.py

def _fetch_from_unsplash_api(prompt: str) -> Union[List[Dict], None]:
    """Helper to fetch and parse data from Unsplash API."""
    if not UNSPLASH_API_KEY: 
        logger.info("Unsplash API key not found in config. Skipping API call.")
        return None

    encoded_prompt = urllib.parse.quote_plus(prompt)
    api_url = f"https://api.unsplash.com/search/photos?query={encoded_prompt}&per_page=5&client_id={UNSPLASH_API_KEY}" 
    logger.info(f"Attempting Unsplash API call: {api_url}")

    try:
        from __main__ import view_text_website 
        raw_response = view_text_website(url=api_url)
    except ImportError:
        logger.error("Tool 'view_text_website' not available for Unsplash API call.")
        return None
    except Exception as e:
        logger.error(f"Error during Unsplash API call with view_text_website: {e}")
        return None

    if not raw_response or raw_response.startswith("Error:") or "Rate Limit Exceeded" in raw_response:
        logger.error(f"Unsplash API request failed or returned error: {raw_response}")
        return None

    try:
        api_data = json.loads(raw_response)
        if "results" in api_data and isinstance(api_data["results"], list):
            inspiration_items = []
            for photo in api_data["results"][:5]: 
                title = photo.get("alt_description") or photo.get("description") or "Unsplash Image"
                description = photo.get("description") or photo.get("alt_description") or prompt
                tags = [tag.get("title") for tag in photo.get("tags", []) if tag.get("title")]
                
                inspiration_items.append({
                    "id": f"unsplash_api_{photo.get('id', '')}",
                    "title": title,
                    "description": description,
                    "tags": tags if tags else [t for t in prompt.lower().split() if len(t) > 3], 
                    "image_url_mock": photo.get("urls", {}).get("regular") or photo.get("urls", {}).get("small"),
                    "source": "Unsplash_API"
                })
            logger.info(f"Successfully fetched and parsed {len(inspiration_items)} items from Unsplash API.")
            return inspiration_items if inspiration_items else None
        else:
            logger.warning(f"Unsplash API response does not contain 'results' list or is malformed. Response: {api_data}")
            return None
    except json.JSONDecodeError as e:
        logger.exception(f"Failed to parse JSON from Unsplash API response. Response snippet: {raw_response[:200]}") # Use .exception for stack trace
        return None

def _fetch_from_unsplash_scrape(prompt: str) -> Union[List[Dict], None]:
    """Helper to fetch and parse data from Unsplash HTML (experimental)."""
    encoded_prompt = urllib.parse.quote_plus(prompt)
    scrape_url = f"https://unsplash.com/s/photos/{encoded_prompt}"
    logger.info(f"Attempting Unsplash HTML scraping: {scrape_url}")

    try:
        from __main__ import view_text_website 
        html_content = view_text_website(url=scrape_url)
    except ImportError:
        logger.error("Tool 'view_text_website' not available for Unsplash HTML scraping.")
        return None
    except Exception as e:
        logger.error(f"Error during Unsplash HTML scraping with view_text_website: {e}")
        return None

    if not html_content or html_content.startswith("Error:"):
        logger.error(f"Unsplash HTML scraping request failed or returned error: {html_content}")
        return None

    inspiration_items = []
    try:
        json_blobs = re.findall(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html_content)
        if json_blobs:
            next_data = json.loads(json_blobs[0])
            photos_data = next_data.get("props", {}).get("pageProps", {}).get("results", []) 
            if not photos_data and "search" in next_data.get("props",{}).get("pageProps",{}): 
                photos_data = next_data.get("props",{}).get("pageProps",{}).get("search",{}).get("results",[])

            if photos_data and isinstance(photos_data, list):
                for i, photo_data in enumerate(photos_data[:5]): 
                    if isinstance(photo_data, dict):
                        title = photo_data.get("alt_description") or photo_data.get("description") or f"Scraped Image {i+1}"
                        img_url = photo_data.get("urls", {}).get("regular") or photo_data.get("urls", {}).get("small")
                        photo_id = photo_data.get("id", f"scraped_{i}")
                        tags = [tag.get("title") for tag in photo_data.get("tags", []) if tag.get("title")]

                        if img_url:
                            inspiration_items.append({
                                "id": f"unsplash_scrape_json_{photo_id}",
                                "title": title,
                                "description": title, 
                                "tags": tags if tags else [t for t in prompt.lower().split() if len(t) > 3],
                                "image_url_mock": img_url,
                                "source": "Unsplash_JSON_Scrape"
                            })
                if inspiration_items:
                    logger.info(f"Successfully extracted {len(inspiration_items)} items via JSON scraping from Unsplash.")
                    return inspiration_items
    except Exception as e:
        logger.warning(f"Could not parse __NEXT_DATA__ or other JSON from Unsplash HTML: {e}")

    logger.info("Attempting regex-based HTML scraping for images (experimental, may be unreliable).")
    img_matches = re.findall(r'<img[^>]+src="([^"]+images\.unsplash\.com\/photo-[^"]+)"[^>]+alt="([^"]*)"', html_content, re.IGNORECASE)
    
    for i, (src, alt) in enumerate(img_matches[:5]): 
        inspiration_items.append({
            "id": f"unsplash_scrape_img_{i}",
            "title": alt if alt else f"Scraped Unsplash Image {i+1}",
            "description": alt if alt else prompt,
            "tags": [t for t in prompt.lower().split() if len(t) > 3], 
            "image_url_mock": src.split('?')[0], 
            "source": "Unsplash_HTML_Img_Scrape"
        })

    if inspiration_items:
        logger.info(f"Successfully scraped {len(inspiration_items)} items via regex from Unsplash HTML.")
        return inspiration_items
    else:
        logger.warning("HTML scraping (regex) yielded no results or failed to find image patterns.")
        return None

def _fetch_from_mock_data(prompt: str) -> Union[str, List[Dict]]:
    """Helper to fetch and filter data from local mock JSON file."""
    logger.info(f"Falling back to mock data for prompt: '{prompt}'")
    try:
        with open(DATA_FILE_PATH, 'r') as f:
            inspiration_data = json.load(f)
    except FileNotFoundError:
        logger.error(f"Mock data file not found at: {DATA_FILE_PATH}")
        return "Error: Mock inspiration data file not found."
    except json.JSONDecodeError as e:
        logger.exception(f"Could not decode mock inspiration data.") # Use .exception for stack trace
        return "Error: Could not decode mock inspiration data."

    prompt_keywords = set(word for word in prompt.lower().split() if len(word) > 2) 
    matched_items = []

    for item in inspiration_data:
        searchable_text = f"{item.get('title', '')} {item.get('description', '')} {' '.join(item.get('tags', []))}".lower()
        if any(keyword in searchable_text for keyword in prompt_keywords):
            matched_items.append(item)
    
    if not matched_items:
        logger.info(f"No items matched in mock data for prompt: '{prompt}'")
        return f"No specific inspiration found in mock data for prompt: '{prompt}'. Consider broadening your search."
    
    logger.info(f"Found {len(matched_items)} items in mock data for prompt '{prompt}'.")
    return matched_items

def get_inspiration(prompt: str) -> Union[str, List[Dict]]:
    """
    Gathers design inspiration based on a user prompt.
    Attempts Unsplash API, then Unsplash HTML scraping, then falls back to local mock data.
    """
    logger.info(f"Starting inspiration gathering for prompt: '{prompt}'")

    if UNSPLASH_API_KEY: 
        api_results = _fetch_from_unsplash_api(prompt) 
        if api_results:
            return api_results
        logger.info("Unsplash API call did not return results or failed, proceeding to next method.")
    else:
        logger.info("Unsplash API key not configured in config.py. Skipping API call.")

    scrape_results = _fetch_from_unsplash_scrape(prompt)
    if scrape_results:
        return scrape_results
    logger.info("Unsplash HTML scraping did not return results or failed, proceeding to mock data.")
    
    return _fetch_from_mock_data(prompt)

if __name__ == '__main__':
    # This block is for direct testing of this module.
    # It should use its own logging config if main.py's root logger isn't already set up.
    if not logging.getLogger().hasHandlers() or logging.getLogger().level > logging.DEBUG:
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    logger.info("--- Running gather_inspiration.py standalone examples (using module logger) ---")

    prompt_mock = "minimalist portfolio"
    logger.info(f"\n--- Testing with prompt: '{prompt_mock}' (expect fallback to mock) ---")
    inspiration_mock = get_inspiration(prompt_mock)
    if isinstance(inspiration_mock, list):
        print(f"Found {len(inspiration_mock)} items:") # Keep print for CLI output in __main__
        for item in inspiration_mock:
            print(f"- Title: {item.get('title')}, Source: {item.get('source')}, Tags: {item.get('tags')}")
    else:
        print(inspiration_mock)

    prompt_generic = "modern dashboard"
    logger.info(f"\n--- Testing with prompt: '{prompt_generic}' ---")
    if UNSPLASH_API_KEY: 
        logger.info("An API key is present in config, actual API call will be attempted by get_inspiration.")
    else:
        logger.info("No valid API key in config. This run will attempt scraping then mock data.")
        encoded_p = urllib.parse.quote_plus(prompt_generic)
        logger.info(f"If API key were valid, API URL would be: https://api.unsplash.com/search/photos?query={encoded_p}&per_page=5&client_id=CONFIGURED_KEY")
        logger.info(f"Scraping URL would be: https://unsplash.com/s/photos/{encoded_p}")

    inspiration_generic = get_inspiration(prompt_generic)
    if isinstance(inspiration_generic, list):
        print(f"Found {len(inspiration_generic)} items:")
        for item in inspiration_generic:
            print(f"- Title: {item.get('title')}, Source: {item.get('source')}, Tags: {item.get('tags')}")
    else:
        print(inspiration_generic)

    prompt_nomatch = "antique calligraphy tools"
    logger.info(f"\n--- Testing with prompt: '{prompt_nomatch}' (expect specific no-match from mock or external if successful) ---")
    inspiration_nomatch = get_inspiration(prompt_nomatch)
    if isinstance(inspiration_nomatch, list):
        print(f"Found {len(inspiration_nomatch)} items:")
        for item in inspiration_nomatch:
            print(f"- Title: {item.get('title')}, Source: {item.get('source')}, Tags: {item.get('tags')}")
    else:
        print(inspiration_nomatch)
    
    logger.info("--- End of gather_inspiration.py standalone examples ---")
