import json
from src.utils.prompts_loader import load_prompt
from src.utils.logging_utils import write_json_log

class CreativeGenerator:
    def __init__(self, llm_client, config):
        self.llm_client = llm_client
        self.config = config
        self.prompt_template = load_prompt("creative_generator")

    def generate(self, df=None):
        # Simple static creatives
        creatives = [
            {"idea": "Use a bold headline highlighting discount"},
            {"idea": "Try bright background colors"},
            {"idea": "Add social proof testimonials"},
        ]

        write_json_log("creative_output", creatives)
        return creatives
