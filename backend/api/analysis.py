import pandas as pd

REQUIRED_COLUMNS = {'Equipment Name', 'Type', 'Flowrate', 'Pressure', 'Temperature'}

def analyze_equipment_csv(path_or_buffer):
    """
    Accepts a filepath or file-like buffer and returns (summary_dict, df)
    """
    try:
        df = pd.read_csv(path_or_buffer)
    except Exception as e:
        raise ValueError(f"Could not read CSV: {str(e)}")

    if not REQUIRED_COLUMNS.issubset(set(df.columns)):
        missing = REQUIRED_COLUMNS - set(df.columns)
        raise ValueError(f"Missing required columns: {', '.join(missing)}")

    for col in ['Flowrate', 'Pressure', 'Temperature']:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # drop rows with NaN in numeric columns
    df_clean = df.dropna(subset=['Flowrate', 'Pressure', 'Temperature'])

    summary = {
        "total_equipment": int(len(df_clean)),
        "avg_flowrate": float(df_clean['Flowrate'].mean()) if not df_clean.empty else 0.0,
        "avg_pressure": float(df_clean['Pressure'].mean()) if not df_clean.empty else 0.0,
        "avg_temperature": float(df_clean['Temperature'].mean()) if not df_clean.empty else 0.0,
        "type_distribution": df_clean['Type'].value_counts().to_dict()
    }
    return summary, df_clean
