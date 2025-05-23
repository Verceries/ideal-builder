import json
import os
import re
import logging # Added
from typing import List, Dict

# Get a logger instance for this module
logger = logging.getLogger(__name__) # Added

# Determine the absolute path to the data file
TREND_DICT_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'trend_dictionary.json')

def load_trend_dictionary() -> Dict[str, str]:
    """Loads the trend dictionary from the JSON file."""
    try:
        with open(TREND_DICT_PATH, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"Trend dictionary file not found at {TREND_DICT_PATH}") # Changed from print
        return {}
    except json.JSONDecodeError:
        logger.exception(f"Could not decode trend dictionary file at {TREND_DICT_PATH}") # Changed from print, added exception for stack trace
        return {}

def identify_trends(prompt: str, inspiration_summary: str) -> List[str]:
    """
    Identifies design trends based on a user prompt and inspiration summary
    by looking up keywords in a trend dictionary.
    """
    logger.debug(f"Identifying trends for prompt: '{prompt[:50]}...' and summary: '{inspiration_summary[:50]}...'") # Added debug
    trend_dictionary = load_trend_dictionary()
    if not trend_dictionary:
        logger.warning("Trend dictionary is empty. No trends can be identified.") # Added warning
        return []

    combined_text = (prompt.lower() + " " + inspiration_summary.lower())
    tokens = set(re.findall(r'\b\w+\b', combined_text)) 
    logger.debug(f"Generated {len(tokens)} tokens for trend analysis.") # Added debug

    identified_trends = set()

    for token in tokens:
        if token in trend_dictionary:
            identified_trends.add(trend_dictionary[token])

    for keyword_phrase, trend_tag in trend_dictionary.items():
        if " " in keyword_phrase: 
            if keyword_phrase in combined_text: 
                identified_trends.add(trend_tag)
    
    if not identified_trends:
        logger.info(f"No specific trends identified from text (first 200 chars): '{combined_text[:200]}...' using dictionary.") # Changed from print to info
        return []
    
    logger.info(f"Identified trends: {list(identified_trends)}") # Added info
    return list(identified_trends)

if __name__ == '__main__':
    # This block is for direct testing of this module.
    # It should use its own logging config if main.py's root logger isn't already set up.
    if not logging.getLogger().hasHandlers() or logging.getLogger().level > logging.DEBUG:
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    logger.info("--- Running analyze_trends.py standalone examples (using module logger) ---")
    
    test_prompt_1 = "a sleek glassmorphic dashboard for a crypto fintech app"
    test_inspiration_1 = "Inspiration includes clean lines, data visualization, and a focus on clarity. Uses frosted glass."
    trends_1 = identify_trends(test_prompt_1, test_inspiration_1)
    print(f"\n--- Trends for '{test_prompt_1}' & short inspiration ---") # Kept print for CLI output
    print(f"Identified trends: {trends_1}")

    test_prompt_2 = "minimalist website with pastel colors"
    test_inspiration_2 = "The user wants a very simple and clean page, perhaps with soft UI elements."
    trends_2 = identify_trends(test_prompt_2, test_inspiration_2)
    print(f"\n--- Trends for '{test_prompt_2}' & short inspiration ---")
    print(f"Identified trends: {trends_2}")
    
    # ... (other print statements in if __name__ == '__main__' block are kept for CLI testing) ...
    test_prompt_3 = "A retro style homepage for a gaming blog"
    test_inspiration_3 = "Thinking of 80s or 90s arcade games. Maybe some bold typography."
    trends_3 = identify_trends(test_prompt_3, test_inspiration_3)
    print(f"\n--- Trends for '{test_prompt_3}' & short inspiration ---")
    print(f"Identified trends: {trends_3}")

    test_prompt_4 = "An organic food delivery app with flat design elements"
    test_inspiration_4 = "Natural looking, not too complex. Focus on accessibility."
    trends_4 = identify_trends(test_prompt_4, test_inspiration_4)
    print(f"\n--- Trends for '{test_prompt_4}' & short inspiration ---")
    print(f"Identified trends: {trends_4}")
    
    test_prompt_5 = "No relevant keywords here"
    test_inspiration_5 = "Just some generic text without trend words"
    trends_5 = identify_trends(test_prompt_5, test_inspiration_5)
    print(f"\n--- Trends for '{test_prompt_5}' & short inspiration ---")
    print(f"Identified trends: {trends_5}") 
    
    test_prompt_6 = "glass components"
    test_inspiration_6 = "User likes frosted glass effects."
    trends_6 = identify_trends(test_prompt_6, test_inspiration_6)
    print(f"\n--- Trends for '{test_prompt_6}' & short inspiration ---")
    print(f"Identified trends: {trends_6}")

    # Test cases for new/updated trend tags
    logger.info("\n--- Verifying new and updated trend tags ---")

    test_cases_new_trends = {
        "cyberpunk_test": {
            "prompt": "A website design with a cyberpunk feel, neon future vibes.",
            "inspiration": "Think dystopian tech and hacker aesthetic.",
            "expected": ["cyberpunk"]
        },
        "art_deco_test": {
            "prompt": "An art deco login page for a luxury hotel.",
            "inspiration": "Inspired by gatsby style and geometric opulence.",
            "expected": ["art_deco", "luxury_aesthetic", "Login Form", "geometric_patterns"]
        },
        "skeuomorphism_test": {
            "prompt": "A skeuomorphic UI for a music app.",
            "inspiration": "Wants real world textures and realistic UI elements.",
            "expected": ["skeuomorphism"]
        },
        "playful_aesthetic_test": {
            "prompt": "A playful and fun website for a children's toy store.",
            "inspiration": "Should be whimsical and quirky.",
            "expected": ["playful_aesthetic"]
        },
        "corporate_style_test": {
            "prompt": "A professional and formal UI for a businesslike corporate portal.",
            "inspiration": "The company wants a very corporate style for their new site.",
            "expected": ["corporate_style"]
        },
         "mixed_trends_test": {
            "prompt": "A dark mode cyberpunk dashboard with art deco elements.",
            "inspiration": "User wants a tech noir feel combined with roaring twenties opulence.",
            "expected": ["dark_mode", "cyberpunk", "art_deco", "data_visualization"] # data_visualization from "dashboard"
        }
    }

    for test_name, data in test_cases_new_trends.items():
        logger.info(f"\n--- Running Test: {test_name} ---")
        print(f"\n--- Test: {test_name} ---")
        print(f"Prompt: {data['prompt']}")
        print(f"Inspiration: {data['inspiration']}")
        trends_identified = identify_trends(data['prompt'], data['inspiration'])
        print(f"Identified trends: {trends_identified}")
        
        missing_trends = set(data['expected']) - set(trends_identified)
        unexpected_trends = set(trends_identified) - set(data['expected'])
        
        if not missing_trends and not unexpected_trends:
            print(f"VERIFICATION PASSED for {test_name}.")
            logger.info(f"VERIFICATION PASSED for {test_name}.")
        else:
            print(f"VERIFICATION FAILED for {test_name}:")
            logger.error(f"VERIFICATION FAILED for {test_name}:")
            if missing_trends:
                print(f"  Missing expected trends: {missing_trends}")
                logger.error(f"  Missing expected trends: {missing_trends}")
            if unexpected_trends:
                print(f"  Found unexpected trends: {unexpected_trends}")
                logger.error(f"  Found unexpected trends: {unexpected_trends}")

    logger.info("--- End of analyze_trends.py standalone examples ---")
