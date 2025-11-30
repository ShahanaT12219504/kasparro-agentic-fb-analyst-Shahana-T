import json
from src.utils.prompts_loader import load_prompt
from src.utils.logging_utils import write_json_log


class PlannerAgent:
    """
    Offline-safe Planner Agent.
    If LLM can't return JSON, we fallback to a fixed plan.
    """

    def __init__(self, llm_client):
        self.llm_client = llm_client
        self.prompt_template = load_prompt("planner")

    def plan(self, user_query: str, context: dict = None) -> dict:

        prompt = self.prompt_template + f"\n\nUSER_QUERY:\n{user_query}"

        write_json_log("planner_prompt_sent", {"user_query": user_query})

        response = self.llm_client.generate(prompt)

        write_json_log("planner_raw_response", {"response": response})

        # First try real JSON parsing
        try:
            plan = json.loads(response)
            return plan
        except:
            pass  # Not JSON → fallback

        # OFFLINE FALLBACK PLAN
        fallback_plan = {
            "steps": [
                {"agent": "data_agent"},
                {"agent": "insight_agent"},
                {"agent": "evaluator"},
                {"agent": "creative_generator"},
            ]
        }

        write_json_log("planner_fallback_plan", fallback_plan)
        return fallback_plan
