import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Keys
UNSPLASH_API_KEY = os.getenv("UNSPLASH_API_KEY")
GOOGLE_FONTS_API_KEY = os.getenv("GOOGLE_FONTS_API_KEY")

# You can add other configurations here later, e.g.:
# LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
# DEFAULT_TECH_STACK = os.getenv("DEFAULT_TECH_STACK", "react-tailwind")

if __name__ == '__main__':
    # This block is for testing the config loading.
    # It will only run when config.py is executed directly.
    print("--- Configuration Test ---")
    if UNSPLASH_API_KEY:
        print(f"Unsplash API Key: ...{UNSPLASH_API_KEY[-4:]}") # Print last 4 chars for verification
    else:
        print("Unsplash API Key: Not set")

    if GOOGLE_FONTS_API_KEY:
        print(f"Google Fonts API Key: ...{GOOGLE_FONTS_API_KEY[-4:]}") # Print last 4 chars
    else:
        print("Google Fonts API Key: Not set")
    
    # Example of how action modules might try to use it (for testing import paths)
    # print(f"LOG_LEVEL: {LOG_LEVEL}") 
    # print(f"DEFAULT_TECH_STACK: {DEFAULT_TECH_STACK}")
