from zev.config import config
from zev.constants import ANTHROPIC_DEFAULT_MODEL, PROMPT
from zev.llms.inference_provider_base import InferenceProvider
from zev.llms.types import OptionsResponse

# Models that support server-side refusal fallbacks (re-runs a declined request on another model)
FALLBACK_SUPPORTED_MODELS = {"claude-opus-5-5", "claude-sonnet-5-5"}


class AnthropicProvider(InferenceProvider):
    AUTH_ERROR_MESSAGE = (
        "Error: There was an error with your Anthropic API key. You can change it by running `zev --setup`."
    )

    def __init__(self):
        try:
            # pylint: disable=import-outside-toplevel
            import anthropic
        except ImportError as e:
            raise ImportError(
                "The Anthropic provider requires the anthropic package. Install it with `pipx install zev[anthropic]`."
            ) from e

        if not config.anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY must be set. Try running `zev --setup`.")

        self.anthropic = anthropic
        self.client = anthropic.Anthropic(api_key=config.anthropic_api_key)
        self.model = config.anthropic_model or ANTHROPIC_DEFAULT_MODEL

    def get_options(self, prompt: str, context: str) -> OptionsResponse | None:
        assembled_prompt = PROMPT.format(prompt=prompt, context=context)
        request = {
            "model": self.model,
            "max_tokens": 16000,
            "messages": [{"role": "user", "content": assembled_prompt}],
            "output_format": OptionsResponse,
        }
        if self.model in FALLBACK_SUPPORTED_MODELS:
            request["betas"] = ["server-side-fallback-2026-07-01"]
            request["fallbacks"] = "default"

        try:
            response = self.client.beta.messages.parse(**request)
        except self.anthropic.AuthenticationError:
            print(self.AUTH_ERROR_MESSAGE)
            return None
        except self.anthropic.NotFoundError:
            print(f"Error: Model '{self.model}' was not found. You can change it by running `zev --setup`.")
            return None
        except self.anthropic.RateLimitError:
            print("Error: Rate limited by the Anthropic API. Please try again shortly.")
            return None
        except self.anthropic.APIStatusError as e:
            print(f"Anthropic API error ({e.status_code}): {e.message}")
            return None
        except self.anthropic.APIConnectionError:
            print("Error: Could not connect to the Anthropic API. Check your internet connection.")
            return None

        if response.stop_reason == "refusal":
            print("Claude declined to answer this request. Try rephrasing it.")
            return None
        return response.parsed_output
