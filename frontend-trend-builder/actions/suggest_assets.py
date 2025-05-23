import json
import os
import logging 
from typing import List, Dict, Set # Added Set

# Imports from our project
from ..config import GOOGLE_FONTS_API_KEY # Still needed for logging in __main__
from ..data_providers.google_fonts_provider import (
    fetch_google_fonts,
    CONFIG_GOOGLE_FONTS_KEY_PLACEHOLDER # Import this if used for check by provider (it is)
)
# from ..data_providers.http_client import DataProviderError # Provider handles this

# Get a logger instance for this module
logger = logging.getLogger(__name__)

# Determine the absolute path to the mock data file
MOCK_ASSET_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'mock_asset_data.json')


def get_asset_suggestions(inspiration_summary: str, trend_tags: List[str]) -> List[Dict]:
    """
    Suggests assets based on inspiration summary and design trends.
    Attempts to fetch fonts from Google Fonts API via provider if key is available and relevant trends are present.
    Other assets (icons, images) and fallback fonts are sourced from mock_asset_data.json.
    """
    logger.info(f"Suggesting assets based on summary: '{inspiration_summary[:50]}...' and trends: {trend_tags}")
    final_suggestions: List[Dict] = []
    processed_font_names: Set[str] = set() 

    # 1. Attempt to get Font suggestions from API via Provider
    api_font_suggestions: List[Dict] = []
    
    # Determine font categories to fetch based on trend_tags
    font_categories_to_fetch: Set[str] = set()
    if "serif_fonts" in trend_tags: font_categories_to_fetch.add("serif")
    if "sans_serif_fonts" in trend_tags: font_categories_to_fetch.add("sans-serif")
    if "handwritten_fonts" in trend_tags: font_categories_to_fetch.add("handwriting") # Assuming 'handwriting' is a category in Google Fonts
    # If no specific font type trend, but general font need is implied
    if not font_categories_to_fetch and ("fonts" in inspiration_summary.lower() or "typography" in inspiration_summary.lower()):
        logger.info("Generic font keywords found, considering default categories (e.g., sans-serif, serif) for API.")
        font_categories_to_fetch.update(["sans-serif", "serif"]) # Default to try both
    elif not font_categories_to_fetch and ("modern_ui" in trend_tags or "minimalism" in trend_tags):
        logger.info("Modern/Minimal trend implies sans-serif, adding for API lookup.")
        font_categories_to_fetch.add("sans-serif")


    if font_categories_to_fetch:
        logger.info(f"Attempting to fetch fonts from Google Fonts API for categories: {list(font_categories_to_fetch)}")
        for category in font_categories_to_fetch:
            try:
                # fetch_google_fonts in provider already checks API key and logs appropriately
                fonts_from_api = fetch_google_fonts(category=category, sort_by="popularity")
                
                # Provider might return more than needed, limit here if necessary (e.g., top 2 per category)
                for font_item in fonts_from_api[:2]: # Taking top 2 per category from API results
                    if font_item.get("name") not in processed_font_names:
                        api_font_suggestions.append(font_item) # Provider should format it correctly
                        processed_font_names.add(font_item["name"])
            except Exception as e: 
                logger.error(f"Error fetching/processing fonts for category '{category}' from API provider: {e}", exc_info=True)
        
        if api_font_suggestions:
            logger.info(f"Successfully fetched {len(api_font_suggestions)} unique font(s) from Google Fonts API.")
            final_suggestions.extend(api_font_suggestions)
        else:
            logger.info("No fonts fetched from Google Fonts API for specified categories (or API key issue).")
    else:
        logger.info("No specific font categories identified from trends for API lookup.")

    # 2. Load mock data for other assets AND for font fallback
    all_mock_items: List[Dict] = []
    try:
        with open(MOCK_ASSET_PATH, 'r') as f:
            all_mock_items = json.load(f)
    except Exception as e:
        logger.exception(f"Error loading mock asset data from {MOCK_ASSET_PATH}.") # Use .exception
        # If mock data fails to load, return whatever API fonts we got, if any.
        # Or, if this is critical, raise an error or return an empty list always.
        return final_suggestions 

    # Process mock items: icons, images, and fonts (if no API fonts were added)
    search_terms = set((inspiration_summary.lower() + " " + " ".join(trend_tags).lower()).split())
    
    # Add other assets (icons, images) from mock data
    for item in all_mock_items:
        item_type = item.get("type","").lower()
        item_name = item.get("name")

        if item_type != "font": # Handle fonts separately for fallback
            item_tags_lower = set(t.lower() for t in item.get("tags", []))
            # Basic matching: if any search term (from prompt/trends) is in item's tags
            if any(term in item_tags_lower for term in search_terms) or not search_terms: # if no search terms, match all of this type?
                if item_name not in processed_font_names: # Though this is for non-fonts, good for consistency
                    final_suggestions.append(item)
                    if item_name: processed_font_names.add(item_name) # Track all added asset names
    
    # Font Fallback: If no fonts came from API (i.e., api_font_suggestions is still empty), use mock fonts
    # Check if any font was actually added from API by checking final_suggestions for type 'font' from API
    api_fonts_were_added = any(s.get("type") == "font" and s.get("source") == "GoogleFonts_API" for s in final_suggestions)

    if not api_fonts_were_added:
        logger.info("No API fonts were successfully added, using mock fonts as fallback.")
        for item in all_mock_items:
            if item.get("type", "").lower() == "font":
                item_name = item.get("name")
                if item_name in processed_font_names: # Avoid duplicates if somehow processed already
                    continue

                mock_font_cat = item.get("category_mock", "").lower() # Mock data uses 'category_mock'
                
                # Match mock font category with identified trend categories
                # Or if no specific categories were targeted by API, match general font tags
                category_match = (font_categories_to_fetch and mock_font_cat in font_categories_to_fetch)
                general_tag_match = (not font_categories_to_fetch and any(term in set(t.lower() for t in item.get("tags",[])) for term in search_terms))

                if category_match or general_tag_match:
                    final_suggestions.append(item)
                    if item_name: processed_font_names.add(item_name)
    
    logger.info(f"Total asset suggestions: {len(final_suggestions)}")
    if not final_suggestions:
        logger.info(f"No assets suggested for summary: '{inspiration_summary[:50]}...' and trends: {trend_tags}")
    return final_suggestions


