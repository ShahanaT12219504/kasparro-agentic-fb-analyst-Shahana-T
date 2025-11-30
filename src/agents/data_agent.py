import pandas as pd
from src.utils.data_loader import (
    load_dataset,
    filter_last_n_days,
    safe_div
)
from src.utils.logging_utils import write_json_log


class DataAgent:
    """
    The Data Agent handles all heavy lifting around the dataset:
    - loading the CSV
    - filtering date ranges
    - computing CTR, ROAS, spend summaries
    - preparing clean numeric structures for downstream agents

    This agent NEVER generates insights. It only produces clean numbers.
    """

    def __init__(self, config: dict):
        self.config = config

    def load_and_prepare(self, days: int = 7) -> dict:
        """
        Main entry point for the Data Agent.

        Steps:
        1. Load dataset (sample or full)
        2. Filter last N days
        3. Compute summary metrics
        """

        df = load_dataset(self.config)
        df = filter_last_n_days(df, days)
        df = df.copy()

        # Basic cleaning
        df["ctr"] = df.apply(lambda x: safe_div(x["clicks"], x["impressions"]), axis=1)
        df["roas"] = df.apply(lambda x: safe_div(x["revenue"], x["spend"]), axis=1)

        # Log dataset shape
        write_json_log("data_loaded", {"rows": len(df)})

        summary = {
            "roas_trend": self._compute_roas_trend(df),
            "campaign_performance": self._campaign_performance(df),
            "top_campaigns": self._top_campaigns(df),
            "bottom_campaigns": self._bottom_campaigns(df),
            "spend_distribution": self._spend_distribution(df)
        }

        # Log summary
        write_json_log("data_summary_ready", {"summary_keys": list(summary.keys())})

        return {"summary": summary}

    # --------------------------------------------------------
    # INTERNAL HELPERS
    # --------------------------------------------------------

    def _compute_roas_trend(self, df: pd.DataFrame):
        """
        ROAS over time (daily).
        Helps detect whether the system is improving or declining.
        """

        trend = (
            df.groupby("date")
              .agg({
                  "spend": "sum",
                  "revenue": "sum"
              })
              .reset_index()
        )
        trend["roas"] = trend.apply(lambda x: safe_div(x["revenue"], x["spend"]), axis=1)
        return trend.to_dict(orient="records")

    def _campaign_performance(self, df: pd.DataFrame):
        """
        Computes CTR, ROAS, and spend for each campaign.
        """

        grouped = (
            df.groupby("campaign_name")
            .agg({
                "impressions": "sum",
                "clicks": "sum",
                "spend": "sum",
                "revenue": "sum"
            })
            .reset_index()
        )

        grouped["ctr"] = grouped.apply(lambda x: safe_div(x["clicks"], x["impressions"]), axis=1)
        grouped["roas"] = grouped.apply(lambda x: safe_div(x["revenue"], x["spend"]), axis=1)

        # Filter out tiny campaigns
        grouped = grouped[grouped["impressions"] >= self.config["data"]["min_impressions"]]

        return grouped.to_dict(orient="records")

    def _top_campaigns(self, df: pd.DataFrame):
        """
        Top 5 campaigns by ROAS. Helps identify what's working.
        """

        perf = self._campaign_performance(df)
        perf_sorted = sorted(perf, key=lambda x: x["roas"], reverse=True)
        return perf_sorted[:5]

    def _bottom_campaigns(self, df: pd.DataFrame):
        """
        Bottom 5 campaigns by ROAS. Helps spot problem areas.
        """

        perf = self._campaign_performance(df)
        perf_sorted = sorted(perf, key=lambda x: x["roas"])
        return perf_sorted[:5]

    def _spend_distribution(self, df: pd.DataFrame):
        """
        Shows how budget is distributed across campaigns.
        Good for seeing if you're overspending on underperformers.
        """

        spend = (
            df.groupby("campaign_name")["spend"].sum()
        )
        total = spend.sum()

        distribution = [
            {
                "campaign_name": name,
                "spend": float(val),
                "share_pct": float((val / total) * 100) if total > 0 else 0
            }
            for name, val in spend.items()
        ]

        return distribution
