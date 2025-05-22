import sys
import os

# Adjust the Python path to include the parent directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from schema import AgentInput # Note: Direct import from schema, assuming it's in the parent dir
from main import run_agent   # Note: Direct import from main, assuming it's in the parent dir

def test_run_agent():
    """
    Tests the main run_agent function with sample input.
    """
    sample_input: AgentInput = {
        "prompt": "Test main agent: a futuristic web3 dashboard",
        "tech_stack": "react-tailwind",
        "color_mode": "dark",
        "layout_type": "full-page"
    }

    result = run_agent(sample_input)

    assert result is not None, "Agent output should not be None"
    
    # Test inspiration_summary
    assert isinstance(result["inspiration_summary"], str), "inspiration_summary should be a string"
    assert len(result["inspiration_summary"]) > 0, "inspiration_summary should not be empty"
    assert sample_input["prompt"] in result["inspiration_summary"], "inspiration_summary should contain the prompt"

    # Test trend_tags
    assert isinstance(result["trend_tags"], list), "trend_tags should be a list"
    assert len(result["trend_tags"]) > 0, "trend_tags list should not be empty"
    for tag in result["trend_tags"]:
        assert isinstance(tag, str), "Each trend_tag should be a string"
    assert "glassmorphism" in result["trend_tags"], "Default trend 'glassmorphism' should be present"

    # Test frontend_code
    assert isinstance(result["frontend_code"], str), "frontend_code should be a string"
    assert len(result["frontend_code"]) > 0, "frontend_code should not be empty"
    assert sample_input["tech_stack"] in result["frontend_code"], "frontend_code should mention the tech_stack"
    assert sample_input["color_mode"] in result["frontend_code"], "frontend_code should mention the color_mode"
    assert sample_input["layout_type"] in result["frontend_code"], "frontend_code should mention the layout_type"

    # Test asset_suggestions
    assert isinstance(result["asset_suggestions"], list), "asset_suggestions should be a list"
    assert len(result["asset_suggestions"]) > 0, "asset_suggestions list should not be empty"
    for asset in result["asset_suggestions"]:
        assert isinstance(asset, str), "Each asset_suggestion should be a string"
    assert "icon_placeholder.svg" in result["asset_suggestions"], "Default asset 'icon_placeholder.svg' should be present"
    
    print("test_run_agent PASSED")

if __name__ == "__main__":
    test_run_agent()
