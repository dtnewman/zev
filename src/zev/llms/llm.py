from zev.config import config
from zev.constants import LLMProviders
from zev.llms.azure_openai.provider import AzureOpenAIProvider
from zev.llms.gemini.provider import GeminiProvider
from zev.llms.inference_provider_base import InferenceProvider
from zev.llms.ollama.provider import OllamaProvider
from zev.llms.openai.provider import OpenAIProvider


def get_inference_provider() -> InferenceProvider:
    if config.llm_provider == LLMProviders.OPENAI:
        return OpenAIProvider()
    elif config.llm_provider == LLMProviders.OLLAMA:
        return OllamaProvider()
    elif config.llm_provider == LLMProviders.GEMINI:
        return GeminiProvider()
    elif config.llm_provider == LLMProviders.AZURE_OPENAI:
        return AzureOpenAIProvider()
    else:
        raise ValueError(f"Invalid LLM provider: {config.llm_provider}")
