import pandas as pd
import numpy as np
from backend.utils.openrouter_client import call_openrouter_api
import os
from dotenv import load_dotenv
import re

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
        'Dataset Summary': generate_dataset_summary(df, file_name),
        'Automated Insights': generate_automated_insights(df, file_name)
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
        # Convert the first 3 rows to CSV string for context (limit size for prompt)
        file_content = df.head(3).to_csv(index=False)
        prompt = "Give a short, easy-to-understand summary of what info this data holds—keep it under 20 words"
        messages = [
            {"role": "system", "content": "You are a helpful AI assistant. You analyze uploaded datasets and provide concise summaries."},
            {"role": "user", "content": f"File: {file_name if file_name else 'uploaded_data.csv'}\n\nContent:\n{file_content}\n\nUser question: {prompt}"}
        ]
        from backend.utils.openrouter_client import call_openrouter_api
        response = call_openrouter_api(messages)
        return response
    except Exception as e:
        error_msg = str(e)
        if "Rate limit exceeded" in error_msg:
            return """
                <div class=\"alert alert-warning\" role=\"alert\">
                    <h4 class=\"alert-heading\">AI Model Limit Reached</h4>
                    <p>The AI model has reached its daily usage limit.</p>
                    <hr>
                    <p class=\"mb-0\">Please try again tomorrow or upgrade your account for more requests.</p>
                </div>
            """
        if "401" in error_msg or "No auth credentials found" in error_msg:
            return """
                <div class='alert alert-warning' role='alert'>
                    <h4 class='alert-heading'>AI Credentials Exhausted</h4>
                    <ul>
                        <li>Please try again after 24 hours, or insert a new API key in your settings/environment.</li>
                    </ul>
                    <hr>                    
                </div>
            """
        return f"<div class='alert alert-warning'>Unable to generate AI summary: {error_msg}</div>"

def generate_data_summary(df):
    summary_lines = []
    summary_lines.append(f"Rows: {len(df)}, Columns: {len(df.columns)}")
    summary_lines.append("\nColumn Details:")
    for col in df.columns:
        col_type = str(df[col].dtype)
        unique = df[col].nunique()
        missing = df[col].isnull().sum()
        line = f"- {col} (type: {col_type}, unique: {unique}, missing: {missing})"
        # Numeric stats
        if pd.api.types.is_numeric_dtype(df[col]):
            desc = df[col].describe()
            line += f", min: {desc.get('min', 'NA')}, max: {desc.get('max', 'NA')}, mean: {desc.get('mean', 'NA'):.2f}, median: {df[col].median():.2f}, std: {desc.get('std', 'NA'):.2f}"
        # Categorical stats
        elif pd.api.types.is_object_dtype(df[col]) or pd.api.types.is_categorical_dtype(df[col]):
            top_vals = df[col].value_counts().head(3)
            top_vals_str = ", ".join([f"{idx} ({val})" for idx, val in top_vals.items()])
            line += f", top: {top_vals_str}"
        summary_lines.append(line)
    return "\n".join(summary_lines)

def generate_automated_insights(df, file_name=None):
    """
    Generate automated insights for the dataset using the AI model.
    """
    try:
        # Use a concise but informative summary for the AI
        data_summary = generate_data_summary(df)
        prompt = (
            "You are a data analytics expert. Given the following dataset summary, "
            "generate 4 concise short, actionable insights about the data. "
            "Use bullet points. Avoid repeating the summary."
        )
        messages = [
            {"role": "system", "content": "You are a helpful AI assistant for data analytics."},
            {"role": "user", "content": f"File: {file_name if file_name else 'uploaded_data.csv'}\n\nSummary:\n{data_summary}\n\nUser question: {prompt}"}
        ]
        from backend.utils.openrouter_client import call_openrouter_api
        response = call_openrouter_api(messages, max_tokens=180)
        # Clean up response: remove code blocks if present
        import re
        match = re.search(r'```(?:[a-zA-Z]+)?\s*([\s\S]+?)\s*```', response)
        if match:
            response = match.group(1).strip()
        return response
    except Exception as e:
        error_msg = str(e)
        if "Rate limit exceeded" in error_msg:
            return """
                <div class=\"alert alert-warning\" role=\"alert\">
                    <h4 class=\"alert-heading\">AI Model Limit Reached</h4>
                    <p>The AI model has reached its daily usage limit.</p>
                    <hr>
                    <p class=\"mb-0\">Please try again tomorrow or upgrade your account for more requests.</p>
                </div>
            """
        if "401" in error_msg or "No auth credentials found" in error_msg:
            return """
                <div class='alert alert-warning' role='alert'>
                    <h4 class='alert-heading'>AI Credentials Exhausted</h4>
                   <ul>
                        <li>Please try again after 24 hours, or insert a new API key in your settings/environment.</li>
                    </ul>
                </div>
            """
        return f"<div class='alert alert-warning'>Unable to generate AI insights: {error_msg}</div>"

