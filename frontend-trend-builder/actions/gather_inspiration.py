import json
import os
import urllib.parse
import logging # For logging
import re # For basic HTML scraping
from typing import List, Dict, Union

# --- Configuration for Unsplash API ---
# Obtain an Unsplash Access Key by registering an application at https://unsplash.com/developers
# If you have a key, replace "YOUR_UNSPLASH_ACCESS_KEY_IF_AVAILABLE" with it.
# If you don't have a key, or for offline use, it will fallback to HTML scraping then mock data.
# UNSPLASH_ACCESS_KEY = "YOUR_UNSPLASH_ACCESS_KEY_IF_AVAILABLE" # Old placeholder
# UNSPLASH_ACCESS_KEY = None # Set to None to skip API attempt directly
from ..config import UNSPLASH_API_KEY # Use config.py

# Determine the absolute path to the mock data file
DATA_FILE_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'mock_inspiration_data.json')

# Setup basic logging (if not already configured by a higher-level module like main.py)
# This ensures logging works if the action is run standalone.
if not logging.getLogger().hasHandlers():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(module)s - %(message)s')


def _fetch_from_unsplash_api(prompt: str) -> Union[List[Dict], None]: # Removed access_key parameter
    """Helper to fetch and parse data from Unsplash API."""
    if not UNSPLASH_API_KEY: # Use imported config variable
        logging.info("Unsplash API key not found in config. Skipping API call.")
        return None

    encoded_prompt = urllib.parse.quote_plus(prompt)
    api_url = f"https://api.unsplash.com/search/photos?query={encoded_prompt}&per_page=5&client_id={UNSPLASH_API_KEY}" # Use imported
    logging.info(f"Attempting Unsplash API call: {api_url}")

    # This import is here because view_text_website is a tool provided by the environment,
    # not a standard Python library. In a real scenario, this would be `requests.get()`.
    try:
        from __main__ import view_text_website # Tool simulation
        raw_response = view_text_website(url=api_url)
    except ImportError:
        logging.error("Tool 'view_text_website' not available for Unsplash API call.")
        return None
    except Exception as e:
        logging.error(f"Error during Unsplash API call with view_text_website: {e}")
        return None

    if not raw_response or raw_response.startswith("Error:") or "Rate Limit Exceeded" in raw_response:
        logging.error(f"Unsplash API request failed or returned error: {raw_response}")
        return None

    try:
        api_data = json.loads(raw_response)
        if "results" in api_data and isinstance(api_data["results"], list):
            inspiration_items = []
            for photo in api_data["results"][:5]: # Process up to 5 results
                title = photo.get("alt_description") or photo.get("description") or "Unsplash Image"
                description = photo.get("description") or photo.get("alt_description") or prompt
                tags = [tag.get("title") for tag in photo.get("tags", []) if tag.get("title")]
                
                inspiration_items.append({
                    "id": f"unsplash_api_{photo.get('id', '')}",
                    "title": title,
                    "description": description,
                    "tags": tags if tags else [t for t in prompt.lower().split() if len(t) > 3], # fallback tags
                    "image_url_mock": photo.get("urls", {}).get("regular") or photo.get("urls", {}).get("small"),
                    "source": "Unsplash_API"
                })
            logging.info(f"Successfully fetched and parsed {len(inspiration_items)} items from Unsplash API.")
            return inspiration_items if inspiration_items else None
        else:
            logging.warning(f"Unsplash API response does not contain 'results' list or is malformed. Response: {api_data}")
            return None
    except json.JSONDecodeError as e:
        logging.error(f"Failed to parse JSON from Unsplash API response: {e}. Response snippet: {raw_response[:200]}")
        return None

