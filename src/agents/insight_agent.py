import json
from src.utils.prompts_loader import load_prompt
from src.utils.logging_utils import write_json_log

class InsightAgent:
    def __init__(self, llm_client):
        self.llm_client = llm_client
        self.prompt_template = load_prompt("insight_agent")

    def generate_hypotheses(self, data_summary: dict, user_query: str):
        prompt = (
            self.prompt_template +
            "\n\nDATA SUMMARY:\n" + json.dumps(data_summary, indent=2) +
            "\n\nUSER QUERY:\n" + user_query
        )

        write_json_log("insight_prompt_sent", {"prompt": prompt})
        response = self.llm_client.generate(prompt)
        write_json_log("insight_raw_response", {"response": response})

        # Try to parse JSON first
        try:
            return json.loads(response)
        except:
            # Offline fallback
            return [
                {"issue": "Low CTR", "reason": "Creative fatigue"},
                {"issue": "ROAS Drop", "reason": "Weak targeting"}
            ]
