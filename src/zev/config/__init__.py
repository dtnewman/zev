from pathlib import Path

from zev.paths import get_config_path


def read_config_file(path: Path) -> dict[str, str]:
    """Parse the KEY=value config file (a dotenv subset: comments, `export`, quoted values)."""
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip().removeprefix("export ").strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "'\"":
            value = value[1:-1]
        elif " #" in value:
            value = value.split(" #", 1)[0].rstrip()
        values[key] = value
    return values


class Config:
    def __init__(self):
        self.config_path = get_config_path()
        self.reload()

    def reload(self):
        self.vals = read_config_file(self.config_path)

    @property
    def llm_provider(self):
        return self.vals.get("LLM_PROVIDER")

    # OpenAI
    @property
    def openai_api_key(self):
        return self.vals.get("OPENAI_API_KEY")

    @property
    def openai_model(self):
        return self.vals.get("OPENAI_MODEL")

    # Ollama
    @property
    def ollama_base_url(self):
        return self.vals.get("OLLAMA_BASE_URL")

    @property
    def ollama_model(self):
        return self.vals.get("OLLAMA_MODEL")

    # Gemini
    @property
    def gemini_model(self):
        return self.vals.get("GEMINI_MODEL")

    @property
    def gemini_api_key(self):
        return self.vals.get("GEMINI_API_KEY")

    # Azure OpenAI
    @property
    def azure_openai_account_name(self):
        return self.vals.get("AZURE_OPENAI_ACCOUNT_NAME")

    @property
    def azure_openai_api_key(self):
        return self.vals.get("AZURE_OPENAI_API_KEY")

    @property
    def azure_openai_deployment(self):
        return self.vals.get("AZURE_OPENAI_DEPLOYMENT")

    @property
    def azure_openai_api_version(self):
        return self.vals.get("AZURE_OPENAI_API_VERSION")

    # Anthropic
    @property
    def anthropic_api_key(self):
        return self.vals.get("ANTHROPIC_API_KEY")

    @property
    def anthropic_model(self):
        return self.vals.get("ANTHROPIC_MODEL")


config = Config()
