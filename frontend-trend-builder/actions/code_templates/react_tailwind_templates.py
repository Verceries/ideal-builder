"""
React + Tailwind CSS component templates.
Each function returns a string representing a React functional component.
"""

def get_button_template(text: str = "Click Me", custom_styles: str = "") -> str:
    """Returns a string for a React button component with Tailwind CSS."""
    base_styles = "bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
    combined_styles = f"{base_styles} {custom_styles}".strip()
    return f"""
const MyButton = () => {{
  return (
    <button className="{combined_styles}">
      {text}
    </button>
  );
}};

export default MyButton;
"""

def get_card_template(title: str = "Card Title", content: str = "Card content.", custom_styles: str = "") -> str:
    """Returns a string for a React card component with Tailwind CSS."""
    base_styles = "bg-white shadow-md rounded-lg p-6"
    combined_styles = f"{base_styles} {custom_styles}".strip()
    return f"""
const MyCard = () => {{
  return (
    <div className="{combined_styles}">
      <h2 className="text-xl font-semibold mb-2">{title}</h2>
      <p>{content}</p>
    </div>
  );
}};

export default MyCard;
"""

def get_login_form_template(custom_styles: str = "") -> str:
    """Returns a string for a basic React login form with Tailwind CSS."""
    base_styles = "p-8 rounded-lg shadow-lg w-full max-w-sm"
    combined_styles = f"{base_styles} {custom_styles}".strip()
    button_custom_styles = "w-full" # Example: make button full width

    return f"""
const LoginForm = () => {{
  return (
    <form className="{combined_styles}">
      <h2 className="text-2xl font-bold mb-6 text-center">Login</h2>
      <div className="mb-4">
        <label className="block text-sm font-medium mb-1" htmlFor="username">
          Username
        </label>
        <input
          type="text"
          id="username"
          className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
        />
      </div>
      <div className="mb-6">
        <label className="block text-sm font-medium mb-1" htmlFor="password">
          Password
        </label>
        <input
          type="password"
          id="password"
          className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
        />
      </div>
      {get_button_template(text="Sign In", custom_styles=button_custom_styles)}
    </form>
  );
}};

export default LoginForm;
"""

if __name__ == "__main__":
    print("--- Button Template ---")
    print(get_button_template())
    print("\n--- Button Template (Custom) ---")
    print(get_button_template(text="Submit", custom_styles="bg-green-500 hover:bg-green-700"))

    print("\n--- Card Template ---")
    print(get_card_template())
    print("\n--- Card Template (Custom) ---")
    print(get_card_template(title="My Custom Card", content="This is custom content.", custom_styles="border-2 border-blue-500"))

    print("\n--- Login Form Template ---")
    print(get_login_form_template(custom_styles="bg-gray-100"))
    print("\n--- Login Form Template (Dark Mode Attempt) ---")
    print(get_login_form_template(custom_styles="bg-gray-800 text-white"))

    # Example of how the login form reuses the button, though the output here will be verbose
    # print("\n--- Login Form with Dark Button ---")
    # Note: The button within the login form is also a template; direct styling is tricky here
    # without more complex template logic. This is a simplified example.
    # For now, the button inside login will get its own dark mode if custom_styles for login form is dark.
    # A more robust solution would pass dark mode props down.
    dark_login_form = get_login_form_template(custom_styles="bg-gray-700 text-gray-200")
    # To make the button inside also dark, we'd need to adjust get_login_form_template
    # to pass appropriate styles to its internal get_button_template call,
    # or the button template itself needs to be dark mode aware based on its own custom_styles.
    # The current get_button_template doesn't automatically inherit parent dark mode.
    print(dark_login_form)


# --- New Templates from Step 15 ---

def get_navbar_template(logoText="Logo", navLinks=None, ctaText=None, ctaLink="#", styles="") -> str:
    """Returns a string for a React Navbar component with Tailwind CSS."""
    if navLinks is None:
        navLinks = [
            {'text': 'Home', 'href': '#home'}, 
            {'text': 'About', 'href': '#about'}, 
            {'text': 'Contact', 'href': '#contact'}
        ]

    nav_links_html = ""
    for link in navLinks:
        nav_links_html += f"""
          <li>
            <a href="{link['href']}" className="text-gray-700 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium">{link['text']}</a>
          </li>"""

    cta_button_html = ""
    if ctaText:
        cta_button_html = f"""
        <a href="{ctaLink}" className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-md text-sm font-medium ml-4">
          {ctaText}
        </a>"""

    base_styles = "bg-white shadow-sm"
    combined_styles = f"{base_styles} {styles}".strip()

    return f"""
const Navbar = () => {{
  return (
    <nav className="p-4 {combined_styles}">
      <div className="container mx-auto flex items-center justify-between">
        <div className="text-xl font-bold text-blue-600">
          {logoText}
        </div>
        <ul className="flex items-center">
          {nav_links_html}
        </ul>
        <div>
          {cta_button_html}
        </div>
      </div>
    </nav>
  );
}};

export default Navbar;
"""

