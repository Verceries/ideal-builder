import logging
from typing import List, Dict # Added Dict for asset_suggestions typing
from .schema import AgentInput, AgentOutput
from .actions import gather_inspiration, analyze_trends, generate_code, suggest_assets

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_agent(input_data: AgentInput) -> AgentOutput:
    """
    Orchestrates the Frontend Trend Builder agent's workflow with error handling and logging.
    """
    logging.info(f"Agent run started with input: {input_data}")

    inspiration_summary_str: str
    raw_inspiration_output: any # Can be list of dicts or string (error/no match)
    
    # 1. Gather inspiration
    logging.info(f"Calling get_inspiration with prompt: {input_data['prompt']}")
    try:
        raw_inspiration_output = gather_inspiration.get_inspiration(prompt=input_data["prompt"])
        if isinstance(raw_inspiration_output, list) and raw_inspiration_output:
            titles = [item.get('title', 'N/A') for item in raw_inspiration_output]
            inspiration_summary_str = f"Found inspiration from: {'; '.join(titles)}. Based on prompt: {input_data['prompt']}"
            logging.info(f"get_inspiration returned {len(raw_inspiration_output)} items. Summary: {inspiration_summary_str}")
        elif isinstance(raw_inspiration_output, str): # Error or no match message from action
            inspiration_summary_str = raw_inspiration_output
            logging.warning(f"get_inspiration returned a message: {inspiration_summary_str}")
        else: # Should not happen if get_inspiration works as expected (e.g. empty list if no match but no error)
            inspiration_summary_str = "No specific inspiration details were processed or an unexpected data type was received."
            logging.error(f"get_inspiration returned unexpected data type: {type(raw_inspiration_output)}. Output: {raw_inspiration_output}")
    except Exception as e:
        logging.error(f"Exception in get_inspiration: {e}", exc_info=True)
        inspiration_summary_str = "Error fetching inspiration."
        # Ensure raw_inspiration_output is not used later if it caused an exception or is unexpected
        raw_inspiration_output = [] # Default to empty list to prevent downstream issues if it was expected to be iterable

    # 2. Analyze trends
    trend_tags: List[str] = []
    logging.info(f"Calling identify_trends with prompt: '{input_data['prompt']}' and inspiration_summary: '{inspiration_summary_str}'")
    try:
        trend_tags = analyze_trends.identify_trends(
            prompt=input_data["prompt"],
            inspiration_summary=inspiration_summary_str
        )
        logging.info(f"identify_trends returned: {trend_tags}")
    except Exception as e:
        logging.error(f"Exception in identify_trends: {e}", exc_info=True)
        # trend_tags is already defaulted to []

    # 3. Generate code
    frontend_code: str = "Error generating code." # Default error message
    logging.info(f"Calling create_code with inspiration_summary: '{inspiration_summary_str}', trends: {trend_tags}, stack: {input_data['tech_stack']}")
    try:
        frontend_code = generate_code.create_code(
            inspiration_summary=inspiration_summary_str,
            trend_tags=trend_tags,
            tech_stack=input_data["tech_stack"],
            color_mode=input_data["color_mode"],
            layout_type=input_data["layout_type"]
        )
        logging.info(f"create_code returned code snippet (first 100 chars): {frontend_code[:100]}...")
    except Exception as e:
        logging.error(f"Exception in create_code: {e}", exc_info=True)
        # frontend_code is already defaulted

    # 4. Suggest assets
    asset_suggestions: List[Dict] = [] # Ensure it's always a list of dicts
    logging.info(f"Calling get_asset_suggestions with inspiration_summary: '{inspiration_summary_str}' and trends: {trend_tags}")
    try:
        # get_asset_suggestions is expected to return List[Dict]
        raw_asset_output = suggest_assets.get_asset_suggestions(
            inspiration_summary=inspiration_summary_str,
            trend_tags=trend_tags
        )
        if isinstance(raw_asset_output, list):
            # Further check if all items are dicts, or handle mixed types if necessary
            asset_suggestions = [item for item in raw_asset_output if isinstance(item, dict)]
            if len(asset_suggestions) != len(raw_asset_output):
                logging.warning("Some items in asset suggestions were not dictionaries and were filtered out.")
            logging.info(f"get_asset_suggestions returned {len(asset_suggestions)} asset(s).")
        else:
            logging.error(f"get_asset_suggestions returned non-list type: {type(raw_asset_output)}. Defaulting to empty list.")
            # asset_suggestions already defaulted to []
            
    except Exception as e:
        logging.error(f"Exception in get_asset_suggestions: {e}", exc_info=True)
        # asset_suggestions is already defaulted to []

    # 5. Populate and return AgentOutput
    output_data: AgentOutput = {
        "frontend_code": frontend_code,
        "asset_suggestions": asset_suggestions, 
        "trend_tags": trend_tags,
        "inspiration_summary": inspiration_summary_str
    }
    logging.info(f"Agent run completed. Output: {output_data}")
    return output_data

