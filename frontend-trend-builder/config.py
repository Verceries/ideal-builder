import os
import logging # Added
from dotenv import load_dotenv

# Get a logger instance for this module
logger = logging.getLogger(__name__) # Added

# Load environment variables from .env file
load_dotenv()

# API Keys
UNSPLASH_API_KEY = os.getenv("UNSPLASH_API_KEY")
GOOGLE_FONTS_API_KEY = os.getenv("GOOGLE_FONTS_API_KEY")

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

# You can add other configurations here later, e.g.:
# DEFAULT_TECH_STACK = os.getenv("DEFAULT_TECH_STACK", "react-tailwind")

if __name__ == '__main__':
    # This block is for testing the config loading.
    # It will only run when config.py is executed directly.
    
    # Configure a basic logger for standalone execution of this file, if not already configured by main.py
    if not logging.getLogger().hasHandlers() or logging.getLogger().level > logging.DEBUG : # Check if root logger is set or level is too high
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    logger.info("--- Configuration Test ---") # Changed from print
    if UNSPLASH_API_KEY:
        logger.info(f"Unsplash API Key: ...{UNSPLASH_API_KEY[-4:]}") # Changed from print
    else:
        logger.info("Unsplash API Key: Not set") # Changed from print

    if GOOGLE_FONTS_API_KEY:
        logger.info(f"Google Fonts API Key: ...{GOOGLE_FONTS_API_KEY[-4:]}") # Changed from print
    else:
        logger.info("Google Fonts API Key: Not set") # Changed from print
    
    logger.info(f"Configured Log Level: {LOG_LEVEL}") # Changed from print
    
    # Example of how action modules might try to use it (for testing import paths)
    # logger.info(f"DEFAULT_TECH_STACK: {DEFAULT_TECH_STACK}")
