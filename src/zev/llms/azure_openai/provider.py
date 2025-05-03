from openai import AzureOpenAI

from zev.config import config
from zev.llms.openai.provider import OpenAIProvider


class AzureOpenAIProvider(OpenAIProvider):
    AUTH_ERROR_MESSAGE = "Error: There was an error authenticating with Azure OpenAI. Check Azure credentials or run `zev --setup` again."

    def __init__(self):
        required_vars = {
            "AZURE_OPENAI_ACCOUNT_NAME": config.azure_openai_account_name,
            "AZURE_OPENAI_DEPLOYMENT": config.azure_openai_deployment,
            "AZURE_OPENAI_API_VERSION": config.azure_openai_api_version,
        }

        for var, value in required_vars.items():
            if not value:
                raise ValueError(f"{var} must be set. Run `zev --setup`.")

        azure_openai_endpoint = f"https://{config.azure_openai_account_name}.openai.azure.com/"

        if config.azure_openai_api_key:
            self.client = AzureOpenAI(
                api_key=config.azure_openai_api_key,
                azure_endpoint=azure_openai_endpoint,
                api_version=config.azure_openai_api_version,
            )
        else:
            try:
                from azure.identity import (  # pylint: disable=import-outside-toplevel
                    DefaultAzureCredential,
                    get_bearer_token_provider,
                )
            except ImportError as exc:
                raise ImportError("Missing required Azure packages. Run `pip install zev[azure]`") from exc
            token_provider = get_bearer_token_provider(
                DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default"
            )
            self.client = AzureOpenAI(
                azure_endpoint=azure_openai_endpoint,
                api_version=config.azure_openai_api_version,
                azure_ad_token_provider=token_provider,
            )

        self.model = config.azure_openai_deployment
