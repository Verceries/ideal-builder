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
    light_button_styles = generate_code.apply_trend_styles("p-2", [], "light", "Button") 
    assert "text-gray-900" in light_button_styles and "p-2" in light_button_styles
    assert "bg-gray-50" not in light_button_styles 
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
    assert "bg-blue-100" not in pastel_dark_card 
    print("apply_trend_styles: Pastel Dark Card (no pastel) OK")
    
    # Serif Fonts
    serif_styles = generate_code.apply_trend_styles("", ["serif_fonts"], "light", "Unknown")
    assert "font-serif" in serif_styles
    print("apply_trend_styles: Serif Fonts OK")

    # Minimalism
    minimal_card_light = generate_code.apply_trend_styles("p-6", ["minimalism"], "light", "Card")
    assert "shadow-none" in minimal_card_light and "bg-white" in minimal_card_light and "p-4" in minimal_card_light
    assert "p-6" not in minimal_card_light 
    print("apply_trend_styles: Minimalism Card Light OK")

    minimal_hero_dark = generate_code.apply_trend_styles("", ["minimalism"], "dark", "Hero Section")
    assert "shadow-none" in minimal_hero_dark and "bg-white" not in minimal_hero_dark 
    print("apply_trend_styles: Minimalism Hero Dark OK")

    # Modern UI
    modern_button_light = generate_code.apply_trend_styles("", ["modern_ui"], "light", "Button")
    assert "rounded-lg" in modern_button_light and "shadow-md" in modern_button_light
    print("apply_trend_styles: Modern UI Button Light OK")

    modern_minimal_card = generate_code.apply_trend_styles("", ["modern_ui", "minimalism"], "light", "Card")
    assert "rounded-lg" in modern_minimal_card and "shadow-none" in modern_minimal_card 
    print("apply_trend_styles: Modern UI Minimal Card OK")
    
    glass_minimal_card = generate_code.apply_trend_styles("", ["glassmorphism", "minimalism"], "light", "Card")
    assert "backdrop-blur-lg" in glass_minimal_card 
    assert "shadow-lg" in glass_minimal_card 
    assert "bg-white/10" in glass_minimal_card 
    print("apply_trend_styles: Glassmorphism Minimal Card OK")

    # --- New Core Trend Styling Tests for apply_trend_styles ---
    cyberpunk_styles = generate_code.apply_trend_styles("", ["cyberpunk"], "dark", "Hero Section")
    assert "text-lime-400" in cyberpunk_styles and "rounded-none" in cyberpunk_styles
    assert "border-pink-500" in cyberpunk_styles # Optional border
    print("apply_trend_styles: Cyberpunk Hero Dark OK")

    handwritten_styles = generate_code.apply_trend_styles("", ["handwritten_fonts"], "light", "Testimonial")
    assert "font-['cursive']" in handwritten_styles
    print("apply_trend_styles: Handwritten Fonts Testimonial OK")

    luxury_styles_light = generate_code.apply_trend_styles("", ["luxury_aesthetic"], "light", "Card")
    assert "font-serif" in luxury_styles_light and "border-yellow-400" in luxury_styles_light
    print("apply_trend_styles: Luxury Aesthetic Card Light OK")
    
    luxury_styles_dark = generate_code.apply_trend_styles("", ["luxury_aesthetic"], "dark", "Navbar")
    assert "font-serif" in luxury_styles_dark and "text-yellow-300" in luxury_styles_dark
    print("apply_trend_styles: Luxury Aesthetic Navbar Dark OK")

    playful_styles = generate_code.apply_trend_styles("", ["playful_aesthetic"], "light", "Button")
    assert "rounded-xl" in playful_styles and "border-sky-500" in playful_styles
    print("apply_trend_styles: Playful Aesthetic Button OK")

    corporate_styles = generate_code.apply_trend_styles("", ["corporate_aesthetic"], "light", "Login Form")
    assert "font-sans" in corporate_styles and "rounded-md" in corporate_styles and "shadow-sm" in corporate_styles
    print("apply_trend_styles: Corporate Aesthetic Login Form OK")

    corporate_button_styles = generate_code.apply_trend_styles("", ["corporate_aesthetic"], "light", "Button")
    assert "bg-blue-600" in corporate_button_styles and "text-white" in corporate_button_styles
    print("apply_trend_styles: Corporate Aesthetic Button specific OK")


# --- Test Generation of Specific Components ---
def test_generate_navbar_component():
    result = generate_code.create_code("A sleek navbar", ["modern_ui"], "react-tailwind", "light", "component")
    assert "Navbar" in result and "<nav" in result and "Logo" in result
    assert "rounded-lg" in result 
    print("test_generate_navbar_component PASSED")

