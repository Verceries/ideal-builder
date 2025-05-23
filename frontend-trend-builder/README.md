# Frontend Trend Builder

**Version:** 0.5.0 (Data Provider Refactor)

## Description

The Frontend Trend Builder is an autonomous agent designed to streamline the initial phases of frontend development. It attempts to gather live design inspiration (from Unsplash) and font suggestions (from Google Fonts) if API keys are configured via a `.env` file. Data fetching from external sources is handled by dedicated data provider modules. If live data fetching is not possible (e.g., missing keys, network issues), it falls back to analyzing user prompts against local mock data. It then interprets current UI/UX trends from a predefined dictionary and uses this information to generate boilerplate frontend code (React + Tailwind CSS) and suggest relevant assets. This agent aims to accelerate the process of translating ideas into tangible frontend structures.

## Features

-   **Inspiration Gathering (Unsplash):**
    -   The `unsplash_provider.py` module (via `fetch_unsplash_images`) attempts to fetch inspiration images from Unsplash using an API key (`UNSPLASH_API_KEY` in `.env`).
    -   **Scraping Fallback:** If the API key is missing, invalid, or the API call fails, it attempts to scrape Unsplash search results.
    -   **Mock Data Fallback:** If both API and scraping fail, it uses a predefined list of mock Unsplash images.
    -   All returned image data includes a `source` field indicating its origin (e.g., `"Unsplash_API"`, `"Unsplash_Scrape"`, `"Unsplash_Mock_Fallback"`).
-   **Font Suggestions (Google Fonts):**
    -   The `google_fonts_provider.py` module (via `fetch_google_fonts`, used within `suggest_assets.py`) attempts to fetch font suggestions from the Google Fonts API if `GOOGLE_FONTS_API_KEY` is configured in `.env`.
    -   Font suggestions are targeted based on identified trend tags (e.g., "serif_fonts", "cyberpunk_fonts").
    -   **Mock Fallback:** If the API call fails, is not configured, or returns no results for a requested category, `suggest_assets.py` falls back to providing relevant fonts from `mock_asset_data.json`, matching by font category.
    -   All suggested fonts include a `source` field (e.g., `"GoogleFonts_API"`, `"mock_fallback_font"`).
-   **Trend Analysis:**
    *   Identifies relevant UI/UX trends from the user's prompt and inspiration summary using an expanded keyword dictionary (`data/trend_dictionary.json`).
    *   Recognizes a broader range of styles, including `cyberpunk`, `art_deco`, `skeuomorphism`, `playful_aesthetic`, and `corporate_style`, among others.
-   **Code Generation (React + Tailwind CSS):**
    -   **Component Templates:** Provides templates for `Navbar`, `Hero Section`, `Features Section`, `Footer`, `Testimonial`, and `Modal` components. These templates are now organized into individual files within `actions/code_templates/react_tailwind/`.
    -   **Full-Page Layout Assembly:** Implemented logic in `generate_code.py` (specifically `assemble_full_page_layout`) to construct full-page layouts. This function interprets the user's prompt to determine the sequence and count of components (e.g., "a page with a navbar, two hero sections, and a footer"). If the prompt is vague, a default layout (Navbar, Features Section, Footer) is used.
    -   **Single Component Generation:** Can still generate code for individual components based on keywords in the prompt.
-   **Asset Suggestion Improvements:**
    -   Font suggestions are more targeted based on trend analysis (e.g., suggesting "handwriting" category fonts for "playful_aesthetic_fonts").
    -   All suggested assets (fonts, icons, images) now include a `source` field (e.g., `"GoogleFonts_API"`, `"Unsplash_API"`, `"mock_icon"`, `"mock_font"`) for better clarity on their origin.

## Inputs

The agent accepts the following inputs, defined in `schema.py` as `AgentInput`:

-   `prompt` (str): A textual description of the desired UI component or page (e.g., "Create a page with a navbar, a hero section, two features sections, and a footer.").
-   `tech_stack` (Literal["react-tailwind", "html-css", "vue", "svelte"]): The desired technology stack. **Currently, only "react-tailwind" is actively implemented for code generation.**
-   `color_mode` (Literal["light", "dark", "auto"]): The preferred color scheme for the UI.
-   `layout_type` (Literal["component", "full-page"]): Specifies whether to generate a single component or a full page structure.

