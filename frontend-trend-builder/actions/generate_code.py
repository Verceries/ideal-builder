from typing import List, Dict # Added Dict for potential future use with more complex templates
# Assuming react_tailwind_templates.py is in a subdirectory 'code_templates'
from .code_templates import react_tailwind_templates

def apply_trend_styles(base_styles: str, trend_tags: List[str], color_mode: str) -> str:
    """
    Applies styles based on trend_tags and color_mode.
    This is a simplified version.
    """
    additional_styles = []
    
    if "glassmorphism" in trend_tags:
        additional_styles.append("bg-white bg-opacity-20 backdrop-blur-lg border border-gray-200 shadow-lg")
    if "minimalism" in trend_tags:
        # Minimalism might mean removing default shadows or borders, or ensuring simple ones
        # This is context dependent. For now, let's ensure a clean look.
        additional_styles.append("border-gray-200") # ensure border for card/button if not already dark
        if "dark_mode" not in trend_tags and color_mode != "dark": # avoid conflict with dark mode
             additional_styles.append("bg-white")


    if color_mode == "dark":
        additional_styles.append("bg-gray-800 text-white")
        # If it's a card or button, dark mode borders might be different
        if "glassmorphism" in trend_tags: # Adjust glassmorphism for dark mode
            additional_styles.append("border-gray-700")
        else:
            additional_styles.append("border-gray-600")
    elif color_mode == "light" and "glassmorphism" not in trend_tags:
        additional_styles.append("bg-gray-100 text-gray-900 border-gray-300")


    # Remove duplicates by converting to set and back, preserving order is not critical for CSS classes
    final_styles = base_styles.split() + additional_styles
    return " ".join(list(dict.fromkeys(final_styles))) # dict.fromkeys to remove duplicates preserving order somewhat

def create_code(
    inspiration_summary: str, # Now used to infer component type
    trend_tags: List[str],
    tech_stack: str,
    color_mode: str,
    layout_type: str
) -> str:
    """
    Generates frontend code based on inspiration, trends, and user preferences,
    using templates for specific tech stacks.
    """
    print(f"Generating code for tech_stack: {tech_stack}, layout: {layout_type}, color: {color_mode}")
    print(f"Inspiration: '{inspiration_summary}', Trends: {trend_tags}")

    if tech_stack == "react-tailwind":
        chosen_template_func = None
        template_params = {}
        custom_styles = ""

        # Determine component type from inspiration_summary (very basic keyword matching)
        # or layout_type for broader categories.
        # This logic can be significantly expanded.
        summary_lower = inspiration_summary.lower()
        if "login form" in summary_lower or "login" in summary_lower and layout_type == "component":
            chosen_template_func = react_tailwind_templates.get_login_form_template
        elif "button" in summary_lower and layout_type == "component":
            chosen_template_func = react_tailwind_templates.get_button_template
            template_params["text"] = "Dynamic Button" # Example: could extract from summary
        elif "card" in summary_lower and layout_type == "component":
            chosen_template_func = react_tailwind_templates.get_card_template
            template_params["title"] = "Dynamic Card"
            template_params["content"] = "Generated card content based on trends."
        elif layout_type == "full-page":
            # For a full page, we might start with a card as a placeholder, or a more complex layout
            # For now, let's use a card as a main content block.
            chosen_template_func = react_tailwind_templates.get_card_template
            template_params["title"] = "Full Page Content Area"
            template_params["content"] = f"This is a placeholder for a full-page layout using {tech_stack} with {color_mode} mode. Trends: {', '.join(trend_tags)}."
            custom_styles = "w-full min-h-screen" # Make card take full space
        else: # Default to a button if specific component not recognized
            chosen_template_func = react_tailwind_templates.get_button_template
            template_params["text"] = "Default Button"

        # Apply styles based on trends and color mode
        final_styles = apply_trend_styles(custom_styles, trend_tags, color_mode)
        template_params["custom_styles"] = final_styles
        
        # A special case for login form as its button is internal
        if chosen_template_func == react_tailwind_templates.get_login_form_template:
            # The login form template itself handles its internal button.
            # We pass overall form styles.
            # If the button inside needs separate trend styling, the template would need more props.
            # For now, the `custom_styles` in `get_login_form_template` apply to the form container.
            # The button inside uses its own default + whatever `get_button_template` adds.
            # Let's assume the login form template's internal button benefits from general color_mode.
             pass # Styles are passed to the form container

        if chosen_template_func:
            return chosen_template_func(**template_params)
        else:
            return "Error: Could not determine a suitable template for React-Tailwind."

    else:
        return f"Code generation for tech_stack '{tech_stack}' is not yet implemented."

if __name__ == '__main__':
    print("--- Example Code Generation ---")

    # Example 1: React-Tailwind Button with Dark Mode and Glassmorphism
    inspiration_1 = "A cool glassmorphic button for a dark themed UI"
    trends_1 = ["glassmorphism", "dark_mode", "modern_ui"]
    code_1 = create_code(inspiration_1, trends_1, "react-tailwind", "dark", "component")
    print(f"\n1. React-Tailwind Button (Dark, Glassmorphic):\n{code_1}")

    # Example 2: React-Tailwind Login Form, Light Mode
    inspiration_2 = "A simple login form for my new website"
    trends_2 = ["minimalism"] # Minimalism might affect styles if handled in apply_trend_styles
    code_2 = create_code(inspiration_2, trends_2, "react-tailwind", "light", "component")
    print(f"\n2. React-Tailwind Login Form (Light, Minimal):\n{code_2}")

    # Example 3: React-Tailwind Card, Dark Mode, no specific trends
    inspiration_3 = "A card to display user information"
    trends_3 = ["modern_ui"]
    code_3 = create_code(inspiration_3, trends_3, "react-tailwind", "dark", "component")
    print(f"\n3. React-Tailwind Card (Dark):\n{code_3}")
    
    # Example 4: Full Page Layout Placeholder
    inspiration_4 = "A full page layout for a portfolio"
    trends_4 = ["minimalism", "bold_typography"]
    code_4 = create_code(inspiration_4, trends_4, "react-tailwind", "light", "full-page")
    print(f"\n4. React-Tailwind Full Page (Light, Minimal):\n{code_4}")

    # Example 5: Vue (Not Implemented)
    inspiration_5 = "A data table for a Vue application"
    trends_5 = ["data_visualization"]
    code_5 = create_code(inspiration_5, trends_5, "vue", "auto", "component")
    print(f"\n5. Vue Component (Not Implemented):\n{code_5}")

    # Example 6: React-Tailwind Button with Light Mode and specific prompt
    inspiration_6 = "Need a submit button"
    trends_6 = ["minimalism"]
    code_6 = create_code(inspiration_6, trends_6, "react-tailwind", "light", "component")
    print(f"\n6. React-Tailwind Submit Button (Light, Minimal):\n{code_6}")
    
    # Example 7: Default component if no keywords match
    inspiration_7 = "Some random thoughts for a webpage section"
    trends_7 = ["abstract_design"]
    code_7 = create_code(inspiration_7, trends_7, "react-tailwind", "dark", "component")
    print(f"\n7. React-Tailwind Default Component (Dark):\n{code_7}")
