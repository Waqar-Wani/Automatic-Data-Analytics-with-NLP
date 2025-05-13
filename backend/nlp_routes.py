from flask import Blueprint, request, jsonify, render_template
import os
from openai import OpenAI
from dotenv import load_dotenv
from backend.utils.openrouter_client import call_openrouter_api
from backend.data_preprocessing.filter_handler import get_global_filters, save_all_filters, update_filtered_cache
import json
import re

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
        return jsonify({'html': '<div class="alert alert-warning">Dataset not found. Please upload your dataset first.</div>'})

    row_count = len(df)
    col_count = len(df.columns)
    numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    schema = ', '.join([f'{col} ({str(dtype)})' for col, dtype in zip(df.columns, df.dtypes)])
    
    # Stronger system prompt for valid JSON
    messages = [
        {
        "role": "system",
        "content": (
            "You are a data analyst assistant. Given a user's question, return a JSON array of filter conditions (not code) "
            "that can be used to filter a pandas DataFrame. Each filter should be a JSON object with \"column\", \"operator\", and \"value\" keys. "
            "Use only double quotes for all keys and string values, and use operators like '==', '!=', '>', '<', '>=', '<=', 'in', 'not in'. "
            "Do not include any explanation or code, only the JSON array."
        )
    },
    {
        "role": "user",
        "content": f"""Analyze this dataset and answer the user's question by returning a JSON array of filter conditions.\n\nDataset Information:\n- Number of rows: {row_count}\n- Number of columns: {col_count}\n- Numeric columns: {', '.join(numeric_cols) if numeric_cols else 'None'}\n- Categorical columns: {', '.join(categorical_cols) if categorical_cols else 'None'}\n- Schema: {schema}\n\nUser question: {query}\n\nRespond ONLY with the JSON array of filter conditions."""
    }
    ]

    def fix_stringified_filters(filters):
        # If filters is a list of strings, try to convert each to a dict
        fixed = []
        for f in filters:
            if isinstance(f, str):
                # Replace single quotes with double quotes and fix operator if needed
                f_fixed = f.replace("'", '"').replace('"equal"', '"=="').replace('equal', '==')
                try:
                    fixed.append(json.loads(f_fixed))
                except Exception:
                    continue
            else:
                fixed.append(f)
        return fixed

    try:
        try:
            ai_response = call_openrouter_api(messages)
        except Exception as e:
            print(f"OpenRouter API error: {str(e)}")
            return jsonify({'html': parse_api_error_message(e)})

        # Extract JSON array from AI response
        json_match = re.search(r'\[.*?\]', ai_response, re.DOTALL)
        filter_json = json_match.group(0) if json_match else None
        html = ""
        if filter_json:
            try:
                new_filters = json.loads(filter_json)
                # Auto-fix if list of strings
                if new_filters and isinstance(new_filters[0], str):
                    new_filters = fix_stringified_filters(new_filters)
                # Overwrite global filters with new filters
                if isinstance(new_filters, dict):
                    new_filters = [new_filters]
                save_all_filters(new_filters)
                update_filtered_cache(temp_id)
                html = f"<div class='alert alert-success'>Filter(s) set and will be applied to all data previews.<br>JSON: <pre>{json.dumps(new_filters, indent=2)}</pre></div>"
            except Exception as ex:
                html = f"<div class='alert alert-danger'>Failed to parse filter JSON: {str(ex)}<br>AI response: <pre>{ai_response}</pre></div>"
        else:
            html = f"<div class='alert alert-warning'>No valid JSON filter found in AI response.<br>AI response: <pre>{ai_response}</pre></div>"

        return jsonify({
            'html': html,
            'filtered_data': None
        })
    except Exception as e:
        html = parse_api_error_message(e)
        return jsonify({'html': html, 'filtered_data': None})

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
    # Hardcoded max_tokens value
    max_tokens = 500
    
    # Prepare the messages array with conversation history
    messages = []
    
    # Add system message to set context
    messages.append({
        "role": "system",
        "content": "You are a helpful AI assistant. You maintain context from previous messages in the conversation. Keep your responses concise and under 200 tokens."
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
            response = call_openrouter_api(messages, max_tokens=max_tokens)
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
            'model': 'qwen/qwen3-0.6b-04-28:free'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500 