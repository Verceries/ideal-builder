import json
import os
# import urllib.parse # No longer needed here, provider handles it
import logging 
# import re # No longer needed here, provider handles it
from typing import List, Dict, Union # Union might not be needed if always returning List[Dict]

# Imports from our project
from ..config import UNSPLASH_API_KEY # Keep for logging in __main__ or if direct check is desired
from ..data_providers.unsplash_provider import (
    fetch_unsplash_inspiration, 
    scrape_unsplash_inspiration,
    # CONFIG_UNSPLASH_KEY_PLACEHOLDER # Not needed here if provider handles placeholder check
)
# Assuming http_client.DataProviderError is not directly caught here unless re-raised by provider
# from ..data_providers.http_client import DataProviderError 

# Get a logger instance for this module
logger = logging.getLogger(__name__)

# Determine the absolute path to the mock data file
MOCK_INSPIRATION_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'mock_inspiration_data.json')


def get_inspiration(prompt: str) -> List[Dict]: # Changed return type to always List[Dict]
    """
    Gathers design inspiration based on a user prompt.
    Attempts Unsplash API, then Unsplash HTML scraping (via providers), then falls back to local mock data.
    """
    logger.info(f"Gathering inspiration for prompt: '{prompt}'")
    inspiration_items: List[Dict] = []

    # 1. Attempt API call via provider
    # The provider's fetch_unsplash_inspiration function already checks the key and logs.
    logger.info("Trying Unsplash API via provider...")
    inspiration_items = fetch_unsplash_inspiration(prompt)

    # 2. Attempt HTML Scrape via provider (if API failed or was skipped by provider)
    if not inspiration_items:
        logger.info("API did not return results, trying Unsplash HTML scrape via provider...")
        inspiration_items = scrape_unsplash_inspiration(prompt)

    # 3. Fallback to Mock Data
    if not inspiration_items:
        logger.info("Neither API nor scrape returned results. Falling back to mock inspiration data.")
        try:
            with open(MOCK_INSPIRATION_PATH, 'r') as f:
                all_mock_items = json.load(f)
            
            prompt_keywords = set(word for word in prompt.lower().split() if len(word) > 2)
            filtered_mock_items = []
            for item in all_mock_items:
                searchable_text = f"{item.get('title', '')} {item.get('description', '')} {' '.join(item.get('tags', []))}".lower()
                if any(keyword in searchable_text for keyword in prompt_keywords):
                    filtered_mock_items.append(item)
            
            inspiration_items = filtered_mock_items[:5] # Limit results from mock as well
            if inspiration_items:
                logger.info(f"Found {len(inspiration_items)} items in mock data for prompt.")
            else:
                logger.info("No relevant items found in mock data for prompt.")
        except FileNotFoundError:
            logger.error(f"Mock inspiration data file not found at: {MOCK_INSPIRATION_PATH}")
            inspiration_items = [] 
        except json.JSONDecodeError:
            logger.exception(f"Error decoding mock inspiration data from: {MOCK_INSPIRATION_PATH}")
            inspiration_items = []
        except Exception as e:
            logger.exception(f"An unexpected error occurred while loading mock inspiration data: {e}")
            inspiration_items = []

    if not isinstance(inspiration_items, list):
        # This case should ideally not be reached if providers and mock loading always return lists
        logger.error(f"Inspiration items is not a list (type: {type(inspiration_items)}). Returning empty list.")
        return []
        
    return inspiration_items

if __name__ == '__main__':
    # This block is for direct testing of this module.
    if not logging.getLogger().hasHandlers() or logging.getLogger().level > logging.DEBUG:
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    logger.info("--- Running gather_inspiration.py (refactored with providers) standalone examples ---")

    prompt_mock = "minimalist portfolio"
    logger.info(f"\n--- Testing with prompt: '{prompt_mock}' ---")
    inspiration_mock = get_inspiration(prompt_mock)
    if isinstance(inspiration_mock, list): # Should always be list now
        print(f"Found {len(inspiration_mock)} items:") 
        for item in inspiration_mock:
            print(f"- Title: {item.get('title')}, Source: {item.get('source', 'mock_data_fallback')}, Tags: {item.get('tags')}")
    else: # Should not happen
        print(f"Unexpected return type: {type(inspiration_mock)}, value: {inspiration_mock}")

    prompt_generic = "modern dashboard"
    logger.info(f"\n--- Testing with prompt: '{prompt_generic}' ---")
    if UNSPLASH_API_KEY: 
        logger.info("An API key is present in config. Provider will attempt API call.")
    else:
        logger.info("No valid API key in config. Provider will attempt scraping then mock data.")

    inspiration_generic = get_inspiration(prompt_generic)
    if isinstance(inspiration_generic, list):
        print(f"Found {len(inspiration_generic)} items:")
        for item in inspiration_generic:
            print(f"- Title: {item.get('title')}, Source: {item.get('source', 'mock_data_fallback')}, Tags: {item.get('tags')}")
    else:
        print(f"Unexpected return type: {type(inspiration_generic)}, value: {inspiration_generic}")

    prompt_nomatch = "antique calligraphy tools for Martian poetry"
    logger.info(f"\n--- Testing with prompt: '{prompt_nomatch}' (expect few/no matches) ---")
    inspiration_nomatch = get_inspiration(prompt_nomatch)
    if isinstance(inspiration_nomatch, list):
        print(f"Found {len(inspiration_nomatch)} items:")
        if not inspiration_nomatch:
            print("No items found, as might be expected for a very specific prompt.")
        for item in inspiration_nomatch:
            print(f"- Title: {item.get('title')}, Source: {item.get('source', 'mock_data_fallback')}, Tags: {item.get('tags')}")
    else:
        print(f"Unexpected return type: {type(inspiration_nomatch)}, value: {inspiration_nomatch}")
    
    logger.info("--- End of gather_inspiration.py (refactored) standalone examples ---")
