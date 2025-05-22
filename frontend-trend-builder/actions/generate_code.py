from typing import List, Dict, Callable, Any
# Import all templates from react_tailwind_templates
from .code_templates import react_tailwind_templates 

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
            if "text-white" not in additional_styles: additional_styles.append("text-white")
                 
    if "pastel_colors" in trend_tags and color_mode != "dark":
        if component_type in ["Hero Section", "Card", "Feature Card", "Testimonial", "Navbar", "Button"]:
            if "glassmorphism" not in trend_tags: 
                additional_styles = [s for s in additional_styles if not (s.startswith("bg-gray") or s.startswith("bg-white"))]
                additional_styles.append("bg-blue-100") 
            if component_type == "Navbar" or component_type == "Button":
                 additional_styles.append("text-blue-800") 
            elif "glassmorphism" not in trend_tags : 
                 additional_styles.append("text-gray-700")

    if "serif_fonts" in trend_tags:
        additional_styles.append("font-serif")

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
        additional_styles.append("rounded-lg") 
        if "glassmorphism" not in trend_tags and "minimalism" not in trend_tags:
            additional_styles = [s for s in additional_styles if not s.startswith("shadow-")] 
            additional_styles.append("shadow-md") 
            
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
    print(f"Generating code for tech_stack: {tech_stack}, layout: {layout_type}, color: {color_mode}")
    print(f"Inspiration: '{inspiration_summary}', Trends: {trend_tags}")

    if tech_stack != "react-tailwind":
        return f"Code generation for tech_stack '{tech_stack}' is not yet implemented."

    searchable_text = inspiration_summary.lower() + " " + " ".join(trend_tags).lower()
    generated_components: List[str] = []

    if layout_type == "full-page":
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
                
                print(f"Generating {comp_config['name']} (type: {component_name_for_style}) with params: {params}")
                component_code = template_func(**params)
            
            if component_code: generated_components.append(f"\n{/* --- {comp_config['name']} Start --- */}\n{component_code}\n{/* --- {comp_config['name']} End --- */}\n")
        return "\n".join(generated_components)

    elif layout_type == "component":
        chosen_component_info = find_component_from_keywords(searchable_text)
        template_func: Callable = None
        template_params: Dict[str, Any] = {}
        component_name_for_style = "Unknown"

        if chosen_component_info:
            template_func = chosen_component_info["func"]
            component_name_for_style = chosen_component_info["name"]
            print(f"Keyword match: Selected '{component_name_for_style}' component.")
            if component_name_for_style == "Navbar": template_params = {"logoText": "MyApp"}
            elif component_name_for_style == "Footer": template_params = {}
            elif component_name_for_style == "Hero Section": template_params = {"heading": "Hero Title", "subheading": "Hero subtitle text."}
            elif component_name_for_style == "Feature Card": template_params = {"title": "Feature", "description": "Description of feature.", "iconPlaceholder": True}
            elif component_name_for_style == "Testimonial": template_params = {"quote": "This is great!", "authorName": "Satisfied User"}
            elif component_name_for_style == "Login Form": pass
            elif component_name_for_style == "Button": template_params["text"] = "Dynamic Button"
            elif component_name_for_style == "Card": template_params = {"title": "Dynamic Card", "content": "Generated card content."}
        else: 
            print("No specific new component keywords matched. Falling back to general components.")
            if "login" in searchable_text:
                template_func, component_name_for_style = react_tailwind_templates.get_login_form_template, "Login Form"
            elif "card" in searchable_text: 
                template_func, component_name_for_style = react_tailwind_templates.get_card_template, "Card"
                template_params = {"title": "Generic Card", "content": "Some card content."}
            else: 
                template_func, component_name_for_style = react_tailwind_templates.get_button_template, "Button"
                template_params = {"text": "Default Button"}
            print(f"Fallback: Selected '{component_name_for_style}' component.")

        component_base_styles = "" 
        final_styles = apply_trend_styles(component_base_styles, trend_tags, color_mode, component_name_for_style)
        
        if template_func in [react_tailwind_templates.get_button_template, 
                               react_tailwind_templates.get_card_template,
                               react_tailwind_templates.get_login_form_template]:
            template_params["custom_styles"] = final_styles
        else:
            template_params["styles"] = final_styles

        if template_func:
            print(f"Generating single component '{component_name_for_style}' with params: {template_params}")
            return template_func(**template_params)
        else: return "Error: Could not determine a suitable template for React-Tailwind component."
    return "Error: Invalid layout_type or other configuration issue."

