import yfinance as yf
import pandas as pd

def fetch_full(symbol: str) -> pd.DataFrame:
    df = yf.download(symbol, period="5y", interval="1d")

    if df.empty:
        return pd.DataFrame()

    df.reset_index(inplace=True)

    # 🔥 FIX: flatten columns if multi-index
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    return df


def fetch_incremental(symbol: str, start_date: pd.Timestamp) -> pd.DataFrame:
    df = yf.download(symbol, start=start_date)

    if df.empty:
        return pd.DataFrame()

    df.reset_index(inplace=True)

    # 🔥 FIX: flatten columns
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    return df