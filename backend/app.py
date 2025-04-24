import pandas as pd
from flask import Flask, render_template, request
from io import BytesIO

app = Flask(__name__)

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

    # Convert to HTML table
    preview = df.head().to_html(classes='table table-striped')
    return render_template('preview.html', table=preview)

if __name__ == '__main__':
    app.run(debug=True)