def get_available_chart_types():
    # List of chart types supported in your project (from preview.html)
    return [
        'bar', 'line', 'scatter', 'pie', 'histogram', 'box', 'heatmap',
        'area', 'bubble', 'donut', 'stacked_bar', 'horizontal_bar', 'violin',
        'treemap', 'sunburst', 'funnel', 'waterfall',
        'contour', 'density_heatmap', 'polar', 'radar',
        'parallel_coordinates', 'parallel_categories',
        'scatter_3d', 'surface_3d', 'line_3d', 'mesh_3d',
        'wordcloud'
    ]

def suggest_charts(df):
    suggestions = []
    available = set(get_available_chart_types())
    num_cols = df.select_dtypes(include='number').columns.tolist()
    cat_cols = [col for col in df.select_dtypes(include='object').columns if df[col].nunique() < 15]
    datetime_cols = df.select_dtypes(include=['datetime', 'datetime64']).columns.tolist()

    # Bar/Box/Violin for categorical + numeric
    for num in num_cols:
        for cat in cat_cols:
            if 'bar' in available:
                suggestions.append({
                    "chart_type": "bar",
                    "x_axis": cat,
                    "y_axis": num,
                    "explanation": f"Compare {num} across {cat} categories using a bar chart."
                })
            if 'box' in available:
                suggestions.append({
                    "chart_type": "box",
                    "x_axis": cat,
                    "y_axis": num,
                    "explanation": f"Show distribution of {num} for each {cat} using a box plot."
                })
            if 'violin' in available:
                suggestions.append({
                    "chart_type": "violin",
                    "x_axis": cat,
                    "y_axis": num,
                    "explanation": f"Show distribution of {num} for each {cat} using a violin plot."
                })

    # Scatter/Line for numeric + numeric
    for i, col1 in enumerate(num_cols):
        for col2 in num_cols[i+1:]:
            if 'scatter' in available:
                suggestions.append({
                    "chart_type": "scatter",
                    "x_axis": col1,
                    "y_axis": col2,
                    "explanation": f"Visualize the relationship between {col1} and {col2} using a scatter plot."
                })
            if 'line' in available:
                suggestions.append({
                    "chart_type": "line",
                    "x_axis": col1,
                    "y_axis": col2,
                    "explanation": f"Show trend between {col1} and {col2} using a line chart."
                })

    # Line for datetime + numeric
    for dt in datetime_cols:
        for num in num_cols:
            if 'line' in available:
                suggestions.append({
                    "chart_type": "line",
                    "x_axis": dt,
                    "y_axis": num,
                    "explanation": f"Show how {num} changes over time ({dt}) using a line chart."
                })

    # Word cloud for text columns
    for col in df.select_dtypes(include='object').columns:
        if df[col].str.len().mean() > 15 and 'wordcloud' in available:
            suggestions.append({
                "chart_type": "wordcloud",
                "x_axis": col,
                "y_axis": None,
                "explanation": f"Visualize most common words in {col} using a word cloud."
            })

    return suggestions

def generate_chart_suggestion(df, dataset_summary=None):
    available = get_available_chart_types()
    columns_info = []
    for col in df.columns:
        col_type = str(df[col].dtype)
        unique = df[col].nunique()
        columns_info.append(f"{col} ({col_type}, unique: {unique})")
    columns_str = ", ".join(columns_info)
    prompt = (
        "You are a data visualization expert. Based on the following dataset summary and technical details, "
        "suggest ONLY the most appropriate chart type names (from this list: " + ', '.join(sorted(available)) + ") for visualizing this data. "
        "Return your answer as a JSON array of chart type names only, e.g. ['bar', 'scatter']. Do not include any explanation or axis names.\n\n"
        f"Dataset summary: {dataset_summary if dataset_summary else 'N/A'}\n"
        f"Columns: {columns_str}\n"
        f"Rows: {len(df)}\n"
    )
    messages = [
        {"role": "system", "content": "You are a helpful AI assistant for data visualization."},
        {"role": "user", "content": prompt}
    ]
    from backend.utils.openrouter_client import call_openrouter_api
    try:
        response = call_openrouter_api(messages, max_tokens=80)
        import re, json
        # Extract JSON array from code block or plain text
        match = re.search(r'```json\s*(\[.*?\])\s*```', response, re.DOTALL)
        if match:
            json_str = match.group(1)
        else:
            match = re.search(r'(\[.*?\])', response, re.DOTALL)
            json_str = match.group(1) if match else None
        if json_str:
            result = json.loads(json_str)
            # Only keep chart types that are in available
            filtered = [ct for ct in result if ct in available]
            return filtered
        return []
    except Exception as e:
        return []
