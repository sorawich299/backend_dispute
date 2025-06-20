import pandas as pd

def process_excel(file_path):
    data = pd.read_excel(file_path, sheet_name='Worksheet', header=1).fillna("")
    raw = pd.read_excel(file_path, sheet_name='Worksheet', header=None)
    cell_a1 = raw.iloc[0, 0] if pd.notna(raw.iloc[0, 0]) else ""
    cell_b1 = raw.iloc[0, 1] if pd.notna(raw.iloc[0, 1]) else ""
    return {"cell_a1": cell_a1, "cell_b1": cell_b1, "data_table": data}