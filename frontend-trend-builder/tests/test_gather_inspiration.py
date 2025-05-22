import sys
import os
from typing import List, Dict, Union

# Adjust the Python path to include the parent directory
# This allows direct import of 'actions' and 'schema'
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from actions import gather_inspiration

# Ensure the data file path is correct relative to this test file,
# or ensure tests are run from a context where 'data/mock_inspiration_data.json' is accessible.
# For actions, the path is usually constructed like:
# os.path.join(os.path.dirname(__file__), '..', 'data', 'mock_inspiration_data.json')
# This test file is in tests/, so '..' goes to frontend-trend-builder/, then 'data/...'
# gather_inspiration.DATA_FILE_PATH should be correct if called from root or if actions/ is in sys.path

def test_get_inspiration_with_matches():
    """
    Tests if get_inspiration returns a list of dicts when matches are found.
    """
    prompt = "glassmorphic crypto login" # Should match mock1 and mock6
    result = gather_inspiration.get_inspiration(prompt)
    
    assert isinstance(result, list), "Output should be a list for matches."
    assert len(result) > 0, "Should return at least one item for 'glassmorphic crypto'."
    
    found_ids = []
    for item in result:
        assert isinstance(item, dict), "Each item in the list should be a dictionary."
        assert "id" in item, "Each item should have an 'id'."
        assert "title" in item, "Each item should have a 'title'."
        found_ids.append(item["id"])
        # Check if prompt keywords are somewhere in the matched item's text
        assert "glassmorphism" in item["title"].lower() or "glassmorphism" in " ".join(item.get("tags", [])).lower() or \
               "crypto" in item["title"].lower() or "crypto" in " ".join(item.get("tags", [])).lower()

    assert "mock1" in found_ids, "Should have found 'mock1' for 'glassmorphic crypto login'"
    assert "mock6" in found_ids, "Should have found 'mock6' for 'glassmorphic crypto login'"
    print("test_get_inspiration_with_matches PASSED")

def test_get_inspiration_no_matches():
    """
    Tests if get_inspiration returns a specific string when no matches are found.
    """
    prompt = "zyxw_unmatchable_keyword_12345"
    result = gather_inspiration.get_inspiration(prompt)
    
    assert isinstance(result, str), "Output should be a string for no matches."
    assert "No specific inspiration found" in result, "Message should indicate no matches found."
    print("test_get_inspiration_no_matches PASSED")

def test_get_inspiration_data_file_issues():
    """
    Tests error handling if the data file is missing or corrupt.
    This requires temporarily altering the path or file.
    """
    original_path = gather_inspiration.DATA_FILE_PATH
    
    # Test FileNotFoundError
    gather_inspiration.DATA_FILE_PATH = "non_existent_data_file.json"
    result_not_found = gather_inspiration.get_inspiration("test")
    assert isinstance(result_not_found, str)
    assert "Error: Inspiration data file not found" in result_not_found
    print("test_get_inspiration_data_file_not_found PASSED")

    # Test JSONDecodeError (create a temporary malformed file)
    temp_malformed_file = os.path.join(os.path.dirname(original_path), "temp_malformed.json")
    with open(temp_malformed_file, 'w') as f:
        f.write("{'invalid_json': ") # Malformed JSON
    
    gather_inspiration.DATA_FILE_PATH = temp_malformed_file
    result_decode_error = gather_inspiration.get_inspiration("test")
    assert isinstance(result_decode_error, str)
    assert "Error: Could not decode inspiration data" in result_decode_error
    print("test_get_inspiration_data_file_decode_error PASSED")
    
    os.remove(temp_malformed_file) # Clean up
    gather_inspiration.DATA_FILE_PATH = original_path # Restore original path
    print("test_get_inspiration_data_file_issues (overall) PASSED")

if __name__ == "__main__":
    print("--- Running test_gather_inspiration.py ---")
    test_get_inspiration_with_matches()
    test_get_inspiration_no_matches()
    test_get_inspiration_data_file_issues()
    print("--- All gather_inspiration tests completed ---")
