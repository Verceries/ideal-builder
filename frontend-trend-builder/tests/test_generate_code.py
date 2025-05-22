import sys
import os
# Add List, Dict, Any for more complex type hints if needed later
from typing import List 

# Adjust the Python path to include the parent directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from actions import generate_code
# It's good practice to import the specific things you need
# from actions.code_templates import react_tailwind_templates # Not strictly needed for these tests

# --- Test apply_trend_styles directly ---
def test_apply_trend_styles_helper_contextual():
    """Directly tests the apply_trend_styles helper with component_type context."""
    print("\n--- Testing apply_trend_styles helper directly ---")

    # Dark mode styling
    dark_card_styles = generate_code.apply_trend_styles("", [], "dark", "Card")
    assert "text-white" in dark_card_styles and "bg-gray-800" in dark_card_styles and "border-gray-700" in dark_card_styles
    print("apply_trend_styles: Dark mode Card OK")

    dark_navbar_styles = generate_code.apply_trend_styles("", [], "dark", "Navbar")
    assert "text-white" in dark_navbar_styles and "bg-gray-900" in dark_navbar_styles
    print("apply_trend_styles: Dark mode Navbar OK")

    # Light mode styling
    light_button_styles = generate_code.apply_trend_styles("p-2", [], "light", "Button") # Buttons have their own bg usually
    assert "text-gray-900" in light_button_styles and "p-2" in light_button_styles
    assert "bg-gray-50" not in light_button_styles # Button should not get default bg-gray-50
    print("apply_trend_styles: Light mode Button OK")

    # Glassmorphism
    glass_hero_dark = generate_code.apply_trend_styles("", ["glassmorphism"], "dark", "Hero Section")
    assert "backdrop-blur-lg" in glass_hero_dark and "bg-gray-800/10" in glass_hero_dark and "text-white" in glass_hero_dark
    print("apply_trend_styles: Glassmorphism Hero Dark OK")

    glass_nav_light = generate_code.apply_trend_styles("", ["glassmorphism"], "light", "Navbar")
    assert "bg-white/30" in glass_nav_light and "backdrop-blur-md" in glass_nav_light
    print("apply_trend_styles: Glassmorphism Navbar Light OK")

    # Pastel Colors
    pastel_card_light = generate_code.apply_trend_styles("", ["pastel_colors"], "light", "Card")
    assert "bg-blue-100" in pastel_card_light and "text-gray-700" in pastel_card_light
    print("apply_trend_styles: Pastel Card Light OK")

    pastel_button_light = generate_code.apply_trend_styles("", ["pastel_colors"], "light", "Button")
    assert "bg-blue-100" in pastel_button_light and "text-blue-800" in pastel_button_light
    print("apply_trend_styles: Pastel Button Light OK")

    pastel_dark_card = generate_code.apply_trend_styles("", ["pastel_colors"], "dark", "Card")
    assert "bg-blue-100" not in pastel_dark_card # Pastel should not apply in dark mode
    print("apply_trend_styles: Pastel Dark Card (no pastel) OK")
    
    # Serif Fonts
    serif_styles = generate_code.apply_trend_styles("", ["serif_fonts"], "light", "Unknown")
    assert "font-serif" in serif_styles
    print("apply_trend_styles: Serif Fonts OK")

    # Minimalism
    minimal_card_light = generate_code.apply_trend_styles("p-6", ["minimalism"], "light", "Card")
    assert "shadow-none" in minimal_card_light and "bg-white" in minimal_card_light and "p-4" in minimal_card_light
    assert "p-6" not in minimal_card_light # p-4 should replace p-6
    print("apply_trend_styles: Minimalism Card Light OK")

    minimal_hero_dark = generate_code.apply_trend_styles("", ["minimalism"], "dark", "Hero Section")
    assert "shadow-none" in minimal_hero_dark and "bg-white" not in minimal_hero_dark # No bg-white in dark
    print("apply_trend_styles: Minimalism Hero Dark OK")

    # Modern UI
    modern_button_light = generate_code.apply_trend_styles("", ["modern_ui"], "light", "Button")
    assert "rounded-lg" in modern_button_light and "shadow-md" in modern_button_light
    print("apply_trend_styles: Modern UI Button Light OK")

    modern_minimal_card = generate_code.apply_trend_styles("", ["modern_ui", "minimalism"], "light", "Card")
    assert "rounded-lg" in modern_minimal_card and "shadow-none" in modern_minimal_card # Minimalism shadow overrides modern
    print("apply_trend_styles: Modern UI Minimal Card OK")
    
    # Conflict: Glassmorphism and Minimalism
    glass_minimal_card = generate_code.apply_trend_styles("", ["glassmorphism", "minimalism"], "light", "Card")
    assert "backdrop-blur-lg" in glass_minimal_card # Glassmorphism visuals
    assert "shadow-lg" in glass_minimal_card # Glassmorphism shadow should win over minimalism's shadow-none if glass is prioritized
    assert "bg-white/10" in glass_minimal_card # Glassmorphism bg
    print("apply_trend_styles: Glassmorphism Minimal Card OK")


