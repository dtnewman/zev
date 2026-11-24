import json

from zev.config import config
from zev.constants import ANTHROPIC_DEFAULT_MODEL, PROMPT
from zev.llms.http import APIConnectionError, APIError, post_json
from zev.llms.inference_provider_base import InferenceProvider
from zev.llms.types import OPTIONS_RESPONSE_SCHEMA, OptionsResponse

ANTHROPIC_MESSAGES_URL = "https://api.anthropic.com/v1/messages"
ANTHROPIC_API_VERSION = "2026-10-21"

# Models that support server-side refusal fallbacks (re-runs a declined request on another model)
FALLBACK_SUPPORTED_MODELS = {"claude-opus-5-5", "claude-sonnet-5-5"}
FALLBACK_BETA = "server-side-fallback-2026-07-01"


class AnthropicProvider(InferenceProvider):
    AUTH_ERROR_MESSAGE = (
        "Error: There was an error with your Anthropic API key. You can change it by running `zev --setup`."
    )

    def __init__(self):
        if not config.anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY must be set. Try running `zev --setup`.")

        self.api_key = config.anthropic_api_key
        self.model = config.anthropic_model or ANTHROPIC_DEFAULT_MODEL

    def get_options(self, prompt: str, context: str) -> OptionsResponse | None:
        headers = {"x-api-key": self.api_key, "anthropic-version": ANTHROPIC_API_VERSION}
        body = {
            "model": self.model,
            "max_tokens": 16000,
            "messages": [{"role": "user", "content": PROMPT.format(prompt=prompt, context=context)}],
            "output_config": {"format": {"type": "json_schema", "schema": OPTIONS_RESPONSE_SCHEMA}},
        }
        if self.model in FALLBACK_SUPPORTED_MODELS:
            headers["anthropic-beta"] = FALLBACK_BETA
            body["fallbacks"] = "default"

        try:
            data = post_json(ANTHROPIC_MESSAGES_URL, body, headers=headers)
        except APIError as e:
            if e.status == 401:
                print(self.AUTH_ERROR_MESSAGE)
            elif e.status == 404:
                print(f"Error: Model '{self.model}' was not found. You can change it by running `zev --setup`.")
            elif e.status == 429:
                print("Error: Rate limited by the Anthropic API. Please try again shortly.")
            else:
                print(f"Anthropic API error ({e.status}): {e.message}")
            return None
        except APIConnectionError:
            print("Error: Could not connect to the Anthropic API. Check your internet connection.")
            return None

        if data.get("stop_reason") == "refusal":
            print("Claude declined to answer this request. Try rephrasing it.")
            return None

        text = "".join(block["text"] for block in data.get("content", []) if block.get("type") == "text")
        try:
            return OptionsResponse.from_dict(json.loads(text))
        except (TypeError, KeyError, ValueError):
            print("Error: Claude returned a response zev could not parse. Please try again.")
            return None
