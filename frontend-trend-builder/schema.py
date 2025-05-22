from typing import TypedDict, Literal, List, Union

class AgentInput(TypedDict):
    prompt: str
    tech_stack: Literal["react-tailwind", "html-css", "vue", "svelte"]
    color_mode: Literal["light", "dark", "auto"]
    layout_type: Literal["component", "full-page"]

class AgentOutput(TypedDict):
    frontend_code: str
    asset_suggestions: Union[List[str], List[dict]] # Can be a list of strings (URLs) or dicts (e.g. for DALL-E prompts)
    trend_tags: List[str]
    inspiration_summary: str