# --- Test Generation of Specific Components ---
def test_generate_navbar_component():
    result = generate_code.create_code("A sleek navbar", ["modern_ui"], "react-tailwind", "light", "component")
    assert "Navbar" in result and "<nav" in result and "Logo" in result
    assert "rounded-lg" in result # from modern_ui
    print("test_generate_navbar_component PASSED")

def test_generate_footer_component():
    result = generate_code.create_code("Page bottom-bar with copyright", ["dark_mode"], "react-tailwind", "dark", "component")
    assert "Footer" in result and "<footer>" in result and "© 2024" in result
    assert "bg-gray-800" in result or "bg-gray-900" in result # Dark mode footer
    print("test_generate_footer_component PASSED")

def test_generate_hero_component():
    result = generate_code.create_code("Landing page hero section", ["serif_fonts"], "react-tailwind", "light", "component")
    assert "HeroSection" in result and "<section" in result and "Main Heading" in result
    assert "font-serif" in result
    print("test_generate_hero_component PASSED")

def test_generate_feature_card_component():
    result = generate_code.create_code("Info card about a feature", ["pastel_colors"], "react-tailwind", "light", "component")
    assert "FeatureCard" in result and "Feature Title" in result
    assert "bg-blue-100" in result # Pastel color
    print("test_generate_feature_card_component PASSED")

def test_generate_testimonial_component():
    result = generate_code.create_code("User review quote", ["minimalism"], "react-tailwind", "dark", "component")
    assert "Testimonial" in result and "fantastic product" in result
    assert "shadow-none" in result # Minimalism
    assert "bg-gray-800" in result # Dark mode
    print("test_generate_testimonial_component PASSED")

# --- Test Full-Page Layout Generation ---
def test_generate_full_page_with_hero():
    summary = "A full landing page intro with a hero section and modern look."
    trends = ["modern_ui", "light_mode", "hero"]
    result = generate_code.create_code(summary, trends, "react-tailwind", "light", "full-page")
    assert "/* --- Navbar Start --- */" in result and "/* --- Navbar End --- */" in result
    assert "/* --- Hero Section Start --- */" in result and "/* --- Hero Section End --- */" in result
    assert "/* --- Footer Start --- */" in result and "/* --- Footer End --- */" in result
    assert "FeatureCard1" not in result # Should pick Hero over features
    assert "rounded-lg" in result # Modern UI
    print("test_generate_full_page_with_hero PASSED")

def test_generate_full_page_with_features():
    summary = "A full product features page, dark theme."
    trends = ["dark_mode"] # No "hero" keyword
    result = generate_code.create_code(summary, trends, "react-tailwind", "dark", "full-page")
    assert "/* --- Navbar Start --- */" in result
    assert "<!-- Feature Section -->" in result and "/* --- FeatureCard1 Start --- */" in result
    assert "/* --- Footer Start --- */" in result
    assert "HeroSection" not in result
    assert "bg-gray-900" in result # Navbar dark
    assert "bg-gray-800" in result # Feature card dark
    print("test_generate_full_page_with_features PASSED")

# --- Test Enhanced Styling Logic on Components ---
def test_styling_glassmorphism_serif_dark_hero():
    summary = "A hero section with glass and serif type."
    trends = ["glassmorphism", "serif_fonts", "dark_mode", "hero"]
    result = generate_code.create_code(summary, trends, "react-tailwind", "dark", "component")
    assert "HeroSection" in result
    assert "font-serif" in result
    assert "bg-gray-800/10" in result # Dark glass for Hero
    assert "backdrop-blur-lg" in result
    assert "text-white" in result
    print("test_styling_glassmorphism_serif_dark_hero PASSED")

