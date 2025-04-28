from zev.config import config
from zev.llms.openai.provider import OpenAIProvider
from zev.llms.ollama.provider import OllamaProvider
from zev.llms.gemini.provider import GeminiProvider
from zev.llms.inference_provider_base import InferenceProvider
from constants import LLMProviders

def get_inference_provider() -> InferenceProvider:
    if config.llm_provider == LLMProviders.OPENAI:
        return OpenAIProvider()
    elif config.llm_provider == LLMProviders.OLLAMA:
        return OllamaProvider()
    elif config.llm_provider == LLMProviders.GEMINI:
        return GeminiProvider()
    else:
        raise ValueError(f"Invalid LLM provider: {config.llm_provider}")
