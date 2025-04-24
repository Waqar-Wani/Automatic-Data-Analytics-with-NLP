def generate_overview(df, file_name, data_type, file_format):
    # Generate the overview details
    overview = {
        "Dataset File Name": file_name,
        "Data Type": data_type,
        "Data Format": file_format,
        "Columns & Rows": f"{df.shape[1]} Columns, {df.shape[0]} Rows",
        "Summary": ""  # Placeholder for now
    }
    return overview
