import pandas as pd
import numpy as np

def generate_overview(df, file_name, data_type, file_format):
    """
    Generate a comprehensive overview of the dataset.
    
    Args:
        df (pd.DataFrame): The input dataframe
        file_name (str): Name of the uploaded file
        data_type (str): Type of data (e.g., 'Uploaded')
        file_format (str): Format of the file (e.g., 'csv', 'xls/xlsx')
        
    Returns:
        dict: Dictionary containing overview information
    """
    overview = {
        'File Name': file_name,
        'Data Type': data_type,
        'File Format': file_format,
        'Number of Rows': len(df),
        'Number of Columns': len(df.columns),
        'Column Information': {},
        'Missing Values': {},
        'Data Types': {},
        'Dataset Summary': generate_dataset_summary(df)
    }

    # Column Information
    for col in df.columns:
        overview['Column Information'][col] = {
            'Type': str(df[col].dtype),
            'Unique Values': df[col].nunique(),
            'Missing Values': int(df[col].isnull().sum())  # Convert to int
        }

    # Missing Values Summary
    missing_values = df.isnull().sum()
    total_missing = int(missing_values.sum())  # Convert to int
    columns_with_missing = {col: int(count) for col, count in missing_values[missing_values > 0].items()}  # Convert to int
    
    overview['Missing Values'] = {
        'Total Missing Values': total_missing,
        'Columns with Missing Values': columns_with_missing
    }

    # Data Types Summary
    data_types = df.dtypes.value_counts().to_dict()
    overview['Data Types'] = {str(k): int(v) for k, v in data_types.items()}

    return overview

def generate_dataset_summary(df):
    """
    Generate a basic summary of the dataset (AI feature temporarily disabled).
    """
    return "AI Generated summary is still in development"
