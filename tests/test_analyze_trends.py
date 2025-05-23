import unittest
import sys
import os

# Adjust path to import from the actions package
# Assuming this test file is in tests/ and analyze_trends.py is in frontend-trend-builder/actions/
# This adds the 'frontend-trend-builder' directory to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from frontend_trend_builder.actions.analyze_trends import identify_trends, load_trend_dictionary

class TestAnalyzeTrends(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Load the trend dictionary once for all tests
        cls.trend_dictionary = load_trend_dictionary()
        if not cls.trend_dictionary:
            raise RuntimeError("Failed to load trend_dictionary.json for tests.")

    def test_existing_keywords_glassmorphism(self):
        prompt = "a sleek glassmorphic dashboard for a crypto fintech app"
        inspiration = "Inspiration includes clean lines, data visualization, and a focus on clarity. Uses frosted glass."
        expected_trends = sorted(['data_visualization', 'glassmorphism', 'minimalism', 'modern_ui'])
        # 'minimalism' from "clean lines", "clarity"
        # 'modern_ui' from "crypto fintech app"
        # 'data_visualization' from "dashboard"
        # 'glassmorphism' from "glassmorphic", "frosted glass"
        
        # Temporarily patch the loaded dictionary for this test if it helps isolate
        # For now, assumes global dictionary is loaded and correct.
        identified = sorted(identify_trends(prompt, inspiration))
        self.assertEqual(identified, expected_trends)

    def test_existing_keywords_pastel_minimalism(self):
        prompt = "minimalist website with pastel colors"
        inspiration = "The user wants a very simple and clean page, perhaps with soft UI elements."
        # 'minimalism' from "minimalist", "simple", "clean"
        # 'pastel_colors' from "pastel colors"
        # 'neumorphism' from "soft UI" (as per current dictionary)
        expected_trends = sorted(['minimalism', 'pastel_colors', 'neumorphism'])
        identified = sorted(identify_trends(prompt, inspiration))
        self.assertEqual(identified, expected_trends)

    def test_existing_keywords_retro_bold(self):
        prompt = "A retro style homepage for a gaming blog"
        inspiration = "Thinking of 80s or 90s arcade games. Maybe some bold typography."
        # 'retro_style' from "retro style", "80s", "90s"
        # 'bold_typography' from "bold typography"
        expected_trends = sorted(['retro_style', 'bold_typography'])
        identified = sorted(identify_trends(prompt, inspiration))
        self.assertEqual(identified, expected_trends)

    def test_no_relevant_keywords(self):
        prompt = "No relevant keywords here"
        inspiration = "Just some generic text without trend words"
        expected_trends = []
        identified = sorted(identify_trends(prompt, inspiration))
        self.assertEqual(identified, expected_trends)

    def test_cyberpunk_keywords(self):
        prompt = "A website design with a cyberpunk feel, neon future vibes."
        inspiration = "Think dystopian tech and hacker aesthetic."
        expected = ["cyberpunk"]
        identified = identify_trends(prompt, inspiration)
        self.assertIn("cyberpunk", identified)
        # Check if only cyberpunk is identified or if other general terms also trigger
        # For this test, we mainly care that "cyberpunk" is present.
        self.assertTrue(all(item in identified for item in expected), f"Expected {expected}, got {identified}")


    def test_art_deco_keywords(self):
        prompt = "An art deco login page for a luxury hotel."
        inspiration = "Inspired by gatsby style and geometric opulence."
        # Expected: art_deco, luxury_aesthetic (from "luxury hotel"), Login Form, geometric_patterns
        # The original test in generate_code's __main__ had these.
        expected_trends_set = {"art_deco", "luxury_aesthetic", "Login Form", "geometric_patterns"}
        identified_set = set(identify_trends(prompt, inspiration))
        self.assertTrue(expected_trends_set.issubset(identified_set), 
                        f"Expected at least {expected_trends_set}, got {identified_set}")

    def test_skeuomorphism_keywords(self):
        prompt = "A skeuomorphic UI for a music app."
        inspiration = "Wants real world textures and realistic UI elements."
        expected = ["skeuomorphism"]
        identified = identify_trends(prompt, inspiration)
        self.assertIn("skeuomorphism", identified)
        self.assertTrue(all(item in identified for item in expected), f"Expected {expected}, got {identified}")


    def test_playful_aesthetic_keywords(self):
        prompt = "A playful and fun website for a children's toy store."
        inspiration = "Should be whimsical and quirky."
        expected = ["playful_aesthetic"]
        identified = identify_trends(prompt, inspiration)
        self.assertIn("playful_aesthetic", identified)
        self.assertTrue(all(item in identified for item in expected), f"Expected {expected}, got {identified}")


    def test_corporate_style_keywords(self):
        # This test verifies the change from "corporate_aesthetic" to "corporate_style"
        prompt = "A professional and formal UI for a businesslike corporate portal."
        inspiration = "The company wants a very corporate style for their new site."
        expected = ["corporate_style"]
        identified = identify_trends(prompt, inspiration)
        self.assertIn("corporate_style", identified)
        # Ensure 'corporate_aesthetic' is NOT present if the dictionary was updated correctly
        self.assertNotIn("corporate_aesthetic", identified)
        self.assertTrue(all(item in identified for item in expected), f"Expected {expected}, got {identified}")

    def test_mixed_trends_complex_prompt(self):
        prompt = "A dark mode cyberpunk dashboard with art deco elements and skeuomorphic details on cards."
        inspiration = "User wants a tech noir feel, roaring twenties opulence, and realistic textures on card UI elements."
        # Expected: dark_mode, cyberpunk, data_visualization (dashboard), art_deco, skeuomorphism, card_ui
        expected_trends_set = {"dark_mode", "cyberpunk", "data_visualization", "art_deco", "skeuomorphism", "card_ui"}
        identified_set = set(identify_trends(prompt, inspiration))
        self.assertTrue(expected_trends_set.issubset(identified_set),
                        f"Expected at least {expected_trends_set}, got {identified_set}")

if __name__ == '__main__':
    # Similar sys.path adjustment as in other test files for direct execution
    # Not strictly necessary if run via `python -m unittest discover` from project root
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root_for_test = os.path.abspath(os.path.join(current_dir, '..', '..'))
    if project_root_for_test not in sys.path:
        sys.path.insert(0, project_root_for_test)
    
    # It's better to run tests using `python -m unittest discover tests` or specific module like
    # `python -m unittest tests.test_analyze_trends` from the project root directory.
    unittest.main()
