from typing import List, Dict, Callable, Any
import logging # Added
# Import the template registry
from .code_templates.react_tailwind_templates import REACT_TAILWIND_TEMPLATES

# Get a logger instance for this module
logger = logging.getLogger(__name__)

# Component keyword mapping
# Maps keywords (lowercase) to component names as defined in REACT_TAILWIND_TEMPLATES.
COMPONENT_KEYWORDS_MAP: Dict[str, str] = {
    "navbar": "Navbar",
    "navigation": "Navbar",
    "header": "Navbar",
    "menu": "Navbar",
    "footer": "Footer",
    "bottom-bar": "Footer",
    "hero": "Hero Section",
    "banner": "Hero Section",
    "jumbotron": "Hero Section",
    "landing intro": "Hero Section",
    "feature": "Features Section",  # Maps to the section containing feature cards
    "features": "Features Section", # Added for clarity
    "highlight": "Features Section",# Can be part of a feature
    "info card": "Features Section",# Feature cards can be info cards
    "testimonial": "Testimonial",
    "quote": "Testimonial",
    "review": "Testimonial",
    "modal": "Modal", # Added Modal
    # Note: "Login Form", "Button", "Card" were not part of the specified refactoring scope
    # for the new file structure. If needed, they would be added to REACT_TAILWIND_TEMPLATES
    # and this map. For now, they are omitted to align with the refactored templates.
    # "login form": "Login Form",
    # "login": "Login Form",
    # "button": "Button",
    # "card": "Card",
}

# Prioritized list of keywords to resolve component type from prompt/summary.
# Order matters: more specific or primary components should come first.
KEYWORD_PRIORITY = [
    "landing intro", "hero", "banner", "jumbotron", # Hero first
    "navbar", "navigation", "header", "menu",    # Then Navbar
    "features", "feature", "highlight", "info card", # Then Features
    "testimonial", "quote", "review",            # Then Testimonial
    "modal",                                     # Then Modal
    "footer", "bottom-bar",                      # Footer last for full page
    # "login form", "login",
    # "card", "button"
]

