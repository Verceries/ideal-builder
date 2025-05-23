import sys
import os
import logging
from unittest import TestCase, mock 
# If using python < 3.8, you might need `mock` from PyPI for AsyncMock etc.
# For this, `unittest.mock` should be fine.

# Adjust path to import from the root of the project
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from data_providers.http_client import fetch_url_text, DataProviderError

# Configure logging for tests if needed, or rely on global config.
# This ensures that if you run this test file directly, logs are visible.
if not logging.getLogger().hasHandlers() or logging.getLogger().level > logging.DEBUG:
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
logger = logging.getLogger(__name__)


class TestFetchUrlText(TestCase):

    @mock.patch('data_providers.http_client.view_text_website')
    def test_fetch_url_text_success(self, mock_view_tool):
        logger.info("Running test_fetch_url_text_success")
        expected_content = "<html><body>Mocked Content</body></html>"
        mock_view_tool.return_value = expected_content
        
        url = "http://example.com/success"
        content = fetch_url_text(url)
        
        self.assertEqual(content, expected_content)
        mock_view_tool.assert_called_once_with(url=url)
        logger.info("test_fetch_url_text_success PASSED")

    @mock.patch('data_providers.http_client.view_text_website')
    def test_fetch_url_text_returns_none(self, mock_view_tool):
        logger.info("Running test_fetch_url_text_returns_none")
        mock_view_tool.return_value = None
        
        url = "http://example.com/returns_none"
        with self.assertRaisesRegex(DataProviderError, "No content returned from URL"):
            fetch_url_text(url)
        mock_view_tool.assert_called_once_with(url=url)
        logger.info("test_fetch_url_text_returns_none PASSED")

    @mock.patch('data_providers.http_client.view_text_website')
    def test_fetch_url_text_tool_raises_exception(self, mock_view_tool):
        logger.info("Running test_fetch_url_text_tool_raises_exception")
        original_exception_message = "Simulated tool network error"
        mock_view_tool.side_effect = Exception(original_exception_message)
        
        url = "http://example.com/tool_exception"
        with self.assertRaisesRegex(DataProviderError, f"Failed to fetch content from {url}: {original_exception_message}"):
            fetch_url_text(url)
        mock_view_tool.assert_called_once_with(url=url)
        logger.info("test_fetch_url_text_tool_raises_exception PASSED")

    @mock.patch('data_providers.http_client.view_text_website')
    def test_fetch_url_text_tool_raises_name_error(self, mock_view_tool):
        logger.info("Running test_fetch_url_text_tool_raises_name_error")
        # This simulates the scenario where 'view_text_website' is not defined when http_client tries to call it.
        # The patch above already replaces it, so to test NameError inside fetch_url_text,
        # we'd have to make the *mock itself* raise NameError.
        mock_view_tool.side_effect = NameError("Mock: view_text_website is not defined")
        
        url = "http://example.com/name_error_scenario"
        # The DataProviderError should wrap the NameError.
        with self.assertRaisesRegex(DataProviderError, "Failed to fetch content from http://example.com/name_error_scenario: Mock: view_text_website is not defined"):
             fetch_url_text(url)
        mock_view_tool.assert_called_once_with(url=url)
        logger.info("test_fetch_url_text_tool_raises_name_error PASSED")
        
    # Test for NameError if view_text_website is *truly* not in scope of http_client.py
    # This requires a different kind of patching: temporarily remove it from the module's globals.
    # This is more complex and might not be the primary scenario if the tool is always expected.
    # The above test (mock_view_tool.side_effect = NameError) is a good proxy.

    @mock.patch('data_providers.http_client.view_text_website')
    def test_fetch_url_text_with_headers_logs_them(self, mock_view_tool):
        logger.info("Running test_fetch_url_text_with_headers_logs_them")
        expected_content = "Content with headers"
        mock_view_tool.return_value = expected_content
        
        url = "http://example.com/with_headers"
        headers = {"Authorization": "Bearer testtoken"}
        
        # Use assertLogs to check for the specific log message
        with self.assertLogs(logger='data_providers.http_client', level='DEBUG') as cm:
            content = fetch_url_text(url, headers=headers)
        
        self.assertEqual(content, expected_content)
        mock_view_tool.assert_called_once_with(url=url) # Headers are not passed to the mock
        
        # Check if the log message about headers is present
        self.assertTrue(any("headers' argument provided but not used" in message for message in cm.output))
        logger.info("test_fetch_url_text_with_headers_logs_them PASSED")


if __name__ == '__main__':
    # This allows running tests directly using `python -m unittest path/to/test_http_client.py`
    # or `python path/to/test_http_client.py` if TestCase.main() is used.
    # For simplicity, just running the tests if script is main.
    
    # Create a TestSuite and run it
    # This is one way to run tests without needing `python -m unittest`
    # suite = unittest.TestSuite()
    # suite.addTest(unittest.makeSuite(TestFetchUrlText))
    # runner = unittest.TextTestRunner()
    # runner.run(suite)
    
    # Simpler: if you want to run this file directly, you can use this,
    # but it's often better to use `python -m unittest discover` from the root.
    logger.info("Running tests for http_client.py directly. Consider using 'python -m unittest discover'.")
    # To run with unittest's test runner when executing the file directly:
    # unittest.main() # This would run all TestCases in this file.
    
    # For now, let's just call them to see output during development if needed.
    # This is NOT standard practice for unittest.
    # test_instance = TestFetchUrlText()
    # test_instance.test_fetch_url_text_success()
    # test_instance.test_fetch_url_text_returns_none()
    # test_instance.test_fetch_url_text_tool_raises_exception()
    # test_instance.test_fetch_url_text_tool_raises_name_error()
    # test_instance.test_fetch_url_text_with_headers_logs_them()
    
    # The standard way to run is `python -m unittest tests.data_providers.test_http_client` from root,
    # or `python -m unittest discover tests`
    pass # No direct execution of tests here, use unittest runner.