def _fetch_from_unsplash_scrape(prompt: str) -> Union[List[Dict], None]:
    """Helper to fetch and parse data from Unsplash HTML (experimental)."""
    encoded_prompt = urllib.parse.quote_plus(prompt)
    scrape_url = f"https://unsplash.com/s/photos/{encoded_prompt}"
    logging.info(f"Attempting Unsplash HTML scraping: {scrape_url}")

    try:
        from __main__ import view_text_website # Tool simulation
        html_content = view_text_website(url=scrape_url)
    except ImportError:
        logging.error("Tool 'view_text_website' not available for Unsplash HTML scraping.")
        return None
    except Exception as e:
        logging.error(f"Error during Unsplash HTML scraping with view_text_website: {e}")
        return None

    if not html_content or html_content.startswith("Error:"):
        logging.error(f"Unsplash HTML scraping request failed or returned error: {html_content}")
        return None

    inspiration_items = []
    # Basic regex to find image blocks (highly dependent on Unsplash's current HTML structure, very fragile)
    # This looks for a common pattern in image URLs and alt text.
    # Example: <img ... src="https://images.unsplash.com/photo-..." ... alt="A description...">
    # This is a simplified regex and might need significant refinement or a different approach.
    # A more robust scraping method would involve parsing specific JSON blobs if available (e.g., __NEXT_DATA__).
    # For now, this is a placeholder for the concept.
    
    # Let's try to find JSON in script tags first, as it's more reliable
    try:
        # Common pattern for Next.js apps
        json_blobs = re.findall(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html_content)
        if json_blobs:
            next_data = json.loads(json_blobs[0])
            # The exact path to photos can vary wildly. This is a hypothetical path.
            # User would need to inspect Unsplash's __NEXT_DATA__ structure to find correct path.
            # For example: photos = next_data.get("props", {}).get("pageProps", {}).get("photos", [])
            # This path is illustrative and likely incorrect for the actual Unsplash site.
            # For this exercise, we'll assume a placeholder structure.
            photos_data = next_data.get("props", {}).get("pageProps", {}).get("results", []) # Example path
            if not photos_data and "search" in next_data.get("props",{}).get("pageProps",{}): # another possible path for search results
                photos_data = next_data.get("props",{}).get("pageProps",{}).get("search",{}).get("results",[])


            if photos_data and isinstance(photos_data, list):
                for i, photo_data in enumerate(photos_data[:5]): # Limit to 5
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
                    logging.info(f"Successfully extracted {len(inspiration_items)} items via JSON scraping from Unsplash.")
                    return inspiration_items

    except Exception as e:
        logging.warning(f"Could not parse __NEXT_DATA__ or other JSON from Unsplash HTML: {e}")


    # Fallback to basic regex on img tags if JSON scraping fails
    # This is very fragile and likely to break.
    logging.info("Attempting regex-based HTML scraping for images (experimental, may be unreliable).")
    # Simplified regex for <img> tags with Unsplash URLs
    img_matches = re.findall(r'<img[^>]+src="([^"]+images\.unsplash\.com\/photo-[^"]+)"[^>]+alt="([^"]*)"', html_content, re.IGNORECASE)
    
    for i, (src, alt) in enumerate(img_matches[:5]): # Limit to 5
        inspiration_items.append({
            "id": f"unsplash_scrape_img_{i}",
            "title": alt if alt else f"Scraped Unsplash Image {i+1}",
            "description": alt if alt else prompt,
            "tags": [t for t in prompt.lower().split() if len(t) > 3], # Basic tags from prompt
            "image_url_mock": src.split('?')[0], # Clean URL
            "source": "Unsplash_HTML_Img_Scrape"
        })

    if inspiration_items:
        logging.info(f"Successfully scraped {len(inspiration_items)} items via regex from Unsplash HTML.")
        return inspiration_items
    else:
        logging.warning("HTML scraping (regex) yielded no results or failed to find image patterns.")
        return None


def _fetch_from_mock_data(prompt: str) -> Union[str, List[Dict]]:
    """Helper to fetch and filter data from local mock JSON file."""
    logging.info(f"Falling back to mock data for prompt: '{prompt}'")
    try:
        with open(DATA_FILE_PATH, 'r') as f:
            inspiration_data = json.load(f)
    except FileNotFoundError:
        logging.error(f"Mock data file not found at: {DATA_FILE_PATH}")
        return "Error: Mock inspiration data file not found."
    except json.JSONDecodeError as e:
        logging.error(f"Could not decode mock inspiration data: {e}")
        return "Error: Could not decode mock inspiration data."

    prompt_keywords = set(word for word in prompt.lower().split() if len(word) > 2) # Use more meaningful keywords
    matched_items = []

    for item in inspiration_data:
        searchable_text = f"{item.get('title', '')} {item.get('description', '')} {' '.join(item.get('tags', []))}".lower()
        # Match if at least one keyword is found (or more sophisticated logic)
        if any(keyword in searchable_text for keyword in prompt_keywords):
            matched_items.append(item)
    
    if not matched_items:
        logging.info(f"No items matched in mock data for prompt: '{prompt}'")
        return f"No specific inspiration found in mock data for prompt: '{prompt}'. Consider broadening your search."
    
    logging.info(f"Found {len(matched_items)} items in mock data for prompt '{prompt}'.")
    return matched_items


