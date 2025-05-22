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
            inspiration_summary=inspiration_summary_str,
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
            inspiration_summary=inspiration_summary_str,
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
    logger.info("--- Starting Agent Demo from main.py ---") # Changed from logging.info

    logger.info("\n--- Example 1: React-Tailwind Dark Mode Component ---")
    sample_input_1: AgentInput = {
        "prompt": "A sleek glassmorphic login form for a modern crypto app.",
        "tech_stack": "react-tailwind",
        "color_mode": "dark",
        "layout_type": "component"
    }
    agent_result_1 = run_agent(sample_input_1)
    logger.info("\n--- Agent Output 1 (Logged) ---") # Changed from print
    logger.info(f"Inspiration: {agent_result_1['inspiration_summary']}")
    logger.info(f"Identified Trends: {agent_result_1['trend_tags']}")
    logger.info(f"Generated Code Snippet (first 200 chars): {agent_result_1['frontend_code'][:200]}...")
    logger.info(f"Suggested Assets: {agent_result_1['asset_suggestions']}")

    logger.info("\n--- Example 2: Vue Component (Code Gen Not Implemented) ---")
    sample_input_2: AgentInput = {
        "prompt": "Minimalist portfolio page with pastel color accents.",
        "tech_stack": "vue", 
        "color_mode": "light",
        "layout_type": "full-page"
    }
    agent_result_2 = run_agent(sample_input_2)
    logger.info("\n--- Agent Output 2 (Logged) ---") # Changed from print
    logger.info(f"Inspiration: {agent_result_2['inspiration_summary']}")
    logger.info(f"Identified Trends: {agent_result_2['trend_tags']}")
    logger.info(f"Generated Code Snippet: {agent_result_2['frontend_code']}") 
    logger.info(f"Suggested Assets: {agent_result_2['asset_suggestions']}")

    logger.info("\n--- Example 3: Prompt with No Inspiration Matches ---")
    sample_input_3: AgentInput = {
        "prompt": "asdfghjkl_unlikely_to_match_anything_qwertyuiop",
        "tech_stack": "react-tailwind",
        "color_mode": "light",
        "layout_type": "component"
    }
    agent_result_3 = run_agent(sample_input_3)
    logger.info("\n--- Agent Output 3 (Logged) ---") # Changed from print
    logger.info(f"Inspiration: {agent_result_3['inspiration_summary']}") 
    logger.info(f"Identified Trends: {agent_result_3['trend_tags']}")     
    logger.info(f"Generated Code Snippet: {agent_result_3['frontend_code']}") 
    logger.info(f"Suggested Assets: {agent_result_3['asset_suggestions']}") 

    logger.info("\n--- Agent Demo Completed ---")
