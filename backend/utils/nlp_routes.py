from flask import Blueprint, request, jsonify, render_template
import os
from openai import OpenAI
from dotenv import load_dotenv
from backend.utils.openrouter_client import call_openrouter_api, MODEL_NAME
from backend.data_preprocessing.filter_handler import get_global_filters, save_all_filters, update_filtered_cache
import json
import re

nlp_bp = Blueprint('nlp', __name__)

# Load environment variables
load_dotenv()

# Get OpenRouter API key
OPENROUTER_API_KEY = "sk-or-v1-79a666da353e45c220573ef5dea02e5350ee3709e7571d390b39a1c566a9e1b"

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

def extract_json_from_code_block(text):
    # Extract JSON from a code block if present
    match = re.search(r'```json\s*(\{[\s\S]*?\})\s*```', text)
    if match:
        return match.group(1)
    # Fallback: try to find any JSON object
    match = re.search(r'(\{[\s\S]*?\})', text)
    if match:
        return match.group(1)
    return None

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
    
    # Updated prompt for both answer and filter
    messages = [
        {
        "role": "system",
        "content": (
            "You are a data analyst assistant. Given a user's question and the dataset schema, always reply in this JSON format: "
            "{\"answer\": <short plain-language answer>, \"filters\": <JSON array of filter conditions>} "
            "The 'answer' should be a short, clear response to the user's question, using the data context provided. "
            "The 'filters' array should be suitable for filtering a pandas DataFrame, with each filter as a JSON object with 'column', 'operator', and 'value'. "
            "Use only double quotes for all keys and string values, and use operators like '==', '!=', '>', '<', '>=', '<=', 'in', 'not in'. "
            "If no filter is needed, return an empty array for 'filters'."
        )
    },
    {
        "role": "user",
        "content": f"""Analyze this dataset and answer the user's question.\n\nDataset Information:\n- Number of rows: {row_count}\n- Number of columns: {col_count}\n- Numeric columns: {', '.join(numeric_cols) if numeric_cols else 'None'}\n- Categorical columns: {', '.join(categorical_cols) if categorical_cols else 'None'}\n- Schema: {schema}\n\nUser question: {query}\n\nRespond ONLY with a JSON object with 'answer' and 'filters' fields as described above."""
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
            print("[DEBUG] Raw AI response:", ai_response)
        except Exception as e:
            print(f"OpenRouter API error: {str(e)}")
            return jsonify({'html': parse_api_error_message(e)})

        # Extract answer and filters from AI response
        answer = None
        filter_json = None
        ai_json = None
        # 1. Try to parse as JSON directly
        try:
            ai_json = json.loads(ai_response)
            print("[DEBUG] Parsed as JSON directly:", ai_json)
            answer = ai_json.get('answer', None)
            filter_json = json.dumps(ai_json.get('filters', []), indent=2)
        except Exception:
            # 2. Try to extract JSON from code block
            ai_json_str = extract_json_from_code_block(ai_response)
            print("[DEBUG] Extracted JSON from code block:", ai_json_str)
            if ai_json_str:
                try:
                    ai_json = json.loads(ai_json_str)
                    print("[DEBUG] Parsed JSON from code block:", ai_json)
                    answer = ai_json.get('answer', None)
                    filter_json = json.dumps(ai_json.get('filters', []), indent=2)
                except Exception as e:
                    print("[DEBUG] Failed to parse JSON from code block:", e)
                    filter_json = None
                    answer = None
            else:
                # 3. Fallback: try to extract JSON array for filters as before
                json_match = re.search(r'\[.*?\]', ai_response, re.DOTALL)
                filter_json = json_match.group(0) if json_match else None
                print("[DEBUG] Fallback filter_json:", filter_json)
                answer = None
        html = ""
        if filter_json:
            try:
                new_filters = json.loads(filter_json)
                print("[DEBUG] Parsed filters:", new_filters)
                # Auto-fix if list of strings
                if new_filters and isinstance(new_filters[0], str):
                    new_filters = fix_stringified_filters(new_filters)
                # Overwrite global filters with new filters
                if isinstance(new_filters, dict):
                    new_filters = [new_filters]
                save_all_filters(new_filters)
                print("[DEBUG] Filters saved to file.")
                update_filtered_cache(temp_id)
                # Get filtered data (first 10 rows)
                from backend.data_preprocessing.filtered_cache import get_filtered_cache
                filtered_df = get_filtered_cache().get(temp_id)
                filtered_data = filtered_df.head(10).to_dict(orient='records') if filtered_df is not None else []
                html = f"<div class='alert alert-success'>Filter(s) set and will be applied to all data previews.<br>JSON: <pre>{filter_json}</pre></div>"
            except Exception as ex:
                print("[DEBUG] Exception during filter processing:", ex)
                html = f"<div class='alert alert-danger'>Failed to parse filter JSON: {str(ex)}<br>AI response: <pre>{ai_response}</pre></div>"
                filtered_data = []
        else:
            html = f"<div class='alert alert-warning'>No valid JSON filter found in AI response.<br>AI response: <pre>{ai_response}</pre></div>"
            filtered_data = []

        return jsonify({
            'html': html,
            'filtered_data': filtered_data,
            'nlp_answer': answer
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
            'model': MODEL_NAME
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500 