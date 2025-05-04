from zev.config.types import SetupQuestionText

questions = (
    SetupQuestionText(
        name="AZURE_OPENAI_ACCOUNT_NAME",
        prompt="Azure OpenAI account name (e.g. my-openai-resource):",
        default="",
    ),
    SetupQuestionText(
        name="AZURE_OPENAI_API_KEY",
        prompt="Azure OpenAI API key (leave blank to use Entra ID / keyless auth):",
        default="",
    ),
    SetupQuestionText(
        name="AZURE_OPENAI_DEPLOYMENT",
        prompt="Azure OpenAI deployment name (e.g. gpt-4, gpt-4o, etc):",
        default="gpt-4o",
    ),
    SetupQuestionText(
        name="AZURE_OPENAI_API_VERSION",
        prompt="Azure OpenAI API version:",
        default="2025-03-01-preview",
    ),
)
