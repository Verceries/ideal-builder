from .schema import AgentInput, AgentOutput
from .actions import gather_inspiration, analyze_trends, generate_code, suggest_assets

def run_agent(input_data: AgentInput) -> AgentOutput:
    """
    Orchestrates the Frontend Trend Builder agent's workflow.
    """
    print(f"Starting agent run with input: {input_data['prompt']}")

    # 1. Gather inspiration
    inspiration_summary = gather_inspiration.get_inspiration(prompt=input_data["prompt"])
    print(f"Inspiration gathered: {inspiration_summary}")

    # 2. Analyze trends
    trend_tags = analyze_trends.identify_trends(
        prompt=input_data["prompt"],
        inspiration_summary=inspiration_summary
    )
    print(f"Trends identified: {trend_tags}")

    # 3. Generate code
    frontend_code = generate_code.create_code(
        inspiration_summary=inspiration_summary,
        trend_tags=trend_tags,
        tech_stack=input_data["tech_stack"],
        color_mode=input_data["color_mode"],
        layout_type=input_data["layout_type"]
    )
    print(f"Code generated: {frontend_code}")

    # 4. Suggest assets
    asset_suggestions = suggest_assets.get_asset_suggestions(
        inspiration_summary=inspiration_summary,
        trend_tags=trend_tags
    )
    print(f"Assets suggested: {asset_suggestions}")

    # 5. Populate and return AgentOutput
    output_data: AgentOutput = {
        "frontend_code": frontend_code,
        "asset_suggestions": asset_suggestions,
        "trend_tags": trend_tags,
        "inspiration_summary": inspiration_summary
    }
    print(f"Agent run completed. Output: {output_data}")
    return output_data

if __name__ == '__main__':
    # Example usage of the agent
    sample_input: AgentInput = {
        "prompt": "Create a landing page for a new AI-powered productivity app.",
        "tech_stack": "react-tailwind",
        "color_mode": "dark",
        "layout_type": "full-page"
    }
    
    print("--- Running Frontend Trend Builder Agent ---")
    agent_result = run_agent(sample_input)
    print("\n--- Agent Output ---")
    print(f"Inspiration: {agent_result['inspiration_summary']}")
    print(f"Identified Trends: {agent_result['trend_tags']}")
    print(f"Generated Code Snippet: {agent_result['frontend_code']}")
    print(f"Suggested Assets: {agent_result['asset_suggestions']}")

    print("\n--- Another Example: Vue Component ---")
    sample_input_vue: AgentInput = {
        "prompt": "Design a modern login form component.",
        "tech_stack": "vue",
        "color_mode": "light",
        "layout_type": "component"
    }
    agent_result_vue = run_agent(sample_input_vue)
    print("\n--- Agent Output (Vue Component) ---")
    print(f"Inspiration: {agent_result_vue['inspiration_summary']}")
    print(f"Identified Trends: {agent_result_vue['trend_tags']}")
    print(f"Generated Code Snippet: {agent_result_vue['frontend_code']}")
    print(f"Suggested Assets: {agent_result_vue['asset_suggestions']}")
