from zev.config.types import SetupQuestionText

questions = (
    SetupQuestionText(
        name="OLLAMA_BASE_URL",
        prompt="Enter the Ollama URL:",
        default="http://localhost:11434/v1",
    ),
    SetupQuestionText(name="OLLAMA_MODEL", prompt="Enter the model to use (e.g. llama3.2):"),
)
