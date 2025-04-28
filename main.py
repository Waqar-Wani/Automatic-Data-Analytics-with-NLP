import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

import pandas as pd
from flask import Flask, render_template, request, jsonify, send_from_directory
import plotly.express as px
from dotenv import load_dotenv
import PyPDF2

from backend.data_preprocessing.file_processing import read_file
from backend.data_preprocessing.data_cleaning import handle_missing_values, normalize_column_names
from backend.data_preprocessing.data_overview import generate_overview
from backend.nlp_routes import nlp_bp

# Initialize Flask app
app = Flask(__name__, static_folder=os.path.join('backend', 'static'), template_folder=os.path.join('backend', 'templates'))

# In-memory cache (for temporary session-like storage)
cache = {}

# Enable CORS for all routes
from flask_cors import CORS, cross_origin
CORS(app)

load_dotenv()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['GET'])
def upload_form():
    return render_template('upload.html')

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

        if not all([x_column, y_column, temp_id]):
            return "Missing required parameters. Please select both X and Y columns."

        df = cache.get(temp_id)
        if df is None:
            return "Session expired or dataset not found."

        # Validate that columns exist in the dataframe
        if x_column not in df.columns or y_column not in df.columns:
            return f"Selected columns not found in dataset. Available columns: {', '.join(df.columns)}"

        # Handle any NaN/undefined values in the selected columns
        df = df.dropna(subset=[x_column, y_column])

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

@app.route('/data/<temp_id>')
@cross_origin()
def get_data(temp_id):
    df = cache.get(temp_id)
    if df is None:
        return jsonify({
            'draw': int(request.args.get('draw', 1)),
            'recordsTotal': 0,
            'recordsFiltered': 0,
            'data': []
        })
    try:
        draw = int(request.args.get('draw', 1))
        start = int(request.args.get('start', 0))
        length = int(request.args.get('length', 10))
        search_value = request.args.get('search[value]', '')

        # Filtering
        if search_value:
            df_filtered = df[df.apply(lambda row: row.astype(str).str.contains(search_value, case=False, na=False).any(), axis=1)]
        else:
            df_filtered = df

        # Sorting
        order_col_index = request.args.get('order[0][column]')
        order_dir = request.args.get('order[0][dir]', 'asc')
        if order_col_index is not None:
            order_col_index = int(order_col_index)
            columns = list(df_filtered.columns)
            if 0 <= order_col_index < len(columns):
                order_col = columns[order_col_index]
                df_filtered = df_filtered.sort_values(by=order_col, ascending=(order_dir == 'asc'))

        # Paging
        data_page = df_filtered.iloc[start:start+length]

        return jsonify({
            'draw': draw,
            'recordsTotal': len(df),
            'recordsFiltered': len(df_filtered),
            'data': data_page.to_dict(orient='records')
        })
    except Exception as e:
        return jsonify({
            'draw': 1,
            'recordsTotal': 0,
            'recordsFiltered': 0,
            'data': [],
            'error': str(e)
        })

@app.route('/data-source')
def data_source():
    return render_template('data_source.html')

@app.route('/about-project')
def about_project():
    pdf_path = os.path.join('Datasets', 'AI Powered Data Analysis with NLP.pdf')
    pdf_text = ""
    try:
        with open(pdf_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                pdf_text += page.extract_text() + "\n"
    except Exception as e:
        pdf_text = f"Could not extract PDF content: {e}"
    return render_template('about_project.html', pdf_text=pdf_text)

@app.route('/datasets/<filename>')
def serve_dataset(filename):
    return send_from_directory('Datasets', filename)

app.register_blueprint(nlp_bp)

if __name__ == '__main__':
    app.run(debug=True)