if __name__ == '__main__':
    print("--- Example Code Generation (Enhanced with Refined Styles) ---")

    # Test 1: Hero Section (Dark, Glassmorphism, Serif)
    print("\n--- Test 1: Hero Section Component (Dark, Glassmorphism, Serif) ---")
    inspiration_hero = "A hero banner for our app, with glassmorphism style and serif fonts"
    trends_hero = ["glassmorphism", "dark_mode", "modern_ui", "hero", "serif_fonts"]
    code_hero = create_code(inspiration_hero, trends_hero, "react-tailwind", "dark", "component")
    print(f"Generated Hero Section Code (first 300 chars):\n{code_hero[:300]}...")
    assert "HeroSection" in code_hero, "HeroSection component not found"
    assert "font-serif" in code_hero, "Serif font style missing"
    assert "bg-gray-800/10" in code_hero or ("bg-white/10" in code_hero and "text-white" in code_hero), "Dark glassmorphism style missing"
    assert "text-white" in code_hero, "Dark mode text color missing"

    # Test 2: Full Page (Light, Minimalist, Pastel accents, Serif)
    print("\n--- Test 2: Full Page Layout (Light, Minimalist, Pastel, Serif) ---")
    inspiration_page_min_pastel = "A landing page intro for my portfolio, minimalist style with pastel colors and serif type."
    trends_page_min_pastel = ["minimalism", "light_mode", "hero", "pastel_colors", "serif_fonts"]
    code_page_min_pastel = create_code(inspiration_page_min_pastel, trends_page_min_pastel, "react-tailwind", "light", "full-page")
    print(f"Generated Full Page Code (Minimal, Pastel) (first 400 chars):\n{code_page_min_pastel[:400]}...")
    assert "Navbar" in code_page_min_pastel, "Navbar not found in full page"
    assert "HeroSection" in code_page_min_pastel, "HeroSection not found in full page"
    assert "Footer" in code_page_min_pastel, "Footer not found in full page"
    assert "font-serif" in code_page_min_pastel, "Serif font style missing in full page"
    assert "bg-blue-100" in code_page_min_pastel, "Pastel color style missing in full page"
    assert "shadow-none" in code_page_min_pastel, "Minimalism shadow-none style missing"
    assert "bg-white" in code_page_min_pastel or "bg-blue-100" in code_page_min_pastel, "Light mode background (white or pastel) missing"

    # Test 3: Feature Card (Dark Mode, Modern UI)
    print("\n--- Test 3: Feature Card (Dark, Modern UI) ---")
    inspiration_feature_dark = "A feature highlight card for a modern dark themed dashboard."
    trends_feature_dark = ["dark_mode", "modern_ui", "feature"]
    code_feature_dark = create_code(inspiration_feature_dark, trends_feature_dark, "react-tailwind", "dark", "component")
    print(f"Generated Feature Card Code (Dark, Modern) (first 300 chars):\n{code_feature_dark[:300]}...")
    assert "FeatureCard" in code_feature_dark, "FeatureCard component not found"
    assert "rounded-lg" in code_feature_dark, "Modern UI rounded-lg style missing"
    assert "bg-gray-800" in code_feature_dark, "Dark mode background missing"
    assert "shadow-md" in code_feature_dark or "shadow-lg" in code_feature_dark, "Modern UI shadow missing"

    # Test 4: Navbar (Light Mode, Glassmorphism, Modern UI)
    print("\n--- Test 4: Navbar (Light, Glassmorphism, Modern UI) ---")
    inspiration_navbar_glass = "A modern navigation bar with a frosted glass effect."
    trends_navbar_glass = ["light_mode", "glassmorphism", "modern_ui", "navbar"]
    code_navbar_glass = create_code(inspiration_navbar_glass, trends_navbar_glass, "react-tailwind", "light", "component")
    print(f"Generated Navbar Code (Light, Glass) (first 300 chars):\n{code_navbar_glass[:300]}...")
    assert "Navbar" in code_navbar_glass, "Navbar component not found"
    assert "bg-white/30" in code_navbar_glass, "Light glassmorphism style for Navbar missing"
    assert "backdrop-blur-md" in code_navbar_glass, "Navbar backdrop blur missing"
    assert "rounded-lg" in code_navbar_glass, "Modern UI rounded-lg style missing for Navbar"

    # Test 5: Footer (Dark Mode, Minimalist)
    print("\n--- Test 5: Footer Component (Dark, Minimalist) ---")
    inspiration_footer_min_dark = "A simple, clean footer for dark mode."
    trends_footer_min_dark = ["dark_mode", "minimalism", "footer"]
    code_footer_min_dark = create_code(inspiration_footer_min_dark, trends_footer_min_dark, "react-tailwind", "dark", "component")
    print(f"Generated Footer Code (Dark, Minimal) (first 300 chars):\n{code_footer_min_dark[:300]}...")
    assert "Footer" in code_footer_min_dark, "Footer component not found"
    assert "shadow-none" in code_footer_min_dark, "Minimalism shadow-none style missing for Footer"
    assert "bg-gray-800" in code_footer_min_dark or "bg-gray-900" in code_footer_min_dark, "Dark mode background missing for Footer"

    # Test 6: Button (Light Mode, Pastel, Serif)
    print("\n--- Test 6: Button Component (Light, Pastel, Serif) ---")
    inspiration_button_pastel = "A button with light pastel colors and serif font."
    trends_button_pastel = ["light_mode", "pastel_colors", "serif_fonts", "button"]
    code_button_pastel = create_code(inspiration_button_pastel, trends_button_pastel, "react-tailwind", "light", "component")
    print(f"Generated Button Code (Pastel, Serif) (first 300 chars):\n{code_button_pastel[:300]}...")
    assert "MyButton" in code_button_pastel, "Button component not found"
    assert "font-serif" in code_button_pastel, "Serif font style missing for Button"
    assert "bg-blue-100" in code_button_pastel, "Pastel background missing for Button"
    assert "text-blue-800" in code_button_pastel, "Pastel text color missing for Button"

    print("\n--- All generate_code examples with refined styles run ---")
