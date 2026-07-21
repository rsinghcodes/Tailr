import os
from typing import Optional


class PromptRegistry:
    """Registry to load, cache, and manage file-based prompt templates from the filesystem."""

    def __init__(self, prompts_dir: Optional[str] = None):
        """Initializes the prompt registry.

        Args:
            prompts_dir: Optional custom path to the prompts directory. If not specified,
                defaults to the directory containing this file.
        """
        if prompts_dir:
            self.prompts_dir = prompts_dir
        else:
            self.prompts_dir = os.path.dirname(os.path.abspath(__file__))

    def get_prompt(self, category: str, name: str, version: str = "v1") -> str:
        """Loads a prompt template from the filesystem.

        Args:
            category: The directory name of the prompt category (e.g. 'jd_analyzer').
            name: The base name of the role/prompt (e.g. 'system' or 'user').
            version: The version identifier string (default: 'v1').

        Returns:
            The raw text content of the prompt template.

        Raises:
            FileNotFoundError: If no matching file can be found in the template directory.
        """
        file_name = f"{name}_{version}.txt"
        file_path = os.path.join(self.prompts_dir, category, file_name)

        if not os.path.exists(file_path):
            # Fall back to markdown extension if txt is missing
            file_name = f"{name}_{version}.md"
            file_path = os.path.join(self.prompts_dir, category, file_name)

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Prompt template file not found at: {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            return f.read().strip()
