import json

from zev.config import config
from zev.constants import OPENAI_BASE_URL, OPENAI_DEFAULT_MODEL, PROMPT
from zev.llms.http import APIConnectionError, APIError, post_json
from zev.llms.inference_provider_base import InferenceProvider
from zev.llms.types import OPTIONS_RESPONSE_SCHEMA, OptionsResponse


class OpenAIProvider(InferenceProvider):
    """Calls the OpenAI Chat Completions API directly. Subclasses override the URL and headers."""

    AUTH_ERROR_MESSAGE = (
        "Error: There was an error with your OpenAI API key. You can change it by running `zev --setup`."
    )

    def __init__(self):
        if not config.openai_api_key:
            raise ValueError("OPENAI_API_KEY must be set. Try running `zev --setup`.")

        self.url = f"{OPENAI_BASE_URL}/chat/completions"
        self.api_key = config.openai_api_key
        self.model = config.openai_model or OPENAI_DEFAULT_MODEL

    def get_headers(self) -> dict:
        return {"Authorization": f"Bearer {self.api_key}"}

    def get_options(self, prompt: str, context: str) -> OptionsResponse | None:
        body = {
            "model": self.model,
            "messages": [{"role": "user", "content": PROMPT.format(prompt=prompt, context=context)}],
            "response_format": {
                "type": "json_schema",
                "json_schema": {"name": "options_response", "strict": True, "schema": OPTIONS_RESPONSE_SCHEMA},
            },
        }
        try:
            data = post_json(self.url, body, headers=self.get_headers())
        except APIError as e:
            if e.status == 401:
                print(self.AUTH_ERROR_MESSAGE)
            else:
                print(f"API error ({e.status}): {e.message}")
            return None
        except APIConnectionError as e:
            print(f"Error: Could not connect to {self.url} ({e}).")
            return None

        message = data["choices"][0]["message"]
        if message.get("refusal"):
            print(f"The model declined to answer: {message['refusal']}")
            return None
        try:
            return OptionsResponse.from_dict(json.loads(message["content"]))
        except (TypeError, KeyError, ValueError):
            print("Error: The model returned a response zev could not parse. Please try again.")
            return None
