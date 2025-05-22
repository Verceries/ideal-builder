import json
import os
from typing import List, Dict, Union

# Determine the absolute path to the data file
DATA_FILE_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'mock_inspiration_data.json')

def get_inspiration(prompt: str) -> Union[str, List[Dict]]:
    """
    Gathers design inspiration based on a user prompt by searching mock data.
    Filters mock data based on keywords in the prompt, looking in title, description, and tags.
    Returns a list of matched inspiration items or a message if no matches are found.
    """
    try:
        with open(DATA_FILE_PATH, 'r') as f:
            inspiration_data = json.load(f)
    except FileNotFoundError:
        return "Error: Inspiration data file not found."
    except json.JSONDecodeError:
        return "Error: Could not decode inspiration data."

    prompt_keywords = set(prompt.lower().split())
    matched_items = []

    for item in inspiration_data:
        searchable_text = f"{item.get('title', '')} {item.get('description', '')} {' '.join(item.get('tags', []))}".lower()
        if any(keyword in searchable_text for keyword in prompt_keywords):
            matched_items.append(item)

    if not matched_items:
        return f"No specific inspiration found for prompt: '{prompt}'. Consider broadening your search or checking available mock data."

    # Return a summary of matched items (or the full items)
    # For this placeholder, let's return a list of titles and sources
    # In a real scenario, this might be a more structured summary or the full objects
    
    # Returning the full matched items as a list of dictionaries
    # return [f"{item['title']} (Source: {item['source']})" for item in matched_items]
    return matched_items


if __name__ == '__main__':
    # Example usage
    test_prompt_1 = "glassmorphism crypto login"
    inspiration_1 = get_inspiration(test_prompt_1)
    print(f"\n--- Inspiration for '{test_prompt_1}' ---")
    if isinstance(inspiration_1, list):
        for item in inspiration_1:
            print(f"- {item.get('title')} (Tags: {', '.join(item.get('tags', []))})")
    else:
        print(inspiration_1)

    test_prompt_2 = "minimalist homepage"
    inspiration_2 = get_inspiration(test_prompt_2)
    print(f"\n--- Inspiration for '{test_prompt_2}' ---")
    if isinstance(inspiration_2, list):
        for item in inspiration_2:
            print(f"- {item.get('title')} (Tags: {', '.join(item.get('tags', []))})")
    else:
        print(inspiration_2)
    
    test_prompt_3 = "something completely random that won't match"
    inspiration_3 = get_inspiration(test_prompt_3)
    print(f"\n--- Inspiration for '{test_prompt_3}' ---")
    if isinstance(inspiration_3, list):
        for item in inspiration_3:
            print(f"- {item.get('title')} (Tags: {', '.join(item.get('tags', []))})")
    else:
        print(inspiration_3)

    test_prompt_4 = "dashboard" # Should match multiple
    inspiration_4 = get_inspiration(test_prompt_4)
    print(f"\n--- Inspiration for '{test_prompt_4}' ---")
    if isinstance(inspiration_4, list):
        for item in inspiration_4:
            print(f"- {item.get('title')} (Description: {item.get('description')})")
    else:
        print(inspiration_4)
