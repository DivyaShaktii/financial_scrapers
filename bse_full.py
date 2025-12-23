import os
import requests
import pandas as pd
import yfinance as yf
from concurrent.futures import ThreadPoolExecutor, as_completed

# ================= CONFIG =================
BSE_URL = (
    "https://api.bseindia.com/BseIndiaAPI/api/ListofScripData/w"
    "?Group=&Scripcode=&segment=Equity"
)

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json",
    "Referer": "https://www.bseindia.com/",
    "Origin": "https://www.bseindia.com"
}

OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "bse_useful_stocks.csv")

MAX_WORKERS = 8  # safe parallelism

# ================= STEP 1: FETCH BSE DATA =================
print("📥 Fetching BSE master data...")

response = requests.get(BSE_URL, headers=HEADERS, timeout=30)
response.raise_for_status()

df = pd.DataFrame(response.json())

# ================= STEP 2: FILTER USEFUL STOCKS =================
useful = df[
    (df["Segment"] == "Equity") &
    (df["Status"] == "Active")
].copy()

final_df = useful[[
    "SCRIP_CD",
    "Scrip_Name",
    "scrip_id",
    "Segment",
    "FACE_VALUE",
    "NSURL",
    "Issuer_Name",
    "Mktcap"
]].copy()

# ================= STEP 3: YAHOO FETCH FUNCTION =================
def fetch_yahoo(security_id):
    ticker = f"{security_id}.BO"
    try:
        info = yf.Ticker(ticker).info
        return {
            "Security ID": security_id,
            "Sector": info.get("sector"),
            "Industry": info.get("industry"),
            "PE": info.get("trailingPE")
        }
    except Exception:
        return {
            "Security ID": security_id,
            "Sector": None,
            "Industry": None,
            "PE": None
        }

# ================= STEP 4: PARALLEL YAHOO ENRICHMENT =================
print("⚡ Fetching Sector, Industry, PE from Yahoo (parallel)...")

results = []

with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
    futures = {
        executor.submit(fetch_yahoo, row["scrip_id"]): row["scrip_id"]
        for _, row in final_df.iterrows()
    }

    for i, future in enumerate(as_completed(futures), start=1):
        results.append(future.result())
        if i % 100 == 0:
            print(f"⏳ Yahoo processed: {i}/{len(final_df)}")

yahoo_df = pd.DataFrame(results)

# ================= STEP 5: RENAME COLUMNS =================
final_df = final_df.rename(columns={
    "SCRIP_CD": "Security Code",
    "Scrip_Name": "Issue Name",
    "scrip_id": "Security ID",
    "Segment": "Instrument",
    "FACE_VALUE": "Face Value",
    "Issuer_Name": "Issuer Name",
    "Mktcap": "Market Cap",
    "NSURL": "BSE URL"
})

# ================= STEP 6: MERGE YAHOO DATA =================
final_df = final_df.merge(yahoo_df, on="Security ID", how="left")

# ================= STEP 7: SAVE =================
final_df.to_csv(OUTPUT_FILE, index=False)

print("\n✅ BSE useful stocks with Yahoo data saved")
print(f"📁 File: {OUTPUT_FILE}")
print(f"📊 Total stocks: {len(final_df)}")
print("\nSample:")
print(final_df.head())
