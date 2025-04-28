from google import genai
import json

from zev.config import config
from zev.constants import PROMPT, GEMINI_DEFAULT_MODEL
from zev.llms.inference_provider_base import InferenceProvider
from zev.llms.openai.provider import OpenAIProvider
from zev.llms.types import OptionsResponse


class GeminiProvider(InferenceProvider):
    def __init__(self):
        if not config.gemini_api_key:
            raise ValueError("GEMINI_API_KEY must be set. Try running `zev --setup`.")

        self.client = genai.Client(api_key=config.gemini_api_key)
        self.model = config.gemini_model or GEMINI_DEFAULT_MODEL

    def get_options(self, prompt: str, context: str) -> OptionsResponse | None:
        try:
            assembled_prompt = PROMPT.format(prompt=prompt, context=context)
            response = self.client.models.generate_content(
                model=self.model,
                contents=assembled_prompt,
                config={
                    "response_mime_type": "application/json",
                    "response_schema": OptionsResponse,
                },
            )
            return response.parsed
        except genai.errors.ClientError as e:
            print("Error:", e.details["error"]["message"])
            print("Note that to update settings, you can run `zev --setup`.")
            return
