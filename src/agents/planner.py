import json
from src.utils.prompts_loader import load_prompt
from src.utils.logging_utils import write_json_log

class PlannerAgent:
    """
    The Planner Agent converts a user query into a step-by-step plan.
    It reads the planner prompt, fills in the user query, and expects
    a structured JSON plan as output.

    Why this exists:
    - Lets the system adjust dynamically depending on the user's question
    - Keeps your pipeline modular and flexible
    """

    def __init__(self, llm_client):
        self.llm_client = llm_client
        self.prompt_template = load_prompt("planner")

    def plan(self, user_query: str, context: dict = None) -> dict:
        """
        Produces a JSON execution plan.

        Steps:
        1. Build prompt by inserting user query
        2. Ask LLM to return a strict JSON plan
        3. Validate output
        """

        filled_prompt = self.prompt_template + f"\n\nUSER_QUERY:\n{user_query}"

        # Log this event
        write_json_log("planner_prompt_sent", {"user_query": user_query})

        # Call LLM
        response = self.llm_client.generate(
            prompt=filled_prompt,
            temperature=0.2
        )

        # Log raw response
        write_json_log("planner_raw_response", {"response": response})

        # Try parsing JSON
        try:
            plan = json.loads(response)
        except Exception:
            # If LLM returns invalid JSON, try to fix by asking again
            fix_prompt = (
                filled_prompt
                + "\n\nYour previous output was invalid JSON. Return ONLY a valid JSON plan."
            )
            response = self.llm_client.generate(prompt=fix_prompt, temperature=0.2)
            plan = json.loads(response)

        # Final log
        write_json_log("planner_final_plan", plan)

        return plan
