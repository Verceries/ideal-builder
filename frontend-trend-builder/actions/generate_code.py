from typing import List, Dict, Callable, Any
import logging # Added
# Import all templates from react_tailwind_templates
from .code_templates import react_tailwind_templates 

# Get a logger instance for this module
logger = logging.getLogger(__name__) # Added

# Component keyword mapping
# Maps keywords (lowercase) to template functions and their default display names for logging/selection.
COMPONENT_KEYWORDS_MAP: Dict[str, Dict[str, Any]] = {
    "navbar": {"func": react_tailwind_templates.get_navbar_template, "name": "Navbar"},
    "navigation": {"func": react_tailwind_templates.get_navbar_template, "name": "Navbar"},
    "header": {"func": react_tailwind_templates.get_navbar_template, "name": "Navbar"},
    "menu": {"func": react_tailwind_templates.get_navbar_template, "name": "Navbar"},
    "footer": {"func": react_tailwind_templates.get_footer_template, "name": "Footer"},
    "bottom-bar": {"func": react_tailwind_templates.get_footer_template, "name": "Footer"},
    "hero": {"func": react_tailwind_templates.get_hero_template, "name": "Hero Section"},
    "banner": {"func": react_tailwind_templates.get_hero_template, "name": "Hero Section"},
    "jumbotron": {"func": react_tailwind_templates.get_hero_template, "name": "Hero Section"},
    "landing intro": {"func": react_tailwind_templates.get_hero_template, "name": "Hero Section"},
    "feature": {"func": react_tailwind_templates.get_feature_card_template, "name": "Feature Card"}, 
    "highlight": {"func": react_tailwind_templates.get_feature_card_template, "name": "Feature Card"},
    "info card": {"func": react_tailwind_templates.get_feature_card_template, "name": "Feature Card"},
    "testimonial": {"func": react_tailwind_templates.get_testimonial_template, "name": "Testimonial"},
    "quote": {"func": react_tailwind_templates.get_testimonial_template, "name": "Testimonial"},
    "review": {"func": react_tailwind_templates.get_testimonial_template, "name": "Testimonial"},
    "login form": {"func": react_tailwind_templates.get_login_form_template, "name": "Login Form"},
    "login": {"func": react_tailwind_templates.get_login_form_template, "name": "Login Form"},
    "button": {"func": react_tailwind_templates.get_button_template, "name": "Button"},
    "card": {"func": react_tailwind_templates.get_card_template, "name": "Card"}, 
}