def get_footer_template(copyrightText="© 2024 Your Company", socialLinks=None, linkColumns=None, styles="") -> str:
    """Returns a string for a React Footer component with Tailwind CSS."""
    if socialLinks is None:
        socialLinks = [
            {'icon': 'Twitter', 'href': '#twitter'}, 
            {'icon': 'GitHub', 'href': '#github'}
        ]
    
    social_links_html = ""
    for link in socialLinks:
        social_links_html += f"""
          <a href="{link['href']}" className="text-gray-500 hover:text-blue-600 ml-4">
            {link['icon']} {/* Replace with actual icons in a real app */}
          </a>"""

    link_columns_html = ""
    if linkColumns: # Expects linkColumns to be a list of dicts like: [{'title': 'Column 1', 'links': [{'text': 'Link 1', 'href': '#'}]}]
        link_columns_html = "<div class='grid grid-cols-2 md:grid-cols-4 gap-8 mb-8'>"
        for col in linkColumns:
            link_columns_html += "\n<div>"
            link_columns_html += f"<h3 class='text-sm font-semibold text-gray-600 uppercase tracking-wider'>{col['title']}</h3>"
            link_columns_html += "<ul class='mt-4 space-y-2'>"
            for link in col['links']:
                link_columns_html += f"<li><a href='{link['href']}' class='text-gray-500 hover:text-gray-900 text-base'>{link['text']}</a></li>"
            link_columns_html += "</ul>\n</div>"
        link_columns_html += "\n</div>"


    base_styles = "bg-gray-100 text-gray-700 py-12"
    combined_styles = f"{base_styles} {styles}".strip()
    
    return f"""
const Footer = () => {{
  return (
    <footer className="{combined_styles}">
      <div className="container mx-auto px-4">
        {link_columns_html}
        <div className="mt-8 border-t border-gray-200 pt-8 flex flex-col md:flex-row justify-between items-center">
          <p className="text-base text-gray-500">
            {copyrightText}
          </p>
          <div className="flex items-center mt-4 md:mt-0">
            {social_links_html}
          </div>
        </div>
      </div>
    </footer>
  );
}};

export default Footer;
"""

def get_hero_template(heading="Main Heading", subheading="Subheading text...", primaryCtaText="Get Started", 
                      primaryCtaLink="#", secondaryCtaText=None, secondaryCtaLink="#", 
                      backgroundImagePlaceholder=False, styles="") -> str:
    """Returns a string for a React Hero section component with Tailwind CSS."""
    
    secondary_cta_html = ""
    if secondaryCtaText:
        secondary_cta_html = f"""
          <a href="{secondaryCtaLink}" className="mt-3 sm:mt-0 sm:ml-3 inline-flex justify-center items-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-blue-700 bg-blue-100 hover:bg-blue-200">
            {secondaryCtaText}
          </a>"""

    bg_placeholder_html = ""
    if backgroundImagePlaceholder:
        bg_placeholder_html = """
        {/* Background Image Placeholder: Implement as needed, e.g., a div with background-image style */}
        <div className="absolute inset-0 bg-gray-300 opacity-50 -z-10"></div>"""

    base_styles = "bg-gray-50 py-12 sm:py-20 relative" # Added relative for z-indexing of placeholder
    combined_styles = f"{base_styles} {styles}".strip()

    return f"""
const HeroSection = () => {{
  return (
    <section className="{combined_styles}">
      {bg_placeholder_html}
      <div className="container mx-auto px-4 text-center">
        <h1 className="text-4xl tracking-tight font-extrabold text-gray-900 sm:text-5xl md:text-6xl">
          {heading}
        </h1>
        <p className="mt-3 max-w-md mx-auto text-base text-gray-500 sm:text-lg md:mt-5 md:text-xl md:max-w-3xl">
          {subheading}
        </p>
        <div className="mt-5 max-w-md mx-auto sm:flex sm:justify-center md:mt-8">
          <div className="rounded-md shadow">
            <a href="{primaryCtaLink}" className="w-full flex items-center justify-center px-8 py-3 border border-transparent text-base font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 md:py-4 md:text-lg md:px-10">
              {primaryCtaText}
            </a>
          </div>
          {secondary_cta_html}
        </div>
      </div>
    </section>
  );
}};

export default HeroSection;
"""

