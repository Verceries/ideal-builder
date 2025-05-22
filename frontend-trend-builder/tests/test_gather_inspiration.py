import sys
import os

# Adjust the Python path to include the parent directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from actions import gather_inspiration

def test_get_inspiration():
    """
    Tests if get_inspiration returns a non-empty string.
    """
    prompt = "test prompt"
    result = gather_inspiration.get_inspiration(prompt)
    assert isinstance(result, str), "Output should be a string"
    assert len(result) > 0, "Output string should not be empty"
    assert prompt in result, "Output string should contain the input prompt"
    print("test_get_inspiration PASSED")

if __name__ == "__main__":
    test_get_inspiration()
