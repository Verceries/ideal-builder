import json
import os
import logging
from typing import List, Dict, Union

# --- Configuration for Google Fonts API ---
# Obtain a Google Fonts API Key from the Google Cloud Console.
# If you have a key, replace "YOUR_GOOGLE_FONTS_API_KEY_IF_AVAILABLE" with it.
GOOGLE_FONTS_API_KEY = "YOUR_GOOGLE_FONTS_API_KEY_IF_AVAILABLE"
# GOOGLE_FONTS_API_KEY = None # Set to None to skip API attempt directly

# Determine the absolute path to the mock data file
ASSET_DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'mock_asset_data.json')

# Setup basic logging (if not already configured by a higher-level module)
if not logging.getLogger().hasHandlers():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(module)s - %(message)s')


def _fetch_fonts_from_google_api(categories: List[str], access_key: str) -> List[Dict]:
    """Helper to fetch and parse font data from Google Fonts API."""
    if not access_key or access_key == "YOUR_GOOGLE_FONTS_API_KEY_IF_AVAILABLE":
        logging.info("Google Fonts API key not provided or is placeholder. Skipping API call for fonts.")
        return []

    font_suggestions = []
    # This import is here because view_text_website is a tool provided by the environment
    try:
        from __main__ import view_text_website # Tool simulation
    except ImportError:
        logging.error("Tool 'view_text_website' not available for Google Fonts API call.")
        return []

    for category in categories:
        # Note: Google Fonts API uses `family` for search, not category for listing all in category directly.
        # The API `https://www.googleapis.com/webfonts/v1/webfonts?key=YOUR_API_KEY&sort=popularity`
        # lists ALL fonts. We'd have to filter by category client-side.
        # For simplicity, let's assume we fetch all and then filter, or if a category filter existed, use it.
        # The provided URL sorts by popularity. We'll fetch the list and filter.
        api_url = f"https://www.googleapis.com/webfonts/v1/webfonts?key={access_key}&sort=popularity"
        logging.info(f"Attempting Google Fonts API call for category '{category}' (will filter client-side): {api_url}")
        
        try:
            raw_response = view_text_website(url=api_url)
        except Exception as e:
            logging.error(f"Error during Google Fonts API call for category {category}: {e}")
            continue # Try next category or fail gracefully

        if not raw_response or raw_response.startswith("Error:"):
            logging.error(f"Google Fonts API request for {category} failed or returned error: {raw_response}")
            continue

        try:
            api_data = json.loads(raw_response)
            if "items" in api_data and isinstance(api_data["items"], list):
                count = 0
                for font_item in api_data["items"]:
                    if count >= 3: # Limit to top 3 per matched category for this example
                        break
                    font_cat = font_item.get("category", "").lower()
                    # Check if the fetched font's category matches the desired category
                    if category == font_cat or (category == "sans-serif" and font_cat == "sans_serif"): # ensure correct mapping
                        font_suggestions.append({
                            "type": "font",
                            "name": font_item.get("family"),
                            "category_mock": font_cat, # Store actual category
                            "source": "GoogleFonts_API",
                            "url_mock": f"https://fonts.google.com/specimen/{font_item.get('family', '').replace(' ', '+')}" # Example URL
                        })
                        count += 1
                logging.info(f"Fetched {count} fonts for category '{category}' from Google Fonts API.")
            else:
                logging.warning(f"Google Fonts API response for {category} does not contain 'items' list or is malformed.")
        except json.JSONDecodeError as e:
            logging.error(f"Failed to parse JSON from Google Fonts API for {category}: {e}. Response snippet: {raw_response[:200]}")
            continue
            
    return font_suggestions


