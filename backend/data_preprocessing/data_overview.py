import pandas as pd
import numpy as np
from backend.utils.openrouter_client import call_openrouter_api
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

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
        'Dataset Summary': generate_dataset_summary(df, file_name)
    }

    # Column Information
    for col in df.columns:
        overview['Column Information'][col] = {
            'Type': str(df[col].dtype),
            'Unique Values': df[col].nunique(),
            'Missing Values': int(df[col].isnull().sum())
        }

    # Missing Values Summary
    missing_values = df.isnull().sum()
    total_missing = int(missing_values.sum())
    columns_with_missing = {col: int(count) for col, count in missing_values[missing_values > 0].items()}
    if total_missing == 0:
        missing_values_str = "No missing values."
    else:
        missing_cols_str = ", ".join([f"{col}: {count}" for col, count in columns_with_missing.items()])
        missing_values_str = f"Total missing values: {total_missing}. Columns with missing values: {missing_cols_str}"
    overview['Missing Values'] = missing_values_str

    return overview

def generate_dataset_summary(df, file_name=None):
    """
    Generate a basic summary of the dataset by sending a prompt and the file content to the AI model.
    """
    try:
        # Convert the first 1000 rows to CSV string for context (limit size for prompt)
        file_content = df.head(4).to_csv(index=False)
        prompt = "Give a short, easy-to-understand summary of what info this data holds—keep it under 20 words"
        messages = [
            {"role": "system", "content": "You are a helpful AI assistant. You analyze uploaded datasets and provide concise summaries."},
            {"role": "user", "content": f"File: {file_name if file_name else 'uploaded_data.csv'}\n\nContent:\n{file_content}\n\nUser question: {prompt}"}
        ]
        response = call_openrouter_api(messages)
        return response
    except Exception as e:
        error_msg = str(e)
        if "Rate limit exceeded" in error_msg:
            return """
                <div class="alert alert-warning" role="alert">
                    <h4 class="alert-heading">AI Model Limit Reached</h4>
                    <p>The AI model has reached its daily usage limit.</p>
                    <hr>
                    <p class="mb-0">Please try again tomorrow or upgrade your account for more requests.</p>
                </div>
            """
        return f"<div class='alert alert-warning'>Unable to generate AI summary: {error_msg}</div>"
