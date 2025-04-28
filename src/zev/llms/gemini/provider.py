from openai import OpenAI

from zev.llms.inference_provider_base import InferenceProvider
from zev.llms.openai.provider import OpenAIProvider
from zev.config import config
from google import genai
from zev.llms.types import OptionsResponse
from zev.constants import PROMPT
import json


class GeminiProvider(InferenceProvider):
    def __init__(self):
        if not config.gemini_model:
            raise ValueError("GEMINI_MODEL must be set. Try running `zev --setup`.")

        self.client = genai.Client(api_key=config.gemini_api_key)
        self.model = config.gemini_model

    def get_options(self, prompt: str, context: str) -> OptionsResponse | None:
        try:
            assembled_prompt = PROMPT.format(prompt=prompt, context=context)
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config={
                    'response_mime_type': 'application/json',
                    'response_schema': OptionsResponse,
                },
            )
            try:
                response_json = json.loads(response.text)
                return OptionsResponse.parse_obj(response_json)

            except json.JSONDecodeError as json_err:
                print(f"Error: Failed to parse JSON response from Gemini API: {json_err}")
                print(f"Raw response: {response.text[:100]}...") 
                return None

        except Exception as e:
            print(f"Error: There was an error with your Gemini API key. You can change it by running `zev --setup`.") 
            return
