from flask import Blueprint, request, jsonify, render_template
import os
from openai import OpenAI
from dotenv import load_dotenv
from backend.utils.openrouter_client import call_openrouter_api

nlp_bp = Blueprint('nlp', __name__)

# Load environment variables
load_dotenv()

# Get OpenRouter API key
OPENROUTER_API_KEY = "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"

# Initialize OpenRouter client
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

def extract_code_from_response(response):
    """Extract code blocks from the AI response."""
    import re
    code_blocks = re.findall(r'```(?:python)?\n(.*?)\n```', response, re.DOTALL)
    return code_blocks[0] if code_blocks else None

def parse_api_error_message(e):
    msg = str(e)
    if 'API key is not set' in msg:
        return "<b>OpenRouter API Error:</b> API key is not set. Please add your OpenRouter API key to your .env file."
    elif 'Rate limit exceeded' in msg:
        return """<b>OpenRouter API Rate Limit Reached:</b><br>
        You've reached the daily limit for free API calls.<br>
        Please try again tomorrow or add credits to your OpenRouter account to increase the limit.<br>
        <a href='https://openrouter.ai/credits' target='_blank'>Add Credits to OpenRouter</a>"""
    return f"<b>OpenRouter API Error:</b> {msg}"

# NLP Query Route
@nlp_bp.route('/nlp_query', methods=['POST'])
def nlp_query():
    from backend.data_preprocessing.data_cache import get_cache
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
        try:
            ai_response = call_openrouter_api(prompt)
        except Exception as e:
            print(f"OpenRouter API error: {str(e)}")
            return jsonify({'html': parse_api_error_message(e)})

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
        html = parse_api_error_message(e)

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
    message_history = data.get('message_history', [])
    
    # Prepare the messages array with conversation history
    messages = []
    
    # Add system message to set context
    messages.append({
        "role": "system",
        "content": "You are a helpful AI assistant. You maintain context from previous messages in the conversation."
    })
    
    # Add message history
    for msg in message_history:
        messages.append({
            "role": msg['role'],
            "content": msg['content']
        })
    
    # Add current query
    if 'file_content' in data and 'file_name' in data:
        file_content = data['file_content']
        file_name = data['file_name']
        messages.append({
            "role": "user",
            "content": f"File: {file_name}\n\nContent:\n{file_content}\n\nUser question: {query}"
        })
    else:
        messages.append({
            "role": "user",
            "content": query
        })

    try:
        try:
            response = call_openrouter_api(messages)
        except Exception as e:
            print(f"OpenRouter API error: {str(e)}")
            return jsonify({'html': parse_api_error_message(e)})
        return jsonify({'html': f"<pre>{response}</pre>"})
    except Exception as e:
        return jsonify({'html': parse_api_error_message(e)})

@nlp_bp.route('/analyze', methods=['POST'])
def analyze_data():
    try:
        data = request.json
        query = data.get('query')
        
        if not query:
            return jsonify({'error': 'No query provided'}), 400
            
        response = call_openrouter_api(query)
        
        return jsonify({
            'response': response,
            'model': 'mistralai/mistral-small-3.1-24b-instruct:free'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500 