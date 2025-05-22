import sys
import os
from typing import List

# Adjust the Python path to include the parent directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from actions import analyze_trends

def test_identify_trends_with_matches():
    """
    Tests if identify_trends correctly identifies trends from keywords.
    """
    prompt = "A sleek glassmorphic dashboard for a crypto fintech app"
    inspiration_summary = "Inspiration includes clean lines, data visualization, and a focus on clarity. Uses frosted glass effects."
    result = analyze_trends.identify_trends(prompt, inspiration_summary)
    
    assert isinstance(result, list), "Output should be a list."
    assert len(result) > 0, "Should identify trends for the given input."
    
    expected_trends = ["glassmorphism", "data_visualization", "modern_ui"]
    for trend in expected_trends:
        assert trend in result, f"Expected trend '{trend}' not found in {result}."
    print("test_identify_trends_with_matches PASSED")

def test_identify_trends_no_matches():
    """
    Tests if identify_trends returns an empty list when no keywords match.
    """
    prompt = "A website about cooking traditional food."
    inspiration_summary = "Focus on rustic imagery and simple recipes."
    result = analyze_trends.identify_trends(prompt, inspiration_summary)
    
    assert isinstance(result, list), "Output should be a list."
    assert len(result) == 0, f"Should return an empty list for no matching keywords, but got {result}."
    print("test_identify_trends_no_matches PASSED")

def test_identify_trends_from_prompt_only():
    prompt = "dark mode login page with pastel accents"
    inspiration_summary = "User needs a form."
    result = analyze_trends.identify_trends(prompt, inspiration_summary)
    assert isinstance(result, list)
    assert "dark_mode" in result
    assert "pastel_colors" in result
    print("test_identify_trends_from_prompt_only PASSED")

def test_identify_trends_from_summary_only():
    prompt = "A new component for the application."
    inspiration_summary = "The design should feature bold typography and some microinteractions."
    result = analyze_trends.identify_trends(prompt, inspiration_summary)
    assert isinstance(result, list)
    assert "bold_typography" in result
    assert "microinteractions" in result
    print("test_identify_trends_from_summary_only PASSED")

def test_identify_trends_empty_inputs():
    prompt = ""
    inspiration_summary = ""
    result = analyze_trends.identify_trends(prompt, inspiration_summary)
    assert isinstance(result, list)
    assert len(result) == 0, "Should be empty for empty inputs."
    print("test_identify_trends_empty_inputs PASSED")

# --- Tests for New Trend Keywords (from Step 18 & dictionary update) ---

def test_identify_trends_cyberpunk():
    prompt = "A cyberpunk login form with neon future elements."
    summary = "Hacker aesthetic for a tech noir game."
    result = analyze_trends.identify_trends(prompt, summary)
    assert "cyberpunk" in result
    assert "Login Form" in result # Assuming "login form" maps to component name
    print("test_identify_trends_cyberpunk PASSED")

def test_identify_trends_art_deco_luxury():
    prompt = "Elegant art deco hero section for a high-end brand."
    summary = "Roaring twenties gatsby style."
    result = analyze_trends.identify_trends(prompt, summary)
    assert "art_deco" in result
    assert "luxury_aesthetic" in result
    assert "Hero Section" in result 
    print("test_identify_trends_art_deco_luxury PASSED")

def test_identify_trends_playful_handwritten():
    prompt = "Playful UI with handwritten fonts for a children's app."
    summary = "Whimsical and fun, script font needed."
    result = analyze_trends.identify_trends(prompt, summary)
    assert "playful_aesthetic" in result
    assert "handwritten_fonts" in result
    print("test_identify_trends_playful_handwritten PASSED")

def test_identify_trends_corporate_data_viz():
    prompt = "Professional corporate dashboard showing company stats."
    summary = "Businesslike interface for data visualization."
    result = analyze_trends.identify_trends(prompt, summary)
    assert "corporate_aesthetic" in result
    assert "data_visualization" in result
    print("test_identify_trends_corporate_data_viz PASSED")

