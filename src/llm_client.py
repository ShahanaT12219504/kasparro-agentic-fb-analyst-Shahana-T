class LLMClient:
    """
    Dummy LLM client used for offline mode.
    This version does NOT call any API (OpenAI, Gemini, etc.).
    
    It simply returns realistic placeholder responses so the rest of the
    agent pipeline works smoothly without internet or payment.
    """

    def __init__(self, model="offline-dummy"):
        self.model = model

    def generate(self, prompt: str, temperature: float = 0.2):
        """
        Returns a mock response for any given prompt.
        This keeps the architecture intact without requiring an actual API key.
        """

        # You can customize this if you want more variety
        mock_responses = [
            "Based on the data, performance dropped mainly due to low CTR and weak audience targeting.",
            "Insight: Certain creatives underperformed due to ad fatigue and poor click-through engagement.",
            "Recommendation: Refresh visuals and test new audience segments to improve performance.",
            "The ads performed well overall but showed inconsistencies across device types."
        ]

        # Pick one response (simple deterministic selection)
        index = abs(hash(prompt)) % len(mock_responses)
        return mock_responses[index]
