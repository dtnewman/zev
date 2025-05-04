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

    # Gemini
    @property
    def gemini_model(self):
        return self.vals.get("GEMINI_MODEL")

    @property
    def gemini_api_key(self):
        return self.vals.get("GEMINI_API_KEY")

    # Azure OpenAI
    @property
    def azure_openai_account_name(self):
        return self.vals.get("AZURE_OPENAI_ACCOUNT_NAME")

    @property
    def azure_openai_api_key(self):
        return self.vals.get("AZURE_OPENAI_API_KEY")

    @property
    def azure_openai_deployment(self):
        return self.vals.get("AZURE_OPENAI_DEPLOYMENT")

    @property
    def azure_openai_api_version(self):
        return self.vals.get("AZURE_OPENAI_API_VERSION")


config = Config()