KEYWORD_PRIORITY = [
    "landing intro", "info card", "login form", 
    "navbar", "navigation", "header", "menu", 
    "footer", "bottom-bar", 
    "hero", "banner", "jumbotron", 
    "feature", "testimonial", "quote", "review", "highlight",
    "login", "card", "button" 
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
    # Replaced print with logger.info and logger.debug
    logger.info(f"Generating code for tech_stack: {tech_stack}, layout: {layout_type}, color: {color_mode}")
    logger.debug(f"Inspiration: '{inspiration_summary}', Trends: {trend_tags}")

    if tech_stack != "react-tailwind":
        logger.warning(f"Code generation for tech_stack '{tech_stack}' is not yet implemented.")
        return f"Code generation for tech_stack '{tech_stack}' is not yet implemented."

    searchable_text = inspiration_summary.lower() + " " + " ".join(trend_tags).lower()
    generated_components: List[str] = []

    if layout_type == "full-page":
        logger.info("Attempting to generate a full-page layout.")
        page_components_config = [
            {"name": "Navbar", "func": react_tailwind_templates.get_navbar_template, "params": {"logoText": "MyApp"}, "required": True},
        ]
        hero_keywords_present = any(kw in searchable_text for kw in ["hero", "banner", "jumbotron", "landing intro"])
        if hero_keywords_present:
            page_components_config.append(
                {"name": "Hero Section", "func": react_tailwind_templates.get_hero_template, 
                 "params": {"heading": "Welcome!", "subheading": "Discover our amazing features."}, "required": False}
            )
        else: 
            page_components_config.append({"name": "Feature Section Start", "code": "\n<!-- Feature Section -->\n<div class='container mx-auto py-8 grid md:grid-cols-3 gap-6'>", "required": False})
            for i in range(3): 
                page_components_config.append(
                    {"name": f"FeatureCard{i+1}", "func": react_tailwind_templates.get_feature_card_template,
                     "params": {"title": f"Feature {i+1}", "description": "Detail about this cool feature.", "iconPlaceholder": True}, "required": False}
                )
            page_components_config.append({"name": "Feature Section End", "code": "</div>", "required": False})
        page_components_config.append({"name": "Footer", "func": react_tailwind_templates.get_footer_template, "params": {}, "required": True})

        for comp_config in page_components_config:
            component_code = ""
            component_name_for_style = comp_config.get("name", "Unknown")
            if "FeatureCard" in component_name_for_style: component_name_for_style = "Feature Card"

            if "code" in comp_config: 
                component_code = comp_config["code"]
            elif "func" in comp_config:
                template_func: Callable = comp_config["func"]
                params: Dict[str, Any] = comp_config.get("params", {})
                component_base_styles = "" 
                final_styles = apply_trend_styles(component_base_styles, trend_tags, color_mode, component_name_for_style)
                
                if template_func in [react_tailwind_templates.get_button_template, 
                                     react_tailwind_templates.get_card_template,
                                     react_tailwind_templates.get_login_form_template]:
                    params["custom_styles"] = final_styles
                else:
                    params["styles"] = final_styles
                
                logger.debug(f"Generating page component '{comp_config['name']}' (type: {component_name_for_style}) with params: {params}")
                component_code = template_func(**params)
            
            if component_code: generated_components.append(f"\n{/* --- {comp_config['name']} Start --- */}\n{component_code}\n{/* --- {comp_config['name']} End --- */}\n")
        return "\n".join(generated_components)

    elif layout_type == "component":
        logger.info(f"Attempting to generate a single component based on keywords: '{searchable_text[:100]}...'")
        chosen_component_info = find_component_from_keywords(searchable_text)
        template_func: Callable = None
        template_params: Dict[str, Any] = {}
        component_name_for_style = "Unknown"

        if chosen_component_info:
            template_func = chosen_component_info["func"]
            component_name_for_style = chosen_component_info["name"]
            logger.info(f"Keyword match: Selected '{component_name_for_style}' component.")
            if component_name_for_style == "Navbar": template_params = {"logoText": "MyApp"}
            elif component_name_for_style == "Footer": template_params = {}
            elif component_name_for_style == "Hero Section": template_params = {"heading": "Hero Title", "subheading": "Hero subtitle text."}
            elif component_name_for_style == "Feature Card": template_params = {"title": "Feature", "description": "Description of feature.", "iconPlaceholder": True}
            elif component_name_for_style == "Testimonial": template_params = {"quote": "This is great!", "authorName": "Satisfied User"}
            elif component_name_for_style == "Login Form": pass
            elif component_name_for_style == "Button": template_params["text"] = "Dynamic Button"
            elif component_name_for_style == "Card": template_params = {"title": "Dynamic Card", "content": "Generated card content."}
        else: 
            logger.info("No specific new component keywords matched. Falling back to general components.")
            if "login" in searchable_text:
                template_func, component_name_for_style = react_tailwind_templates.get_login_form_template, "Login Form"
            elif "card" in searchable_text: 
                template_func, component_name_for_style = react_tailwind_templates.get_card_template, "Card"
                template_params = {"title": "Generic Card", "content": "Some card content."}
            else: 
                template_func, component_name_for_style = react_tailwind_templates.get_button_template, "Button"
                template_params = {"text": "Default Button"}
            logger.info(f"Fallback: Selected '{component_name_for_style}' component.")

        component_base_styles = "" 
        final_styles = apply_trend_styles(component_base_styles, trend_tags, color_mode, component_name_for_style)
        
        if template_func in [react_tailwind_templates.get_button_template, 
                               react_tailwind_templates.get_card_template,
                               react_tailwind_templates.get_login_form_template]:
            template_params["custom_styles"] = final_styles
        else:
            template_params["styles"] = final_styles

        if template_func:
            logger.debug(f"Generating single component '{component_name_for_style}' with params: {template_params}")
            return template_func(**template_params)
        else: 
            logger.error("Could not determine a suitable template for React-Tailwind component.")
            return "Error: Could not determine a suitable template for React-Tailwind component."
    
    logger.error(f"Invalid layout_type '{layout_type}' or other configuration issue.")
    return "Error: Invalid layout_type or other configuration issue."

if __name__ == '__main__':
    # This block is for direct testing of this module.
    # It should use its own logging config if main.py's root logger isn't already set up.
    if not logging.getLogger().hasHandlers() or logging.getLogger().level > logging.DEBUG:
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    logger.info("--- Running generate_code.py standalone examples (using module logger) ---") # Changed from print

    # Test 1: Cyberpunk Hero Section
    print("\n--- Test 1: Cyberpunk Hero Section (Dark) ---") # Keep print for CLI output
    inspiration_cyber_hero = "A cyberpunk hero banner for a tech noir game website."
    trends_cyber_hero = ["cyberpunk", "dark_mode", "hero"]
    code_cyber_hero = create_code(inspiration_cyber_hero, trends_cyber_hero, "react-tailwind", "dark", "component")
    print(f"Generated Cyberpunk Hero Code (first 300 chars):\n{code_cyber_hero[:300]}...")
    assert "HeroSection" in code_cyber_hero
    assert "text-lime-400" in code_cyber_hero 
    assert "rounded-none" in code_cyber_hero
    assert "border-pink-500" in code_cyber_hero 

    # ... (other print statements in if __name__ == '__main__' block are kept for CLI testing) ...
    print("\n--- Test 2: Playful Feature Card (Light, Handwritten) ---")
    inspiration_playful_feature = "A playful feature card with handwritten title."
    trends_playful_feature = ["playful_aesthetic", "handwritten_fonts", "light_mode", "feature"]
    code_playful_feature = create_code(inspiration_playful_feature, trends_playful_feature, "react-tailwind", "light", "component")
    print(f"Generated Playful Feature Card Code (first 300 chars):\n{code_playful_feature[:300]}...")
    assert "FeatureCard" in code_playful_feature
    assert "font-['cursive']" in code_playful_feature
    assert "rounded-xl" in code_playful_feature
    assert "border-sky-500" in code_playful_feature 

    print("\n--- Test 3: Corporate Navbar with Luxury Accents (Light) ---")
    inspiration_corp_luxury_nav = "A corporate navbar with a touch of luxury and serif font."
    trends_corp_luxury_nav = ["corporate_aesthetic", "luxury_aesthetic", "serif_fonts", "light_mode", "navbar"]
    code_corp_luxury_nav = create_code(inspiration_corp_luxury_nav, trends_corp_luxury_nav, "react-tailwind", "light", "component")
    print(f"Generated Corporate Luxury Navbar Code (first 300 chars):\n{code_corp_luxury_nav[:300]}...")
    assert "Navbar" in code_corp_luxury_nav
    assert "font-serif" in code_corp_luxury_nav 
    assert "border-yellow-400" in code_corp_luxury_nav 
    assert "rounded-md" in code_corp_luxury_nav or "rounded-lg" in code_corp_luxury_nav 

    print("\n--- Test 4: Full Page Cyberpunk Theme ---")
    inspiration_full_cyber = "A full website with a cyberpunk theme, including a hero section."
    trends_full_cyber = ["cyberpunk", "hero"] 
    code_full_cyber = create_code(inspiration_full_cyber, trends_full_cyber, "react-tailwind", "dark", "full-page") 
    print(f"Generated Full Cyberpunk Page Code (first 400 chars):\n{code_full_cyber[:400]}...")
    assert "Navbar" in code_full_cyber and "HeroSection" in code_full_cyber and "Footer" in code_full_cyber
    assert "text-lime-400" in code_full_cyber
    assert "bg-black" in code_full_cyber or "bg-gray-900" in code_full_cyber
    assert "rounded-none" in code_full_cyber
    
    print("\n--- Test 5: Button - Corporate & Playful Mix ---")
    insp_corp_play_button = "A button for a fun corporate event."
    trends_corp_play_button = ["corporate_aesthetic", "playful_aesthetic", "button", "light_mode"]
    code_corp_play_button = create_code(insp_corp_play_button, trends_corp_play_button, "react-tailwind", "light", "component")
    print(f"Generated Corp Playful Button (first 300 chars):\n{code_corp_play_button[:300]}...")
    assert "MyButton" in code_corp_play_button
    assert "rounded-xl" in code_corp_play_button 
    assert "font-sans" in code_corp_play_button 
    assert "bg-blue-600" not in code_corp_play_button 

    logger.info("--- End of generate_code.py standalone examples ---") # Changed from print