## Outputs

The agent produces the following outputs, defined in `schema.py` as `AgentOutput`:

-   `frontend_code` (str): The generated frontend code (React + Tailwind CSS). For full pages, this includes a main layout component and definitions for the included components.
-   `asset_suggestions` (List[Dict]): A list of suggested asset dictionaries, each with a `source` field.
-   `trend_tags` (List[str]): A list of identified UI/UX trends.
-   `inspiration_summary` (str): A summary string derived from matched inspiration items (if any).

## Configuration

This project uses a `.env` file to manage API keys for external services and other configurations like logging levels.

1.  **Install `python-dotenv`**:
    This project uses the `python-dotenv` library to load environment variables from a `.env` file. If you are setting this project up manually and haven't installed dependencies, you might need to install it:
    ```bash
    pip install python-dotenv
    ```
    *(Note: If a `requirements.txt` file is present in the project, prefer installing dependencies from it, e.g., `pip install -r requirements.txt`)*

2.  **Create your `.env` file**:
    In the root of the `frontend-trend-builder` project, copy the example environment file:
    ```bash
    cp .env.example .env
    ```

3.  **Edit your `.env` file**:
    Open the newly created `.env` file with a text editor.

    ### API Keys for Live Data (Optional but Recommended for Full Functionality)
    Add your API keys if you want to enable live data fetching from Unsplash and Google Fonts:
    ```env
    # Unsplash API Key (Client ID)
    # Obtain from your Unsplash developer dashboard: https://unsplash.com/developers
    UNSPLASH_API_KEY=YOUR_ACTUAL_UNSPLASH_KEY_HERE

    # Google Fonts API Key
    # Obtain from your Google Cloud Platform Console: https://console.cloud.google.com/apis/credentials
    GOOGLE_FONTS_API_KEY=YOUR_ACTUAL_GOOGLE_FONTS_KEY_HERE
    ```
    Replace `YOUR_ACTUAL_..._KEY_HERE` with your real keys. If keys are not provided, are invalid, or are placeholders, the agent will gracefully fall back to using local mock data or scraping (for Unsplash).

    ### Logging Configuration (Optional)
    You can also set the `LOG_LEVEL` in your `.env` file. This controls the verbosity of the application's logs.
    Supported levels are `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`. The default is `INFO` if not set.

    Example in `.env`:
    ```env
    LOG_LEVEL=DEBUG
    ```

The application, via `config.py`, will load these settings from the `.env` file at runtime.

**Important:** Remember to keep your `.env` file private and **do not commit it to version control**. The `.gitignore` file in this project is already configured to ignore `.env` files.

**Note on API Usage Simulation:** The agent uses the `view_text_website` tool (via `data_providers/http_client.py`) to simulate API calls. In a real-world scenario, these would be direct HTTP requests using libraries like `requests`.

## How to Run

1.  Ensure you have Python installed.
2.  (Optional but recommended for live data and custom logging) Configure your `.env` file as described in the "Configuration" section.
3.  Navigate to the `frontend-trend-builder` root directory.
4.  The primary way to interact with the agent is by calling the `run_agent` function from `frontend_trend_builder.main`.

### Example Usage (Python Script)
```python
from frontend_trend_builder.main import run_agent
from frontend_trend_builder.schema import AgentInput

# Example: Generate a full landing page with specific trends
inputs = AgentInput(
    prompt="Create a page with a navbar, a hero section, two features sections, and a footer. The style should be modern and minimalist.",
    tech_stack="react-tailwind",
    color_mode="light",
    layout_type="full-page"
)
output = run_agent(inputs)

# The run_agent function logs its progress and the final output.
# To see more detailed logs (like DEBUG), set LOG_LEVEL=DEBUG in your .env file.

# You can also inspect the 'output' dictionary:
# print("\\n--- Generated Frontend Code (Full Page) ---")
# print(output['frontend_code']) 

# print("\\n--- Suggested Assets ---")
# for asset in output['asset_suggestions']:
#     print(f"- Name: {asset.get('name')} (Type: {asset.get('type')}, Source: {asset.get('source', 'mock_data')})")

# print("\\n--- Trend Tags ---")
# print(output['trend_tags'])

# print("\\n--- Inspiration Summary ---")
# print(output['inspiration_summary'])

# To run the default example in main.py (which also uses run_agent):
# python frontend_trend_builder/main.py
```

