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
