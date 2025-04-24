import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

import pandas as pd
from flask import Flask, render_template, request
from io import BytesIO
from backend.data_preprocessing.data_utils import handle_missing_values, normalize_column_names
from backend.data_preprocessing.summary_utils import generate_overview

app = Flask(__name__, template_folder=os.path.join(os.getcwd(), 'backend', 'templates'))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    if not file:
        return "No file uploaded"

    try:
        if file.filename.endswith('.csv'):
            df = pd.read_csv(file)
        elif file.filename.endswith(('.xls', '.xlsx')):
            in_memory_file = BytesIO(file.read())
            df = pd.read_excel(in_memory_file)
        else:
            return "Unsupported file type"
    except Exception as e:
        return f"Error reading file: {str(e)}"

    # Preprocessing steps
    df = handle_missing_values(df)
    df = normalize_column_names(df)
    overview = generate_overview(df)

    # Render table and overview
    preview = df.head().to_html(classes='table table-striped')
    return render_template('preview.html', table=preview, overview=overview)

if __name__ == '__main__':
    app.run(debug=True)
