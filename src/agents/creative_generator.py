import json
import pandas as pd
from src.utils.data_loader import safe_div
from src.utils.logging_utils import write_json_log
from src.utils.prompts_loader import load_prompt


class CreativeGenerator:
    """
    The Creative Generator Agent is responsible for turning
    underperforming ads into *actionable creative ideas*.

    It does NOT invent numbers.
    It only:
    - identifies low-performing campaigns/adsets
    - looks at what has worked well historically
    - asks the LLM to suggest better creatives in a structured format
    """

    def __init__(self, llm_client, config: dict):
        self.llm_client = llm_client
        self.config = config
        self.prompt_template = load_prompt("creative_generator")

    def generate(self, df: pd.DataFrame, top_n_low_ctr: int = 5) -> list:
        """
        Main entry point for the creative generator.

        Steps:
        1. Compute CTR/ROAS if missing
        2. Select low-performing rows (low CTR, enough impressions)
        3. Select high-performing creatives for inspiration
        4. Build a compact JSON payload
        5. Ask the LLM to return new creative ideas in JSON
        """

        df = df.copy()

        # Ensure CTR/ROAS exist
        if "ctr" not in df.columns:
            df["ctr"] = df.apply(lambda x: safe_div(x["clicks"], x["impressions"]), axis=1)
        if "roas" not in df.columns:
            df["roas"] = df.apply(lambda x: safe_div(x["revenue"], x["spend"]), axis=1)

        min_impr = self.config["data"]["min_impressions"]
        low_ctr_threshold = self.config["thresholds"]["low_ctr"]

        # Filter to meaningful traffic only
        df_filtered = df[df["impressions"] >= min_impr]

        # Low-performing: lowest CTR first
        low_performers = (
            df_filtered.sort_values("ctr", ascending=True)
            .head(top_n_low_ctr)
        )

        # High-performing: best ROAS (to copy good patterns)
        high_performers = (
            df_filtered.sort_values("roas", ascending=False)
            .head(10)
        )

        # Build simplified structures for the LLM
        low_perf_payload = [
            {
                "campaign_name": row.get("campaign_name"),
                "adset_name": row.get("adset_name"),
                "ctr": float(row.get("ctr", 0) or 0),
                "roas": float(row.get("roas", 0) or 0),
                "creative_message": row.get("creative_message"),
                "audience_type": row.get("audience_type"),
                "platform": row.get("platform"),
                "country": row.get("country")
            }
            for _, row in low_performers.iterrows()
            if float(row.get("ctr", 0) or 0) <= low_ctr_threshold
        ]

        high_perf_payload = [
            {
                "campaign_name": row.get("campaign_name"),
                "adset_name": row.get("adset_name"),
                "ctr": float(row.get("ctr", 0) or 0),
                "roas": float(row.get("roas", 0) or 0),
                "creative_message": row.get("creative_message"),
                "audience_type": row.get("audience_type"),
                "platform": row.get("platform"),
                "country": row.get("country")
            }
            for _, row in high_performers.iterrows()
        ]

        payload = {
            "low_performers": low_perf_payload,
            "high_performers": high_perf_payload
        }

        write_json_log("creative_payload_built", {
            "low_count": len(low_perf_payload),
            "high_count": len(high_perf_payload)
        })

        # If nothing is low-performing, we can safely return empty list
        if not low_perf_payload:
            write_json_log("creative_no_low_performers", {})
            return []

        # Build final prompt for LLM
        prompt = (
            self.prompt_template
            + "\n\nDATA_FOR_CREATIVE_IDEAS:\n"
            + json.dumps(payload, indent=2)
        )

        response = self.llm_client.generate(
            prompt=prompt,
            temperature=0.4
        )

        write_json_log("creative_raw_output", {"response": response})

        # Parse JSON safely
        try:
            ideas = json.loads(response)
        except Exception:
            fix_prompt = (
                prompt
                + "\n\nYour previous output was invalid JSON. "
                  "Return ONLY a valid JSON list of creative suggestions."
            )
            response = self.llm_client.generate(prompt=fix_prompt, temperature=0.4)
            ideas = json.loads(response)

        write_json_log("creative_final_output", {"count": len(ideas)})

        return ideas
