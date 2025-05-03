from openai import AuthenticationError, OpenAI

from zev.config import config
from zev.constants import OPENAI_BASE_URL, OPENAI_DEFAULT_MODEL, PROMPT
from zev.llms.inference_provider_base import InferenceProvider
from zev.llms.types import OptionsResponse


class OpenAIProvider(InferenceProvider):
    AUTH_ERROR_MESSAGE = (
        "Error: There was an error with your OpenAI API key. You can change it by running `zev --setup`."
    )

    def __init__(self):
        if not config.openai_api_key:
            raise ValueError("OPENAI_API_KEY must be set. Try running `zev --setup`.")

        self.client = OpenAI(base_url=OPENAI_BASE_URL, api_key=config.openai_api_key)
        self.model = config.openai_model or OPENAI_DEFAULT_MODEL

    def get_options(self, prompt: str, context: str) -> OptionsResponse | None:
        try:
            assembled_prompt = PROMPT.format(prompt=prompt, context=context)
            response = self.client.beta.chat.completions.parse(
                model=self.model,
                messages=[{"role": "user", "content": assembled_prompt}],
                response_format=OptionsResponse,
            )
            return response.choices[0].message.parsed
        except AuthenticationError:
            print(self.AUTH_ERROR_MESSAGE)
            return None
