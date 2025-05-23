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

# Mapping from specific trend tags to Google Font API categories
TREND_TAG_TO_FONT_CATEGORY = {
    "serif_fonts": ["serif"],
    "sans_serif_fonts": ["sans-serif"],
    "handwritten_fonts": ["handwriting"],
    "display_fonts": ["display"],
    "monospace_fonts": ["monospace"],
    "cyberpunk_fonts": ["display", "monospace"],
    "art_deco_fonts": ["display", "sans-serif"],
    "skeuomorphism_fonts": ["serif", "sans-serif"], # Often standard, legible fonts
    "playful_aesthetic_fonts": ["handwriting", "display"],
    "corporate_style_fonts": ["sans-serif", "serif"],
    # General trend tags that might imply font styles
    "modern_ui": ["sans-serif"],
    "minimalism": ["sans-serif"],
    "elegant": ["serif", "display"],
    "retro_style": ["display", "serif"], # Can vary widely
    "developer_tools": ["monospace"], # For "JetBrains Mono" style code fonts
}

def get_asset_suggestions(inspiration_summary: str, trend_tags: List[str]) -> List[Dict]:
    """
    Suggests assets based on inspiration summary and design trends.
    Attempts to fetch fonts from Google Fonts API. Falls back to mock data by category if API fails or yields no results.
    Other assets (icons, images) are sourced from mock_asset_data.json.
    """
    logger.info(f"Suggesting assets based on summary: '{inspiration_summary[:50]}...' and trends: {trend_tags}")
    final_suggestions: List[Dict] = []
    processed_asset_names: Set[str] = set() # Tracks names of all added assets to avoid duplicates

    # 1. Font Suggestions (API with Category-Aware Mock Fallback)
    requested_font_categories: Dict[str, bool] = {} # Key: category, Value: True if API returned results for it

    # Determine which Google Font categories to query based on trend_tags
    categories_to_query_from_trends: Set[str] = set()
    for tag in trend_tags:
        if tag in TREND_TAG_TO_FONT_CATEGORY:
            categories_to_query_from_trends.update(TREND_TAG_TO_FONT_CATEGORY[tag])
        # Add specific font type tags directly if they are categories
        if tag in ["serif", "sans-serif", "display", "handwriting", "monospace"]: # direct category names
             categories_to_query_from_trends.add(tag)


    if not categories_to_query_from_trends and \
       ("fonts" in inspiration_summary.lower() or "typography" in inspiration_summary.lower()):
        logger.info("Generic font keywords in summary, defaulting to 'sans-serif' and 'serif' for API lookup.")
        categories_to_query_from_trends.update(["sans-serif", "serif"])

    if categories_to_query_from_trends:
        logger.info(f"Attempting to fetch fonts from Google Fonts API for categories: {list(categories_to_query_from_trends)}")
        for category in categories_to_query_from_trends:
            requested_font_categories[category] = False # Mark as not yet fulfilled by API
            try:
                fonts_from_api = fetch_google_fonts(category=category, sort_by="popularity")
                if fonts_from_api:
                    requested_font_categories[category] = True # Mark as fulfilled by API
                    logger.info(f"API returned {len(fonts_from_api)} fonts for category '{category}'.")
                    for font_item in fonts_from_api[:2]: # Limit to top 2 per category
                        font_name = font_item.get("name")
                        if font_name and font_name not in processed_asset_names:
                            final_suggestions.append(font_item)
                            processed_asset_names.add(font_name)
                else:
                    logger.info(f"No fonts returned from API for category '{category}'. Will try mock fallback.")
            except Exception as e:
                logger.error(f"Error fetching/processing API fonts for category '{category}': {e}", exc_info=True)
                # Fallback for this category will be attempted via mock data
    else:
        logger.info("No specific font categories identified from trends or summary for API lookup.")

    # 2. Load All Mock Data (for non-fonts and font fallback)
    all_mock_items: List[Dict] = []
    try:
        with open(MOCK_ASSET_PATH, 'r') as f:
            all_mock_items = json.load(f)
    except Exception as e:
        logger.exception(f"Error loading mock asset data from {MOCK_ASSET_PATH}.")
        # If mock data fails, proceed with any API fonts gathered, or return empty if none.
        # This behavior might need adjustment based on how critical mock data is.
        return final_suggestions 

    # 3. Add Non-Font Assets (Icons, Images) from Mock Data
    # Create a combined set of search terms from summary and trend tags for matching
    search_terms = set(inspiration_summary.lower().split()) | set(t.lower() for t in trend_tags)

    for item in all_mock_items:
        item_type = item.get("type","").lower()
        item_name = item.get("name")

        if item_type != "font": # Fonts are handled separately with API priority
            if item_name and item_name in processed_asset_names: # Avoid duplicates
                continue
            
            item_tags_lower = {t.lower() for t in item.get("tags", [])}
            # Match if any of the item's tags are present in the combined search_terms from trends/summary
            # Or if a trend tag directly matches an item tag (e.g. "modern_ui" trend, item has "modern_ui" tag)
            if search_terms.intersection(item_tags_lower):
                if "source" not in item: # Add default source if missing
                    item_type_for_source = item.get("type", "data").lower() # Use "data" as a very generic fallback for type
                    item["source"] = f"mock_{item_type_for_source}"
                final_suggestions.append(item)
                if item_name: processed_asset_names.add(item_name)
    
    # 4. Font Fallback from Mock Data (Category-Aware)
    # Iterate through categories that API did not fulfill
    for category, api_fulfilled in requested_font_categories.items():
        if not api_fulfilled:
            logger.info(f"Attempting mock fallback for font category: '{category}'.")
            mock_fonts_for_category_added = 0
            for item in all_mock_items:
                if item.get("type","").lower() == "font" and item.get("category_mock","").lower() == category:
                    font_name = item.get("name")
                    if font_name and font_name not in processed_asset_names:
                        # Also check if this mock font's general tags align with the overall trend tags
                        item_tags_lower = {t.lower() for t in item.get("tags", [])}
                        if search_terms.intersection(item_tags_lower): # Ensure some thematic relevance
                            if "source" not in item: # Ensure source for these mock fonts
                                item["source"] = "mock_category_fallback_font"
                            final_suggestions.append(item)
                            processed_asset_names.add(font_name)
                            mock_fonts_for_category_added +=1
                            if mock_fonts_for_category_added >= 2: # Limit mock fallback per category
                                break 
            if mock_fonts_for_category_added > 0:
                logger.info(f"Added {mock_fonts_for_category_added} mock font(s) for category '{category}'.")
            else:
                logger.info(f"No suitable mock fonts found for category '{category}' matching current trends.")
    
    # If no font categories were requested at all (e.g. no font-related trend tags or summary keywords)
    # and yet we want to suggest some default mock fonts if the user simply mentioned "fonts" in general.
    # This part is a bit tricky; the current logic for `categories_to_query_from_trends` tries to be smart.
    # If `requested_font_categories` is empty, it implies no API calls were even attempted.
    # In this case, we might want a generic mock font fallback based on general tags.
    if not requested_font_categories:
        logger.info("No specific font categories were targeted by API. Checking for general mock font relevance.")
        generic_mock_fonts_added = 0
        for item in all_mock_items:
            if item.get("type","").lower() == "font":
                font_name = item.get("name")
                if font_name and font_name not in processed_asset_names:
                    item_tags_lower = {t.lower() for t in item.get("tags", [])}
                    if search_terms.intersection(item_tags_lower):
                        if "source" not in item: # Ensure source for these general mock fonts
                             item["source"] = "mock_general_font"
                        final_suggestions.append(item)
                        processed_asset_names.add(font_name)
                        generic_mock_fonts_added += 1
                        if generic_mock_fonts_added >= 2: # Limit generic fallback too
                            break
        if generic_mock_fonts_added > 0:
            logger.info(f"Added {generic_mock_fonts_added} generic mock font(s) based on overall tags.")


    logger.info(f"Total asset suggestions: {len(final_suggestions)}")
    if not final_suggestions:
        logger.warning(f"No assets suggested for summary: '{inspiration_summary[:50]}...' and trends: {trend_tags}")
    return final_suggestions


