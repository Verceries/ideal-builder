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
    # Expected based on trend_dictionary.json:
    # "glassmorphic" -> "glassmorphism"
    # "frosted glass" -> "glassmorphism"
    # "dashboard" -> "data_visualization"
    # "crypto" -> "modern_ui"
    # "sleek" -> "modern_ui"
    # "data visualization" -> "data_visualization" (if present in summary, or "data" and "visualization" separately)
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
    """
    Tests if trends are identified from prompt when inspiration_summary is generic.
    """
    prompt = "dark mode login page with pastel accents"
    inspiration_summary = "User needs a form."
    # Expected: "dark_mode", "pastel_colors"
    result = analyze_trends.identify_trends(prompt, inspiration_summary)
    
    assert isinstance(result, list)
    assert "dark_mode" in result
    assert "pastel_colors" in result
    print("test_identify_trends_from_prompt_only PASSED")

def test_identify_trends_from_summary_only():
    """
    Tests if trends are identified from inspiration_summary when prompt is generic.
    """
    prompt = "A new component for the application."
    inspiration_summary = "The design should feature bold typography and some microinteractions."
    # Expected: "bold_typography", "microinteractions"
    result = analyze_trends.identify_trends(prompt, inspiration_summary)
    
    assert isinstance(result, list)
    assert "bold_typography" in result
    assert "microinteractions" in result
    print("test_identify_trends_from_summary_only PASSED")

def test_identify_trends_empty_inputs():
    """
    Tests behavior with empty prompt and summary.
    """
    prompt = ""
    inspiration_summary = ""
    result = analyze_trends.identify_trends(prompt, inspiration_summary)
    assert isinstance(result, list)
    assert len(result) == 0, "Should be empty for empty inputs."
    print("test_identify_trends_empty_inputs PASSED")

def test_identify_trends_data_file_issues():
    """
    Tests error handling if the trend dictionary file is missing or corrupt.
    """
    original_path = analyze_trends.TREND_DICT_PATH
    
    # Test FileNotFoundError
    analyze_trends.TREND_DICT_PATH = "non_existent_trend_dict.json"
    result_not_found = analyze_trends.identify_trends("test", "test")
    assert isinstance(result_not_found, list)
    assert len(result_not_found) == 0 # Function should return empty list on error
    # Check console output for error message (cannot assert directly here)
    print("test_identify_trends_data_file_not_found (check console for error print) PASSED")

    # Test JSONDecodeError
    temp_malformed_file = os.path.join(os.path.dirname(original_path), "temp_malformed_trend.json")
    with open(temp_malformed_file, 'w') as f:
        f.write("{'invalid_json': ") # Malformed JSON
    
    analyze_trends.TREND_DICT_PATH = temp_malformed_file
    result_decode_error = analyze_trends.identify_trends("test", "test")
    assert isinstance(result_decode_error, list)
    assert len(result_decode_error) == 0 # Function should return empty list on error
    print("test_identify_trends_data_file_decode_error (check console for error print) PASSED")
    
    os.remove(temp_malformed_file) # Clean up
    analyze_trends.TREND_DICT_PATH = original_path # Restore original path
    print("test_identify_trends_data_file_issues (overall) PASSED")


if __name__ == "__main__":
    print("--- Running test_analyze_trends.py ---")
    test_identify_trends_with_matches()
    test_identify_trends_no_matches()
    test_identify_trends_from_prompt_only()
    test_identify_trends_from_summary_only()
    test_identify_trends_empty_inputs()
    test_identify_trends_data_file_issues()
    print("--- All analyze_trends tests completed ---")
