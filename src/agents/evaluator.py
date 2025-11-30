import json
import pandas as pd
from src.utils.data_loader import safe_div
from src.utils.logging_utils import write_json_log
from src.utils.prompts_loader import load_prompt


class EvaluatorAgent:
    """
    The Evaluator Agent validates hypotheses using:
    1. Real numeric evidence computed in Python
    2. LLM interpretation to assign confidence + status

    This agent makes your pipeline reliable:
    - No hallucinated insights
    - Every hypothesis must be backed by data
    - Output becomes actionable for marketers
    """

    def __init__(self, llm_client, config: dict):
        self.llm_client = llm_client
        self.config = config
        self.prompt_template = load_prompt("evaluator")

    # ---------------------------------------------------------
    # PUBLIC ENTRY POINT
    # ---------------------------------------------------------
    def evaluate(self, df: pd.DataFrame, hypotheses: list) -> list:
        """
        Validates each hypothesis:
        - Build numeric evidence for it
        - Pass it to LLM for reasoning and scoring
        - Return a structured JSON object

        df: raw filtered dataset (last N days)
        hypotheses: list of hypotheses from InsightAgent
        """

        results = []

        for hyp in hypotheses:
            evidence = self._build_evidence(df, hyp)
            llm_output = self._evaluate_single(hyp, evidence)
            results.append(llm_output)

        write_json_log("evaluation_complete", {"count": len(results)})

        return results

    # ---------------------------------------------------------
    # INTERNAL: NUMERIC CHECKS
    # ---------------------------------------------------------
    def _build_evidence(self, df: pd.DataFrame, hypothesis: dict) -> dict:
        """
        Creates numeric evidence the LLM will use for validation.

        Example:
        - CTR last 7 days vs previous 7 days
        - ROAS changes for a specific campaign or audience
        """

        segments = hypothesis.get("segments", [])
        metric = hypothesis.get("metrics_involved", ["ctr"])[0]

        # Filter based on segments (e.g., audience_type:retargeting)
        filtered_df = df.copy()
        for seg in segments:
            if ":" in seg:
                col, val = seg.split(":")
                filtered_df = filtered_df[filtered_df[col] == val]

        # Build time windows
        last_7 = filtered_df
        # For simplicity we compare last 7 days vs entire dataset (sample limitation)
        prev = df[df["date"] < last_7["date"].min()] if len(df) > 0 else df

        evidence = {}

        # CTR checks
        if metric == "ctr":
            ctr_last = safe_div(last_7["clicks"].sum(), last_7["impressions"].sum())
            ctr_prev = safe_div(prev["clicks"].sum(), prev["impressions"].sum())

            evidence = {
                "ctr_last_7_days": round(ctr_last, 5),
                "ctr_prev_7_days": round(ctr_prev, 5),
                "delta_ctr_pct": round(((ctr_last - ctr_prev) / ctr_prev * 100), 2) if ctr_prev > 0 else 0,
                "significant_drop": ctr_last < ctr_prev
            }

        # ROAS checks
        if metric == "roas":
            roas_last = safe_div(last_7["revenue"].sum(), last_7["spend"].sum())
            roas_prev = safe_div(prev["revenue"].sum(), prev["spend"].sum())

            evidence = {
                "roas_last_7_days": round(roas_last, 5),
                "roas_prev_7_days": round(roas_prev, 5),
                "delta_roas_pct": round(((roas_last - roas_prev) / roas_prev * 100), 2) if roas_prev > 0 else 0,
                "significant_drop": roas_last < roas_prev
            }

        write_json_log("evidence_built", {
            "hypothesis_id": hypothesis["id"],
            "evidence": evidence
        })

        return evidence

    # ---------------------------------------------------------
    # INTERNAL: LLM SCORING
    # ---------------------------------------------------------
    def _evaluate_single(self, hypothesis: dict, evidence: dict) -> dict:
        """
        Sends the hypothesis + numeric evidence to the LLM
        so it can return:
        - status (validated / partially_validated / rejected)
        - confidence score
        - explanation
        - recommended next steps
        """

        payload = {
            "hypothesis": hypothesis,
            "evidence": evidence
        }

        filled_prompt = (
            self.prompt_template
            + "\n\nEVIDENCE:\n"
            + json.dumps(payload, indent=2)
        )

        # Send prompt to LLM
        response = self.llm_client.generate(
            prompt=filled_prompt,
            temperature=0.1
        )

        write_json_log("evaluator_raw_output", {"response": response})

        # Validate JSON
        try:
            result = json.loads(response)
        except Exception:
            fix_prompt = (
                filled_prompt
                + "\n\nYour previous output was invalid JSON. Return ONLY valid JSON."
            )
            response = self.llm_client.generate(prompt=fix_prompt, temperature=0.1)
            result = json.loads(response)

        write_json_log("evaluator_final_output", result)

        return result
