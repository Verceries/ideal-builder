import logging
from typing import List, Dict 
from .schema import AgentInput, AgentOutput
from .actions import gather_inspiration, analyze_trends, generate_code, suggest_assets
from .config import LOG_LEVEL 

# Configure the root logger
# This is done once here and will be used by all modules.
logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# Get a logger instance for this module (main.py)
logger = logging.getLogger(__name__)


def run_agent(input_data: AgentInput) -> AgentOutput:
    """
    Orchestrates the Frontend Trend Builder agent's workflow with error handling and logging.
    """
    logger.info(f"Agent run started with input: {input_data}") 

    inspiration_summary_str: str
    raw_inspiration_output: any 
    
    logger.info(f"Calling get_inspiration with prompt: {input_data['prompt']}")
    try:
        raw_inspiration_output = gather_inspiration.get_inspiration(prompt=input_data["prompt"])
        if isinstance(raw_inspiration_output, list) and raw_inspiration_output:
            titles = [item.get('title', 'N/A') for item in raw_inspiration_output]
            inspiration_summary_str = f"Found inspiration from: {'; '.join(titles)}. Based on prompt: {input_data['prompt']}"
            logger.info(f"get_inspiration returned {len(raw_inspiration_output)} items. Summary (first 100 chars): {inspiration_summary_str[:100]}...")
        elif isinstance(raw_inspiration_output, str): 
            inspiration_summary_str = raw_inspiration_output
            logger.warning(f"get_inspiration returned a message: {inspiration_summary_str}")
        else: 
            inspiration_summary_str = "No specific inspiration details were processed or an unexpected data type was received."
            logger.error(f"get_inspiration returned unexpected data type: {type(raw_inspiration_output)}. Output: {raw_inspiration_output}")
    except Exception as e:
        logger.exception(f"Exception in get_inspiration") # Use .exception for stack trace
        inspiration_summary_str = "Error fetching inspiration."
        raw_inspiration_output = [] 

    trend_tags: List[str] = []
    logger.info(f"Calling identify_trends with prompt: '{input_data['prompt']}' and inspiration_summary (first 100 chars): '{inspiration_summary_str[:100]}...'")
    try:
        trend_tags = analyze_trends.identify_trends(
            prompt=input_data["prompt"],
            inspiration_summary=inspiration_summary_str
        )
        logger.info(f"identify_trends returned: {trend_tags}")
    except Exception as e:
        logger.exception(f"Exception in identify_trends")
        
    frontend_code: str = "Error generating code." 
    logger.info(f"Calling create_code with inspiration_summary (first 100 chars): '{inspiration_summary_str[:100]}...', trends: {trend_tags}, stack: {input_data['tech_stack']}")
    try:
        frontend_code = generate_code.create_code(
            inspiration_summary=inspiration_summary_str, # Pass inspiration_summary (which is the prompt for full page)
            trend_tags=trend_tags,
            tech_stack=input_data["tech_stack"],
            color_mode=input_data["color_mode"],
            layout_type=input_data["layout_type"]
        )
        logger.info(f"create_code returned code snippet (first 100 chars): {frontend_code[:100]}...")
    except Exception as e:
        logger.exception(f"Exception in create_code")
        
    asset_suggestions: List[Dict] = [] 
    logger.info(f"Calling get_asset_suggestions with inspiration_summary (first 100 chars): '{inspiration_summary_str[:100]}...' and trends: {trend_tags}")
    try:
        raw_asset_output = suggest_assets.get_asset_suggestions(
            inspiration_summary=inspiration_summary_str, # Pass inspiration_summary (prompt for asset context)
            trend_tags=trend_tags
        )
        if isinstance(raw_asset_output, list):
            asset_suggestions = [item for item in raw_asset_output if isinstance(item, dict)]
            if len(asset_suggestions) != len(raw_asset_output):
                logger.warning("Some items in asset suggestions were not dictionaries and were filtered out.")
            logger.info(f"get_asset_suggestions returned {len(asset_suggestions)} asset(s).")
        else:
            logger.error(f"get_asset_suggestions returned non-list type: {type(raw_asset_output)}. Defaulting to empty list.")
            
    except Exception as e:
        logger.exception(f"Exception in get_asset_suggestions")
        
    output_data: AgentOutput = {
        "frontend_code": frontend_code,
        "asset_suggestions": asset_suggestions, 
        "trend_tags": trend_tags,
        "inspiration_summary": inspiration_summary_str
    }
    logger.info(f"Agent run completed. Final output data (summary): Inspiration: '{output_data['inspiration_summary'][:100]}...', Trends: {output_data['trend_tags']}, Assets: {len(output_data['asset_suggestions'])}, Code Snippet: '{output_data['frontend_code'][:100]}...'")
    return output_data

if __name__ == '__main__':
    # Default example prompt
    example_input = AgentInput(
        prompt="Create a sleek, modern login page for a new SaaS product. Use dark mode and glassmorphism.",
        tech_stack="react-tailwind",
        color_mode="dark",
        layout_type="component" # Or "full-page" for a broader example
    )
    
    logger.info(f"--- Running Default Example from main.py ---")
    logger.info(f"Input: {example_input}")
    
    result = run_agent(example_input)
    
    print("\n--- Agent Output (Default Example) ---")
    print(f"Identified Trends: {result['trend_tags']}")
    print(f"Inspiration Summary: {result['inspiration_summary']}")
    print("\nSuggested Assets:")
    if result['asset_suggestions']:
        for asset in result['asset_suggestions']:
            print(f"- Name: {asset.get('name', 'N/A')}, Type: {asset.get('type', 'N/A')}, Source: {asset.get('source', 'N/A')}")
    else:
        print("No assets suggested.")
    print("\nGenerated Frontend Code (React + Tailwind CSS - Snippet):")
    print(result['frontend_code'][:1000] + "..." if len(result['frontend_code']) > 1000 else result['frontend_code'])
    logger.info(f"--- Default Example Run Completed ---")
