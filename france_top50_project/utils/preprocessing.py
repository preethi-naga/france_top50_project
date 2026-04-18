import pandas as pd


def load_and_clean_data(file_path):
    df = pd.read_csv(file_path)

    df['date'] = pd.to_datetime(df['date'])
    df['duration_min'] = df['duration_ms'] / 60000
    df['album_type'] = df['album_type'].str.lower().str.strip()

    return df