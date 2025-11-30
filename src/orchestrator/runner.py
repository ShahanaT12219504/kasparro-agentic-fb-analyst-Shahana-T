import pandas as pd
from src.agents.planner import PlannerAgent
from src.agents.data_agent import DataAgent
from src.agents.insight_agent import InsightAgent
from src.agents.evaluator import EvaluatorAgent
from src.agents.creative_generator import CreativeGenerator
from src.utils.data_loader import load_config, load_dataset, filter_last_n_days
from src.utils.logging_utils import write_json_log


class Orchestrator:
    """
    Offline-safe Orchestrator.
    Supports two types of planner outputs:
    1. dict steps → {"agent": "...", "action": "..."}   (real LLM mode)
    2. string steps → "load_data", "generate_insights"  (offline dummy LLM mode)
    """

    def __init__(self, llm_client):
        self.config = load_config()
        self.llm_client = llm_client

        self.planner = PlannerAgent(llm_client)
        self.data_agent = DataAgent(self.config)
        self.insight_agent = InsightAgent(llm_client)
        self.evaluator = EvaluatorAgent(llm_client, self.config)
        self.creative_gen = CreativeGenerator(llm_client, self.config)

    def run(self, user_query: str):

        write_json_log("pipeline_started", {"query": user_query})

        # Step 1: Planner output
        plan = self.planner.plan(user_query)

        # Step 2: Load dataset
        df = load_dataset(self.config)
        df = filter_last_n_days(df, 7)

        data_summary = None
        insights = None
        evaluated = None
        creatives = None

        # Step 3: Execute steps
        for step in plan["steps"]:

            # ==========================
            # OFFLINE MODE (string steps)
            # ==========================
            if isinstance(step, str):

                if step == "load_data":
                    data_summary = self.data_agent.load_and_prepare()

                elif step == "analyze_metrics":
                    # Some pipelines merge analysis into load; safe fallback
                    if data_summary is not None:
                        data_summary = data_summary
                    else:
                        data_summary = self.data_agent.load_and_prepare()

                elif step == "generate_insights":
                    insights = self.insight_agent.generate_hypotheses(
                        data_summary.get("summary", {}),
                        user_query
                    )

                elif step == "evaluate_insights":
                    evaluated = self.evaluator.evaluate(df, insights)

                elif step == "produce_creatives":
                    creatives = self.creative_gen.generate(df)

                # Continue to next step
                continue

            # ==========================
            # NORMAL MODE (dict steps)
            # ==========================
            agent = step.get("agent", "")
            action = step.get("action", "")

            if agent == "data_agent":
                data_summary = self.data_agent.load_and_prepare()

            elif agent == "insight_agent":
                insights = self.insight_agent.generate_hypotheses(
                    data_summary["summary"], user_query
                )

            elif agent == "evaluator":
                evaluated = self.evaluator.evaluate(df, insights)

            elif agent == "creative_generator":
                creatives = self.creative_gen.generate(df)

        return {
            "summary": data_summary,
            "hypotheses": insights,
            "evaluated": evaluated,
            "creatives": creatives
        }
