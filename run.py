import json
from src.llm_client import LLMClient
from src.orchestrator.runner import Orchestrator


def save_output(output):
    """
    Saves the pipeline results into the reports/ directory.
    This includes:
    - insights.json (validated hypotheses)
    - creatives.json (creative recommendations)
    - report.md (simple markdown report)
    """

    # Save insights
    if output.get("evaluated") is not None:
        with open("reports/insights.json", "w", encoding="utf-8") as f:
            json.dump(output["evaluated"], f, indent=2)

    # Save creative ideas
    if output.get("creatives") is not None:
        with open("reports/creatives.json", "w", encoding="utf-8") as f:
            json.dump(output["creatives"], f, indent=2)

    # Save markdown report
    with open("reports/report.md", "w", encoding="utf-8") as f:
        f.write("# Facebook Ads Performance Report\n\n")

        f.write("## ✓ Validated Insights\n")
        f.write("```\n")
        f.write(json.dumps(output.get("evaluated", []), indent=2))
        f.write("\n```\n\n")

        f.write("## ✓ Creative Recommendations\n")
        f.write("```\n")
        f.write(json.dumps(output.get("creatives", []), indent=2))
        f.write("\n```\n")

    print("\n✔ All outputs saved in /reports folder.\n")


if __name__ == "__main__":
    # Default query (you can modify this)
    user_query = "Analyze ad performance and generate insights."

    print("Running pipeline...\n")

    # Initialize LLM + Orchestrator
    client = LLMClient()
    orchestrator = Orchestrator(client)

    # Run full pipeline
    output = orchestrator.run(user_query)

    # Save final outputs
    save_output(output)

    print("✔ Pipeline complete.")
