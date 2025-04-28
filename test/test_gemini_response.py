import os
import sys
from google import genai
import json
from pydantic import ValidationError
from dotenv import load_dotenv
from zev.llms.types import OptionsResponse, Command
from zev.constants import PROMPT

# Load environment variables if using a .env file
load_dotenv()

def test_gemini_response():
    # Get API key
    api_key = os.getenv("GEMINI_API_KEY", "AIzaSyA9aGoEHcBROlFWFdd0Enep8HmlNgV1IQs").strip()
    if not api_key:
        print("Error: GEMINI_API_KEY not set. Please set it first.")
        sys.exit(1)
        
    # Configure Gemini
    # genai.configure(api_key=api_key)
    client = genai.Client(api_key=api_key)
    
    # Setup test data
    test_prompt = "How to list all files in a directory"
    test_context = "I'm using Ubuntu 22.04"
    model_name = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    
    # Assemble prompt
    assembled_prompt = PROMPT.format(prompt=test_prompt, context=test_context)
    print(f"Using model: {model_name}")
    
    # Create model
    # model = genai.GenerativeModel(model_name=model_name)
    
    # Generate response
    try:
        print("\n=== Sending request to Gemini API ===\n")
        # response = model.generate_content(
        #     assembled_prompt,
        #     config={
        #         'response_schema': OptionsResponse,
        #     }
        # )

        response = client.models.generate_content(
            model=model_name,
            contents=assembled_prompt,
            config={
                'response_mime_type': 'application/json',
                'response_schema': OptionsResponse,
            },
        )
        
        # Print raw response
        print("\n=== RAW RESPONSE ===")
        raw_text = response.text
        print(raw_text)
        
        # Clean response (remove markdown code blocks)
        cleaned_text = raw_text.replace("```json", "").replace("```", "").strip()
        print("\n=== CLEANED RESPONSE ===")
        print(cleaned_text)
        
        # Try parsing the JSON
        print("\n=== PARSED JSON ===")
        try:
            response_json = json.loads(response.text)
            print(json.dumps(response_json, indent=2))
            
            # Try creating a Pydantic model from it
            print("\n=== PYDANTIC MODEL ===")
            options_response = OptionsResponse.parse_obj(response_json)
            print(f"is_valid: {options_response.is_valid}")
            print(f"explanation_if_not_valid: {options_response.explanation_if_not_valid}")
            print("commands:")
            for cmd in options_response.commands:
                print(f"  - {cmd.command}: {cmd.short_explanation}")
                
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            print(f"Error at position {e.pos}: around '{cleaned_text[max(0, e.pos-20):min(len(cleaned_text), e.pos+20)]}'")
        except ValidationError as e:
            print(f"Pydantic validation error: {e}")
            
    except Exception as e:
        print(f"API request error: {e}")

if __name__ == "__main__":
    test_gemini_response()