def get_feature_card_template(iconPlaceholder=False, imagePlaceholder=False, title="Feature Title", 
                              description="Feature description.", learnMoreLink=None, styles="") -> str:
    """Returns a string for a React Feature Card component with Tailwind CSS."""

    placeholder_html = ""
    if iconPlaceholder:
        placeholder_html = """
        <div className="flex items-center justify-center h-12 w-12 rounded-md bg-blue-500 text-white mb-4">
          {/* Icon Placeholder (e.g., SVG) */}
          <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" /></svg>
        </div>"""
    elif imagePlaceholder:
        placeholder_html = """
        <div className="w-full h-48 bg-gray-300 rounded-t-lg mb-4">
          {/* Image Placeholder */}
        </div>"""
        
    learn_more_html = ""
    if learnMoreLink:
        learn_more_html = f"""
        <div className="mt-4">
          <a href="{learnMoreLink}" className="text-blue-600 hover:text-blue-800 font-semibold text-sm">
            Learn More &rarr;
          </a>
        </div>"""

    base_styles = "bg-white shadow-lg rounded-lg p-6"
    # If there's an image placeholder, card padding might need adjustment or image placeholder needs rounded-t-lg
    card_content_class = "flex flex-col" if imagePlaceholder else "" # Adjust layout if image is on top
    combined_styles = f"{base_styles} {styles}".strip()


    return f"""
const FeatureCard = () => {{
  return (
    <div className="{combined_styles} {card_content_class}">
      {placeholder_html}
      <h3 className="text-xl font-semibold text-gray-900 mb-2">{title}</h3>
      <p className="text-gray-600 text-base">
        {description}
      </p>
      {learn_more_html}
    </div>
  );
}};

export default FeatureCard;
"""

def get_testimonial_template(quote="This is a fantastic product!", authorName="Jane Doe", 
                             authorTitle="CEO, ExampleCo", imagePlaceholder=False, styles="") -> str:
    """Returns a string for a React Testimonial component with Tailwind CSS."""

    author_image_html = ""
    if imagePlaceholder:
        author_image_html = """
          <div className="flex-shrink-0">
            {/* Author Image Placeholder */}
            <div className="w-12 h-12 rounded-full bg-gray-300"></div>
          </div>"""
    
    base_styles = "bg-gray-50 p-6 rounded-lg shadow"
    combined_styles = f"{base_styles} {styles}".strip()

    return f"""
const Testimonial = () => {{
  return (
    <div className="{combined_styles}">
      <blockquote className="text-gray-600 italic mb-4">
        "{quote}"
      </blockquote>
      <div className="flex items-center">
        {author_image_html}
        <div className={"ml-4" if imagePlaceholder else ""}>
          <p className="font-semibold text-gray-900">{authorName}</p>
          <p className="text-sm text-gray-500">{authorTitle}</p>
        </div>
      </div>
    </div>
  );
}};

export default Testimonial;
"""


if __name__ == "__main__":
    print("--- Button Template ---")
    print(get_button_template())
    print("\n--- Button Template (Custom) ---")
    print(get_button_template(text="Submit", custom_styles="bg-green-500 hover:bg-green-700"))

    print("\n--- Card Template ---")
    print(get_card_template())
    print("\n--- Card Template (Custom) ---")
    print(get_card_template(title="My Custom Card", content="This is custom content.", custom_styles="border-2 border-blue-500"))

    print("\n--- Login Form Template ---")
    print(get_login_form_template(custom_styles="bg-gray-100"))
    
    dark_login_form = get_login_form_template(custom_styles="bg-gray-700 text-gray-200")
    print("\n--- Login Form Template (Dark Mode Attempt) ---")
    print(dark_login_form)

    print("\n--- Navbar Template (Default) ---")
    print(get_navbar_template())
    print("\n--- Navbar Template (With CTA) ---")
    print(get_navbar_template(logoText="MyApp", ctaText="Sign Up", styles="bg-blue-100"))

    print("\n--- Footer Template (Default) ---")
    print(get_footer_template())
    print("\n--- Footer Template (With Link Columns) ---")
    footer_link_cols = [
        {'title': 'Products', 'links': [{'text': 'Product A', 'href': '#'}, {'text': 'Product B', 'href': '#'}]},
        {'title': 'Company', 'links': [{'text': 'About Us', 'href': '#'}, {'text': 'Careers', 'href': '#'}]}
    ]
    print(get_footer_template(linkColumns=footer_link_cols, styles="bg-gray-800 text-white"))

    print("\n--- Hero Template (Default) ---")
    print(get_hero_template())
    print("\n--- Hero Template (With Secondary CTA & BG Placeholder) ---")
    print(get_hero_template(heading="Welcome to Awesome", subheading="Discover the future with us.", 
                            primaryCtaText="Learn More", secondaryCtaText="View Pricing", 
                            backgroundImagePlaceholder=True, styles="text-indigo-600"))

    print("\n--- Feature Card Template (Icon) ---")
    print(get_feature_card_template(iconPlaceholder=True, title="Fast Performance", learnMoreLink="#"))
    print("\n--- Feature Card Template (Image & Custom Style) ---")
    print(get_feature_card_template(imagePlaceholder=True, title="Beautiful Design", 
                                    description="Modern and intuitive user interface.", 
                                    styles="border-2 border-green-500"))
    
    print("\n--- Testimonial Template (Default) ---")
    print(get_testimonial_template())
    print("\n--- Testimonial Template (With Image & Custom Style) ---")
    print(get_testimonial_template(quote="Absolutely changed the way we work!", authorName="Sam B.", 
                                   authorTitle="Lead Developer, TechCorp", imagePlaceholder=True, 
                                   styles="bg-purple-100"))