if __name__ == '__main__':
    # Setup basic logging for __main__ if not already configured
    if not logging.getLogger().hasHandlers() or logging.getLogger().level > logging.DEBUG :
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    logger.info("--- Running suggest_assets.py standalone examples ---")

    # Mock view_text_website for google_fonts_provider if it's not available (e.g. running locally without tools)
    # This is a simplified version of the mock in google_fonts_provider.py's __main__
    # It needs to be available globally for the provider to use it.
    if 'view_text_website' not in globals() and 'google_fonts_provider' in sys.modules:
        def local_mock_view_text_website_for_suggest_assets(url: str) -> Optional[str]:
            global _TEST_API_KEY_STATE_FOR_SUGGEST_ASSETS # Control variable for this mock

            logger.debug(f"[SuggestAssets Local Mock] view_text_website called for URL: {url}")
            
            api_key_to_check = sys.modules['frontend-trend-builder.config'].GOOGLE_FONTS_API_KEY
            placeholder_key = sys.modules['frontend-trend-builder.data_providers.google_fonts_provider'].CONFIG_GOOGLE_FONTS_KEY_PLACEHOLDER

            if not api_key_to_check or api_key_to_check == placeholder_key:
                 logger.warning("[SuggestAssets Local Mock] API key is placeholder or None. Simulating API skip/error.")
                 raise DataProviderError("Mock API Key Error for suggest_assets")

            if _TEST_API_KEY_STATE_FOR_SUGGEST_ASSETS == "API_RETURNS_NO_FONTS":
                logger.info("[SuggestAssets Local Mock] Simulating API returning NO fonts for requested category.")
                return json.dumps({"items": []})
            
            if _TEST_API_KEY_STATE_FOR_SUGGEST_ASSETS == "API_ERROR":
                logger.warning("[SuggestAssets Local Mock] Simulating a generic API error.")
                raise DataProviderError("Simulated generic API error for suggest_assets")

            # Default: Simulate API returning some fonts based on category
            mock_items = []
            if "category=serif" in url:
                mock_items = [{"family": "API Serif Mock", "category": "serif", "source": "GoogleFonts_API"}]
            elif "category=sans-serif" in url:
                mock_items = [{"family": "API Sans Mock", "category": "sans-serif", "source": "GoogleFonts_API"}]
            elif "category=display" in url: # For cyberpunk, art_deco
                mock_items = [{"family": "API Display Mock", "category": "display", "source": "GoogleFonts_API"}]
            # Add more categories as needed for tests
            
            return json.dumps({"items": mock_items})

        # This is a bit of a hack. Ideally, the provider itself would have its mock if run standalone.
        # If this script is run, and the provider's view_text_website is already mocked by ITS __main__, that's fine.
        # If not, we provide a basic one here.
        # The key is that fetch_google_fonts needs *a* view_text_website.
        import sys # Ensure sys is imported
        # Patch it into the http_client module where fetch_url_text expects it
        if 'frontend_trend_builder.data_providers.http_client' in sys.modules:
            sys.modules['frontend_trend_builder.data_providers.http_client'].view_text_website = local_mock_view_text_website_for_suggest_assets
            logger.info("Patched http_client.view_text_website with a local mock for suggest_assets.py testing.")
        else:
            # If http_client is not loaded, try to make it global hoping the provider finds it.
            globals()['view_text_website'] = local_mock_view_text_website_for_suggest_assets
            logger.info("Made view_text_website globally available from suggest_assets.py for testing.")


    original_api_key = GOOGLE_FONTS_API_KEY # Save to restore later
    global _TEST_API_KEY_STATE_FOR_SUGGEST_ASSETS # To control mock API behavior
    _TEST_API_KEY_STATE_FOR_SUGGEST_ASSETS = "API_WORKS_NORMALLY" # Default


    # Test Case 1: API key valid, API returns fonts for "serif"
    logger.info("\n--- Test Case 1: API key valid, API returns 'serif' fonts ---")
    sys.modules['frontend-trend-builder.config'].GOOGLE_FONTS_API_KEY = "VALID_KEY_TEST"
    _TEST_API_KEY_STATE_FOR_SUGGEST_ASSETS = "API_WORKS_NORMALLY" # Mock returns API Serif Mock
    suggestions = get_asset_suggestions("Elegant blog with serif typography", ["serif_fonts", "minimalism", "elegant"])
    logger.info(f"Test Case 1 Results: {json.dumps(suggestions, indent=2)}")
    assert any(a['name'] == "API Serif Mock" and a['source'] == "GoogleFonts_API" for a in suggestions if a['type'] == 'font'), "Test Case 1 Failed: API Serif font missing or wrong source."
    for asset in suggestions: assert "source" in asset, f"Test Case 1 Failed: Asset missing source field: {asset.get('name')}"


    # Test Case 2: API key valid, API returns NO fonts for "display" (e.g. for cyberpunk) -> fallback to mock
    logger.info("\n--- Test Case 2: API key valid, API returns NO 'display' or 'monospace' fonts (triggering mock fallback for cyberpunk) ---")
    sys.modules['frontend-trend-builder.config'].GOOGLE_FONTS_API_KEY = "VALID_KEY_TEST"
    _TEST_API_KEY_STATE_FOR_SUGGEST_ASSETS = "API_RETURNS_NO_FONTS" 
    suggestions = get_asset_suggestions("Cyberpunk theme website", ["cyberpunk_fonts", "dark_mode"]) # cyberpunk_fonts -> display, monospace
    logger.info(f"Test Case 2 Results: {json.dumps(suggestions, indent=2)}")
    found_cyberpunk_mock_font = any(
        a['type'] == 'font' and 
        a.get('source', '').startswith('mock_') and # mock_fallback_font or mock_category_fallback_font
        (a['name'] == 'Orbitron' or a['name'] == 'Monoton') # Expected mock fonts for cyberpunk
        for a in suggestions
    )
    assert found_cyberpunk_mock_font, "Test Case 2 Failed: Expected cyberpunk mock font with correct source."
    for asset in suggestions: assert "source" in asset, f"Test Case 2 Failed: Asset missing source field: {asset.get('name')}"


    # Test Case 3: API key is placeholder -> full fallback to mock for requested categories
    logger.info("\n--- Test Case 3: API key is placeholder (full mock fallback for playful fonts) ---")
    sys.modules['frontend-trend-builder.config'].GOOGLE_FONTS_API_KEY = CONFIG_GOOGLE_FONTS_KEY_PLACEHOLDER
    _TEST_API_KEY_STATE_FOR_SUGGEST_ASSETS = "API_WORKS_NORMALLY" # Won't be hit
    suggestions = get_asset_suggestions("Playful design for kids", ["playful_aesthetic_fonts", "pastel_colors"]) # playful_aesthetic_fonts -> handwriting, display
    logger.info(f"Test Case 3 Results: {json.dumps(suggestions, indent=2)}")
    found_playful_mock_font = any(
        a['type'] == 'font' and 
        a.get('source', '').startswith('mock_') and 
        (a['name'] == 'Pacifico' or a['name'] == 'Comfortaa' or a['name'] == 'Monoton') # Monoton is display
        for a in suggestions
    )
    assert found_playful_mock_font, "Test Case 3 Failed: Expected playful mock font with correct source."
    # Check a mock icon/image for source tagging
    found_mock_non_font = any(a['type'] != 'font' and a.get('source', '').startswith('mock_') for a in suggestions)
    assert found_mock_non_font, "Test Case 3 Failed: Expected mock non-font asset with source."
    for asset in suggestions: assert "source" in asset, f"Test Case 3 Failed: Asset missing source field: {asset.get('name')}"


    # Test Case 4: API key valid, but general API error -> full fallback to mock
    logger.info("\n--- Test Case 4: API key valid, but general API error (full mock fallback for corporate fonts) ---")
    sys.modules['frontend-trend-builder.config'].GOOGLE_FONTS_API_KEY = "VALID_KEY_TEST"
    _TEST_API_KEY_STATE_FOR_SUGGEST_ASSETS = "API_ERROR" 
    suggestions = get_asset_suggestions("Corporate website landing page", ["corporate_style_fonts", "modern_ui"]) # corporate_style_fonts -> sans-serif, serif
    logger.info(f"Test Case 4 Results: {json.dumps(suggestions, indent=2)}")
    found_corporate_mock_font = any(
        a['type'] == 'font' and 
        a.get('source', '').startswith('mock_') and 
        (a['name'] == 'Open Sans' or a['name'] == 'Merriweather')
        for a in suggestions
    )
    assert found_corporate_mock_font, "Test Case 4 Failed: Expected corporate mock font with correct source."
    for asset in suggestions: assert "source" in asset, f"Test Case 4 Failed: Asset missing source field: {asset.get('name')}"
    

    # Test Case 5: Art Deco - API provides 'display', mock for 'sans-serif' (Illustrative)
    # This test requires nuanced mocking. We'll simplify by checking if *any* art deco font is found,
    # and that all items have a source.
    logger.info("\n--- Test Case 5: Art Deco fonts - check for presence and source tags ---")
    sys.modules['frontend-trend-builder.config'].GOOGLE_FONTS_API_KEY = "VALID_KEY_TEST_ARTDECO"
    _TEST_API_KEY_STATE_FOR_SUGGEST_ASSETS = "API_WORKS_NORMALLY" # Mock will provide for display and sans-serif
    suggestions = get_asset_suggestions("Art Deco Hotel lobby", ["art_deco_fonts"])
    logger.info(f"Test Case 5 Results: {json.dumps(suggestions, indent=2)}")
    
    found_art_deco_font = any(
        a['type'] == 'font' and 
        (a.get('source') == 'GoogleFonts_API' or a.get('source', '').startswith('mock_')) and
        (a['name'] == 'API Display Mock' or a['name'] == 'API Sans Mock' or a['name'] == 'Bebas Neue' or a['name'] == 'Poppins')
        for a in suggestions
    )
    assert found_art_deco_font, "Test Case 5 Failed: Expected some Art Deco font (API or mock)."
    for asset in suggestions: assert "source" in asset, f"Test Case 5 Failed: Asset missing source field: {asset.get('name')}"

    # Test Case 6: Skeuomorphism fonts - Expecting 'Inter' (mock) or 'API Serif Mock' / 'API Sans Mock' (API)
    logger.info("\n--- Test Case 6: Skeuomorphism fonts ---")
    sys.modules['frontend-trend-builder.config'].GOOGLE_FONTS_API_KEY = "VALID_KEY_TEST_SK"
    _TEST_API_KEY_STATE_FOR_SUGGEST_ASSETS = "API_WORKS_NORMALLY"
    suggestions = get_asset_suggestions("Skeuomorphic dashboard", ["skeuomorphism_fonts", "dashboard"]) # skeuomorphism_fonts -> serif, sans-serif
    logger.info(f"Test Case 6 Results: {json.dumps(suggestions, indent=2)}")
    found_skeu_font = any(
        a['type'] == 'font' and
        (a['name'] == 'Inter' or a['name'] == 'API Serif Mock' or a['name'] == 'API Sans Mock')
        for a in suggestions
    )
    assert found_skeu_font, "Test Case 6 Failed: Expected skeuomorphism font."
    for asset in suggestions: assert "source" in asset, f"Test Case 6 Failed: Asset missing source field: {asset.get('name')}"


    # Restore API key
    sys.modules['frontend-trend-builder.config'].GOOGLE_FONTS_API_KEY = original_api_key
    logger.info("\n--- suggest_assets.py standalone examples complete ---")
