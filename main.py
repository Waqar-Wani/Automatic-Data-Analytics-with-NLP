import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

import pandas as pd
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from flask_cors import CORS, cross_origin

from backend.data_preprocessing.file_processing import read_file
from backend.data_preprocessing.data_cleaning import handle_missing_values, normalize_column_names
from backend.data_preprocessing.data_overview import generate_overview
from backend.data_preprocessing.data_cache import get_cache, set_cache
from backend.data_visualization.chart_generation import generate_chart
from backend.nlp_routes import nlp_bp
from backend.data_preprocessing.filter_handler import apply_filters, safe_query, get_global_filters, clear_all_filters, update_filtered_cache
from backend.data_preprocessing.filtered_cache import get_filtered_cache, set_filtered_cache, clear_filtered_cache

# Initialize Flask app
app = Flask(__name__, static_folder=os.path.join('backend', 'static'), template_folder=os.path.join('backend', 'templates'))

# Enable CORS for all routes
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
        file_format = 'csv' if file.filename.endswith('.csv') else 'xls/xlsx' if file.filename.endswith(('.xls', '.xlsx')) else 'json'
        data_type = 'Uploaded'

        df = read_file(file)
        df = handle_missing_values(df)
        df = normalize_column_names(df)

        # Clear all filters and filtered cache after each new upload
        clear_all_filters()
        clear_filtered_cache()

        # Overview (handles all AI summary and error logic)
        overview = generate_overview(df, file_name, data_type, file_format)
        overview['columns'] = df.columns.tolist()
        overview['numeric_columns'] = df.select_dtypes(include='number').columns.tolist()

        # Store DataFrame temporarily
        temp_id = str(len(get_cache()) + 1)
        set_cache(temp_id, df)
        update_filtered_cache(temp_id)

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
        error_msg = str(e)
        return f"Error reading file: {error_msg}"

@app.route('/dashboard', methods=['POST'])
def dashboard():
    try:
        x_column = request.form.get('x_column')
        # Support multiple Y columns
        y_column = request.form.getlist('y_column')
        chart_type = request.form.get('chart_type', 'bar')  # Default to bar chart
        temp_id = request.form.get('temp_path')
        color_column = request.form.get('color_column')  # New: group by
        sort_order = request.form.get('sort_order', 'asc')
        custom_order = request.form.get('custom_order', None)

        if not all([x_column, y_column, temp_id]) or len(y_column) == 0:
            return "Missing required parameters. Please select both X and Y columns."

        # Use filtered cache for graph generation
        df = get_filtered_cache().get(temp_id)
        if df is None:
            return "Session expired or dataset not found."

        # Validate that columns exist in the dataframe
        if x_column not in df.columns or any(col not in df.columns for col in y_column):
            return f"Selected columns not found in dataset. Available columns: {', '.join(df.columns)}"

        # If only one Y column is selected, use as string for compatibility
        y_column_arg = y_column if len(y_column) > 1 else y_column[0]

        # Generate chart using the chart_generation module
        fig = generate_chart(df, x_column, y_column_arg, chart_type, color_column, sort_order, custom_order)
        graph_html = fig.to_html(full_html=False)

        return render_template('dashboard.html',
                               x_column=x_column,
                               y_column=y_column,
                               chart_type=chart_type,
                               color_column=color_column,
                               sort_order=sort_order,
                               custom_order=custom_order,
                               graph_html=graph_html)

    except Exception as e:
        print(f"Error: {str(e)}")
        return f"Error generating chart: {str(e)}"

@app.route('/data/<temp_id>')
@cross_origin()
def get_data(temp_id):
    df = get_filtered_cache().get(temp_id)
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

        # Filtering (search)
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

        # Convert data to list of dictionaries, handling NaN values
        data = []
        for _, row in data_page.iterrows():
            row_dict = {}
            for col in df.columns:
                val = row[col]
                # Convert NaN to None for proper JSON serialization
                if pd.isna(val):
                    val = None
                row_dict[col] = val
            data.append(row_dict)

        return jsonify({
            'draw': draw,
            'recordsTotal': len(df),
            'recordsFiltered': len(df_filtered),
            'data': data
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
    return render_template('about_project.html')

@app.route('/apply_filter_file', methods=['POST'])
def apply_filter_file():
    try:
        filter_file = request.files['filter_file']
        temp_id = request.form.get('temp_id')
        
        if not filter_file or not temp_id:
            return jsonify({"error": "Missing filter file or dataset ID"}), 400
            
        # Get the dataset from cache
        df = get_cache().get(temp_id)
        if df is None:
            return jsonify({"error": "Dataset not found"}), 404
            
        # Apply filters
        filtered_df = apply_filters(df, filter_file)
        
        # Update the cache with filtered data
        set_cache(temp_id, filtered_df)
        
        # Return success response
        return jsonify({
            "message": "Filter applied successfully",
            "total_rows": len(filtered_df),
            "preview": filtered_df.head(10).to_dict(orient='records')
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 400

app.register_blueprint(nlp_bp)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)