from zev.config import config
from zev.constants import LLMProviders
from zev.llms.inference_provider_base import InferenceProvider


def get_inference_provider() -> InferenceProvider:
    if config.llm_provider == LLMProviders.OPENAI:
        # pylint: disable=import-outside-toplevel
        from zev.llms.openai.provider import OpenAIProvider

        return OpenAIProvider()
    elif config.llm_provider == LLMProviders.OLLAMA:
        # pylint: disable=import-outside-toplevel
        from zev.llms.ollama.provider import OllamaProvider

        return OllamaProvider()
    elif config.llm_provider == LLMProviders.GEMINI:
        # pylint: disable=import-outside-toplevel
        from zev.llms.gemini.provider import GeminiProvider

        return GeminiProvider()
    elif config.llm_provider == LLMProviders.AZURE_OPENAI:
        # pylint: disable=import-outside-toplevel
        from zev.llms.azure_openai.provider import AzureOpenAIProvider

        return AzureOpenAIProvider()
    else:
        raise ValueError(f"Invalid LLM provider: {config.llm_provider}")
