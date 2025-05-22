import json
import os
from typing import List, Dict, Union

# Determine the absolute path to the data file
ASSET_DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'mock_asset_data.json')

def load_asset_data() -> List[Dict]:
    """Loads the asset data from the JSON file."""
    try:
        with open(ASSET_DATA_PATH, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: Asset data file not found at {ASSET_DATA_PATH}")
        return []
    except json.JSONDecodeError:
        print(f"Error: Could not decode asset data file at {ASSET_DATA_PATH}")
        return []

def get_asset_suggestions(inspiration_summary: str, trend_tags: List[str]) -> List[Dict]:
    """
    Suggests assets based on inspiration summary and design trends by filtering mock asset data.
    """
    asset_data = load_asset_data()
    if not asset_data:
        return []

    # Combine inspiration summary keywords and trend tags for a broader search
    # For simplicity, we'll treat inspiration_summary as a source of keywords.
    # A more advanced approach would be NLP to extract relevant terms.
    summary_keywords = set(inspiration_summary.lower().split())
    search_tags = set(tag.lower() for tag in trend_tags) | summary_keywords

    matched_assets = []
    matched_asset_names = set() # To avoid duplicate assets by name

    for asset in asset_data:
        asset_tags_lower = set(t.lower() for t in asset.get("tags", []))
        # Check if any of the search_tags (from trends or summary) are present in the asset's tags
        if any(tag in asset_tags_lower for tag in search_tags):
            # Also, consider keywords from inspiration summary against asset name/description if available
            # For now, primary matching is via tags.
            if asset.get("name") not in matched_asset_names:
                 matched_assets.append(asset)
                 matched_asset_names.add(asset.get("name"))

    if not matched_assets:
        print(f"No specific assets found for summary: '{inspiration_summary[:50]}...' and trends: {trend_tags}")
    
    return matched_assets

if __name__ == '__main__':
    print("--- Example Asset Suggestion ---")

    # Example 1: Dark mode dashboard
    inspiration_1 = "User needs a modern dashboard for crypto analytics. Dark theme preferred."
    trends_1 = ["dark_mode", "data_visualization", "modern_ui", "glassmorphism"]
    suggestions_1 = get_asset_suggestions(inspiration_1, trends_1)
    print(f"\n1. Assets for Dark Mode Crypto Dashboard (Trends: {trends_1}):")
    if suggestions_1:
        for asset in suggestions_1:
            print(f"- {asset['name']} (Type: {asset['type']}, Tags: {', '.join(asset['tags'])})")
    else:
        print("No assets suggested.")

    # Example 2: Minimalist portfolio
    inspiration_2 = "A clean and minimal portfolio for a photographer. Focus on typography."
    trends_2 = ["minimalism", "portfolio", "serif_fonts", "light_mode"] # Added light_mode
    suggestions_2 = get_asset_suggestions(inspiration_2, trends_2)
    print(f"\n2. Assets for Minimalist Portfolio (Trends: {trends_2}):")
    if suggestions_2:
        for asset in suggestions_2:
            print(f"- {asset['name']} (Type: {asset['type']}, Tags: {', '.join(asset['tags'])})")
    else:
        print("No assets suggested.")

    # Example 3: No specific matching trends or summary keywords
    inspiration_3 = "Some generic component"
    trends_3 = ["unknown_trend"]
    suggestions_3 = get_asset_suggestions(inspiration_3, trends_3)
    print(f"\n3. Assets for Generic Component (Trends: {trends_3}):")
    if suggestions_3:
        for asset in suggestions_3:
            print(f"- {asset['name']} (Type: {asset['type']}, Tags: {', '.join(asset['tags'])})")
    else:
        print("No assets suggested (as expected).")
        
    # Example 4: Login page elements
    inspiration_4 = "Building a login page for a new app."
    trends_4 = ["login", "minimal", "modern_ui"]
    suggestions_4 = get_asset_suggestions(inspiration_4, trends_4)
    print(f"\n4. Assets for Login Page (Trends: {trends_4}):")
    if suggestions_4:
        for asset in suggestions_4:
            print(f"- {asset['name']} (Type: {asset['type']}, Tags: {', '.join(asset['tags'])})")
    else:
        print("No assets suggested.")
