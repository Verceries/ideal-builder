import sys
import os

# Adjust the Python path to include the parent directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from schema import AgentInput, AgentOutput
from main import run_agent


def test_run_agent_login_form_dark_glassmorphism():
    """
    Tests generating a login form component with dark mode and glassmorphism.
    (Original test, slightly adapted for focus)
    """
    sample_input: AgentInput = {
        "prompt": "A futuristic glassmorphic login form for a crypto app.",
        "tech_stack": "react-tailwind",
        "color_mode": "dark",
        "layout_type": "component" 
    }
    result = run_agent(sample_input)
    assert result is not None, "Agent output should not be None"
    
    # Inspiration summary check (basic)
    assert "Glassmorphic Crypto Wallet Login" in result["inspiration_summary"] or \
           "Crypto Trading Dashboard Interface" in result["inspiration_summary"], \
           f"Expected mock titles in inspiration_summary, got: {result['inspiration_summary']}"

    # Trend tags check
    assert "glassmorphism" in result["trend_tags"]
    assert "dark_mode" in result["trend_tags"]
    assert "modern_ui" in result["trend_tags"] # from "crypto"

    # Frontend code check
    assert "LoginForm" in result["frontend_code"]
    assert "bg-gray-800/10" in result["frontend_code"] or "bg-white/10" in result["frontend_code"] # Glassmorphism for dark card-like
    assert "backdrop-blur-lg" in result["frontend_code"]
    assert "text-white" in result["frontend_code"]
    print("test_run_agent_login_form_dark_glassmorphism PASSED")


def test_run_agent_full_page_light_minimalist_pastel_serif():
    """
    Tests generating a full page with light mode, minimalism, pastel colors, and serif fonts.
    """
    sample_input: AgentInput = {
        "prompt": "A full landing page for a creative blog, using minimalist design, soft pastel colors, and serif typography for headings.",
        "tech_stack": "react-tailwind",
        "color_mode": "light",
        "layout_type": "full-page"
    }
    result = run_agent(sample_input)
    assert result is not None

    # Inspiration summary (basic check for prompt reflection)
    assert "minimal" in result["inspiration_summary"].lower() or "pastel" in result["inspiration_summary"].lower()

    # Trend tags check
    assert "minimalism" in result["trend_tags"]
    assert "pastel_colors" in result["trend_tags"]
    assert "serif_fonts" in result["trend_tags"]
    assert "light_mode" in result["trend_tags"] # analyze_trends should also pick this up

    # Frontend code check for full page structure and styles
    assert "/* --- Navbar Start --- */" in result["frontend_code"]
    assert "/* --- Hero Section Start --- */" in result["frontend_code"] or "<!-- Feature Section -->" in result["frontend_code"]
    assert "/* --- Footer Start --- */" in result["frontend_code"]
    assert len(result["frontend_code"]) > 1000, "Full page code should be substantial."

    # Styling checks (examples, not exhaustive for all components on page)
    assert "font-serif" in result["frontend_code"] # Applied somewhere on the page
    assert "bg-blue-100" in result["frontend_code"] # Pastel color from Hero or Feature cards
    assert "shadow-none" in result["frontend_code"] # Minimalism
    assert "bg-white" in result["frontend_code"] or "bg-gray-50" in result["frontend_code"] # Light mode backgrounds
    print("test_run_agent_full_page_light_minimalist_pastel_serif PASSED")


def test_run_agent_hero_component_dark_glass_modern():
    """
    Tests generating a Hero component with dark mode, glassmorphism, and modern UI.
    """
    sample_input: AgentInput = {
        "prompt": "A modern hero section with a glassmorphism effect for a dark themed website.",
        "tech_stack": "react-tailwind",
        "color_mode": "dark",
        "layout_type": "component"
    }
    result = run_agent(sample_input)
    assert result is not None

    # Trend tags
    assert "hero" in result["trend_tags"] or "modern_ui" in result["trend_tags"] # Prompt implies hero
    assert "glassmorphism" in result["trend_tags"]
    assert "dark_mode" in result["trend_tags"]
    
    # Code
    assert "HeroSection" in result["frontend_code"]
    assert "bg-gray-800/10" in result["frontend_code"] # Dark glass for Hero
    assert "backdrop-blur-lg" in result["frontend_code"]
    assert "rounded-lg" in result["frontend_code"] # Modern UI
    assert "text-white" in result["frontend_code"]
    print("test_run_agent_hero_component_dark_glass_modern PASSED")

def test_run_agent_unsupported_tech_stack_full_page():
    """
    Tests graceful handling of an unsupported tech stack for a full-page request.
    (Original test, adapted for full-page context)
    """
    sample_input: AgentInput = {
        "prompt": "A full portfolio homepage.",
        "tech_stack": "html-css", # Code gen not implemented for this
        "color_mode": "light",
        "layout_type": "full-page"
    }
    result = run_agent(sample_input)
    assert result is not None
    assert "minimal" in result["inspiration_summary"].lower() or "portfolio" in result["inspiration_summary"].lower()
    assert "minimalism" in result["trend_tags"] or "modern_ui" in result["trend_tags"] # Default trends might appear
    assert "not yet implemented" in result["frontend_code"].lower()
    assert len(result["asset_suggestions"]) > 0 # Asset suggestions should still work
    print("test_run_agent_unsupported_tech_stack_full_page PASSED")


def test_run_agent_no_inspiration_matches_component():
    """
    Tests agent behavior when no inspiration items match, for a component request.
    (Original test, minor adaptation)
    """
    sample_input: AgentInput = {
        "prompt": "zyxw_unmatchable_keyword_12345_for_all_systems_blah",
        "tech_stack": "react-tailwind",
        "color_mode": "dark",
        "layout_type": "component"
    }
    result = run_agent(sample_input)
    assert result is not None
    assert "No specific inspiration found" in result["inspiration_summary"]
    assert len(result["trend_tags"]) == 0
    assert "MyButton" in result["frontend_code"] # Should generate default button
    assert "bg-gray-800" in result["frontend_code"] and "text-white" in result["frontend_code"] # Dark mode on button
    assert len(result["asset_suggestions"]) == 0
    print("test_run_agent_no_inspiration_matches_component PASSED")


if __name__ == "__main__":
    print("--- Running test_main.py (Updated for Advanced Code Gen) ---")
    test_run_agent_login_form_dark_glassmorphism()
    test_run_agent_full_page_light_minimalist_pastel_serif()
    test_run_agent_hero_component_dark_glass_modern()
    test_run_agent_unsupported_tech_stack_full_page()
    test_run_agent_no_inspiration_matches_component()
    print("--- All test_main.py tests completed ---")
