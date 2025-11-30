
import openai

class LLMClient:
    """
    Tiny wrapper around OpenAI so the rest of the code stays clean.
    If you ever switch to Anthropic or Gemini, only this file changes.
    """

    def __init__(self, model="gpt-4.1"):
        self.model = model

    def generate(self, prompt: str, temperature: float = 0.2):
        """
        Sends a prompt to the OpenAI Chat Completion API and returns text output.
        """

        completion = openai.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature
        )

        return completion.choices[0].message["content"]
