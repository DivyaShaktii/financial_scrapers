import os
import time
import requests
import pandas as pd
import yfinance as yf
from io import StringIO

# ================= CONFIG =================
BASE_URL = "https://www.nseindia.com"
PREOPEN_URL = f"{BASE_URL}/api/market-data-pre-open?key=ALL"

EQUITY_CSV_URLS = [
    "https://www.nseindia.com/content/equities/EQUITY_L.csv",
    "https://archives.nseindia.com/content/equities/EQUITY_L.csv"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept": "application/json",
    "Referer": "https://www.nseindia.com/"
}

OUTPUT_DIR = "output"
OUTPUT_CSV = f"{OUTPUT_DIR}/nse_equities_master_full.csv"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ================= STEP 1: FETCH NSE SYMBOLS =================
def fetch_nse_symbols():
    session = requests.Session()
    session.headers.update(HEADERS)

    session.get(f"{BASE_URL}/api/marketStatus", timeout=10)
    time.sleep(1)

    r = session.get(PREOPEN_URL, timeout=15)
    r.raise_for_status()

    symbols = set()
    for item in r.json().get("data", []):
        sym = item.get("metadata", {}).get("symbol")
        if sym:
            symbols.add(sym)

    df = pd.DataFrame({"symbol": sorted(symbols)})
    print(f"✔ NSE symbols fetched: {len(df)}")
    return df

# ================= STEP 2: LOAD NSE EQUITY MASTER =================
def load_equity_master():
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0",
        "Accept": "text/csv",
        "Referer": "https://www.nseindia.com/"
    })

    session.get("https://www.nseindia.com/api/marketStatus", timeout=10)
    time.sleep(1)

    for url in EQUITY_CSV_URLS:
        try:
            r = session.get(url, timeout=20)
            r.raise_for_status()

            df = pd.read_csv(StringIO(r.text))
            df.columns = df.columns.str.strip()
            df = df[df["SERIES"] == "EQ"]

            df = df.rename(columns={
                "SYMBOL": "symbol",
                "NAME OF COMPANY": "companyName",
                "DATE OF LISTING": "listingDate"
            })

            print("✔ NSE Equity master loaded")
            return df[["symbol", "companyName", "listingDate"]]

        except Exception:
            print(f"⚠️ Failed loading from {url}, trying next...")

    print("❌ NSE Equity master not available")
    return pd.DataFrame(columns=["symbol", "companyName", "listingDate"])

# ================= STEP 3: YAHOO FETCH =================
def yahoo_fetch(symbol):
    try:
        info = yf.Ticker(symbol + ".NS").info

        listing_date = None
        if info.get("firstTradeDateEpochUtc"):
            listing_date = (
                pd.to_datetime(
                    info["firstTradeDateEpochUtc"], unit="s"
                )
                .date()
                .isoformat()
            )

        return {
            "companyName": info.get("longName"),
            "listingDate": listing_date,
            "pe": info.get("trailingPE"),
            "market_cap": info.get("marketCap"),
            "sector": info.get("sector")
        }
    except Exception:
        return {}

# ================= STEP 4: FULL PIPELINE =================
def run():
    symbols_df = fetch_nse_symbols()
    equity_master = load_equity_master()

    # Merge symbols + NSE equity master
    df = symbols_df.merge(equity_master, on="symbol", how="left")

    print("🔹 Enriching from Yahoo Finance (full rebuild)...")

    rows = []

    for i, row in df.iterrows():
        y = yahoo_fetch(row["symbol"])

        rows.append({
            "symbol": row["symbol"],
            "companyName": row["companyName"] or y.get("companyName"),
            "listingDate": row["listingDate"] or y.get("listingDate"),
            "pe": y.get("pe"),
            "market_cap": y.get("market_cap"),
            "sector": y.get("sector")
        })

        if (i + 1) % 25 == 0:
            print(f"⏳ Progress: {i + 1}/{len(df)}")

    final_df = pd.DataFrame(rows)

    final_df.to_csv(OUTPUT_CSV, index=False)

    print("\n✅ NSE FULL master regenerated")
    print(f"📁 File: {OUTPUT_CSV}")
    print(f"📊 Total symbols: {len(final_df)}")
    print("\nSample:")
    print(final_df.head())

# ================= RUN =================
if __name__ == "__main__":
    run()
