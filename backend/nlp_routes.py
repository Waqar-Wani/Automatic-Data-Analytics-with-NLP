from flask import Blueprint, request, jsonify, render_template
import os
import requests
import re
from openai import OpenAI
from dotenv import load_dotenv

nlp_bp = Blueprint('nlp', __name__)

# Load environment variables
load_dotenv()

# Debug: Print all environment variables
print("Loading environment variables...")
print("Current working directory:", os.getcwd())
print("Environment variables:")
for key in ['OPENAI_API_KEY', 'DEEPSEEK_API_KEY', 'HF_API_KEY', 'OPENROUTER_API_KEY']:
    value = os.getenv(key)
    if value:
        print(f"{key}: {'*' * len(value)}")  # Print asterisks instead of actual key
    else:
        print(f"{key}: Not set")

# Get API keys
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
HF_API_KEY = os.getenv('HF_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# Initialize OpenAI client
if OPENAI_API_KEY:
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        print("OpenAI client initialized successfully")
    except Exception as e:
        print(f"Error initializing OpenAI client: {str(e)}")
else:
    print("OpenAI API key not found, client not initialized")

def call_deepseek_api(prompt):
    if not DEEPSEEK_API_KEY:
        raise ValueError("DeepSeek API key is not set. Please check your .env file.")
    
    try:
        # Initialize DeepSeek client with base_url
        deepseek_client = OpenAI(
            api_key=DEEPSEEK_API_KEY,
            base_url="https://api.deepseek.com"
        )
        
        response = deepseek_client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are a helpful assistant"},
                {"role": "user", "content": prompt}
            ],
            stream=False
        )
        return response.choices[0].message.content
    except Exception as e:
        if "401" in str(e):
            raise ValueError("Invalid DeepSeek API key. Please check your .env file and make sure the key is correct.")
        else:
            raise Exception(f"Error calling DeepSeek API: {str(e)}")

def call_huggingface_api(prompt):
    url = "https://api-inference.huggingface.co/models/HuggingFaceH4/zephyr-7b-beta"
    headers = {
        "Authorization": f"Bearer {HF_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "inputs": prompt,
        "parameters": {"max_new_tokens": 256}
    }
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    result = response.json()
    if isinstance(result, list) and 'generated_text' in result[0]:
        return result[0]['generated_text']
    elif 'generated_text' in result:
        return result['generated_text']
    elif 'error' in result:
        return f"Error from Hugging Face: {result['error']}"
    else:
        return str(result)

def call_openai_api(prompt):
    if not OPENAI_API_KEY:
        raise ValueError("OpenAI API key is not set. Please check your .env file.")
    
    if not OPENAI_API_KEY.startswith('sk-'):
        raise ValueError("Invalid OpenAI API key format. The key should start with 'sk-'")
    
    try:
        response = client.chat.completions.create(
            model='gpt-3.5-turbo',
            messages=[{'role': 'user', 'content': prompt}],
            max_tokens=512,
            temperature=0
        )
        return response.choices[0].message.content
    except Exception as e:
        if "401" in str(e):
            raise ValueError("Invalid OpenAI API key. Please check your .env file and make sure the key is correct.")
        else:
            raise Exception(f"Error calling OpenAI API: {str(e)}")

def call_openrouter_api(prompt):
    if not OPENROUTER_API_KEY:
        raise ValueError("OpenRouter API key is not set. Please check your .env file.")
    
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:5000",  # Required by OpenRouter
        "X-Title": "Data Analysis App"  # Required by OpenRouter
    }
    data = {
        "model": "openchat/openchat-3.5-0106",
        "messages": [{"role": "user", "content": prompt}]
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"]
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            raise ValueError("Invalid OpenRouter API key. Please check your .env file and make sure the key is correct.")
        else:
            raise e
    except Exception as e:
        raise Exception(f"Error calling OpenRouter API: {str(e)}")

def extract_code_from_response(response):
    match = re.search(r'```python\n(.*?)```', response, re.DOTALL)
    if match:
        return match.group(1)
    return None

# NLP Query Route
@nlp_bp.route('/nlp_query', methods=['POST'])
def nlp_query():
    from main import cache  # Import cache from main
    data = request.get_json()
    query = data['query']
    temp_id = data['temp_id']
    df = cache.get(temp_id)
    if df is None:
        return jsonify({'html': 'Dataset not found.'})

    schema = ', '.join([f'{col} ({dtype})' for col, dtype in zip(df.columns, df.dtypes)])
    prompt = f"You are a data analyst. The dataset columns are: {schema}. User question: {query}. Respond with a pandas command to answer the question."

    try:
        ai_response = call_openai_api(prompt)
        code = extract_code_from_response(ai_response)
        if code:
            code = code.replace("pd.read_csv('fruit_prices.csv')", "df")
            local_vars = {'df': df}
            try:
                exec(code, {}, local_vars)
                result = None
                for line in code.splitlines():
                    if '=' in line:
                        var_name = line.split('=')[0].strip()
                        if var_name in local_vars:
                            result = local_vars[var_name]
                            break
                if result is None:
                    result = 'No result variable found.'
                html = f"<b>AI Response:</b><br><pre>{ai_response}</pre><br><b>Result:</b> {result}"
            except Exception as ex:
                html = f"<b>AI Response:</b><br><pre>{ai_response}</pre><br><b>Code execution error:</b> {ex}"
        else:
            html = f"<b>AI Response:</b><br><pre>{ai_response}</pre>"
    except Exception as e:
        html = f"Error: {e}"

    return jsonify({'html': html})

# Chatbot Test Page
@nlp_bp.route('/chatbot_test')
def chatbot_test():
    return render_template('chatbot_test.html')

# Chatbot Test API
@nlp_bp.route('/chatbot_test_api', methods=['POST'])
def chatbot_test_api():
    data = request.get_json()
    query = data['query']
    print(f"Received query: {query}")  # Debug log
    
    try:
        if not DEEPSEEK_API_KEY:
            print("DeepSeek API key not found")  # Debug log
            raise ValueError("DeepSeek API key is not set. Please check your .env file.")
        
        print("Calling DeepSeek API...")  # Debug log
        ai_response = call_deepseek_api(query)
        print("Received response from DeepSeek API")  # Debug log
        html = f"<b>AI Response:</b><br><pre>{ai_response}</pre>"
    except Exception as e:
        print(f"Error occurred: {str(e)}")  # Debug log
        html = f"<div style='color: red;'><b>Error:</b> {str(e)}</div>"
    return jsonify({'html': html}) 