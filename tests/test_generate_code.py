import unittest
from unittest.mock import patch, MagicMock
import json

# Adjust import paths based on test execution context
from frontend_trend_builder.actions.generate_code import (
    create_code, 
    assemble_full_page_layout, 
    find_components_in_prompt,
    DEFAULT_FULL_PAGE_ORDER
)
# REACT_TAILWIND_TEMPLATES will be mocked.

MOCK_TEMPLATES_REGISTRY = {
    "Navbar": "const Navbar = () => <nav>Navbar</nav>; export default Navbar;",
    "Hero Section": "const HeroSection = () => <section>Hero Section</section>; export default HeroSection;",
    "Features Section": "const FeaturesSection = () => <section>Features Section</section>; export default FeaturesSection;",
    "Testimonial": "const Testimonial = () => <div>Testimonial</div>; export default Testimonial;",
    "Footer": "const Footer = () => <footer>Footer</footer>; export default Footer;",
    "Modal": "const Modal = () => <div>Modal</div>; export default Modal;"
}

class TestGenerateCode(unittest.TestCase):

    def test_find_components_in_prompt_order_and_count(self):
        prompt = "Build a page with a navbar, then two hero sections, a features section, and finally a footer."
        trends = []
        expected = ["Navbar", "Hero Section", "Hero Section", "Features Section", "Footer"]
        # Note: find_components_in_prompt also adds default Navbar/Footer if "page" context is detected and they are missing.
        # The prompt "Build a page with..." establishes this context.
        actual = find_components_in_prompt(prompt, trends)
        self.assertEqual(actual, expected)

    def test_find_components_in_prompt_default_if_vague(self):
        prompt = "A cool website."
        trends = ["modern_ui"] # modern_ui maps to sans-serif, doesn't directly imply structural components beyond default
        # Default order: Navbar, Features Section, Footer (Hero is optional based on keywords)
        expected = ["Navbar", "Features Section", "Footer"]
        actual = find_components_in_prompt(prompt, trends)
        self.assertEqual(actual, expected)
        
    def test_find_components_in_prompt_hero_from_trend(self):
        prompt = "A cool website."
        trends = ["hero"] 
        # Default order: Navbar, Hero Section (from trend), Features Section, Footer
        expected_with_hero = ["Navbar", "Hero Section", "Features Section", "Footer"]
        actual = find_components_in_prompt(prompt, trends)
        self.assertEqual(actual, expected_with_hero)

    def test_find_components_in_prompt_no_specifics(self):
        prompt = "I want a webpage."
        trends = []
        expected = ["Navbar", "Features Section", "Footer"] # Default, no hero
        actual = find_components_in_prompt(prompt, trends)
        self.assertEqual(actual, expected)

    @patch('frontend_trend_builder.actions.generate_code.REACT_TAILWIND_TEMPLATES', MOCK_TEMPLATES_REGISTRY)
    def test_assemble_full_page_layout_specific_prompt(self):
        prompt = "A page with a navbar, one hero section, and a footer."
        trends = []
        color_mode = "light"
        
        code = assemble_full_page_layout(prompt, trends, color_mode)
        
        self.assertIn("import React from 'react';", code)
        self.assertIn("import Navbar from './components/Navbar';", code)
        self.assertIn("import HeroSection from './components/HeroSection';", code)
        self.assertIn("import Footer from './components/Footer';", code)
        self.assertIn("<Navbar />", code)
        self.assertIn("<HeroSection />", code)
        self.assertIn("<Footer />", code)
        self.assertNotIn("<FeaturesSection />", code)
        self.assertIn("const FullPageLayout = (props) => {", code)
        # Check order
        self.assertTrue(code.find("<Navbar />") < code.find("<HeroSection />") < code.find("<Footer />"))
        # Check that component definitions are appended
        self.assertIn("const Navbar = () => <nav>Navbar</nav>;", code)
        self.assertIn("const HeroSection = () => <section>Hero Section</section>;", code)

    @patch('frontend_trend_builder.actions.generate_code.REACT_TAILWIND_TEMPLATES', MOCK_TEMPLATES_REGISTRY)
    def test_assemble_full_page_layout_default_components(self):
        prompt = "A very simple page." # No specific components, implies default page structure
        trends = []
        color_mode = "light"
        
        code = assemble_full_page_layout(prompt, trends, color_mode)
        
        self.assertIn("<Navbar />", code)
        self.assertIn("<FeaturesSection />", code) # Part of default if no hero
        self.assertIn("<Footer />", code)
        self.assertNotIn("<HeroSection />", code) # Not mentioned, not in simple default
        self.assertNotIn("<Testimonial />", code)

    @patch('frontend_trend_builder.actions.generate_code.REACT_TAILWIND_TEMPLATES', MOCK_TEMPLATES_REGISTRY)
    def test_assemble_full_page_layout_with_counts(self):
        prompt = "I need a page with a navbar, two features sections, and a footer."
        trends = []
        color_mode = "dark"
        
        code = assemble_full_page_layout(prompt, trends, color_mode)
        
        self.assertIn("<Navbar />", code)
        self.assertEqual(code.count("<FeaturesSection />"), 2)
        self.assertIn("<Footer />", code)
        self.assertNotIn("<HeroSection />", code)
        # Check order
        self.assertTrue(code.find("<Navbar />") < code.find("<FeaturesSection />"))
        self.assertTrue(code.rfind("<FeaturesSection />") < code.find("<Footer />"))


    @patch('frontend_trend_builder.actions.generate_code.REACT_TAILWIND_TEMPLATES', MOCK_TEMPLATES_REGISTRY)
    def test_create_code_full_page(self):
        inspiration = "A full page with a navbar and footer."
        trends = []
        # Expected to call assemble_full_page_layout
        code = create_code(inspiration, trends, "react-tailwind", "light", "full-page")
        self.assertIn("const FullPageLayout = (props) => {", code)
        self.assertIn("<Navbar />", code)
        self.assertIn("<Footer />", code)
        self.assertNotIn("<HeroSection />", code) # Not in prompt

    @patch('frontend_trend_builder.actions.generate_code.REACT_TAILWIND_TEMPLATES', MOCK_TEMPLATES_REGISTRY)
    def test_create_code_single_component(self):
        inspiration = "I need a hero section."
        trends = ["hero"]
        code = create_code(inspiration, trends, "react-tailwind", "dark", "component")
        self.assertIn("const HeroSection = () => <section>Hero Section</section>;", code)
        self.assertNotIn("const FullPageLayout", code) # Should be just the component

    @patch('frontend_trend_builder.actions.generate_code.REACT_TAILWIND_TEMPLATES', MOCK_TEMPLATES_REGISTRY)
    def test_create_code_single_component_fallback(self):
        inspiration = "Just a simple element." # No specific keywords
        trends = []
        code = create_code(inspiration, trends, "react-tailwind", "light", "component")
        # Default fallback for single component is Navbar
        self.assertIn("const Navbar = () => <nav>Navbar</nav>;", code) 
        self.assertNotIn("const FullPageLayout", code)

if __name__ == '__main__':
    import sys
    import os
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    unittest.main()