def test_generate_footer_component():
    result = generate_code.create_code("Page bottom-bar with copyright", ["dark_mode"], "react-tailwind", "dark", "component")
    assert "Footer" in result and "<footer>" in result and "© 2024" in result
    assert "bg-gray-800" in result or "bg-gray-900" in result 
    print("test_generate_footer_component PASSED")

# ... (other existing component generation tests remain the same) ...

def test_generate_hero_component():
    result = generate_code.create_code("Landing page hero section", ["serif_fonts"], "react-tailwind", "light", "component")
    assert "HeroSection" in result and "<section" in result and "Main Heading" in result
    assert "font-serif" in result
    print("test_generate_hero_component PASSED")

def test_generate_feature_card_component():
    result = generate_code.create_code("Info card about a feature", ["pastel_colors"], "react-tailwind", "light", "component")
    assert "FeatureCard" in result and "Feature Title" in result
    assert "bg-blue-100" in result 
    print("test_generate_feature_card_component PASSED")

def test_generate_testimonial_component():
    result = generate_code.create_code("User review quote", ["minimalism"], "react-tailwind", "dark", "component")
    assert "Testimonial" in result and "fantastic product" in result
    assert "shadow-none" in result 
    assert "bg-gray-800" in result 
    print("test_generate_testimonial_component PASSED")

# --- Test Full-Page Layout Generation (remains the same) ---
def test_generate_full_page_with_hero():
    summary = "A full landing page intro with a hero section and modern look."
    trends = ["modern_ui", "light_mode", "hero"]
    result = generate_code.create_code(summary, trends, "react-tailwind", "light", "full-page")
    assert "/* --- Navbar Start --- */" in result and "/* --- Navbar End --- */" in result
    assert "/* --- Hero Section Start --- */" in result and "/* --- Hero Section End --- */" in result
    assert "/* --- Footer Start --- */" in result and "/* --- Footer End --- */" in result
    assert "FeatureCard1" not in result 
    assert "rounded-lg" in result 
    print("test_generate_full_page_with_hero PASSED")

def test_generate_full_page_with_features():
    summary = "A full product features page, dark theme."
    trends = ["dark_mode"] 
    result = generate_code.create_code(summary, trends, "react-tailwind", "dark", "full-page")
    assert "/* --- Navbar Start --- */" in result
    assert "<!-- Feature Section -->" in result and "/* --- FeatureCard1 Start --- */" in result
    assert "/* --- Footer Start --- */" in result
    assert "HeroSection" not in result
    assert "bg-gray-900" in result 
    assert "bg-gray-800" in result 
    print("test_generate_full_page_with_features PASSED")

# --- Test Enhanced Styling Logic on Components (existing ones remain, add new ones below) ---
def test_styling_glassmorphism_serif_dark_hero():
    summary = "A hero section with glass and serif type."
    trends = ["glassmorphism", "serif_fonts", "dark_mode", "hero"]
    result = generate_code.create_code(summary, trends, "react-tailwind", "dark", "component")
    assert "HeroSection" in result and "font-serif" in result and "bg-gray-800/10" in result and "text-white" in result
    print("test_styling_glassmorphism_serif_dark_hero PASSED")

def test_styling_minimalism_pastel_light_card():
    summary = "A card that is very simple and has soft pastel colors."
    trends = ["minimalism", "pastel_colors", "light_mode", "card"]
    result = generate_code.create_code(summary, trends, "react-tailwind", "light", "component")
    assert "MyCard" in result and "shadow-none" in result and "bg-blue-100" in result and "p-4" in result
    print("test_styling_minimalism_pastel_light_card PASSED")

def test_styling_modern_dark_navbar():
    summary = "A modern navigation header for a dark website."
    trends = ["modern_ui", "dark_mode", "navbar"]
    result = generate_code.create_code(summary, trends, "react-tailwind", "dark", "component")
    assert "Navbar" in result and "rounded-lg" in result and "bg-gray-900" in result and "shadow-md" in result
    print("test_styling_modern_dark_navbar PASSED")

# --- New Tests for Core Trend Styling on create_code ---
def test_styling_cyberpunk_hero_dark():
    summary = "A cyberpunk hero section for a game."
    trends = ["cyberpunk", "dark_mode", "hero"]
    result = generate_code.create_code(summary, trends, "react-tailwind", "dark", "component")
    assert "HeroSection" in result
    assert "text-lime-400" in result
    assert "rounded-none" in result
    assert "border-pink-500" in result # Check for optional border too
    print("test_styling_cyberpunk_hero_dark PASSED")

def test_styling_handwritten_testimonial_light():
    summary = "A testimonial with a handwritten font."
    trends = ["handwritten_fonts", "light_mode", "testimonial"]
    result = generate_code.create_code(summary, trends, "react-tailwind", "light", "component")
    assert "Testimonial" in result
    assert "font-['cursive']" in result
    print("test_styling_handwritten_testimonial_light PASSED")

