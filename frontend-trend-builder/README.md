# Frontend Trend Builder

**Version:** 0.3.0 (Live Data Integration - Conceptual)

## Description

The Frontend Trend Builder is an autonomous agent designed to streamline the initial phases of frontend development. It attempts to gather live design inspiration (from Unsplash) and font suggestions (from Google Fonts) if API keys are configured. If live data fetching is not possible (e.g., missing keys, network issues), it falls back to analyzing user prompts against local mock data. It then interprets current UI/UX trends from a predefined dictionary and uses this information to generate boilerplate frontend code (React + Tailwind CSS) and suggest relevant assets. This agent aims to accelerate the process of translating ideas into tangible frontend structures.

## Features

-   **Gathers Inspiration (Live & Mock Data):**
    -   **Live (Conceptual):** Attempts to fetch inspiration images from Unsplash via its API if an `UNSPLASH_ACCESS_KEY` is configured.
    -   **Experimental Scraping:** If the Unsplash API call fails or is not configured, it attempts a basic HTML scrape of Unsplash search results.
    -   **Fallback:** If live/scraped data is unavailable, it filters local mock inspiration data based on keywords in a user-provided prompt.
-   **Analyzes Trends:** Identifies relevant UI/UX trends (e.g., "glassmorphism", "minimalism", "dark_mode", "pastel_colors", "serif_fonts") from the prompt and inspiration summary using a keyword dictionary.
-   **Generates React + Tailwind CSS Code:**
    -   Creates code for individual components including: Buttons, Cards, Login Forms, NavBars, Footers, Hero Sections, Feature Cards, and Testimonials.
    -   Generates "full-page" layouts by assembling a sensible structure from available components.
    -   Applies styling to components responsive to identified trends and color modes.
-   **Suggests Assets (Live & Mock Data):**
    -   **Live Fonts (Conceptual):** Attempts to fetch font suggestions from the Google Fonts API if a `GOOGLE_FONTS_API_KEY` is configured and relevant font trends (e.g., "serif_fonts") are identified.
    -   **Mock Assets:** Recommends other assets (icons, images) and fallback fonts from local mock data, aligning with design trends and inspiration.

## Inputs

The agent accepts the following inputs, defined in `schema.py` as `AgentInput`:

-   `prompt` (str): A textual description of the desired UI component or page. Examples:
    -   `"a sleek login form with glassmorphism"`
    -   `"a full-page landing site with a hero section, using glassmorphism and dark mode"`
-   `tech_stack` (Literal["react-tailwind", "html-css", "vue", "svelte"]): The desired technology stack. **Currently, only "react-tailwind" is implemented for code generation.**
-   `color_mode` (Literal["light", "dark", "auto"]): The preferred color scheme for the UI.
-   `layout_type` (Literal["component", "full-page"]): Specifies whether to generate a single component or a full page structure.

## Outputs

The agent produces the following outputs, defined in `schema.py` as `AgentOutput`:

-   `frontend_code` (str): The generated frontend code (React + Tailwind CSS).
-   `asset_suggestions` (List[Dict]): A list of suggested asset dictionaries (name, type, URL mock, tags), potentially including fonts from Google Fonts API.
-   `trend_tags` (List[str]): A list of identified UI/UX trends.
-   `inspiration_summary` (str): A summary string derived from matched inspiration items (live or mock).

## Configuration (API Keys for Live Data)

To enable live data fetching for inspiration and fonts, you need to configure API keys:

1.  **Unsplash API Key (for Inspiration Images):**
    *   Obtain an Access Key by registering an application at [https://unsplash.com/developers](https://unsplash.com/developers).
    *   Open the file: `frontend-trend-builder/actions/gather_inspiration.py`.
    *   Find the line: `UNSPLASH_ACCESS_KEY = "YOUR_UNSPLASH_ACCESS_KEY_IF_AVAILABLE"`
    *   Replace `"YOUR_UNSPLASH_ACCESS_KEY_IF_AVAILABLE"` with your actual Unsplash Access Key.
    *   If this key is not provided or remains the placeholder, the agent will attempt HTML scraping, and then fall back to mock data for inspiration.

2.  **Google Fonts API Key (for Font Suggestions):**
    *   Obtain an API Key from the [Google Cloud Console](https://console.cloud.google.com/apis/library/webfonts.googleapis.com).
    *   Open the file: `frontend-trend-builder/actions/suggest_assets.py`.
    *   Find the line: `GOOGLE_FONTS_API_KEY = "YOUR_GOOGLE_FONTS_API_KEY_IF_AVAILABLE"`
    *   Replace `"YOUR_GOOGLE_FONTS_API_KEY_IF_AVAILABLE"` with your actual Google Fonts API Key.
    *   If this key is not provided or remains the placeholder, the agent will use mock font data.

**Note:** The agent uses the `view_text_website` tool to simulate API calls. In a real-world scenario, these would be direct HTTP requests using libraries like `requests`.

## How to Run

1.  Ensure you have Python installed.
2.  (Optional) Configure API keys as described in the "Configuration" section.
3.  Navigate to the `frontend-trend-builder` root directory.
4.  The primary way to interact with the agent is by calling the `run_agent` function from `frontend_trend_builder.main`.

### Example Usage (Python Script)

```python
from frontend_trend_builder.main import run_agent
from frontend_trend_builder.schema import AgentInput

# Example: Generate a full landing page with specific trends
inputs = AgentInput(
    prompt="Create a full landing page with a hero section, two feature cards, and a footer. Use glassmorphism and dark mode with serif fonts.",
    tech_stack="react-tailwind",
    color_mode="dark",
    layout_type="full-page"
)
output = run_agent(inputs)

# The run_agent function logs its progress and the final output.
# You can also inspect the 'output' dictionary:
print("\n--- Generated Frontend Code (Snippet) ---")
print(output['frontend_code'][:500] + "...") 

print("\n--- Suggested Assets ---")
for asset in output['asset_suggestions']:
    print(f"- {asset.get('name')} (Type: {asset.get('type')}, Source: {asset.get('source', 'mock_data')})")

print("\n--- Trend Tags ---")
print(output['trend_tags'])

print("\n--- Inspiration Summary ---")
print(output['inspiration_summary'])

# To run the default example in main.py (which also uses run_agent):
# python frontend_trend_builder/main.py
```

## Limitations and Known Issues

-   **API Key Requirement:** Live API integration for Unsplash and Google Fonts requires users to obtain and insert their own API keys. Without these, the agent gracefully falls back to mock data.
-   **Experimental Scraping:** The HTML scraping for Unsplash inspiration is a basic implementation and is highly dependent on Unsplash's website structure. It may break if the site's HTML changes significantly.
-   **API Rate Limits:** If using personal or demo API keys, be mindful of potential rate limits imposed by Unsplash and Google Fonts.
-   **Simulated API Calls:** External API calls are simulated using a `view_text_website` tool. A production version would use direct HTTP requests.
-   **Limited Scope of Analysis:** Trend analysis and inspiration matching are based on keyword dictionaries and simple text matching, not advanced AI/NLP.

## Directory Structure

-   `frontend-trend-builder/`
    -   `actions/`: Contains Python scripts for individual agent capabilities.
        -   `code_templates/`: Contains React+Tailwind CSS component string templates.
    -   `data/`: Contains JSON files for mock inspiration, trend definitions, and mock assets.
    -   `tests/`: Contains unit tests for the agent's components.
    -   `main.py`: The main executable script that orchestrates the agent's workflow and includes example runs.
    -   `schema.py`: Defines the data structures (`AgentInput`, `AgentOutput`) for agent inputs and outputs.
    -   `README.md`: This file.