def get_inspiration(prompt: str) -> Union[str, List[Dict]]:
    """
    Gathers design inspiration based on a user prompt.
    Attempts Unsplash API, then Unsplash HTML scraping, then falls back to local mock data.
    """
    logging.info(f"Starting inspiration gathering for prompt: '{prompt}'")

    # 1. Attempt Unsplash API Call
    if UNSPLASH_API_KEY: # Check if key exists from config
        api_results = _fetch_from_unsplash_api(prompt) # Pass prompt only
        if api_results:
            return api_results
        logging.info("Unsplash API call did not return results or failed, proceeding to next method.")
    else:
        logging.info("Unsplash API key not configured in config.py. Skipping API call.")

    # 2. Attempt Unsplash HTML Scraping (Experimental)
    # Note: view_text_website might not be suitable for complex JS-rendered pages.
    # This is a conceptual step; real-world scraping often requires more robust tools.
    # The _fetch_from_unsplash_scrape function is designed to be very basic.
    scrape_results = _fetch_from_unsplash_scrape(prompt)
    if scrape_results:
        return scrape_results
    logging.info("Unsplash HTML scraping did not return results or failed, proceeding to mock data.")
    
    # 3. Fallback to Mock Data
    return _fetch_from_mock_data(prompt)


if __name__ == '__main__':
    logging.info("--- Running gather_inspiration.py standalone examples ---")

    # Example 1: Test with a prompt that should hit mock data (assuming no API key)
    prompt_mock = "minimalist portfolio"
    logging.info(f"\n--- Testing with prompt: '{prompt_mock}' (expect fallback to mock) ---")
    inspiration_mock = get_inspiration(prompt_mock)
    if isinstance(inspiration_mock, list):
        print(f"Found {len(inspiration_mock)} items:")
        for item in inspiration_mock:
            print(f"- Title: {item.get('title')}, Source: {item.get('source')}, Tags: {item.get('tags')}")
    else:
        print(inspiration_mock) # Print error or no-match message

    # Example 2: Test with a generic prompt, showing URL formation if key was present
    prompt_generic = "modern dashboard"
    logging.info(f"\n--- Testing with prompt: '{prompt_generic}' ---")
    if UNSPLASH_API_KEY: # Check imported config variable
        logging.info("An API key is present in config, actual API call will be attempted by get_inspiration.")
    else:
        logging.info("No valid API key in config. This run will attempt scraping then mock data.")
        encoded_p = urllib.parse.quote_plus(prompt_generic)
        logging.info(f"If API key were valid, API URL would be: https://api.unsplash.com/search/photos?query={encoded_p}&per_page=5&client_id=CONFIGURED_KEY")
        logging.info(f"Scraping URL would be: https://unsplash.com/s/photos/{encoded_p}")

    inspiration_generic = get_inspiration(prompt_generic)
    if isinstance(inspiration_generic, list):
        print(f"Found {len(inspiration_generic)} items:")
        for item in inspiration_generic:
            print(f"- Title: {item.get('title')}, Source: {item.get('source')}, Tags: {item.get('tags')}")
    else:
        print(inspiration_generic)

    # Example 3: Prompt that likely won't match mock data well
    prompt_nomatch = "antique calligraphy tools"
    logging.info(f"\n--- Testing with prompt: '{prompt_nomatch}' (expect specific no-match from mock or external if successful) ---")
    inspiration_nomatch = get_inspiration(prompt_nomatch)
    if isinstance(inspiration_nomatch, list):
        print(f"Found {len(inspiration_nomatch)} items:")
        for item in inspiration_nomatch:
            print(f"- Title: {item.get('title')}, Source: {item.get('source')}, Tags: {item.get('tags')}")
    else:
        print(inspiration_nomatch) # Expected: "No specific inspiration found..."
    
    logging.info("--- End of gather_inspiration.py standalone examples ---")