if __name__ == '__main__':
    if not logging.getLogger().hasHandlers() or logging.getLogger().level > logging.DEBUG:
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    logger.info("--- Running suggest_assets.py (refactored with provider) standalone examples ---")

    insp_1 = "An elegant blog design that needs a good serif font."
    trends_1 = ["serif_fonts", "minimalism", "light_mode"]
    logger.info(f"\n--- Testing with: '{insp_1}', Trends: {trends_1} ---")
    if not GOOGLE_FONTS_API_KEY or GOOGLE_FONTS_API_KEY == CONFIG_GOOGLE_FONTS_KEY_PLACEHOLDER: # Check provider's constant
        logger.info("NOTE: No valid Google Fonts API key in config. Expecting fallback to mock fonts.")
    else:
        logger.info("NOTE: Google Fonts API key found in config. Provider will attempt API call for 'serif'.")
    
    suggestions_1 = get_asset_suggestions(insp_1, trends_1)
    if suggestions_1:
        print(f"Found {len(suggestions_1)} asset(s):")
        for asset in suggestions_1:
            print(f"- Name: {asset.get('name')}, Type: {asset.get('type')}, Source: {asset.get('source', 'mock_data')}")
    else:
        print("No assets suggested.")

    insp_2 = "A modern dashboard with charts and user icons, and a nice sans-serif font."
    trends_2 = ["modern_ui", "data_visualization", "dark_mode", "sans_serif_fonts"] 
    logger.info(f"\n--- Testing with: '{insp_2}', Trends: {trends_2} ---")
    suggestions_2 = get_asset_suggestions(insp_2, trends_2)
    if suggestions_2:
        print(f"Found {len(suggestions_2)} asset(s):")
        for asset in suggestions_2:
            print(f"- Name: {asset.get('name')}, Type: {asset.get('type')}, Source: {asset.get('source', 'mock_data')}")
    else:
        print("No assets suggested.")
        
    logger.info("--- End of suggest_assets.py (refactored) standalone examples ---")
