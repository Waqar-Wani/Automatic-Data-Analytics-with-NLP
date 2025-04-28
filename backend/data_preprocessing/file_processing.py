import pandas as pd
from io import BytesIO

def read_file(file):
    """
    Reads the uploaded file based on its extension and returns a pandas DataFrame.
    Supports CSV, Excel (XLSX, XLS), and JSON file formats.
    """
    try:
        # Check for CSV files
        if file.filename.endswith('.csv'):
            # Read CSV with explicit dtype handling
            df = pd.read_csv(file, dtype=str)  # Read all columns as strings initially
            # Convert numeric columns to appropriate types
            for col in df.columns:
                try:
                    # Try to convert to numeric, if successful, keep the numeric type
                    df[col] = pd.to_numeric(df[col], errors='ignore')
                except:
                    # If conversion fails, keep as string
                    pass
        
        # Check for Excel files (.xls, .xlsx)
        elif file.filename.endswith(('.xls', '.xlsx')):
            in_memory_file = BytesIO(file.read())
            # Read Excel with explicit dtype handling
            df = pd.read_excel(in_memory_file, dtype=str)  # Read all columns as strings initially
            # Convert numeric columns to appropriate types
            for col in df.columns:
                try:
                    # Try to convert to numeric, if successful, keep the numeric type
                    df[col] = pd.to_numeric(df[col], errors='ignore')
                except:
                    # If conversion fails, keep as string
                    pass
        
        # Check for JSON files
        elif file.filename.endswith('.json'):
            df = pd.read_json(file)
            # Ensure all columns have proper string representation
            for col in df.columns:
                df[col] = df[col].astype(str)
        
        else:
            raise ValueError("Unsupported file type. Please upload a CSV, Excel, or JSON file.")
        
        # Ensure all column names are strings
        df.columns = df.columns.astype(str)
        
        return df

    except Exception as e:
        raise Exception(f"Error reading the file: {str(e)}")
