import sys
import os
from typing import List

# Adjust the Python path to include the parent directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from actions import generate_code
# Import templates to check against their output structure if needed, though not strictly necessary
from actions.code_templates import react_tailwind_templates 

def test_create_code_react_tailwind_button():
    """Tests generating a React-Tailwind button with specific trends."""
    inspiration_summary = "A simple button component" # "button" keyword
    trend_tags = ["glassmorphism", "modern_ui"]
    tech_stack = "react-tailwind"
    color_mode = "dark"
    layout_type = "component"

    result = generate_code.create_code(
        inspiration_summary, trend_tags, tech_stack, color_mode, layout_type
    )
    
    assert isinstance(result, str), "Output should be a string."
    assert "<button" in result, "Should contain button HTML."
    assert "MyButton" in result, "Should use MyButton component from template."
    assert "bg-opacity-20" in result, "Glassmorphism style should be present." # From apply_trend_styles
    assert "bg-gray-800" in result, "Dark mode style should be present." # From apply_trend_styles
    assert "text-white" in result, "Dark mode text style should be present."
    print("test_create_code_react_tailwind_button PASSED")

def test_create_code_react_tailwind_login_form_light():
    """Tests generating a React-Tailwind login form in light mode."""
    inspiration_summary = "A login form for the main page" # "login form" keyword
    trend_tags = ["minimalism"]
    tech_stack = "react-tailwind"
    color_mode = "light"
    layout_type = "component"

    result = generate_code.create_code(
        inspiration_summary, trend_tags, tech_stack, color_mode, layout_type
    )
    
    assert isinstance(result, str)
    assert "<form" in result, "Should contain form HTML."
    assert "LoginForm" in result, "Should use LoginForm component from template."
    # Check for light mode styles (e.g., from apply_trend_styles if not overridden by component defaults)
    # The base login form has its own styles, apply_trend_styles might add to the container
    assert "bg-gray-100" in result or "bg-white" in result # Light mode bg
    assert "text-gray-900" in result or "text-black" in result # Light mode text
    # Minimalism might add specific classes or ensure lack of others.
    # For example, it adds "border-gray-200" and "bg-white" (if not dark mode)
    assert "border-gray-200" in result # From minimalism
    print("test_create_code_react_tailwind_login_form_light PASSED")

def test_create_code_react_tailwind_card_full_page():
    """Tests generating a React-Tailwind card for a full-page layout."""
    inspiration_summary = "A full page display of user data"
    trend_tags = ["data_visualization"] # This trend doesn't directly add styles in current apply_trend_styles
    tech_stack = "react-tailwind"
    color_mode = "dark"
    layout_type = "full-page" # Should pick card template and make it full width/height

    result = generate_code.create_code(
        inspiration_summary, trend_tags, tech_stack, color_mode, layout_type
    )
    
    assert isinstance(result, str)
    assert "<div" in result and "MyCard" in result, "Should use MyCard component."
    assert "w-full" in result and "min-h-screen" in result, "Full page styles should be applied to the card."
    assert "bg-gray-800" in result, "Dark mode style should be present."
    print("test_create_code_react_tailwind_card_full_page PASSED")

def test_create_code_unknown_tech_stack():
    """Tests response for an unsupported tech stack."""
    inspiration_summary = "Any component"
    trend_tags = ["modern_ui"]
    tech_stack = "vue" # Not implemented
    color_mode = "light"
    layout_type = "component"

    result = generate_code.create_code(
        inspiration_summary, trend_tags, tech_stack, color_mode, layout_type
    )
    
    assert isinstance(result, str)
    assert "not yet implemented" in result.lower(), "Should return 'not implemented' message."
    print("test_create_code_unknown_tech_stack PASSED")

def test_create_code_default_component_react_tailwind():
    """Tests if a default component (button) is generated when no specific keywords match."""
    inspiration_summary = "Some section for a webpage, quite generic." # No strong keywords like 'button', 'card', 'login'
    trend_tags = ["modern_ui"]
    tech_stack = "react-tailwind"
    color_mode = "light"
    layout_type = "component" # Not full-page

    result = generate_code.create_code(
        inspiration_summary, trend_tags, tech_stack, color_mode, layout_type
    )
    
    assert isinstance(result, str)
    assert "<button" in result and "MyButton" in result, "Should default to MyButton component."
    assert "Default Button" in result, "Should use default text for the button."
    print("test_create_code_default_component_react_tailwind PASSED")

def test_apply_trend_styles_helper():
    """Directly tests the apply_trend_styles helper function."""
    base_styles = "p-4"
    
    # Test dark mode
    styles_dark = generate_code.apply_trend_styles(base_styles, [], "dark")
    assert "bg-gray-800 text-white border-gray-600" in styles_dark
    assert base_styles in styles_dark
    
    # Test light mode
    styles_light = generate_code.apply_trend_styles(base_styles, [], "light")
    assert "bg-gray-100 text-gray-900 border-gray-300" in styles_light
    
    # Test glassmorphism
    styles_glass = generate_code.apply_trend_styles(base_styles, ["glassmorphism"], "light")
    assert "bg-white bg-opacity-20 backdrop-blur-lg" in styles_glass
    
    # Test glassmorphism in dark mode
    styles_glass_dark = generate_code.apply_trend_styles(base_styles, ["glassmorphism"], "dark")
    assert "bg-white bg-opacity-20" in styles_glass_dark # Glassmorphism base
    assert "bg-gray-800 text-white" in styles_glass_dark # Dark mode overrides/adds
    assert "border-gray-700" in styles_glass_dark # Glassmorphism dark border
    
    # Test minimalism
    styles_minimal = generate_code.apply_trend_styles(base_styles, ["minimalism"], "light")
    assert "border-gray-200 bg-white" in styles_minimal # Assuming light mode for minimalism default bg
    
    # Test minimalism in dark mode (should not add bg-white)
    styles_minimal_dark = generate_code.apply_trend_styles(base_styles, ["minimalism"], "dark")
    assert "bg-white" not in styles_minimal_dark
    assert "border-gray-200" in styles_minimal_dark # This might need review for dark mode context
    
    print("test_apply_trend_styles_helper PASSED")

if __name__ == "__main__":
    print("--- Running test_generate_code.py ---")
    test_apply_trend_styles_helper()
    test_create_code_react_tailwind_button()
    test_create_code_react_tailwind_login_form_light()
    test_create_code_react_tailwind_card_full_page()
    test_create_code_unknown_tech_stack()
    test_create_code_default_component_react_tailwind()
    print("--- All generate_code tests completed ---")
