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
    The Orchestrator coordinates the entire pipeline step-by-step.
    It decides which agent runs when, based on the Planner's plan.
    
    This keeps everything clean, maintainable, and modular.
    """

    def __init__(self, llm_client):
        # Load config once; used across all agents.
        self.config = load_config()
        self.llm_client = llm_client

        # Initialize all agents.
        self.planner = PlannerAgent(llm_client)
        self.data_agent = DataAgent(self.config)
        self.insight_agent = InsightAgent(llm_client)
        self.evaluator = EvaluatorAgent(llm_client, self.config)
        self.creative_gen = CreativeGenerator(llm_client, self.config)

    def run(self, user_query: str):
        """
        Runs the entire agentic pipeline in the correct order.

        Output:
        - data summary
        - hypotheses
        - evaluated insights
        - creative recommendations
        """

        write_json_log("pipeline_started", {"query": user_query})

        # Step 1 — Planner decides execution steps
        plan = self.planner.plan(user_query)

        # Step 2 — Load dataset (filtered to 7 days)
        df = load_dataset(self.config)
        df = filter_last_n_days(df, 7)

        data_summary = None
        insights = None
        evaluated = None
        creatives = None

        # Step 3 — Execute plan step-by-step
        for step in plan["steps"]:
            agent = step["agent"]

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
