import os
import pandas as pd
from datetime import timedelta
from backend.config import DATA_DIR
from backend.services.data_fetcher import fetch_full, fetch_incremental
from backend.utils.file_utils import read_parquet, write_parquet, file_exists

def update_stock(symbol):
    filename = symbol.replace(".NS", "").replace(" ", "_")
    path = os.path.join(DATA_DIR, f"{filename}.parquet")

    # ---------- FIRST RUN ----------
    if not file_exists(path):
        df = fetch_full(symbol)

        if df.empty:
            print(f"[ERROR] {symbol} returned no data")
            return

        # Ensure Date column exists
        if "Date" not in df.columns:
            df.reset_index(inplace=True)

        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

        write_parquet(df, path)
        print(f"[INIT] {symbol}")
        return

    # ---------- INCREMENTAL UPDATE ----------
    df_old = read_parquet(path)

    # Ensure Date column exists
    if "Date" not in df_old.columns:
        if df_old.index.name == "Date":
            df_old.reset_index(inplace=True)
        else:
            raise ValueError(f"{symbol}: No Date column in stored file")

    df_old["Date"] = pd.to_datetime(df_old["Date"], errors="coerce")
    df_old = df_old.dropna(subset=["Date"])

    last_date = df_old["Date"].max()

    # Fetch new data
    df_new = fetch_incremental(symbol, last_date + timedelta(days=1))

    if df_new.empty:
        print(f"[SKIP] {symbol} (no new data)")
        return

    # Ensure Date column in new data
    if "Date" not in df_new.columns:
        df_new.reset_index(inplace=True)

    df_new["Date"] = pd.to_datetime(df_new["Date"], errors="coerce")
    df_new = df_new.dropna(subset=["Date"])

    # Merge
    df = pd.concat([df_old, df_new], ignore_index=True)

    # Remove duplicates + sort
    df = df.drop_duplicates(subset="Date")
    df = df.sort_values("Date")

    write_parquet(df, path)
    print(f"[UPDATED] {symbol}")
    print(f"PATH USED: {path}")