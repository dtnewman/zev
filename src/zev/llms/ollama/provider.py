from openai import OpenAI

from zev.config import config
from zev.llms.openai.provider import OpenAIProvider


class OllamaProvider(OpenAIProvider):
    """
    Same as OpenAIProvider, but takes a different base url and model.
    """

    def __init__(self):
        if not config.ollama_base_url:
            raise ValueError("OLLAMA_BASE_URL must be set. Try running `zev --setup`.")
        if not config.ollama_model:
            raise ValueError("OLLAMA_MODEL must be set. Try running `zev --setup`.")
        # api_key is not used, but is still required by the OpenAI client
        # https://github.com/ollama/ollama/blob/5cfc1c39f3d5822b0c0906f863f6df45c141c33b/docs/openai.md?plain=1#L19
        self.client = OpenAI(base_url=config.ollama_base_url, api_key="ollama")
        self.model = config.ollama_model