def get_asset_suggestions(inspiration_summary: str, trend_tags: List[str]) -> List[Dict]:
    """
    Suggests assets based on inspiration summary and design trends.
    Attempts to fetch fonts from Google Fonts API if key is available and relevant trends are present.
    Other assets (icons, images) and fallback fonts are sourced from mock_asset_data.json.
    """
    logging.info(f"Starting asset suggestion for summary: '{inspiration_summary[:50]}...', trends: {trend_tags}")
    
    final_suggestions: List[Dict] = []
    font_suggestions_api: List[Dict] = []
    
    # 1. Attempt Google Fonts API Call
    font_categories_to_fetch = []
    if "serif_fonts" in trend_tags:
        font_categories_to_fetch.append("serif")
    if "sans_serif_fonts" in trend_tags or ("minimalism" in trend_tags and not font_categories_to_fetch) or ("modern_ui" in trend_tags and not font_categories_to_fetch) :
         if "sans-serif" not in font_categories_to_fetch: font_categories_to_fetch.append("sans-serif")
    # If no specific font trend, could default to fetching both or popular ones. For now, explicit.
    if not font_categories_to_fetch and ("fonts" in inspiration_summary.lower() or "typography" in inspiration_summary.lower()):
        logging.info("Generic font keywords found in summary, considering both serif and sans-serif for API fetch.")
        font_categories_to_fetch.extend(["serif", "sans-serif"])


    if GOOGLE_FONTS_API_KEY and GOOGLE_FONTS_API_KEY != "YOUR_GOOGLE_FONTS_API_KEY_IF_AVAILABLE" and font_categories_to_fetch:
        logging.info(f"Relevant font trends found ({font_categories_to_fetch}), attempting Google Fonts API call.")
        font_suggestions_api = _fetch_fonts_from_google_api(list(set(font_categories_to_fetch)), GOOGLE_FONTS_API_KEY)
        if font_suggestions_api:
            final_suggestions.extend(font_suggestions_api)
            logging.info(f"Added {len(font_suggestions_api)} fonts from Google Fonts API.")
        else:
            logging.info("Google Fonts API call did not yield results. Will use mock data for fonts.")
    else:
        logging.info("Skipping Google Fonts API call (no key or no relevant font trends).")

    # 2. Process mock_asset_data.json for other assets and fallback fonts
    logging.info("Loading other assets (icons, images) and fallback fonts from mock data.")
    mock_asset_data = []
    try:
        with open(ASSET_DATA_PATH, 'r') as f:
            mock_asset_data = json.load(f)
    except FileNotFoundError:
        logging.error(f"Mock asset data file not found at {ASSET_DATA_PATH}")
    except json.JSONDecodeError:
        logging.error(f"Could not decode mock asset data file at {ASSET_DATA_PATH}")

    summary_keywords = set(inspiration_summary.lower().split())
    search_tags = set(tag.lower() for tag in trend_tags) | summary_keywords
    
    # To avoid duplicates by name if API already provided some fonts
    current_suggestion_names = {sugg.get("name") for sugg in final_suggestions}

    for asset in mock_asset_data:
        asset_type = asset.get("type", "").lower()
        asset_name = asset.get("name")

        if asset_name in current_suggestion_names: # Avoid adding duplicates by name
            continue

        # Handle fonts from mock data only if API didn't provide them or if this one is different
        if asset_type == "font":
            if not font_suggestions_api: # API fonts take precedence
                asset_tags_lower = set(t.lower() for t in asset.get("tags", []))
                # Match font category from trends or general font need
                mock_font_cat = asset.get("category_mock", "").lower()
                category_match = any(cat_to_fetch == mock_font_cat for cat_to_fetch in font_categories_to_fetch)
                
                if font_categories_to_fetch and category_match: # If specific categories were looked for
                     final_suggestions.append(asset)
                     current_suggestion_names.add(asset_name)
                elif not font_categories_to_fetch and any(tag in asset_tags_lower for tag in search_tags): # General match if no API attempt
                     final_suggestions.append(asset)
                     current_suggestion_names.add(asset_name)

        # Handle other asset types (icons, images)
        elif asset_type in ["icon", "image"]:
            asset_tags_lower = set(t.lower() for t in asset.get("tags", []))
            if any(tag in asset_tags_lower for tag in search_tags):
                final_suggestions.append(asset)
                current_suggestion_names.add(asset_name)
    
    logging.info(f"Total asset suggestions after processing mock data: {len(final_suggestions)}")
    if not final_suggestions:
         logging.info(f"No specific assets found for summary: '{inspiration_summary[:50]}...' and trends: {trend_tags}")

    return final_suggestions


if __name__ == '__main__':
    logging.info("--- Running suggest_assets.py standalone examples ---")

    # Example 1: Trends include "serif_fonts", should attempt API if key available, else mock
    insp_1 = "An elegant blog design that needs a good serif font."
    trends_1 = ["serif_fonts", "minimalism", "light_mode"]
    logging.info(f"\n--- Testing with: '{insp_1}', Trends: {trends_1} ---")
    if not GOOGLE_FONTS_API_KEY or GOOGLE_FONTS_API_KEY == "YOUR_GOOGLE_FONTS_API_KEY_IF_AVAILABLE":
        logging.info("NOTE: No valid Google Fonts API key. Expecting fallback to mock fonts.")
    else:
        logging.info("NOTE: Google Fonts API key found. Expecting API call for 'serif'.")
    
    suggestions_1 = get_asset_suggestions(insp_1, trends_1)
    if suggestions_1:
        print(f"Found {len(suggestions_1)} asset(s):")
        for asset in suggestions_1:
            print(f"- Name: {asset.get('name')}, Type: {asset.get('type')}, Source: {asset.get('source', 'mock_data')}")
    else:
        print("No assets suggested.")

    # Example 2: No specific font trends, but general keywords, should get icons/images from mock
    insp_2 = "A modern dashboard with charts and user icons."
    trends_2 = ["modern_ui", "data_visualization", "dark_mode"] # No explicit font type
    logging.info(f"\n--- Testing with: '{insp_2}', Trends: {trends_2} ---")
    suggestions_2 = get_asset_suggestions(insp_2, trends_2)
    if suggestions_2:
        print(f"Found {len(suggestions_2)} asset(s):")
        for asset in suggestions_2:
            print(f"- Name: {asset.get('name')}, Type: {asset.get('type')}, Source: {asset.get('source', 'mock_data')}")
    else:
        print("No assets suggested.")

    # Example 3: Prompt implies "sans-serif" which is a default for modern/minimalism
    insp_3 = "A clean, modern website that needs a good sans-serif font for readability."
    trends_3 = ["modern_ui", "minimalism", "fonts"] # "fonts" implies generic font need
    logging.info(f"\n--- Testing with: '{insp_3}', Trends: {trends_3} (implies sans-serif) ---")
    suggestions_3 = get_asset_suggestions(insp_3, trends_3)
    if suggestions_3:
        print(f"Found {len(suggestions_3)} asset(s):")
        for asset in suggestions_3:
            print(f"- Name: {asset.get('name')}, Type: {asset.get('type')}, Source: {asset.get('source', 'mock_data')}")
    else:
        print("No assets suggested.")
        
    logging.info("--- End of suggest_assets.py standalone examples ---")
