from pathlib import Path
from dotenv import dotenv_values


class Config:
    def __init__(self):
        self.config_path = Path.home() / ".zevrc"
        self.vals = dotenv_values(self.config_path)

    @property
    def llm_provider(self):
        return self.vals.get("LLM_PROVIDER")

    # OpenAI
    @property
    def openai_api_key(self):
        return self.vals.get("OPENAI_API_KEY")

    @property
    def openai_model(self):
        return self.vals.get("OPENAI_MODEL")

    # Ollama
    @property
    def ollama_base_url(self):
        return self.vals.get("OLLAMA_BASE_URL")

    @property
    def ollama_model(self):
        return self.vals.get("OLLAMA_MODEL")


config = Config()
