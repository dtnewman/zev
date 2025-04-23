import openai
import os
from pydantic import BaseModel
from typing import Optional, Literal
import google.generativeai as genai
import json

from zev.constants import DEFAULT_MODEL, DEFAULT_PROVIDER, DEFAULT_OPENAI_MODEL, DEFAULT_GEMINI_MODEL


class Command(BaseModel):
    command: str
    short_explanation: str


class OptionsResponse(BaseModel):
    commands: list[Command]
    is_valid: bool
    explanation_if_not_valid: Optional[str] = None


PROMPT = """
You are a helpful assistant that helps users remember commands for the terminal. You 
will return a JSON object with a list of at most three options.

The options should be related to the prompt that the user provides (the prompt might
either be desciptive or in the form of a question).

The options should be in the form of a command that can be run in a bash terminal.

If the user prompt is not clear, return an empty list and set is_valid to false, and
provide an explanation of why it is not clear in the explanation_if_not_valid field.

Otherwise, set is_valid to true, leave explanation_if_not_valid empty, and provide the 
commands in the commands field (remember, up to 3 options, and they all must be commands
that can be run in a bash terminal without changing anything). Each command should have
a short explanation of what it does.

Here is some context about the user's environment:

============== 

{context}

============== 

Here is the users prompt:

============== 

{prompt}
"""


def get_openai_client():
    base_url = os.getenv("OPENAI_BASE_URL", default="").strip()
    api_key = os.getenv("OPENAI_API_KEY", default="").strip()
    if not base_url or not api_key:
        raise ValueError("OPENAI_BASE_URL and OPENAI_API_KEY must be set. Try running `zev --setup`.")
    return openai.OpenAI(base_url=base_url, api_key=api_key)

def get_gemini_client():
    api_key = os.getenv("GEMINI_API_KEY", default="").strip()
    if not api_key:
        raise ValueError("GEMINI_API_KEY must be set. Try running `zev --setup`.")
    genai.configure(api_key=api_key)
    return genai


def get_client():
    """Returns the appropriate client based on the configured provider."""
    provider = os.getenv("LLM_PROVIDER", default=DEFAULT_PROVIDER).strip().lower()
    
    if provider == "openai":
        return get_openai_client()
    elif provider == "gemini":
        return get_gemini_client()
    else:
        raise ValueError(f"Unsupported provider: {provider}. Use 'openai' or 'gemini'.")


def get_options(prompt: str, context: str) -> OptionsResponse | None:
    provider = os.getenv("LLM_PROVIDER", default=DEFAULT_PROVIDER).strip().lower()
    client = get_client()
    assembled_prompt = PROMPT.format(prompt=prompt, context=context)
    
    try:
        if provider == "openai":
            model = os.getenv("OPENAI_MODEL", default=DEFAULT_OPENAI_MODEL)
            if not model:
                raise ValueError("OPENAI_MODEL must be set. Try running `zev --setup`.")
                
            response = client.beta.chat.completions.parse(
                model=model,
                messages=[{"role": "user", "content": assembled_prompt}],
                response_format=OptionsResponse,
            )
            return response.choices[0].message.parsed
            
        elif provider == "gemini":
            model = os.getenv("GEMINI_MODEL", default=DEFAULT_GEMINI_MODEL)
            if not model:
                raise ValueError("GEMINI_MODEL must be set. Try running `zev --setup`.")
                
            # Enhanced prompt for Gemini to ensure it returns valid JSON
            gemini_prompt = assembled_prompt + """

IMPORTANT: You must respond with a valid JSON object that follows this format exactly:
```json
{
  "commands": [
    {
      "command": "example-command --option",
      "short_explanation": "Brief description of what this command does"
    },
    ...
  ],
  "is_valid": true,
  "explanation_if_not_valid": null
}
```

Only respond with the JSON format above and nothing else. No markdown formatting, no extra text.
"""
            
            # Configure the model
            generation_config = {
                "temperature": 0.1,  # Lower temperature for more deterministic output
                "top_p": 0.95,
                "top_k": 40,
                "response_mime_type": "application/json",  # Hint to return JSON
            }
                
            safety_settings = [
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                }
            ]
                
            model_obj = client.GenerativeModel(
                model_name=model,
                generation_config=generation_config,
                safety_settings=safety_settings
            )
            
            # Generate content
            try:
                response = model_obj.generate_content(gemini_prompt)
                
                # Parse the JSON response
                if not response.text:
                    print("Error: Received empty response from Gemini API.")
                    return None
                    
                # Try to extract JSON from the response
                response_text = response.text
                
                # Remove any potential markdown code block markers
                response_text = response_text.replace("```json", "").replace("```", "").strip()
                
                try:
                    response_json = json.loads(response_text)
                    return OptionsResponse.parse_obj(response_json)
                except json.JSONDecodeError as json_err:
                    print(f"Error: Failed to parse JSON response from Gemini API: {json_err}")
                    print(f"Raw response: {response_text[:100]}...") # Print first 100 chars for debugging
                    return None
            except Exception as gemini_err:
                print(f"Error: Gemini API request failed: {str(gemini_err)}")
                return None
                
    except openai.AuthenticationError:
        print(f"Error: There was an error with your {provider.upper()} API key. You can change it by running `zev --setup`.")
        return
    except Exception as e:
        print(f"Error: An unexpected error occurred: {str(e)}")
        return
