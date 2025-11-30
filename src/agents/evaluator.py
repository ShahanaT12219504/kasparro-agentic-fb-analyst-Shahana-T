import json
from src.utils.prompts_loader import load_prompt
from src.utils.logging_utils import write_json_log

class EvaluatorAgent:
    def __init__(self, llm_client, config):
        self.llm_client = llm_client
        self.config = config
        self.prompt_template = load_prompt("evaluator")

    def evaluate(self, df, hypotheses):
        # Offline evaluation: just mark everything as "valid"
        result = []

        for hyp in hypotheses:
            result.append({
                "hypothesis": hyp,
                "validity": "valid",
                "confidence": 0.78
            })

        write_json_log("evaluator_output", result)
        return result
