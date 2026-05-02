import pandas as pd
import os

def file_exists(path):
    return os.path.exists(path)

def read_parquet(path):
    return pd.read_parquet(path)

def write_parquet(df, path):
    df.to_parquet(path, index=False)