import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

import pandas as pd
from flask import Flask, render_template, request
from io import BytesIO
from backend.data_preprocessing.file_processing import read_file
from backend.data_preprocessing.data_cleaning import handle_missing_values, normalize_column_names
from backend.data_preprocessing.data_overview import generate_overview

# Initialize Flask application
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
        # Metadata
        file_name = file.filename
        file_format = 'csv' if file.filename.endswith('.csv') else \
                      'xls/xlsx' if file.filename.endswith(('.xls', '.xlsx')) else 'unknown'
        data_type = 'Uploaded'

        # Read and preprocess
        df = read_file(file)
        df = handle_missing_values(df)
        df = normalize_column_names(df)

        # Overview
        overview = generate_overview(df, file_name, data_type, file_format)

        # Convert df to HTML (split table)
        html_table = df.to_html(index=False, classes='display nowrap', border=0)
        table_header = html_table.split('<thead>')[1].split('</thead>')[0]
        table_body = html_table.split('<tbody>')[1].split('</tbody>')[0]

        return render_template('preview.html',
                               table_header=table_header,
                               table_body=table_body,
                               overview=overview)

    except Exception as e:
        return f"Error reading file: {str(e)}"

if __name__ == '__main__':
    app.run(debug=True)