if __name__ == '__main__':
    logging.info("--- Starting Agent Demo ---")

    # Example 1: Successful run (React-Tailwind, dark mode, specific prompt)
    logging.info("\n--- Example 1: React-Tailwind Dark Mode Component ---")
    sample_input_1: AgentInput = {
        "prompt": "A sleek glassmorphic login form for a modern crypto app.",
        "tech_stack": "react-tailwind",
        "color_mode": "dark",
        "layout_type": "component"
    }
    agent_result_1 = run_agent(sample_input_1)
    # print("\n--- Agent Output 1 ---") # Logging inside run_agent now shows this
    # print(f"Inspiration: {agent_result_1['inspiration_summary']}")
    # print(f"Identified Trends: {agent_result_1['trend_tags']}")
    # print(f"Generated Code Snippet (first 200 chars): {agent_result_1['frontend_code'][:200]}...")
    # print(f"Suggested Assets: {agent_result_1['asset_suggestions']}")

    # Example 2: Vue (code gen not implemented) + different prompt
    logging.info("\n--- Example 2: Vue Component (Code Gen Not Implemented) ---")
    sample_input_2: AgentInput = {
        "prompt": "Minimalist portfolio page with pastel color accents.",
        "tech_stack": "vue", # Code generation is not implemented for Vue
        "color_mode": "light",
        "layout_type": "full-page"
    }
    agent_result_2 = run_agent(sample_input_2)
    # print("\n--- Agent Output 2 ---")
    # print(f"Inspiration: {agent_result_2['inspiration_summary']}")
    # print(f"Identified Trends: {agent_result_2['trend_tags']}")
    # print(f"Generated Code Snippet: {agent_result_2['frontend_code']}") # Should indicate not implemented
    # print(f"Suggested Assets: {agent_result_2['asset_suggestions']}")

    # Example 3: Simulating an error in one of the actions (e.g., inspiration data file missing)
    # To truly test this, we'd need to temporarily modify a data file path within an action,
    # or have a specific prompt that causes a predictable issue if an action is not robust.
    # For now, let's use a prompt that results in no matches, which is handled gracefully.
    logging.info("\n--- Example 3: Prompt with No Inspiration Matches ---")
    sample_input_3: AgentInput = {
        "prompt": "asdfghjkl_unlikely_to_match_anything_qwertyuiop",
        "tech_stack": "react-tailwind",
        "color_mode": "light",
        "layout_type": "component"
    }
    agent_result_3 = run_agent(sample_input_3)
    # print("\n--- Agent Output 3 ---")
    # print(f"Inspiration: {agent_result_3['inspiration_summary']}") # Should be "No specific inspiration found..."
    # print(f"Identified Trends: {agent_result_3['trend_tags']}")     # Should be empty
    # print(f"Generated Code Snippet: {agent_result_3['frontend_code']}") # Default button
    # print(f"Suggested Assets: {agent_result_3['asset_suggestions']}") # Should be empty

    logging.info("\n--- Agent Demo Completed ---")
