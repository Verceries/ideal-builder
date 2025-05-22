import json
import os
import logging 
from typing import List, Dict, Union # Union not used here, but can keep

from ..config import GOOGLE_FONTS_API_KEY 

# Get a logger instance for this module
logger = logging.getLogger(__name__) # Added

# Determine the absolute path to the mock data file
ASSET_DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'mock_asset_data.json')

# Removed the standalone basicConfig as the root logger is configured in main.py

def _fetch_fonts_from_google_api(categories: List[str]) -> List[Dict]: 
    """Helper to fetch and parse font data from Google Fonts API."""
    if not GOOGLE_FONTS_API_KEY: 
        logger.info("Google Fonts API key not found in config. Skipping API call for fonts.")
        return []

    font_suggestions = []
    try:
        from __main__ import view_text_website 
    except ImportError:
        logger.error("Tool 'view_text_website' not available for Google Fonts API call.")
        return []

    for category in categories:
        api_url = f"https://www.googleapis.com/webfonts/v1/webfonts?key={GOOGLE_FONTS_API_KEY}&sort=popularity" 
        logger.info(f"Attempting Google Fonts API call for category '{category}' (will filter client-side): {api_url}")
        
        try:
            raw_response = view_text_website(url=api_url)
        except Exception as e:
            logger.error(f"Error during Google Fonts API call for category {category}: {e}")
            continue 

        if not raw_response or raw_response.startswith("Error:"):
            logger.error(f"Google Fonts API request for {category} failed or returned error: {raw_response}")
            continue

        try:
            api_data = json.loads(raw_response)
            if "items" in api_data and isinstance(api_data["items"], list):
                count = 0
                for font_item in api_data["items"]:
                    if count >= 3: 
                        break
                    font_cat = font_item.get("category", "").lower()
                    if category == font_cat or (category == "sans-serif" and font_cat == "sans_serif"): 
                        font_suggestions.append({
                            "type": "font",
                            "name": font_item.get("family"),
                            "category_mock": font_cat, 
                            "source": "GoogleFonts_API",
                            "url_mock": f"https://fonts.google.com/specimen/{font_item.get('family', '').replace(' ', '+')}" 
                        })
                        count += 1
                logger.info(f"Fetched {count} fonts for category '{category}' from Google Fonts API.")
            else:
                logger.warning(f"Google Fonts API response for {category} does not contain 'items' list or is malformed.")
        except json.JSONDecodeError: # Corrected from 'except json.JSONDecodeError as e:' to just 'except json.JSONDecodeError:' if not using e
            logger.exception(f"Failed to parse JSON from Google Fonts API for {category}. Response snippet: {raw_response[:200]}") # Use .exception
            continue
            
    return font_suggestions


