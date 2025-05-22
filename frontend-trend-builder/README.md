# Frontend Trend Builder

**Version:** 0.4.0 (Centralized Configuration)

## Description

The Frontend Trend Builder is an autonomous agent designed to streamline the initial phases of frontend development. It attempts to gather live design inspiration (from Unsplash) and font suggestions (from Google Fonts) if API keys are configured via a `.env` file. If live data fetching is not possible (e.g., missing keys, network issues), it falls back to analyzing user prompts against local mock data. It then interprets current UI/UX trends from a predefined dictionary and uses this information to generate boilerplate frontend code (React + Tailwind CSS) and suggest relevant assets. This agent aims to accelerate the process of translating ideas into tangible frontend structures.

## Features

-   **Gathers Inspiration (Live & Mock Data):**
    -   **Live (Conceptual):** Attempts to fetch inspiration images from Unsplash via its API if `UNSPLASH_API_KEY` is configured in `.env`.
    -   **Experimental Scraping:** If the Unsplash API call fails or is not configured, it attempts a basic HTML scrape of Unsplash search results.
    -   **Fallback:** If live/scraped data is unavailable, it filters local mock inspiration data based on keywords in a user-provided prompt.
-   **Analyzes Trends:** Identifies relevant UI/UX trends from the prompt and inspiration summary using an expanded keyword dictionary. Includes broader trend recognition for styles like cyberpunk, art deco, skeuomorphism, playful, and corporate aesthetics, among others.
-   **Generates React + Tailwind CSS Code:**
    -   Creates code for individual components including: Buttons, Cards, Login Forms, NavBars, Footers, Hero Sections, Feature Cards, and Testimonials.
    -   Generates "full-page" layouts by assembling a sensible structure from available components.
    -   Applies styling to components responsive to identified trends and color modes.
-   **Suggests Assets (Live & Mock Data):**
    -   **Live Fonts (Conceptual):** Attempts to fetch font suggestions from the Google Fonts API if `GOOGLE_FONTS_API_KEY` is configured in `.env` and relevant font trends are identified.
    -   **Mock Assets:** Recommends other assets (icons, images) and fallback fonts from local mock data, aligning with design trends and inspiration.

## Inputs

The agent accepts the following inputs, defined in `schema.py` as `AgentInput`:

-   `prompt` (str): A textual description of the desired UI component or page.
-   `tech_stack` (Literal["react-tailwind", "html-css", "vue", "svelte"]): The desired technology stack. **Currently, only "react-tailwind" is implemented for code generation.**
-   `color_mode` (Literal["light", "dark", "auto"]): The preferred color scheme for the UI.
-   `layout_type` (Literal["component", "full-page"]): Specifies whether to generate a single component or a full page structure.

## Outputs

The agent produces the following outputs, defined in `schema.py` as `AgentOutput`:

-   `frontend_code` (str): The generated frontend code (React + Tailwind CSS).
-   `asset_suggestions` (List[Dict]): A list of suggested asset dictionaries.
-   `trend_tags` (List[str]): A list of identified UI/UX trends.
-   `inspiration_summary` (str): A summary string derived from matched inspiration items.

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

    ### API Keys for Live Data (Optional)
    Add your API keys if you want to enable live data fetching:
    ```env
    # Unsplash API Key (Client ID)
    # Obtain from your Unsplash developer dashboard: https://unsplash.com/developers
    UNSPLASH_API_KEY=YOUR_ACTUAL_UNSPLASH_KEY_HERE

    # Google Fonts API Key
    # Obtain from your Google Cloud Platform Console: https://console.cloud.google.com/apis/credentials
    GOOGLE_FONTS_API_KEY=YOUR_ACTUAL_GOOGLE_FONTS_KEY_HERE
    ```
    Replace `YOUR_ACTUAL_..._KEY_HERE` with your real keys. If keys are not provided or are invalid, the agent will gracefully fall back to using local mock data.

    ### Logging Configuration (Optional)
    You can also set the `LOG_LEVEL` in your `.env` file. This controls the verbosity of the application's logs.
    Supported levels are `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`. The default is `INFO` if not set.

    Example in `.env`:
    ```env
    LOG_LEVEL=DEBUG
    ```

The application, via `config.py`, will load these settings from the `.env` file at runtime.

**Important:** Remember to keep your `.env` file private and **do not commit it to version control**. The `.gitignore` file in this project is already configured to ignore `.env` files.

**Note on API Usage Simulation:** The agent uses the `view_text_website` tool to simulate API calls. In a real-world scenario, these would be direct HTTP requests using libraries like `requests`.

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
    prompt="Create a full landing page with a hero section, two feature cards, and a footer. Use glassmorphism and dark mode with serif fonts.",
    tech_stack="react-tailwind",
    color_mode="dark",
    layout_type="full-page"
)
output = run_agent(inputs)

# The run_agent function logs its progress and the final output.
# To see more detailed logs (like DEBUG), set LOG_LEVEL=DEBUG in your .env file.
# You can also inspect the 'output' dictionary:
# print("\n--- Generated Frontend Code (Snippet) ---")
# print(output['frontend_code'][:500] + "...") 

# print("\n--- Suggested Assets ---")
# for asset in output['asset_suggestions']:
#     print(f"- {asset.get('name')} (Type: {asset.get('type')}, Source: {asset.get('source', 'mock_data')})")

# print("\n--- Trend Tags ---")
# print(output['trend_tags'])

# print("\n--- Inspiration Summary ---")
# print(output['inspiration_summary'])

# To run the default example in main.py (which also uses run_agent):
# python frontend_trend_builder/main.py
```

## Limitations and Known Issues

-   **API Key Requirement:** Live API integration for Unsplash and Google Fonts requires users to obtain and correctly configure their own API keys in the `.env` file. Without these, the agent gracefully falls back to mock data.
-   **Experimental Scraping:** The HTML scraping for Unsplash inspiration is a basic implementation and is highly dependent on Unsplash's website structure. It may break if the site's HTML changes significantly.
-   **API Rate Limits:** If using personal or demo API keys, be mindful of potential rate limits imposed by Unsplash and Google Fonts.
-   **Simulated API Calls:** External API calls are simulated using a `view_text_website` tool. A production version would use direct HTTP requests.
-   **Limited Scope of Analysis:** Trend analysis and inspiration matching are based on keyword dictionaries and simple text matching, not advanced AI/NLP.

## Directory Structure

-   `frontend-trend-builder/`
    -   `actions/`: Contains Python scripts for individual agent capabilities.
        -   `code_templates/`: Contains React+Tailwind CSS component string templates.
    -   `config.py`: Manages loading of API keys and other configurations from the `.env` file.
    -   `data/`: Contains JSON files for mock inspiration, trend definitions, and mock assets.
    -   `.env.example`: Example file for environment variable configuration.
    -   `.gitignore`: Specifies intentionally untracked files (like `.env`).
    -   `tests/`: Contains unit tests for the agent's components.
    -   `main.py`: The main executable script that orchestrates the agent's workflow and includes example runs.
    -   `schema.py`: Defines the data structures (`AgentInput`, `AgentOutput`) for agent inputs and outputs.
    -   `README.md`: This file.
