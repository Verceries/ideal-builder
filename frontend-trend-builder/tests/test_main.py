import sys
import os

# Adjust the Python path to include the parent directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from schema import AgentInput, AgentOutput
from main import run_agent

# Note: The action modules (gather_inspiration, analyze_trends, etc.)
# construct file paths to their data files (e.g., mock_inspiration_data.json)
# using os.path.join(os.path.dirname(__file__), '..', 'data', 'filename.json').
# Since __file__ for an action module like gather_inspiration.py is
# /app/frontend-trend-builder/actions/gather_inspiration.py,
# os.path.dirname(__file__) is /app/frontend-trend-builder/actions.
# Then '..' correctly points to /app/frontend-trend-builder/,
# and 'data/filename.json' correctly points to the data files.
# This means tests should run correctly if the PWD is /app or /app/frontend-trend-builder.

def test_run_agent_react_tailwind_dark_glassmorphism():
    """
    Tests the main run_agent function with a React-Tailwind, dark mode, glassmorphism prompt.
    """
    sample_input: AgentInput = {
        "prompt": "A futuristic glassmorphic login form for a crypto app.",
        "tech_stack": "react-tailwind",
        "color_mode": "dark",
        "layout_type": "component" # Should generate a login form
    }

    result = run_agent(sample_input)

    assert result is not None, "Agent output should not be None"
    
    # 1. Test inspiration_summary (processed from get_inspiration)
    assert isinstance(result["inspiration_summary"], str), "inspiration_summary should be a string"
    assert len(result["inspiration_summary"]) > 0, "inspiration_summary should not be empty"
    assert "Glassmorphic Crypto Wallet Login" in result["inspiration_summary"] or \
           "Crypto Trading Dashboard Interface" in result["inspiration_summary"], \
           f"Expected specific mock titles in inspiration_summary, got: {result['inspiration_summary']}"
    assert "futuristic" in result["inspiration_summary"].lower() or \
           "crypto" in result["inspiration_summary"].lower(), \
           "Prompt keywords should be reflected in inspiration_summary string."

    # 2. Test trend_tags (from analyze_trends)
    assert isinstance(result["trend_tags"], list), "trend_tags should be a list"
    assert len(result["trend_tags"]) > 0, "trend_tags list should not be empty for this prompt."
    assert "glassmorphism" in result["trend_tags"], "'glassmorphism' trend should be identified."
    assert "modern_ui" in result["trend_tags"], "'modern_ui' (from crypto/futuristic) should be identified."
    assert "dark_mode" in result["trend_tags"], "'dark_mode' should be identified."

    # 3. Test frontend_code (from generate_code)
    assert isinstance(result["frontend_code"], str), "frontend_code should be a string."
    assert len(result["frontend_code"]) > 0, "frontend_code should not be empty."
    assert "LoginForm" in result["frontend_code"], "Should generate a LoginForm for 'login form' in prompt."
    assert "react-tailwind" in sample_input["tech_stack"], "Tech stack sanity check." # Input check
    # Check for glassmorphism and dark mode styles
    assert "bg-opacity-20" in result["frontend_code"] or "backdrop-blur-lg" in result["frontend_code"], "Glassmorphism style missing."
    assert "bg-gray-800" in result["frontend_code"] and "text-white" in result["frontend_code"], "Dark mode styles missing."

    # 4. Test asset_suggestions (from suggest_assets)
    assert isinstance(result["asset_suggestions"], list), "asset_suggestions should be a list."
    assert len(result["asset_suggestions"]) > 0, "Should suggest some assets for this prompt."
    
    # Check for some expected asset types or specific assets
    has_icon = any(asset["type"] == "icon" for asset in result["asset_suggestions"])
    has_font = any(asset["type"] == "font" for asset in result["asset_suggestions"])
    has_image = any(asset["type"] == "image" for asset in result["asset_suggestions"])
    assert has_icon, "Should suggest at least one icon."
    assert has_font, "Should suggest at least one font."
    
    # Example specific asset checks based on tags like 'glassmorphism', 'dark_mode', 'modern_ui'
    expected_asset_found = any(
        asset["name"] == "Heroicons - Sparkles" or \
        asset["name"] == "Abstract Geometric Background" or \
        asset["name"] == "Material Icons - Dark Mode"
        for asset in result["asset_suggestions"]
    )
    assert expected_asset_found, "Expected specific assets for glassmorphism/dark_mode not found."
    
    print("test_run_agent_react_tailwind_dark_glassmorphism PASSED")

def test_run_agent_html_css_light_minimalist_full_page():
    """
    Tests with HTML-CSS (not implemented for code gen), light mode, minimalist full page.
    """
    sample_input: AgentInput = {
        "prompt": "A minimal and clean portfolio homepage.",
        "tech_stack": "html-css", # Code gen not implemented for this
        "color_mode": "light",
        "layout_type": "full-page"
    }
    result = run_agent(sample_input)

    assert result is not None
    
    # Inspiration
    assert "Minimalist E-commerce Homepage" in result["inspiration_summary"] or \
           "Minimal Portfolio Website with Pastel Accents" in result["inspiration_summary"], \
           f"Expected minimal mock titles in inspiration_summary, got: {result['inspiration_summary']}"
    
    # Trends
    assert "minimalism" in result["trend_tags"]
    
    # Code (should be "not implemented")
    assert "not yet implemented" in result["frontend_code"].lower()
    
    # Assets
    assert len(result["asset_suggestions"]) > 0
    found_minimal_image = any(asset["name"] == "Minimalist Desk Setup" for asset in result["asset_suggestions"])
    found_roboto_font = any(asset["name"] == "Roboto" for asset in result["asset_suggestions"]) # Roboto has 'minimalism' tag
    assert found_minimal_image or found_roboto_font, "Expected minimalist assets."

    print("test_run_agent_html_css_light_minimalist_full_page PASSED")


def test_run_agent_no_matches_or_empty_results_handling():
    """
    Tests agent behavior when sub-actions yield no results or error messages.
    """
    sample_input: AgentInput = {
        "prompt": "zyxw_unmatchable_keyword_12345_for_all_systems", # Should not match inspiration
        "tech_stack": "react-tailwind",
        "color_mode": "dark",
        "layout_type": "component"
    }
    result = run_agent(sample_input)

    assert result is not None
    
    # Inspiration: Should be a "No specific inspiration found" message
    assert "No specific inspiration found" in result["inspiration_summary"]
    
    # Trends: Should be empty as inspiration is a message and prompt is non-matching
    assert isinstance(result["trend_tags"], list)
    assert len(result["trend_tags"]) == 0, f"Trend tags should be empty, got: {result['trend_tags']}"
    
    # Code: Will generate a default button as trends are empty and layout is component
    assert "MyButton" in result["frontend_code"] # Default component
    assert "Default Button" in result["frontend_code"]
    assert "bg-gray-800 text-white" in result["frontend_code"] # Dark mode still applies

    # Assets: Should be empty as trends are empty and summary is a "no inspiration" message
    assert isinstance(result["asset_suggestions"], list)
    assert len(result["asset_suggestions"]) == 0, f"Asset suggestions should be empty, got: {result['asset_suggestions']}"

    print("test_run_agent_no_matches_or_empty_results_handling PASSED")

if __name__ == "__main__":
    print("--- Running test_main.py ---")
    test_run_agent_react_tailwind_dark_glassmorphism()
    test_run_agent_html_css_light_minimalist_full_page()
    test_run_agent_no_matches_or_empty_results_handling()
    print("--- All main agent tests completed ---")