## Limitations and Known Issues

-   **API Key Requirement:** Live API integration for Unsplash and Google Fonts provides the best results and requires users to obtain and correctly configure their own API keys in the `.env` file. Without these, the agent falls back to mock data or scraping.
-   **Experimental Scraping:** The HTML scraping for Unsplash inspiration is a basic implementation and is highly dependent on Unsplash's website structure. It may break if the site's HTML changes significantly and is less reliable than the API.
-   **API Rate Limits:** If using personal or demo API keys, be mindful of potential rate limits imposed by Unsplash and Google Fonts.
-   **Simulated API Calls:** External API calls are simulated using a `view_text_website` tool. A production version would use direct HTTP requests.
-   **Limited Scope of Analysis:** Trend analysis and inspiration matching are based on keyword dictionaries and simple text matching. Prompt interpretation for full-page layout component order and count is rule-based and may not understand all natural language nuances.
-   **Styling Application:** While trend-specific styling rules exist in `apply_trend_styles`, their application to the refactored static template strings (especially for full-page layouts) is currently limited. The generated code uses the base styles from the templates; dynamic and granular style injection based on trends across the entire page structure is an area for future improvement.

## Directory Structure

-   `frontend-trend-builder/`
    -   `actions/`: Contains Python scripts for individual agent capabilities.
        -   `code_templates/`: Contains component string templates.
            -   `react_tailwind/`: Contains React+Tailwind CSS component templates (e.g., `navbar.py`, `hero.py`).
        -   `analyze_trends.py`: Identifies trends from text.
        -   `generate_code.py`: Generates React+Tailwind code from templates.
        -   `suggest_assets.py`: Suggests fonts, icons, and images.
        -   `gather_inspiration.py`: Fetches inspiration from Unsplash.
    -   `config.py`: Manages loading of API keys and configurations.
    -   `data/`: Contains JSON files for mock data and trend definitions.
        -   `mock_asset_data.json`
        -   `mock_inspiration_data.json`
        -   `trend_dictionary.json`
    -   `data_providers/`: Modules for fetching data from external APIs or sources.
        -   `__init__.py`
        -   `http_client.py`: Wrapper for `view_text_website` tool.
        -   `unsplash_provider.py`: Fetches/scrapes data from Unsplash.
        -   `google_fonts_provider.py`: Fetches data from Google Fonts API.
    -   `.env.example`: Example file for environment variable configuration.
    -   `.gitignore`: Specifies intentionally untracked files.
    -   `tests/`: Contains unit tests.
        -   `data_providers/`: Tests for data provider modules (e.g., `test_unsplash_provider.py`, `test_google_fonts_provider.py`).
        -   `test_analyze_trends.py`
        -   `test_generate_code.py`
    -   `main.py`: Main executable script for the agent.
    -   `schema.py`: Defines `AgentInput` and `AgentOutput` data structures.
    -   `README.md`: This file.

## v0.4.0+ Roadmap

The following features and improvements are planned for future versions:

-   **Expanded Template Support:**
    *   Adding Bootstrap or plain HTML+CSS template options.
    *   Implementing robust tech stack branching logic in `generate_code.py` to support different template sets.
-   **Advanced Trend Detection:**
    *   Moving from keyword-based trend detection to basic NLP techniques or embedding-based matching for more nuanced understanding of prompts.
-   **Enhanced Styling Application:**
    *   Improving the `apply_trend_styles` function or developing a new mechanism to more effectively apply trend-based styles to the static template strings, potentially by parsing and modifying templates or using a more sophisticated templating engine.
-   **Interactive Mode:** Allow users to refine component choices or requested elements.
-   **Wider Range of Components:** Add more pre-defined components to the template library.
-   **Error Handling and Resilience:** Improve error handling across all modules.