def get_asset_suggestions(inspiration_summary: str, trend_tags: List[str]) -> List[Dict]:
    """
    Suggests assets based on inspiration summary and design trends.
    Attempts to fetch fonts from Google Fonts API if key is available and relevant trends are present.
    Other assets (icons, images) and fallback fonts are sourced from mock_asset_data.json.
    """
    logger.info(f"Starting asset suggestion for summary: '{inspiration_summary[:50]}...', trends: {trend_tags}")
    
    final_suggestions: List[Dict] = []
    font_suggestions_api: List[Dict] = [] # To track if API fonts were added
    
    font_categories_to_fetch = []
    if "serif_fonts" in trend_tags:
        font_categories_to_fetch.append("serif")
    if "sans_serif_fonts" in trend_tags or ("minimalism" in trend_tags and not font_categories_to_fetch) or ("modern_ui" in trend_tags and not font_categories_to_fetch) :
         if "sans-serif" not in font_categories_to_fetch: font_categories_to_fetch.append("sans-serif")
    if not font_categories_to_fetch and ("fonts" in inspiration_summary.lower() or "typography" in inspiration_summary.lower()):
        logger.info("Generic font keywords found in summary, considering both serif and sans-serif for API fetch.")
        font_categories_to_fetch.extend(["serif", "sans-serif"])

    if GOOGLE_FONTS_API_KEY and font_categories_to_fetch: 
        logger.info(f"Relevant font trends found ({font_categories_to_fetch}), attempting Google Fonts API call.")
        api_fonts_result = _fetch_fonts_from_google_api(list(set(font_categories_to_fetch))) 
        if api_fonts_result: # Check if list is not empty
            font_suggestions_api = api_fonts_result # Store them to check later
            final_suggestions.extend(font_suggestions_api)
            logger.info(f"Added {len(font_suggestions_api)} fonts from Google Fonts API.")
        else:
            logger.info("Google Fonts API call did not yield results. Will use mock data for fonts.")
    else:
        logger.info("Skipping Google Fonts API call (no key in config or no relevant font trends).")

    logger.info("Loading other assets (icons, images) and fallback fonts from mock data.")
    mock_asset_data = []
    try:
        with open(ASSET_DATA_PATH, 'r') as f:
            mock_asset_data = json.load(f)
    except FileNotFoundError:
        logger.error(f"Mock asset data file not found at {ASSET_DATA_PATH}")
    except json.JSONDecodeError:
        logger.exception(f"Could not decode mock asset data file at {ASSET_DATA_PATH}") # Use .exception

    summary_keywords = set(inspiration_summary.lower().split())
    search_tags = set(tag.lower() for tag in trend_tags) | summary_keywords
    current_suggestion_names = {sugg.get("name") for sugg in final_suggestions}

    for asset in mock_asset_data:
        asset_type = asset.get("type", "").lower()
        asset_name = asset.get("name")

        if asset_name in current_suggestion_names: 
            continue

        if asset_type == "font":
            if not font_suggestions_api: # Only use mock fonts if API didn't provide any
                asset_tags_lower = set(t.lower() for t in asset.get("tags", []))
                mock_font_cat = asset.get("category_mock", "").lower()
                category_match = any(cat_to_fetch == mock_font_cat for cat_to_fetch in font_categories_to_fetch)
                
                if font_categories_to_fetch and category_match: 
                     final_suggestions.append(asset)
                     current_suggestion_names.add(asset_name)
                elif not font_categories_to_fetch and any(tag in asset_tags_lower for tag in search_tags): 
                     final_suggestions.append(asset)
                     current_suggestion_names.add(asset_name)

        elif asset_type in ["icon", "image"]:
            asset_tags_lower = set(t.lower() for t in asset.get("tags", []))
            if any(tag in asset_tags_lower for tag in search_tags):
                final_suggestions.append(asset)
                current_suggestion_names.add(asset_name)
    
    logger.info(f"Total asset suggestions after processing mock data: {len(final_suggestions)}")
    if not final_suggestions:
         logger.info(f"No specific assets found for summary: '{inspiration_summary[:50]}...' and trends: {trend_tags}")

    return final_suggestions


if __name__ == '__main__':
    # This block is for direct testing of this module.
    # It should use its own logging config if main.py's root logger isn't already set up.
    if not logging.getLogger().hasHandlers() or logging.getLogger().level > logging.DEBUG: # Check current root logger level
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    logger.info("--- Running suggest_assets.py standalone examples (using module logger) ---") # Changed from logging.info to logger.info

    insp_1 = "An elegant blog design that needs a good serif font."
    trends_1 = ["serif_fonts", "minimalism", "light_mode"]
    logger.info(f"\n--- Testing with: '{insp_1}', Trends: {trends_1} ---")
    if not GOOGLE_FONTS_API_KEY: 
        logger.info("NOTE: No valid Google Fonts API key in config. Expecting fallback to mock fonts.")
    else:
        logger.info("NOTE: Google Fonts API key found in config. Expecting API call for 'serif'.")
    
    suggestions_1 = get_asset_suggestions(insp_1, trends_1)
    if suggestions_1:
        print(f"Found {len(suggestions_1)} asset(s):") # Keep print for CLI output
        for asset in suggestions_1:
            print(f"- Name: {asset.get('name')}, Type: {asset.get('type')}, Source: {asset.get('source', 'mock_data')}")
    else:
        print("No assets suggested.")

    insp_2 = "A modern dashboard with charts and user icons."
    trends_2 = ["modern_ui", "data_visualization", "dark_mode"] 
    logger.info(f"\n--- Testing with: '{insp_2}', Trends: {trends_2} ---")
    suggestions_2 = get_asset_suggestions(insp_2, trends_2)
    if suggestions_2:
        print(f"Found {len(suggestions_2)} asset(s):")
        for asset in suggestions_2:
            print(f"- Name: {asset.get('name')}, Type: {asset.get('type')}, Source: {asset.get('source', 'mock_data')}")
    else:
        print("No assets suggested.")

    insp_3 = "A clean, modern website that needs a good sans-serif font for readability."
    trends_3 = ["modern_ui", "minimalism", "fonts"] 
    logger.info(f"\n--- Testing with: '{insp_3}', Trends: {trends_3} (implies sans-serif) ---")
    suggestions_3 = get_asset_suggestions(insp_3, trends_3)
    if suggestions_3:
        print(f"Found {len(suggestions_3)} asset(s):")
        for asset in suggestions_3:
            print(f"- Name: {asset.get('name')}, Type: {asset.get('type')}, Source: {asset.get('source', 'mock_data')}")
    else:
        print("No assets suggested.")
        
    logger.info("--- End of suggest_assets.py standalone examples ---")
