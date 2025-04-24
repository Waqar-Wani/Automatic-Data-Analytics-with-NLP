import pandas as pd
import re
# backend/data_preprocessing/data_utils.py

def handle_missing_values(df):
    # Simple handling: drop rows with any NaNs
    return df.dropna()

def clean_column_name(name):
    # Function for cleaning column names
    return name.replace('_', ' ').title().replace(' ', '')

def normalize_column_names(df):
    # Step 1: Convert all column names to lowercase
    df.columns = df.columns.str.lower()

    # Step 2: Replace underscores with spaces
    df.columns = df.columns.str.replace('_', ' ')

    # Step 3: Capitalize the first letter of each word, maintaining spaces
    df.columns = [' '.join([word.capitalize() for word in col.split()]) for col in df.columns]

    # Step 4: Ensure that single letters like 'i d' are fixed to 'Id'
    df.columns = [re.sub(r'\b([a-zA-Z]) (\b[a-zA-Z])\b', r'\1\2', col) for col in df.columns]

    # Step 5: Remove any extra leading or trailing spaces
    df.columns = df.columns.str.strip()

    return df