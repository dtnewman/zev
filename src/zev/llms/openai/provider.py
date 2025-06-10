import json
import urllib.request
import urllib.error

from zev.config import config
from zev.constants import OPENAI_BASE_URL, OPENAI_DEFAULT_MODEL, PROMPT
from zev.llms.inference_provider_base import InferenceProvider
from zev.llms.types import OptionsResponse


RESPONSE_JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "commands": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "command": {"type": "string"},
                    "short_explanation": {"type": "string"},
                    "is_dangerous": {"type": "boolean"},
                    "dangerous_explanation": {"type": "string"}
                },
                "required": [
                    "command",
                    "short_explanation",
                    "is_dangerous",
                    "dangerous_explanation"
                ],
                "additionalProperties": False
            }
        },
        "is_valid": {"type": "boolean"},
        "explanation_if_not_valid": {"type": "string"}
    },
    "required": [
        "commands",
        "is_valid",
        "explanation_if_not_valid"
    ],
    "additionalProperties": False
}



class OpenAIProvider(InferenceProvider):
    AUTH_ERROR_MESSAGE = (
        "Error: There was an error with your OpenAI API key. You can change it by running `zev --setup`."
    )

    def __init__(self):
        if not config.openai_api_key:
            raise ValueError("OPENAI_API_KEY must be set. Try running `zev --setup`.")
        self.model = config.openai_model or OPENAI_DEFAULT_MODEL
        self.api_url = f"{OPENAI_BASE_URL}/responses"

    def get_options(self, prompt: str, context: str):
        assembled_prompt = PROMPT.format(prompt=prompt, context=context)

        headers = {
            "Authorization": f"Bearer {config.openai_api_key}",
            "Content-Type": "application/json"
        }

        body = {
            "model": self.model,
            "input": [
                {
                    "role": "system",
                    "content": "You are a command validation assistant. Extract and validate shell commands with safety metadata."
                },
                {
                    "role": "user",
                    "content": assembled_prompt
                }
            ],
            "text": {
                "format": {
                    "type": "json_schema",
                    "name": "shell_command_analysis",
                    "schema": RESPONSE_JSON_SCHEMA,
                    "strict": True
                }
            }
        }

        req = urllib.request.Request(
            self.api_url,
            data=json.dumps(body).encode("utf-8"),
            headers=headers,
            method="POST"
        )
        try:
            with urllib.request.urlopen(req) as response:
                raw_response = response.read().decode("utf-8")
                result = json.loads(raw_response)
                commands_json_str = result['output'][0]['content'][0]['text']
                commands_dict = json.loads(commands_json_str)
                return OptionsResponse(**commands_dict)
        except urllib.error.HTTPError as e:
            if e.code == 401:
                print(self.AUTH_ERROR_MESSAGE)
            else:
                print(f"HTTP Error: {e.code}")
                try:
                    print(e.read().decode())
                except Exception:
                    pass
            print("Note that to update settings, you can run `zev --setup`.")
        except Exception as e:
            print(f"Unexpected error: {e}")
        return None
