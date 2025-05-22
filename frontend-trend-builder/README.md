# Frontend Trend Builder

**Version:** 0.2.0 (Enhanced Generation & Styling)

## Description

The Frontend Trend Builder is an autonomous agent designed to streamline the initial phases of frontend development. It gathers design inspiration by analyzing user prompts and mock data, interprets current UI/UX trends from a predefined dictionary, and then uses this information to generate boilerplate frontend code (React + Tailwind CSS) and suggest relevant assets. This agent aims to accelerate the process of translating ideas into tangible frontend structures.

**Note:** While this agent now generates more complex code structures and applies styling based on trends, it still uses mock data for inspiration and assets. Advanced AI/ML logic for true visual analysis or novel code generation is not part of this implementation.

## Features

-   **Gathers Inspiration:** Filters mock inspiration data based on keywords in a user-provided prompt.
-   **Analyzes Trends:** Identifies relevant UI/UX trends (e.g., "glassmorphism", "minimalism", "dark_mode", "pastel_colors", "serif_fonts") from the prompt and inspiration summary using a keyword dictionary.
-   **Generates React + Tailwind CSS Code:**
    -   Creates code for individual components including:
        -   Buttons
        -   Cards (general purpose)
        -   Login Forms
        -   **New**: NavBars, Footers, Hero Sections, Feature Cards, Testimonials.
    -   Generates "full-page" layouts by assembling a sensible structure from available components (e.g., Navbar, Hero/Features, Footer).
    -   Applies styling to components that is responsive to identified trends and color modes. For example, "minimalism" will aim for cleaner lines and less shadow, "glassmorphism" will apply blur and transparency effects, and "pastel_colors" will use softer color palettes.
-   **Suggests Assets:** Recommends assets (icons, fonts, images) from mock data that align with the identified design trends and inspiration.

## Inputs

The agent accepts the following inputs, defined in `schema.py` as `AgentInput`:

-   `prompt` (str): A textual description of the desired UI component or page. Examples:
    -   `"a sleek login form with glassmorphism"`
    -   `"a full-page landing site with a hero section, using glassmorphism and dark mode"`
    -   `"a minimalist navigation bar with serif fonts"`
    -   `"a feature card component with pastel colors"`
    -   `"generate a page with a navbar, three feature cards, and a footer"`
    -   `"dark mode testimonial quote"`
-   `tech_stack` (Literal["react-tailwind", "html-css", "vue", "svelte"]): The desired technology stack. **Currently, only "react-tailwind" is implemented for code generation.**
-   `color_mode` (Literal["light", "dark", "auto"]): The preferred color scheme for the UI.
-   `layout_type` (Literal["component", "full-page"]): Specifies whether to generate a single component or a full page structure.

## Outputs

The agent produces the following outputs, defined in `schema.py` as `AgentOutput`:

-   `frontend_code` (str): The generated frontend code (React + Tailwind CSS). This can be a single component or a more complex string representing an assembled full page.
-   `asset_suggestions` (List[Dict]): A list of suggested asset dictionaries (name, type, URL mock, tags) from mock data.
-   `trend_tags` (List[str]): A list of identified UI/UX trends that influenced the generation.
-   `inspiration_summary` (str): A summary string derived from matched mock inspiration items based on the input prompt.

## How to Run

1.  Ensure you have Python installed.
2.  Navigate to the `frontend-trend-builder` root directory.
3.  The primary way to interact with the agent's logic is by calling the `run_agent` function from `frontend_trend_builder.main`.

### Example Usage (Python Script)

You can create a Python script to run the agent with specific inputs:

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
print(output['frontend_code'][:500] + "...") # Print a snippet
# print(output['frontend_code']) # To print the full code

print("\n--- Suggested Assets ---")
for asset in output['asset_suggestions']:
    print(f"- {asset['name']} (Type: {asset['type']})")

print("\n--- Trend Tags ---")
print(output['trend_tags'])

print("\n--- Inspiration Summary ---")
print(output['inspiration_summary'])

# To run the default example in main.py (which also uses run_agent):
# python frontend_trend_builder/main.py
```

The agent's core logic is in `main.py`, which orchestrates calls to various action modules located in the `actions/` directory. These modules now leverage data from the `data/` directory (mock inspiration, trend dictionary, mock assets) and code templates from `actions/code_templates/`.

## Directory Structure

-   `frontend-trend-builder/`
    -   `actions/`: Contains Python scripts for individual agent capabilities.
        -   `code_templates/`: Contains React+Tailwind CSS component string templates.
    -   `data/`: Contains JSON files for mock inspiration, trend definitions, and mock assets.
    -   `tests/`: Contains unit tests for the agent's components.
    -   `main.py`: The main executable script that orchestrates the agent's workflow and includes example runs.
    -   `schema.py`: Defines the data structures (`AgentInput`, `AgentOutput`) for agent inputs and outputs.
    -   `README.md`: This file.
