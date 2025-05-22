import json
import os
import re
from typing import List, Dict

# Determine the absolute path to the data file
TREND_DICT_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'trend_dictionary.json')

def load_trend_dictionary() -> Dict[str, str]:
    """Loads the trend dictionary from the JSON file."""
    try:
        with open(TREND_DICT_PATH, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: Trend dictionary file not found at {TREND_DICT_PATH}")
        return {}
    except json.JSONDecodeError:
        print(f"Error: Could not decode trend dictionary file at {TREND_DICT_PATH}")
        return {}

def identify_trends(prompt: str, inspiration_summary: str) -> List[str]:
    """
    Identifies design trends based on a user prompt and inspiration summary
    by looking up keywords in a trend dictionary.
    """
    trend_dictionary = load_trend_dictionary()
    if not trend_dictionary:
        return []

    # Combine prompt and inspiration summary for comprehensive analysis
    combined_text = (prompt.lower() + " " + inspiration_summary.lower())

    # Tokenize the combined text. Using a simple split by space and punctuation.
    # More sophisticated tokenization might be needed for production.
    tokens = set(re.findall(r'\b\w+\b', combined_text)) # Get unique words

    identified_trends = set()

    # Check for single-word tokens first
    for token in tokens:
        if token in trend_dictionary:
            identified_trends.add(trend_dictionary[token])

    # Check for multi-word keywords from the dictionary (keys)
    # This is important because 'dark mode' is a key, but 'mode' alone might not be or mean something else.
    for keyword_phrase, trend_tag in trend_dictionary.items():
        if " " in keyword_phrase: # It's a multi-word key
            if keyword_phrase in combined_text: # Check if the exact phrase is in the text
                identified_trends.add(trend_tag)
    
    if not identified_trends:
        print(f"No specific trends identified from text: '{combined_text[:200]}...' using dictionary.")
        # Fallback: if no trends are found from the dictionary, we could return a default
        # or rely on the calling function to handle empty lists. For now, return empty.
        return []

    return list(identified_trends)

if __name__ == '__main__':
    # Example usage
    test_prompt_1 = "a sleek glassmorphic dashboard for a crypto fintech app"
    test_inspiration_1 = "Inspiration includes clean lines, data visualization, and a focus on clarity. Uses frosted glass."
    trends_1 = identify_trends(test_prompt_1, test_inspiration_1)
    print(f"\n--- Trends for '{test_prompt_1}' & short inspiration ---")
    print(f"Identified trends: {trends_1}") # Expected: glassmorphism, data_visualization, modern_ui

    test_prompt_2 = "minimalist website with pastel colors"
    test_inspiration_2 = "The user wants a very simple and clean page, perhaps with soft UI elements."
    trends_2 = identify_trends(test_prompt_2, test_inspiration_2)
    print(f"\n--- Trends for '{test_prompt_2}' & short inspiration ---")
    print(f"Identified trends: {trends_2}") # Expected: minimalism, pastel_colors, (neumorphism if 'soft ui' maps)

    test_prompt_3 = "A retro style homepage for a gaming blog"
    test_inspiration_3 = "Thinking of 80s or 90s arcade games. Maybe some bold typography."
    trends_3 = identify_trends(test_prompt_3, test_inspiration_3)
    print(f"\n--- Trends for '{test_prompt_3}' & short inspiration ---")
    print(f"Identified trends: {trends_3}") # Expected: retro_style, bold_typography

    test_prompt_4 = "An organic food delivery app with flat design elements"
    test_inspiration_4 = "Natural looking, not too complex. Focus on accessibility."
    trends_4 = identify_trends(test_prompt_4, test_inspiration_4)
    print(f"\n--- Trends for '{test_prompt_4}' & short inspiration ---")
    print(f"Identified trends: {trends_4}") # Expected: organic_design, flat_design, accessibility
    
    test_prompt_5 = "No relevant keywords here"
    test_inspiration_5 = "Just some generic text without trend words"
    trends_5 = identify_trends(test_prompt_5, test_inspiration_5)
    print(f"\n--- Trends for '{test_prompt_5}' & short inspiration ---")
    print(f"Identified trends: {trends_5}") # Expected: []
    
    # Test with a key that is a substring of another key e.g. "glass" vs "frosted glass"
    test_prompt_6 = "glass components"
    test_inspiration_6 = "User likes frosted glass effects."
    trends_6 = identify_trends(test_prompt_6, test_inspiration_6)
    print(f"\n--- Trends for '{test_prompt_6}' & short inspiration ---")
    print(f"Identified trends: {trends_6}") # Expected: ['glassmorphism']