def apply_trend_styles(
    base_styles: str, 
    trend_tags: List[str], 
    color_mode: str, 
    component_type: str = "Unknown" 
) -> str:
    # This function does not have print statements, so no logging changes needed here.
    # Logging for style application would be too verbose for typical use,
    # but could be added at DEBUG level if needed for deep debugging.
    additional_styles = []
    
    # 1. Color Mode Defaults
    if color_mode == "dark":
        additional_styles.append("text-white")
        if component_type not in ["Button", "Navbar", "Hero Section"]:
             additional_styles.append("bg-gray-800")
        if component_type == "Navbar":
            additional_styles.append("bg-gray-900 border-gray-700")
        elif component_type == "Hero Section":
             additional_styles.append("border-gray-700")
        elif component_type in ["Card", "Feature Card", "Login Form", "Testimonial"]:
            additional_styles.append("border-gray-700")
            if not any(s.startswith("bg-") and "opacity" not in s for s in additional_styles):
                additional_styles.append("bg-gray-800")
        elif component_type != "Button":
            additional_styles.append("border-gray-600")

    elif color_mode == "light":
        additional_styles.append("text-gray-900")
        if component_type not in ["Button", "Navbar", "Hero Section"]:
            additional_styles.append("bg-gray-50")
        if component_type == "Navbar":
            additional_styles.append("bg-white border-gray-200")
        elif component_type == "Hero Section":
             additional_styles.append("border-gray-200")
        elif component_type in ["Card", "Feature Card", "Login Form", "Testimonial"]:
            additional_styles.append("border-gray-200")
            if not any(s.startswith("bg-") and "opacity" not in s for s in additional_styles):
                 additional_styles.append("bg-white")
    
    # 2. Trend-specific styles
    if "cyberpunk" in trend_tags:
        additional_styles = [s for s in additional_styles if not s.startswith("rounded-")] 
        additional_styles.append("rounded-none")
        additional_styles.append("text-lime-400") 
        if color_mode != "dark":
            additional_styles = [s for s in additional_styles if not s.startswith("bg-")] 
            additional_styles.append("bg-black text-white") 
        if component_type in ["Card", "Feature Card", "Hero Section", "Navbar"]:
             additional_styles.append("border-2 border-pink-500")

    if "glassmorphism" in trend_tags:
        temp_styles = [s for s in additional_styles if not (s.startswith("bg-gray") or (s.startswith("bg-white") and "/10" not in s and "/20" not in s and "/30" not in s))]
        additional_styles = temp_styles
        additional_styles.append("backdrop-blur-lg shadow-lg")
        if component_type == "Navbar":
            base_bg = "bg-white/30" if color_mode == "light" else "bg-gray-700/30"
            border = "border-white/20" if color_mode == "light" else "border-gray-600/50"
            additional_styles.append(f"{base_bg} backdrop-blur-md {border}")
        elif component_type in ["Card", "Feature Card", "Login Form", "Hero Section"]:
            base_bg = "bg-white/10" if color_mode == "light" else "bg-gray-800/10"
            border = "border-white/20" if color_mode == "light" else "border-gray-700/50"
            additional_styles.append(f"{base_bg} {border}")
        else: 
            base_bg = "bg-white/20" if color_mode == "light" else "bg-gray-700/20"
            additional_styles.append(f"{base_bg} border-gray-200") 
        if color_mode == "dark": 
            if "text-white" not in additional_styles and "text-lime-400" not in additional_styles : additional_styles.append("text-white")
    
    if "handwritten_fonts" in trend_tags:
        additional_styles = [s for s in additional_styles if not s.startswith("font-")] 
        additional_styles.append("font-['cursive']")

    if "luxury_aesthetic" in trend_tags:
        if "font-serif" not in additional_styles and "font-['cursive']" not in additional_styles:
            additional_styles = [s for s in additional_styles if not s.startswith("font-")]
            additional_styles.append("font-serif")
        if color_mode == "light":
            if component_type in ["Card", "Feature Card", "Navbar", "Hero Section"]:
                additional_styles.append("border-yellow-400") 
            additional_styles.append("text-yellow-700") 
        else: 
            additional_styles.append("text-yellow-300") 
            if component_type in ["Card", "Feature Card", "Navbar", "Hero Section"]:
                additional_styles.append("border-yellow-500")
        if "minimalism" in trend_tags:
            additional_styles = [s for s in additional_styles if not s.startswith("shadow-")]
            additional_styles.append("shadow-none")

    if "minimalism" in trend_tags:
        additional_styles = [s for s in additional_styles if not s.startswith("shadow-")]
        additional_styles.append("shadow-none") 
        if component_type in ["Card", "Feature Card", "Button", "Login Form", "Hero Section", "Testimonial"]:
            additional_styles = [s for s in additional_styles if not (s.startswith("p-") or s.startswith("py-") or s.startswith("px-"))]
            additional_styles.append("p-4") 
        if color_mode != "dark" and "glassmorphism" not in trend_tags and "pastel_colors" not in trend_tags:
            additional_styles = [s for s in additional_styles if not (s.startswith("bg-gray") or s.startswith("bg-blue-") or s.startswith("bg-white"))] 
            additional_styles.append("bg-white") 
        current_border_classes = [s for s in (base_styles.split() + additional_styles) if s.startswith("border")]
        if not any(b_class == "border-0" or b_class == "border-transparent" for b_class in current_border_classes):
            if not any(b_class == "border" or (b_class.startswith("border-") and b_class != "border-gray-200") for b_class in current_border_classes):
                 additional_styles.append("border")
            if "border-gray-200" not in additional_styles: additional_styles.append("border-gray-200")
    
    if "modern_ui" in trend_tags:
        if "cyberpunk" not in trend_tags: 
            additional_styles = [s for s in additional_styles if not s.startswith("rounded-")]
            additional_styles.append("rounded-lg") 
        if "glassmorphism" not in trend_tags and "minimalism" not in trend_tags:
            additional_styles = [s for s in additional_styles if not s.startswith("shadow-")] 
            additional_styles.append("shadow-md") 

    if "pastel_colors" in trend_tags and color_mode != "dark":
        if component_type in ["Hero Section", "Card", "Feature Card", "Testimonial", "Navbar", "Button"]:
            if "glassmorphism" not in trend_tags: 
                additional_styles = [s for s in additional_styles if not (s.startswith("bg-gray") or s.startswith("bg-white"))]
                additional_styles.append("bg-blue-100") 
            if component_type == "Navbar" or component_type == "Button":
                 additional_styles.append("text-blue-800") 
            elif "glassmorphism" not in trend_tags : 
                 additional_styles.append("text-gray-700")
    
    if "playful_aesthetic" in trend_tags:
        if "cyberpunk" not in trend_tags: 
            additional_styles = [s for s in additional_styles if not s.startswith("rounded-")]
            additional_styles.append("rounded-xl") 
        if "pastel_colors" not in trend_tags and color_mode != "dark" and component_type in ["Button", "Feature Card"]:
             additional_styles.append("border-2 border-sky-500")

    if "serif_fonts" in trend_tags:
        if "handwritten_fonts" not in trend_tags: 
             additional_styles = [s for s in additional_styles if not s.startswith("font-")]
             additional_styles.append("font-serif")

    if "corporate_aesthetic" in trend_tags:
        if not any(f in additional_styles for f in ["font-serif", "font-['cursive']"]):
            additional_styles = [s for s in additional_styles if not s.startswith("font-")]
            additional_styles.append("font-sans")
        if "modern_ui" not in trend_tags and "minimalism" not in trend_tags and "cyberpunk" not in trend_tags:
            additional_styles = [s for s in additional_styles if not s.startswith("rounded-")]
            additional_styles.append("rounded-md") 
            additional_styles = [s for s in additional_styles if not s.startswith("shadow-")]
            additional_styles.append("shadow-sm") 
        if component_type == "Button": 
             additional_styles.append("bg-blue-600 text-white hover:bg-blue-700")

    base_style_list = base_styles.split()
    final_styles_list = base_style_list + additional_styles
    return " ".join(list(dict.fromkeys(final_styles_list)))

