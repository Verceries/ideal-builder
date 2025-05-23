import logging
from typing import Optional, Dict
# Assuming 'view_text_website' is a globally available tool/function
# For local testing, one might need to mock it if not in the specific execution env.
# Example:
# try:
#     from some_sandbox_tools import view_text_website
# except ImportError:
#     # Define a mock for local testing if needed
#     def view_text_website(url: str) -> str:
#         print(f"[Mock] view_text_website called for: {url}")
#         if "example.com" in url or "jsonplaceholder.typicode.com" in url:
#             return '{ "mock_key": "mock_value" }' # Return simple JSON
#         raise Exception(f"Mock network error for {url}")


logger = logging.getLogger(__name__)

class DataProviderError(Exception):
    """Custom exception for data provider errors."""
    pass

def fetch_url_text(url: str, headers: Optional[Dict[str, str]] = None) -> str:
    """
    Fetches text content from a URL using the available view_text_website tool.
    The 'headers' argument is for future compatibility if a more advanced HTTP client is used.
    """
    logger.info(f"Fetching URL (text): {url}")
    if headers:
        logger.debug(f"Note: 'headers' argument provided but not used by current 'view_text_website' tool.")
    
    try:
        # This is where the actual tool call happens.
        # The tool 'view_text_website' is expected to be in the execution scope.
        content = view_text_website(url=url) 
        if content is None: # Check if content is None, tool might return None on error
            logger.warning(f"No content returned from URL (view_text_website returned None): {url}")
            raise DataProviderError(f"No content returned from URL: {url}")
        return content
    except NameError:
        logger.error("'view_text_website' tool is not defined in the current environment.")
        raise DataProviderError("'view_text_website' tool is not available.")
    except Exception as e:
        # Catch any other exception from view_text_website call
        logger.error(f"Error during 'view_text_website' call for URL {url}: {e}")
        raise DataProviderError(f"Failed to fetch content from {url}: {e}")

if __name__ == '__main__':
    # This block is for basic testing of http_client.py.
    # It requires 'view_text_website' to be available or mocked globally.
    
    # Basic logging setup for standalone execution
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    logger.info("--- Testing http_client.py ---")
    
    # Define a simple mock for view_text_website if it's not available
    # This is for local testing only; in the agent environment, the tool is provided.
    if 'view_text_website' not in globals():
        def view_text_website(url: str) -> str:
            logger.info(f"[Mock] view_text_website called for: {url}")
            if "jsonplaceholder.typicode.com/todos/1" in url:
                return '{ "userId": 1, "id": 1, "title": "delectus aut autem", "completed": false }'
            elif "example.com" in url: # Another success case
                return "<html><body>Mocked Example.com Content</body></html>"
            elif "thisshouldnotexistdomain123abc.com" in url:
                raise Exception("Mock simulated network error for non-existent domain")
            return "" # Default empty for other URLs

    test_url_success_json = "https://jsonplaceholder.typicode.com/todos/1"
    test_url_success_html = "http://example.com"
    test_url_fail_network = "http://thisshouldnotexistdomain123abc.com"
    test_url_fail_empty = "http://someotherurlthatreturnsnothing.com"


    try:
        logger.info(f"Attempting to fetch JSON: {test_url_success_json}")
        content_success = fetch_url_text(test_url_success_json)
        logger.info(f"Success JSON content (first 100 chars): {content_success[:100]}...")
    except DataProviderError as e:
        logger.error(f"Error fetching {test_url_success_json}: {e}")
    
    try:
        logger.info(f"Attempting to fetch HTML: {test_url_success_html}")
        content_success_html = fetch_url_text(test_url_success_html)
        logger.info(f"Success HTML content (first 100 chars): {content_success_html[:100]}...")
    except DataProviderError as e:
        logger.error(f"Error fetching {test_url_success_html}: {e}")

    try:
        logger.info(f"Attempting to fetch (expecting network error): {test_url_fail_network}")
        fetch_url_text(test_url_fail_network)
    except DataProviderError as e:
        logger.info(f"Successfully caught expected error for {test_url_fail_network}: {e}")
    
    if 'view_text_website' in globals() and globals()['view_text_website'].__module__ == __name__: # only if using the local mock
         try:
            logger.info(f"Attempting to fetch (expecting empty content leading to error): {test_url_fail_empty}")
            fetch_url_text(test_url_fail_empty) # This mock returns "" which fetch_url_text should handle
         except DataProviderError as e:
            logger.info(f"Successfully caught expected error for empty content from {test_url_fail_empty}: {e}")
