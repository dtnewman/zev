from zev.config import config
from zev.llms.openai.provider import OpenAIProvider
from zev.llms.ollama.provider import OllamaProvider
from zev.llms.inference_provider_base import InferenceProvider


def get_inference_provider() -> InferenceProvider:
    if config.llm_provider == "openai":
        return OpenAIProvider()
    elif config.llm_provider == "ollama":
        return OllamaProvider()
    else:
        raise ValueError(f"Invalid LLM provider: {config.llm_provider}")