def test_styling_minimalism_pastel_light_card():
    summary = "A card that is very simple and has soft pastel colors."
    trends = ["minimalism", "pastel_colors", "light_mode", "card"]
    result = generate_code.create_code(summary, trends, "react-tailwind", "light", "component")
    assert "MyCard" in result # General card
    assert "shadow-none" in result
    assert "bg-blue-100" in result # Pastel should override minimalism's bg-white here
    assert "p-4" in result # Minimalism padding
    print("test_styling_minimalism_pastel_light_card PASSED")

def test_styling_modern_dark_navbar():
    summary = "A modern navigation header for a dark website."
    trends = ["modern_ui", "dark_mode", "navbar"]
    result = generate_code.create_code(summary, trends, "react-tailwind", "dark", "component")
    assert "Navbar" in result
    assert "rounded-lg" in result
    assert "bg-gray-900" in result # Dark navbar
    assert "shadow-md" in result # Modern UI shadow
    print("test_styling_modern_dark_navbar PASSED")

# --- Test Keyword Prioritization and Fallbacks ---
def test_keyword_priority_hero_over_card():
    summary = "A hero banner that looks like a card." # "hero" and "card"
    trends = ["modern_ui", "light_mode", "hero", "card"] # "hero" is higher priority
    result = generate_code.create_code(summary, trends, "react-tailwind", "light", "component")
    assert "HeroSection" in result
    assert "MyCard" not in result # Should not pick general card if hero is specified
    print("test_keyword_priority_hero_over_card PASSED")

def test_fallback_to_button():
    summary = "Some very generic content piece for a website." # No strong keywords
    trends = ["modern_ui", "dark_mode"]
    result = generate_code.create_code(summary, trends, "react-tailwind", "dark", "component")
    assert "MyButton" in result and "Default Button" in result
    print("test_fallback_to_button PASSED")

# --- Original tests (can be kept if still valid or adapted) ---
def test_create_code_original_button_dark_glass():
    """Original test for button, adapted for new styling if needed."""
    inspiration_summary = "A cool glassmorphic button for a dark themed UI"
    trend_tags = ["glassmorphism", "dark_mode", "button"] # Added button keyword
    tech_stack = "react-tailwind"
    color_mode = "dark"
    layout_type = "component"
    result = generate_code.create_code(inspiration_summary, trend_tags, tech_stack, color_mode, layout_type)
    assert "<button" in result and "MyButton" in result
    # Glassmorphism on button in dark mode might be subtle, specific class check depends on apply_trend_styles
    assert "bg-gray-800/10" in result or "bg-white/20" in result or "bg-gray-700/20" in result 
    assert "text-white" in result
    print("test_create_code_original_button_dark_glass PASSED")

def test_create_code_original_login_light_minimal():
    inspiration_summary = "A simple login form for my new website"
    trend_tags = ["minimalism", "light_mode", "login"] # Added login keyword
    result = generate_code.create_code(inspiration_summary, trend_tags, "react-tailwind", "light", "component")
    assert "<form" in result and "LoginForm" in result
    assert "bg-white" in result # Minimalism light
    assert "shadow-none" in result
    assert "p-4" in result
    print("test_create_code_original_login_light_minimal PASSED")

def test_create_code_unknown_tech_stack():
    result = generate_code.create_code("Any component", [], "vue", "light", "component")
    assert "not yet implemented" in result.lower()
    print("test_create_code_unknown_tech_stack PASSED")


if __name__ == "__main__":
    print("--- Running test_generate_code.py (Comprehensive) ---")
    test_apply_trend_styles_helper_contextual()
    
    test_generate_navbar_component()
    test_generate_footer_component()
    test_generate_hero_component()
    test_generate_feature_card_component()
    test_generate_testimonial_component()
    
    test_generate_full_page_with_hero()
    test_generate_full_page_with_features()
    
    test_styling_glassmorphism_serif_dark_hero()
    test_styling_minimalism_pastel_light_card()
    test_styling_modern_dark_navbar()
    
    test_keyword_priority_hero_over_card()
    test_fallback_to_button()
    
    test_create_code_original_button_dark_glass()
    test_create_code_original_login_light_minimal()
    test_create_code_unknown_tech_stack()
    
    print("--- All generate_code tests completed ---")
