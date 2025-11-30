import os

def load_prompt(prompt_name: str) -> str:
    """
    Loads a prompt file from the /prompts directory.

    Why this exists:
    - Keeps your code clean (no long prompts inside Python files)
    - Allows easy editing of prompts without touching code
    - Ensures all agents use consistent prompt text
    """

    base_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "prompts")
    file_path = os.path.join(base_dir, f"{prompt_name}.md")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Prompt file not found: {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()