def test_identify_trends_skeuomorphism_button():
    prompt = "Skeuomorphic buttons with 3D elements."
    summary = "Realistic UI, real world textures for buttons."
    result = analyze_trends.identify_trends(prompt, summary)
    assert "skeuomorphism" in result
    assert "button" in result # Assuming "buttons" maps to "button" component/UI type
    print("test_identify_trends_skeuomorphism_button PASSED")

def test_identify_trends_bauhaus_minimalism():
    prompt = "A bauhaus style website, very simple and functional."
    summary = "Form follows function, clean lines, minimalist approach."
    result = analyze_trends.identify_trends(prompt, summary)
    assert "bauhaus" in result
    assert "minimalism" in result
    print("test_identify_trends_bauhaus_minimalism PASSED")

def test_identify_trends_monochromatic_high_contrast():
    prompt = "A monochromatic scheme with stark contrast for accessibility."
    summary = "Using shades and tints of a single color, high contrast needed."
    result = analyze_trends.identify_trends(prompt, summary)
    assert "monochromatic_scheme" in result
    assert "high_contrast" in result
    assert "accessibility" in result
    print("test_identify_trends_monochromatic_high_contrast PASSED")

def test_identify_trends_card_ui_parallax():
    prompt = "A card layout with parallax scrolling effects."
    summary = "Card based UI where sections have parallax."
    result = analyze_trends.identify_trends(prompt, summary)
    assert "card_ui" in result
    assert "parallax_effect" in result
    print("test_identify_trends_card_ui_parallax PASSED")
    
def test_identify_trends_component_keywords():
    # Test if component keywords correctly map to their "trend tag" (which is the component name)
    prompt = "Need a navbar, a feature card, and a login form."
    summary = "Also a footer and a testimonial section would be great."
    result = analyze_trends.identify_trends(prompt, summary)
    expected_component_tags = ["Navbar", "Feature Card", "Login Form", "Footer", "Testimonial"]
    for tag in expected_component_tags:
        assert tag in result, f"Expected component tag '{tag}' not found in {result}"
    print("test_identify_trends_component_keywords PASSED")


# --- Original test for file issues (can remain as is) ---
def test_identify_trends_data_file_issues():
    original_path = analyze_trends.TREND_DICT_PATH
    analyze_trends.TREND_DICT_PATH = "non_existent_trend_dict.json"
    result_not_found = analyze_trends.identify_trends("test", "test")
    assert isinstance(result_not_found, list)
    assert len(result_not_found) == 0 
    print("test_identify_trends_data_file_not_found (check console for error print) PASSED")

    temp_malformed_file = os.path.join(os.path.dirname(original_path), "temp_malformed_trend.json")
    with open(temp_malformed_file, 'w') as f:
        f.write("{'invalid_json': ") 
    
    analyze_trends.TREND_DICT_PATH = temp_malformed_file
    result_decode_error = analyze_trends.identify_trends("test", "test")
    assert isinstance(result_decode_error, list)
    assert len(result_decode_error) == 0 
    print("test_identify_trends_data_file_decode_error (check console for error print) PASSED")
    
    os.remove(temp_malformed_file) 
    analyze_trends.TREND_DICT_PATH = original_path 
    print("test_identify_trends_data_file_issues (overall) PASSED")


if __name__ == "__main__":
    print("--- Running test_analyze_trends.py (with new trend keywords) ---")
    test_identify_trends_with_matches()
    test_identify_trends_no_matches()
    test_identify_trends_from_prompt_only()
    test_identify_trends_from_summary_only()
    test_identify_trends_empty_inputs()
    
    test_identify_trends_cyberpunk()
    test_identify_trends_art_deco_luxury()
    test_identify_trends_playful_handwritten()
    test_identify_trends_corporate_data_viz()
    test_identify_trends_skeuomorphism_button()
    test_identify_trends_bauhaus_minimalism()
    test_identify_trends_monochromatic_high_contrast()
    test_identify_trends_card_ui_parallax()
    test_identify_trends_component_keywords()
    
    test_identify_trends_data_file_issues()
    print("--- All analyze_trends tests completed ---")
