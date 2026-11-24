from zev.config import config
from zev.llms.openai.provider import OpenAIProvider


class OllamaProvider(OpenAIProvider):
    """
    Same as OpenAIProvider, but uses Ollama's OpenAI-compatible endpoint, which needs no API key.
    """

    def __init__(self):
        if not config.ollama_base_url:
            raise ValueError("OLLAMA_BASE_URL must be set. Try running `zev --setup`.")
        if not config.ollama_model:
            raise ValueError("OLLAMA_MODEL must be set. Try running `zev --setup`.")
        self.url = f"{config.ollama_base_url.rstrip('/')}/chat/completions"
        self.model = config.ollama_model

    def get_headers(self) -> dict:
        return {}
