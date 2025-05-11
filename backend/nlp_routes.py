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
        return jsonify({'html': '<div class="alert alert-warning">Dataset not found. Please upload your dataset first.</div>'})

    # Get basic dataset statistics
    row_count = len(df)
    col_count = len(df.columns)
    numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    
    # Convert dtypes to strings before joining
    schema = ', '.join([f'{col} ({str(dtype)})' for col, dtype in zip(df.columns, df.dtypes)])
    
    # Create messages array for the API call
    messages = [
        {
            "role": "system",
            "content": """You are a data analyst assistant. Your task is to analyze datasets and answer questions about them.
            You should provide clear explanations, code when needed, and visualization suggestions.
            When providing code, make sure to assign the result to a variable named 'result_df'."""
        },
        {
            "role": "user",
            "content": f"""Analyze this dataset and answer the user's question.

Dataset Information:
- Number of rows: {row_count}
- Number of columns: {col_count}
- Numeric columns: {', '.join(numeric_cols) if numeric_cols else 'None'}
- Categorical columns: {', '.join(categorical_cols) if categorical_cols else 'None'}
- Schema: {schema}

User question: {query}

Instructions:
1. If the question requires data analysis, provide a pandas command to answer it
2. If the question is about the dataset structure, provide a clear explanation
3. If visualization would help, suggest an appropriate chart type
4. Keep your response concise and focused on the question
5. Always assign the result to a variable named 'result_df'

Respond in this format:
1. Analysis/Explanation: [Your analysis or explanation]
2. Code (if needed): [Pandas command in a code block]
3. Visualization Suggestion (if applicable): [Chart type and why it would be helpful]"""
        }
    ]

    try:
        try:
            ai_response = call_openrouter_api(messages)
        except Exception as e:
            print(f"OpenRouter API error: {str(e)}")
            return jsonify({'html': parse_api_error_message(e)})

        code = extract_code_from_response(ai_response)
        filtered_data = None
        
        if code:
            # Replace any potential data loading with our existing DataFrame
            # Handle CSV files
            for ext in ['csv', 'txt', 'dat']:
                code = code.replace(f"pd.read_csv('data.{ext}')", "df")
                code = code.replace(f"pd.read_csv('dataset.{ext}')", "df")
                code = code.replace(f"pd.read_csv('file.{ext}')", "df")
                code = code.replace(f"pd.read_csv('input.{ext}')", "df")
            
            # Handle Excel files
            for ext in ['xlsx', 'xls']:
                code = code.replace(f"pd.read_excel('data.{ext}')", "df")
                code = code.replace(f"pd.read_excel('dataset.{ext}')", "df")
                code = code.replace(f"pd.read_excel('file.{ext}')", "df")
                code = code.replace(f"pd.read_excel('input.{ext}')", "df")
            
            # Handle JSON files
            code = code.replace("pd.read_json('data.json')", "df")
            code = code.replace("pd.read_json('dataset.json')", "df")
            code = code.replace("pd.read_json('file.json')", "df")
            code = code.replace("pd.read_json('input.json')", "df")
            
            # Handle variable-based loading
            code = code.replace("pd.read_csv(csv_file)", "df")
            code = code.replace("pd.read_excel(excel_file)", "df")
            code = code.replace("pd.read_json(json_file)", "df")
            code = code.replace("pd.read_csv(filename)", "df")
            code = code.replace("pd.read_excel(filename)", "df")
            code = code.replace("pd.read_json(filename)", "df")
            
            # Handle direct DataFrame creation
            code = code.replace("pd.DataFrame(data)", "df")
            code = code.replace("pd.DataFrame(dataset)", "df")
            
            local_vars = {'df': df}
            try:
                exec(code, {}, local_vars)
                result_df = local_vars.get('result_df')
                if result_df is not None:
                    filtered_data = result_df.head(20).to_dict(orient='records')
                
                # Format the response with better styling
                html = f"""
                <div class="nlp-response">
                    <div class="ai-analysis">
                        <h4>AI Analysis</h4>
                        <div class="analysis-content">{ai_response}</div>
                    </div>
                    <div class="execution-result">
                        <h4>Result</h4>
                        <div class="result-content">{result_df.head(5).to_string() if result_df is not None else 'No result variable found.'}</div>
                    </div>
                </div>"""
            except Exception as ex:
                html = f"""
                <div class="nlp-response">
                    <div class="ai-analysis">
                        <h4>AI Analysis</h4>
                        <div class="analysis-content">{ai_response}</div>
                    </div>
                    <div class="execution-error">
                        <h4>Error</h4>
                        <div class="error-content">{str(ex)}</div>
                    </div>
                </div>"""
        else:
            html = f"""
            <div class="nlp-response">
                <div class="ai-analysis">
                    <h4>AI Analysis</h4>
                    <div class="analysis-content">{ai_response}</div>
                </div>
            </div>"""
    except Exception as e:
        html = parse_api_error_message(e)

    return jsonify({
        'html': html,
        'filtered_data': filtered_data
    })

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
    max_tokens = 2000
    
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
            'model': 'mistralai/mistral-small-3.1-24b-instruct:free'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500 