import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get OpenRouter API key
OPENROUTER_API_KEY = "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"

# Initialize OpenRouter client
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

def call_openrouter_api(messages, model="qwen/qwen3-0.6b-04-28:free", max_tokens=2000):
    if not OPENROUTER_API_KEY:
        raise ValueError("OpenRouter API key is not set. Please check your .env file.")
    
    if not isinstance(messages, list):
        raise ValueError("Messages must be a list of message objects with 'role' and 'content'")
    
    try:
        print(f"Making OpenRouter API call with model: {model}")
        print(f"Messages: {messages}")
        
        response = client.chat.completions.create(
            extra_headers={
                "HTTP-Referer": "http://localhost:5000",
                "X-Title": "Data Analytics App",
            },
            model=model,
            messages=messages,
            temperature=0.7,
            max_tokens=max_tokens
        )
        
        print(f"Received response: {response}")
        
        # Check for rate limit error in response
        if hasattr(response, 'error') and response.error:
            error_msg = response.error.get('message', '')
            if 'Rate limit exceeded' in error_msg:
                raise Exception("Rate limit exceeded: " + error_msg)
        
        # Validate response structure
        if not response or not hasattr(response, 'choices') or not response.choices:
            raise Exception("Invalid response from OpenRouter API")
        if not response.choices[0] or not hasattr(response.choices[0], 'message'):
            raise Exception("Invalid message in OpenRouter API response")
        if not response.choices[0].message or not hasattr(response.choices[0].message, 'content'):
            raise Exception("Invalid content in OpenRouter API response")
        
        return response.choices[0].message.content
        
    except Exception as e:
        error_msg = str(e)
        print(f"OpenRouter API error details: {error_msg}")
        print(f"Error type: {type(e)}")
        
        if "insufficient_quota" in error_msg.lower():
            raise Exception("OpenRouter API quota exceeded. Please try again later.")
        elif "invalid_api_key" in error_msg.lower():
            raise Exception("Invalid OpenRouter API key. Please check your API key.")
        elif "rate_limit" in error_msg.lower():
            raise Exception("Rate limit exceeded: " + error_msg)
        else:
            raise Exception(f"Error calling OpenRouter API: {error_msg}") 