def find_component_from_keywords(text_to_scan: str) -> Dict[str, Any]:
    text_lower = text_to_scan.lower()
    for keyword in KEYWORD_PRIORITY:
        if keyword in text_lower:
            return COMPONENT_KEYWORDS_MAP[keyword]
    return {} 

def create_code(
    inspiration_summary: str, trend_tags: List[str], tech_stack: str,
    color_mode: str, layout_type: str
) -> str:
    logger.info(f"Generating code for tech_stack: {tech_stack}, layout: {layout_type}, color: {color_mode}")
    logger.debug(f"Inspiration: '{inspiration_summary}', Trends: {trend_tags}")

    if tech_stack != "react-tailwind":
        logger.warning(f"Code generation for tech_stack '{tech_stack}' is not yet implemented.")
        return f"Code generation for tech_stack '{tech_stack}' is not yet implemented."

    searchable_text = (inspiration_summary.lower() + " " + " ".join(trend_tags).lower() + " " + layout_type.lower()).strip()
    # Include layout_type in searchable_text to catch "full page with hero and footer"

    if layout_type == "full-page":
        return assemble_full_page_layout(searchable_text, trend_tags, color_mode)
    elif layout_type == "component":
        logger.info(f"Attempting to generate a single component based on keywords: '{searchable_text[:100]}...'")
        component_name_to_generate = find_component_from_keywords(searchable_text)

        if not component_name_to_generate: # Fallback if no keyword matches
            logger.info("No specific component keywords matched for single component. Defaulting to 'Navbar'.")
            component_name_to_generate = "Navbar" 
            if "feature" in searchable_text or "features" in searchable_text: 
                component_name_to_generate = "Features Section"

        template_string = REACT_TAILWIND_TEMPLATES.get(component_name_to_generate)

        if template_string:
            logger.info(f"Selected '{component_name_to_generate}' component template.")
            # TODO: Revisit styling application for single components as well.
            # final_styles = apply_trend_styles("", trend_tags, color_mode, component_name_to_generate)
            # styled_template_string = template_string.replace('className=""', f'className="{final_styles}"') # Example
            styled_template_string = template_string # Using raw template

            return styled_template_string
        else:
            logger.error(f"Could not find a template for '{component_name_to_generate}'.")
            return f"Error: Could not find a template for '{component_name_to_generate}'."
    
    logger.error(f"Invalid layout_type '{layout_type}' or other configuration issue.")
    return "Error: Invalid layout_type or other configuration issue."

