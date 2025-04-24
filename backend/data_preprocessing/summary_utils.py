def generate_overview(df):
    return {
        "Number of Columns": df.shape[1],
        "Number of Rows": df.shape[0],
        "Column Types": df.dtypes.apply(lambda x: str(x)).to_dict()
    }
