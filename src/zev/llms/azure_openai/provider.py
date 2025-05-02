from azure.identity import DefaultAzureCredential
from zev.config import config
from zev.constants import PROMPT
from zev.llms.inference_provider_base import InferenceProvider
from zev.llms.types import OptionsResponse

from openai import AuthenticationError, AzureOpenAI


class AzureOpenAIProvider(InferenceProvider):
    def __init__(self):
        required_vars = {
            "AZURE_OPENAI_ACCOUNT_NAME": config.azure_openai_account_name,
            "AZURE_OPENAI_DEPLOYMENT": config.azure_openai_deployment,
            "AZURE_OPENAI_API_VERSION": config.azure_openai_api_version,
        }

        for var, value in required_vars.items():
            if not value:
                raise ValueError(f"{var} must be set. Run `zev --setup`.")

        azure_openai_endpoint = (
            f"https://{config.azure_openai_account_name}.openai.azure.com/"
        )

        if config.azure_openai_api_key:
            self.client = AzureOpenAI(
                api_key=config.azure_openai_api_key,
                azure_endpoint=azure_openai_endpoint,
                api_version=config.azure_openai_api_version,
            )
        else:
            token = DefaultAzureCredential().get_token(
                "https://cognitiveservices.azure.com/.default"
            )
            self.client = AzureOpenAI(
                azure_endpoint=azure_openai_endpoint,
                api_version=config.azure_openai_api_version,
                azure_ad_token=token.token,
            )

        self.model = config.azure_openai_deployment

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
            print(
                "Authentication error. Check Azure credentials or run `zev --setup` again."
            )
            return None