def test_styling_luxury_card_dark():
    summary = "A luxury product card in dark mode."
    trends = ["luxury_aesthetic", "dark_mode", "card"]
    result = generate_code.create_code(summary, trends, "react-tailwind", "dark", "component")
    assert "MyCard" in result
    assert "font-serif" in result # Luxury implies serif
    assert "text-yellow-300" in result # Gold-like text for dark
    assert "border-yellow-500" in result # Gold-like border for dark
    print("test_styling_luxury_card_dark PASSED")

def test_styling_playful_button_light():
    summary = "A playful button."
    trends = ["playful_aesthetic", "light_mode", "button"]
    result = generate_code.create_code(summary, trends, "react-tailwind", "light", "component")
    assert "MyButton" in result
    assert "rounded-xl" in result # Playful rounding
    assert "border-sky-500" in result # Playful border accent
    print("test_styling_playful_button_light PASSED")

def test_styling_corporate_navbar_light():
    summary = "A corporate navbar."
    trends = ["corporate_aesthetic", "light_mode", "navbar"]
    result = generate_code.create_code(summary, trends, "react-tailwind", "light", "component")
    assert "Navbar" in result
    assert "font-sans" in result # Corporate default font
    assert "rounded-md" in result or "rounded-lg" in result # Subtle or modern rounding
    assert "shadow-sm" in result or "shadow-md" in result # Subtle or modern shadow
    print("test_styling_corporate_navbar_light PASSED")

def test_styling_corporate_button_override():
    summary = "A corporate button that needs to be primary call to action."
    trends = ["corporate_aesthetic", "light_mode", "button"]
    result = generate_code.create_code(summary, trends, "react-tailwind", "light", "component")
    assert "MyButton" in result
    assert "bg-blue-600" in result and "text-white" in result # Specific corporate button styling
    print("test_styling_corporate_button_override PASSED")


# --- Test Keyword Prioritization and Fallbacks (remains the same) ---
def test_keyword_priority_hero_over_card():
    summary = "A hero banner that looks like a card." 
    trends = ["modern_ui", "light_mode", "hero", "card"] 
    result = generate_code.create_code(summary, trends, "react-tailwind", "light", "component")
    assert "HeroSection" in result and "MyCard" not in result
    print("test_keyword_priority_hero_over_card PASSED")

def test_fallback_to_button():
    summary = "Some very generic content piece for a website." 
    trends = ["modern_ui", "dark_mode"]
    result = generate_code.create_code(summary, trends, "react-tailwind", "dark", "component")
    assert "MyButton" in result and "Default Button" in result
    print("test_fallback_to_button PASSED")

# --- Original tests (adapted or kept if still valid) ---
def test_create_code_original_button_dark_glass():
    inspiration_summary = "A cool glassmorphic button for a dark themed UI"
    trend_tags = ["glassmorphism", "dark_mode", "button"] 
    result = generate_code.create_code(inspiration_summary, trend_tags, "react-tailwind", "dark", "component")
    assert "<button" in result and "MyButton" in result
    assert "bg-gray-800/10" in result or "bg-white/20" in result or "bg-gray-700/20" in result 
    assert "text-white" in result
    print("test_create_code_original_button_dark_glass PASSED")

def test_create_code_original_login_light_minimal():
    inspiration_summary = "A simple login form for my new website"
    trend_tags = ["minimalism", "light_mode", "login"] 
    result = generate_code.create_code(inspiration_summary, trend_tags, "react-tailwind", "light", "component")
    assert "<form" in result and "LoginForm" in result and "bg-white" in result and "shadow-none" in result and "p-4" in result
    print("test_create_code_original_login_light_minimal PASSED")

def test_create_code_unknown_tech_stack():
    result = generate_code.create_code("Any component", [], "vue", "light", "component")
    assert "not yet implemented" in result.lower()
    print("test_create_code_unknown_tech_stack PASSED")


if __name__ == "__main__":
    print("--- Running test_generate_code.py (Comprehensive with New Core Trends) ---")
    test_apply_trend_styles_helper_contextual() # Includes new core trends
    
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

    # New specific styling tests for create_code
    test_styling_cyberpunk_hero_dark()
    test_styling_handwritten_testimonial_light()
    test_styling_luxury_card_dark()
    test_styling_playful_button_light()
    test_styling_corporate_navbar_light()
    test_styling_corporate_button_override()
    
    test_keyword_priority_hero_over_card()
    test_fallback_to_button()
    
    test_create_code_original_button_dark_glass()
    test_create_code_original_login_light_minimal()
    test_create_code_unknown_tech_stack()
    
    print("--- All generate_code tests completed ---")
