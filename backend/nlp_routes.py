from flask import Blueprint, request, jsonify, render_template
import os
import requests
import re
from openai import OpenAI
from dotenv import load_dotenv

nlp_bp = Blueprint('nlp', __name__)

# Load environment variables
load_dotenv()

# Get API keys
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
HF_API_KEY = os.getenv('HF_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# Initialize API clients
clients = {}
if OPENAI_API_KEY:
    clients['openai'] = OpenAI(api_key=OPENAI_API_KEY)
if DEEPSEEK_API_KEY:
    clients['deepseek'] = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")

def call_deepseek_api(prompt):
    if not DEEPSEEK_API_KEY:
        raise ValueError("DeepSeek API key is not set. Please check your .env file.")
    
    try:
        response = clients['deepseek'].chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1000
        )
        return response.choices[0].message.content
    except Exception as e:
        raise Exception(f"Error calling DeepSeek API: {str(e)}")

def call_openai_api(prompt):
    if not OPENAI_API_KEY:
        raise ValueError("OpenAI API key is not set. Please check your .env file.")
    
    try:
        response = clients['openai'].chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1000
        )
        return response.choices[0].message.content
    except Exception as e:
        raise Exception(f"Error calling OpenAI API: {str(e)}")

def extract_code_from_response(response):
    """Extract code blocks from the AI response."""
    code_blocks = re.findall(r'```(?:python)?\n(.*?)\n```', response, re.DOTALL)
    return code_blocks[0] if code_blocks else None

# NLP Query Route
@nlp_bp.route('/nlp_query', methods=['POST'])
def nlp_query():
    from backend.data_preprocessing.data_cache import get_cache  # Import cache from data_cache
    data = request.get_json()
    query = data['query']
    temp_id = data['temp_id']
    df = get_cache().get(temp_id)
    if df is None:
        return jsonify({'html': 'Dataset not found.'})

    # Convert dtypes to strings before joining
    schema = ', '.join([f'{col} ({str(dtype)})' for col, dtype in zip(df.columns, df.dtypes)])
    prompt = f"You are a data analyst. The dataset columns are: {schema}. User question: {query}. Respond with a pandas command to answer the question."

    try:
        # Try DeepSeek first, fall back to OpenAI if needed
        try:
            ai_response = call_deepseek_api(prompt)
        except Exception as e:
            print(f"DeepSeek API error: {str(e)}")
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
    
    try:
        # Try DeepSeek first, fall back to OpenAI if needed
        try:
            response = call_deepseek_api(query)
        except Exception as e:
            print(f"DeepSeek API error: {str(e)}")
            response = call_openai_api(query)
            
        return jsonify({'html': f"<pre>{response}</pre>"})
    except Exception as e:
        return jsonify({'html': f"Error: {str(e)}"}) 