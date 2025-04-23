import openai
import os
from pydantic import BaseModel
from typing import Optional, Literal
from google import genai
import json

from zev.constants import DEFAULT_MODEL, DEFAULT_PROVIDER, DEFAULT_OPENAI_MODEL, DEFAULT_GEMINI_MODEL, PROMPT, LLMProvider


class Command(BaseModel):
    command: str
    short_explanation: str

class OptionsResponse(BaseModel):
    commands: list[Command]
    is_valid: bool
    explanation_if_not_valid: Optional[str] = None

def get_openai_client():
    """Returns the OpenAI client."""

    base_url = os.getenv("OPENAI_BASE_URL", default="").strip()
    api_key = os.getenv("OPENAI_API_KEY", default="").strip()
    if not base_url or not api_key:
        raise ValueError("OPENAI_BASE_URL and OPENAI_API_KEY must be set. Try running `zev --setup`.")
    return openai.OpenAI(base_url=base_url, api_key=api_key)

def get_gemini_client():
    """Returns the Gemini client."""

    api_key = os.getenv("GEMINI_API_KEY", default="").strip()
    if not api_key:
        raise ValueError("GEMINI_API_KEY must be set. Try running `zev --setup`.")
    genai.configure(api_key=api_key)
    return genai

def get_client():
    """Returns the appropriate client based on the configured provider."""

    provider = os.getenv("LLM_PROVIDER", default=DEFAULT_PROVIDER).strip().lower()
    
    if provider == LLMProvider.OPENAI:
        return get_openai_client()
    elif provider == LLMProvider.GEMINI:
        return get_gemini_client()
    else:
        raise ValueError(f"Unsupported provider: {provider}. Use 'openai' or 'gemini'.")

def get_openai_response(client, prompt: str) -> OptionsResponse | None:
    """Get response from OpenAI API."""

    model = os.getenv("OPENAI_MODEL", default=DEFAULT_OPENAI_MODEL)
    if not model:
        raise ValueError("OPENAI_MODEL must be set. Try running `zev --setup`.")
        
    response = client.beta.chat.completions.parse(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        response_format=OptionsResponse,
    )
    return response.choices[0].message.parsed

def get_gemini_response(client, prompt: str) -> OptionsResponse | None:
    """Get response from Gemini API."""

    model = os.getenv("GEMINI_MODEL", default=DEFAULT_GEMINI_MODEL)
    if not model:
        raise ValueError("GEMINI_MODEL must be set. Try running `zev --setup`.")
    
    try:
        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config={
                'response_mime_type': 'application/json',
                'response_schema': OptionsResponse,
            },
        )
        
        if not response.text:
            print("Error: Received empty response from Gemini API.")
            return None
                            
        try:
            response_json = json.loads(response.text)
            return OptionsResponse.parse_obj(response_json)
        except json.JSONDecodeError as json_err:
            print(f"Error: Failed to parse JSON response from Gemini API: {json_err}")
            print(f"Raw response: {response.text[:100]}...") 
            return None

    except Exception as gemini_err:
        print(f"Error: Gemini API request failed: {str(gemini_err)}")
        return None

def get_options(prompt: str, context: str) -> OptionsResponse | None:
    """Get command options from the configured LLM provider."""

    provider = os.getenv("LLM_PROVIDER", default=DEFAULT_PROVIDER).strip().lower()
    client = get_client()
    assembled_prompt = PROMPT.format(prompt=prompt, context=context)
    
    try:
        if provider == LLMProvider.OPENAI:
            return get_openai_response(client, assembled_prompt)
        elif provider == LLMProvider.GEMINI:
            return get_gemini_response(client, assembled_prompt)
        else:
            raise ValueError(f"Provider {provider} is invalid. Use 'openai' or 'gemini'.")
                
    except openai.AuthenticationError:
        print(f"Error: There was an error with your {provider.upper()} API key. You can change it by running `zev --setup`.")
        return None

    except Exception as e:
        print(f"Error: An unexpected error occurred: {str(e)}")
        return None
