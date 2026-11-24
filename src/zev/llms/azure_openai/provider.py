from urllib.parse import quote

from zev.config import config
from zev.llms.openai.provider import OpenAIProvider

AZURE_TOKEN_SCOPE = "https://cognitiveservices.azure.com/.default"


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

        self.url = (
            f"https://{config.azure_openai_account_name}.openai.azure.com/openai/deployments/"
            f"{quote(config.azure_openai_deployment)}/chat/completions"
            f"?api-version={quote(config.azure_openai_api_version)}"
        )
        self.model = config.azure_openai_deployment
        self.api_key = config.azure_openai_api_key
        self.credential = None

        if not self.api_key:
            try:
                from azure.identity import DefaultAzureCredential  # pylint: disable=import-outside-toplevel
            except ImportError as exc:
                raise ImportError("Missing required Azure packages. Run `pipx install zev[azure]`") from exc
            self.credential = DefaultAzureCredential()

    def get_headers(self) -> dict:
        if self.api_key:
            return {"api-key": self.api_key}
        token = self.credential.get_token(AZURE_TOKEN_SCOPE).token
        return {"Authorization": f"Bearer {token}"}
