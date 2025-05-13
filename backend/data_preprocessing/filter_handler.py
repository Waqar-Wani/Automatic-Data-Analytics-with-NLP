import pandas as pd
import json
import os
from typing import List, Dict, Any
from backend.data_preprocessing.data_cache import get_cache
from backend.data_preprocessing.filtered_cache import set_filtered_cache

# Define the filters file path
FILTERS_FILE = os.path.join(os.path.dirname(__file__), 'filters.json')

def load_all_filters() -> List[Dict[str, Any]]:
    """
    Load all filters from the filters file as a global list.
    Returns:
        List[Dict]: List of filter conditions
    """
    try:
        if os.path.exists(FILTERS_FILE):
            with open(FILTERS_FILE, 'r') as f:
                return json.load(f)
        return []
    except Exception:
        return []

def save_all_filters(filters: List[Dict[str, Any]]):
    """
    Save all filters to the filters file as a global list.
    Args:
        filters (List[Dict]): List of filter conditions
    """
    with open(FILTERS_FILE, 'w') as f:
        json.dump(filters, f, indent=2)

def safe_query(df: pd.DataFrame, filters: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Apply filters to a DataFrame safely.
    Args:
        df (pd.DataFrame): The input dataframe
        filters (List[Dict]): List of filter conditions
    Returns:
        pd.DataFrame: Filtered dataframe
    Raises:
        ValueError: If invalid column or operator is specified
    """
    allowed_ops = {'==', '!=', '>', '<', '>=', '<=', 'in', 'not in'}
    mask = pd.Series([True] * len(df))
    for f in filters:
        col = f.get('column')
        op = f.get('operator')
        val = f.get('value')
        if col not in df.columns:
            raise ValueError(f"Column '{col}' not found.")
        if op not in allowed_ops:
            raise ValueError(f"Operator '{op}' not allowed.")
        col_dtype = df[col].dtype
        try:
            if op in {'==', '!=', '>', '<', '>=', '<='} and not isinstance(val, list):
                if pd.api.types.is_numeric_dtype(col_dtype):
                    val = pd.to_numeric(val, errors='ignore')
                elif pd.api.types.is_datetime64_any_dtype(col_dtype):
                    val = pd.to_datetime(val, errors='ignore')
        except Exception:
            pass
        if op == '==':
            mask &= df[col] == val
        elif op == '!=':
            mask &= df[col] != val
        elif op == '>':
            mask &= df[col] > val
        elif op == '<':
            mask &= df[col] < val
        elif op == '>=':
            mask &= df[col] >= val
        elif op == '<=':
            mask &= df[col] <= val
        elif op == 'in':
            if not isinstance(val, list):
                val = [v.strip() for v in val.split(',')] if isinstance(val, str) else []
            mask &= df[col].isin(val)
        elif op == 'not in':
            if not isinstance(val, list):
                val = [v.strip() for v in val.split(',')] if isinstance(val, str) else []
            mask &= ~df[col].isin(val)
    return df[mask]

def read_filter_file(file) -> List[Dict[str, Any]]:
    """
    Read and parse a filter file.
    
    Args:
        file: File object containing the filter configuration
        
    Returns:
        List[Dict]: List of filter conditions
        
    Raises:
        ValueError: If file format is invalid
    """
    try:
        content = file.read().decode('utf-8')
        filters = json.loads(content)
        
        # Save the filter file
        if hasattr(file, 'filename'):
            dataset_id = file.filename.split('_')[0]  # Extract dataset ID from filename
            all_filters = load_all_filters()
            
            # Append new filters to existing ones
            all_filters.extend(filters)
            
            save_all_filters(all_filters)
            
        return filters
    except json.JSONDecodeError:
        raise ValueError("Invalid JSON format in filter file")
    except Exception as e:
        raise ValueError(f"Error reading filter file: {str(e)}")

def apply_filters(df: pd.DataFrame, filter_file) -> pd.DataFrame:
    """
    Apply filters from a file to a DataFrame.
    
    Args:
        df (pd.DataFrame): The input dataframe
        filter_file: File object containing the filter configuration
        
    Returns:
        pd.DataFrame: Filtered dataframe
        
    Raises:
        ValueError: If filter application fails
    """
    try:
        filters = read_filter_file(filter_file)
        return safe_query(df, filters)
    except Exception as e:
        raise ValueError(f"Error applying filters: {str(e)}")

def get_global_filters() -> List[Dict[str, Any]]:
    """
    Get all global filters (list of filter conditions).
    Returns:
        List[Dict]: List of filter conditions
    """
    return load_all_filters()

def clear_all_filters():
    """
    Clear all filters (global).
    """
    save_all_filters([])

def update_filtered_cache(temp_id):
    """
    Update the filtered cache for a given temp_id by applying current filters to the original dataset.
    """
    df = get_cache().get(temp_id)
    filters = get_global_filters()
    if df is not None:
        filtered_df = safe_query(df, filters) if filters else df
        set_filtered_cache(temp_id, filtered_df) 