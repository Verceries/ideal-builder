"""
React + Tailwind CSS component templates registry.
This file imports template strings from individual component files
and aggregates them into a dictionary for use by the code generation logic.
"""
import logging

# Import templates from individual files
from .react_tailwind.navbar import TEMPLATE as NAVBAR_TEMPLATE
from .react_tailwind.hero import TEMPLATE as HERO_TEMPLATE
from .react_tailwind.features import TEMPLATE as FEATURES_TEMPLATE # Assuming FeatureCard is the 'features' section
from .react_tailwind.footer import TEMPLATE as FOOTER_TEMPLATE
from .react_tailwind.testimonial import TEMPLATE as TESTIMONIAL_TEMPLATE
from .react_tailwind.modal import TEMPLATE as MODAL_TEMPLATE

logger = logging.getLogger(__name__)

# Central registry for React + Tailwind CSS component templates
REACT_TAILWIND_TEMPLATES = {
    "Navbar": NAVBAR_TEMPLATE,
    "Hero Section": HERO_TEMPLATE,
    "Features Section": FEATURES_TEMPLATE, # Using "Features Section" as key for clarity
    "Footer": FOOTER_TEMPLATE,
    "Testimonial": TESTIMONIAL_TEMPLATE,
    "Modal": MODAL_TEMPLATE,
    # Note: The original file had get_button_template, get_card_template, 
    # and get_login_form_template. These were not specified in the refactoring task
    # for inclusion in the new structure as separate files and the main registry.
    # If they are needed as standalone components, they would need a similar refactoring
    # or be handled differently by the generation logic. For now, they are removed
    # to align with the task's focus on navbar, hero, features, footer, testimonial, modal.
}

if __name__ == "__main__":
    if not logging.getLogger().hasHandlers() or logging.getLogger().level > logging.DEBUG:
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    logger.info("--- Testing React Tailwind Templates Registry ---")
    
    if not REACT_TAILWIND_TEMPLATES:
        logger.error("REACT_TAILWIND_TEMPLATES dictionary is empty!")
    else:
        logger.info(f"Successfully loaded {len(REACT_TAILWIND_TEMPLATES)} templates into the registry.")
        for name, template_content in REACT_TAILWIND_TEMPLATES.items():
            logger.debug(f"--- Template: {name} ---")
            # logger.debug(template_content[:200] + "..." if template_content else "Template is empty/None") # Print snippet
            if not template_content or not isinstance(template_content, str) or len(template_content.strip()) == 0:
                 logger.error(f"Template for '{name}' is empty or invalid!")
            else:
                 logger.info(f"Template for '{name}' loaded successfully (length: {len(template_content)}).")


    # Example: Print a specific template to verify content
    if "Navbar" in REACT_TAILWIND_TEMPLATES:
        logger.info("\n--- Navbar Template Content (First 200 chars) ---")
        print(REACT_TAILWIND_TEMPLATES["Navbar"][:200] + "...")
    else:
        logger.warning("Navbar template not found in registry for printing example.")

    if "Modal" in REACT_TAILWIND_TEMPLATES:
        logger.info("\n--- Modal Template Content (First 200 chars) ---")
        print(REACT_TAILWIND_TEMPLATES["Modal"][:200] + "...")
    else:
        logger.warning("Modal template not found in registry for printing example.")
        
    logger.info("--- End of React Tailwind Templates Registry Test ---")
