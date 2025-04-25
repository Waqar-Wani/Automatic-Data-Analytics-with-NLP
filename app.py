import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

import pandas as pd
from flask import Flask, render_template, request
import plotly.express as px

from backend.data_preprocessing.file_processing import read_file
from backend.data_preprocessing.data_cleaning import handle_missing_values, normalize_column_names
from backend.data_preprocessing.data_overview import generate_overview

# Initialize Flask app
app = Flask(__name__, template_folder=os.path.join(os.getcwd(), 'backend', 'templates'))

# In-memory cache (for temporary session-like storage)
cache = {}

# Enable CORS for all routes
from flask_cors import CORS
CORS(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    if not file:
        return "No file uploaded"

    try:
        file_name = file.filename
        file_format = 'csv' if file.filename.endswith('.csv') else \
                      'xls/xlsx' if file.filename.endswith(('.xls', '.xlsx')) else 'unknown'
        data_type = 'Uploaded'

        df = read_file(file)
        df = handle_missing_values(df)
        df = normalize_column_names(df)

        # Overview
        overview = generate_overview(df, file_name, data_type, file_format)
        overview['columns'] = df.columns.tolist()
        overview['numeric_columns'] = df.select_dtypes(include='number').columns.tolist()

        # Store DataFrame temporarily
        temp_id = str(len(cache) + 1)
        cache[temp_id] = df

        # Render HTML table
        html_table = df.to_html(index=False, classes='display nowrap', border=0)
        table_header = html_table.split('<thead>')[1].split('</thead>')[0]
        table_body = html_table.split('<tbody>')[1].split('</tbody>')[0]

        return render_template('preview.html',
                               table_header=table_header,
                               table_body=table_body,
                               overview=overview,
                               temp_path=temp_id)

    except Exception as e:
        return f"Error reading file: {str(e)}"

@app.route('/dashboard', methods=['POST'])
def dashboard():
    try:
        x_column = request.form.get('x_column')
        y_column = request.form.get('y_column')
        temp_id = request.form.get('temp_path')

        # Debugging the received data
        print(f"Received data - temp_path: {temp_id}, x_column: {x_column}, y_column: {y_column}")

        df = cache.get(temp_id)
        if df is None:
            return "Session expired or dataset not found."

        # Further processing for chart generation
        fig = px.bar(df, x=x_column, y=y_column, title=f'Bar Chart: {x_column} by {y_column}')
        graph_html = fig.to_html(full_html=False)

        return render_template('dashboard.html',
                               x_column=x_column,
                               y_column=y_column,
                               graph_html=graph_html)

    except Exception as e:
        print(f"Error: {str(e)}")
        return f"Error generating chart: {str(e)}"

if __name__ == '__main__':
    app.run(debug=True)
