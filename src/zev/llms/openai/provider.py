import json
import urllib.request
import urllib.error

from zev.config import config
from zev.constants import OPENAI_BASE_URL, OPENAI_DEFAULT_MODEL, PROMPT,TOOL_SCHEMA
from zev.llms.inference_provider_base import InferenceProvider
from zev.llms.types import OptionsResponse

class OpenAIProvider(InferenceProvider):
    AUTH_ERROR_MESSAGE = (
        "Error: There was an error with your OpenAI API key. You can change it by running `zev --setup`."
    )

    def __init__(self):
        if not config.openai_api_key:
            raise ValueError("OPENAI_API_KEY must be set. Try running `zev --setup`.")

        self.model = config.openai_model or OPENAI_DEFAULT_MODEL
        self.api_url = f"{OPENAI_BASE_URL}/chat/completions"

    def get_options(self, prompt: str, context: str):
        assembled_prompt = PROMPT.format(prompt=prompt, context=context)

        headers = {
            "Authorization": f"Bearer {config.openai_api_key}",
            "Content-Type": "application/json"
        }

        body = json.dumps({
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": assembled_prompt
                }
            ],
            "tools": [TOOL_SCHEMA],
            "tool_choice": {
                "type": "function",
                "function": {
                    "name": "extract_shell_commands"
                }
            }
        }).encode("utf-8")

        req = urllib.request.Request(self.api_url, data=body, headers=headers, method="POST")

        try:
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode("utf-8"))
                variable=json.loads(result['choices'][0]["message"]['tool_calls'][0]['function']['arguments'])
                return OptionsResponse(**variable)
        except urllib.error.HTTPError as e:
            if e.code == 401:
                print(self.AUTH_ERROR_MESSAGE)
            else:
                print(f"HTTP Error: {e.code} - More details is as follows:")
                error_data = json.loads(e.read().decode())
            print("Note that to update settings, you can run `zev --setup`.")
        except Exception as e:
            print(f"Unexpected error: {e}")
        return None
