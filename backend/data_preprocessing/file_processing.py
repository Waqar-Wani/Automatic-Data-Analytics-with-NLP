import pandas as pd
from io import BytesIO

def read_file(file):
    """
    Reads the uploaded file based on its extension and returns a pandas DataFrame.
    Supports CSV, Excel (XLSX, XLS), JSON, and Parquet file formats.
    """
    try:
        # Check for CSV files
        if file.filename.endswith('.csv'):
            df = pd.read_csv(file)
        
        # Check for Excel files (.xls, .xlsx)
        elif file.filename.endswith(('.xls', '.xlsx')):
            in_memory_file = BytesIO(file.read())
            df = pd.read_excel(in_memory_file)
        
        # Check for JSON files
        elif file.filename.endswith('.json'):
            df = pd.read_json(file)
        
        # Check for Parquet files (.parquet)
        elif file.filename.endswith('.parquet'):
            in_memory_file = BytesIO(file.read())
            df = pd.read_parquet(in_memory_file)
        
        # Check for other possible formats, like TSV (Tab Separated Values)
        elif file.filename.endswith('.tsv'):
            df = pd.read_csv(file, sep='\t')
        
        # Add support for other formats as required (e.g., Feather, HDF5, etc.)
        else:
            raise ValueError("Unsupported file type")
        
        return df

    except Exception as e:
        raise Exception(f"Error reading the file: {str(e)}")