if __name__ == '__main__':
    # This block is for direct testing of this module.
    import sys
    import os
    # Temporarily add the parent directory of 'actions' to sys.path to allow relative imports to work
    # when running this script directly.
    # This assumes the script is in 'frontend-trend-builder/actions/generate_code.py'
    # and we want 'frontend-trend-builder' to be on the path.
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir) # This should be 'frontend-trend-builder'
    sys.path.insert(0, parent_dir)
    
    # Now that sys.path is adjusted, we can re-import with the correct package context if needed,
    # but the initial imports at the top of the file should now work when script is run directly.
    # Forcing a re-import or dynamic import here can get complex; the goal is for top-level imports to succeed.

    # It's crucial that the imports at the top of the file:
    # from .code_templates.react_tailwind_templates import REACT_TAILWIND_TEMPLATES
    # can now resolve 'code_templates' as a package within 'actions' (if actions is seen as top-level due to sys.path)
    # or resolve 'actions.code_templates' if 'frontend-trend-builder' is the top-level.
    # The key is that `parent_dir` (frontend-trend-builder) is on sys.path.
    # So, imports should ideally be `from actions.code_templates...` if this file is run.
    # However, the file is written with `from .code_templates...` expecting `actions` to be a package.

    # Let's try to make the existing relative imports work by ensuring the top-level 'actions'
    # can be found relative to the 'frontend-trend-builder' directory that we added to path.
    # This is tricky because the script itself is *in* 'actions'.
    # The most straightforward way if running `python actions/generate_code.py` from `frontend-trend-builder`
    # is that `from .code_templates...` should work if `actions` is treated as a package.
    
    # The `sys.path.insert(0, parent_dir)` makes `frontend-trend-builder` the first place to look.
    # Python will then look for `actions.code_templates...` if we changed the import.
    # With `from .code_templates...`, it implies `generate_code.py` is part of a package,
    # and it looks for `code_templates` as a sibling package/module within that same package.

    # The most robust way to test this script directly is usually to run it as a module
    # `python -m actions.generate_code` from the `frontend-trend-builder` directory.
    # The sys.path modification here is an attempt to make direct execution `python actions/generate_code.py` work.

    if not logging.getLogger().hasHandlers() or logging.getLogger().level > logging.DEBUG:
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    logger.info("--- Running generate_code.py standalone examples (with sys.path modification for direct execution) ---")

    # Test 1: Cyberpunk Hero Section
    print("\n--- Test 1: Cyberpunk Hero Section (Component) ---")
    inspiration_cyber_hero = "A cyberpunk hero banner for a tech noir game website."
    trends_cyber_hero = ["cyberpunk", "dark_mode", "hero"]
    code_cyber_hero = create_code(inspiration_cyber_hero, trends_cyber_hero, "react-tailwind", "dark", "component")
    print(f"Generated Cyberpunk Hero Code (first 300 chars):\n{code_cyber_hero[:300]}...")
    assert "HeroSection" in code_cyber_hero

    # Test 2: Playful Features Section (Component)
    print("\n--- Test 2: Playful Features Section (Component) ---")
    inspiration_playful_feature = "A playful set of feature cards."
    trends_playful_feature = ["playful_aesthetic", "light_mode", "features"]
    code_playful_feature = create_code(inspiration_playful_feature, trends_playful_feature, "react-tailwind", "light", "component")
    print(f"Generated Playful Features Section Code (first 300 chars):\n{code_playful_feature[:300]}...")
    assert "FeaturesSection" in code_playful_feature

    # Test 3: Full Page - Navbar, Hero, Two Features, Footer
    print("\n--- Test 3: Full Page - Navbar, Hero, Two Features, Footer ---")
    inspiration_full_custom = "Create a page with a navbar, a hero section, then two features sections, and finally a footer."
    # trends_full_custom = ["hero", "features", "navbar", "footer"] # Keywords help find_components_in_prompt
    trends_full_custom = [] # Let prompt drive the component selection
    code_full_custom = create_code(inspiration_full_custom, trends_full_custom, "react-tailwind", "light", "full-page")
    print(f"Generated Custom Full Page Code (first 400 chars):\n{code_full_custom[:400]}...")
    assert "const FullPageLayout =" in code_full_custom
    assert code_full_custom.count("<Navbar />") == 1 # Assuming templates are self-closing or simple calls
    assert code_full_custom.count("<HeroSection />") == 1
    assert code_full_custom.count("<FeaturesSection />") == 2
    assert code_full_custom.count("<Footer />") == 1
    # Check order (simplified check)
    navbar_idx = code_full_custom.find("<Navbar />")
    hero_idx = code_full_custom.find("<HeroSection />")
    features1_idx = code_full_custom.find("<FeaturesSection />")
    features2_idx = code_full_custom.find("<FeaturesSection />", features1_idx + 1) if features1_idx != -1 else -1
    footer_idx = code_full_custom.find("<Footer />")
    assert -1 < navbar_idx < hero_idx < features1_idx < features2_idx < footer_idx, "Full page component order incorrect for Test 3"


    # Test 4: Full Page - Default (Navbar, Features, Footer) if no components in prompt
    print("\n--- Test 4: Full Page - Default Layout ---")
    inspiration_full_default = "A simple website."
    trends_full_default = ["minimalism"]
    code_full_default = create_code(inspiration_full_default, trends_full_default, "react-tailwind", "light", "full-page")
    print(f"Generated Default Full Page Code (first 400 chars):\n{code_full_default[:400]}...")
    assert "const FullPageLayout =" in code_full_default
    assert "<Navbar />" in code_full_default
    assert "<HeroSection />" not in code_full_default # Default doesn't include hero unless specified
    assert "<FeaturesSection />" in code_full_default
    assert "<Footer />" in code_full_default

    # Test 5: Full Page - Only Navbar and Footer
    print("\n--- Test 5: Full Page - Navbar and Footer only ---")
    inspiration_nf = "A page with just a navbar and footer."
    trends_nf = []
    code_nf = create_code(inspiration_nf, trends_nf, "react-tailwind", "dark", "full-page")
    print(f"Generated Navbar-Footer Page Code (first 400 chars):\n{code_nf[:400]}...")
    assert "const FullPageLayout =" in code_nf
    assert "<Navbar />" in code_nf
    assert "<HeroSection />" not in code_nf
    assert "<FeaturesSection />" not in code_nf
    assert "<Testimonial />" not in code_nf
    assert "<Footer />" in code_nf
    navbar_idx = code_nf.find("<Navbar />")
    footer_idx = code_nf.find("<Footer />")
    assert -1 < navbar_idx < footer_idx, "Navbar/Footer order incorrect for Test 5"


    # Test 6: Modal Component (remains a single component generation)
    print("\n--- Test 6: Modal Component (Single) ---")
    inspiration_modal = "A modal dialog for user confirmation."
    trends_modal = ["modal", "modern_ui"]
    code_modal = create_code(inspiration_modal, trends_modal, "react-tailwind", "light", "component")
    print(f"Generated Modal Code (first 300 chars):\n{code_modal[:300]}...")
    assert "Modal" in code_modal # Checks if the Modal component name is in the string
    assert "isOpen" in code_modal # Check for a prop specific to the modal template
    assert "const FullPageLayout =" not in code_modal # Ensure it's not a full page

    logger.info("--- End of generate_code.py standalone examples ---")
