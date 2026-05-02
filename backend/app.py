from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import os
import pandas as pd

from backend.config import DATA_DIR
from backend.services.extrema import detect_extrema

app = FastAPI()

# 🔵 CORS (for React frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==============================
# 🔥 GET STOCK DATA + EXTREMA
# ==============================
@app.get("/stock/{symbol}")
def get_stock(symbol: str, range: str = Query("5Y")):

    filename = symbol.replace(".NS", "")
    path = os.path.join(DATA_DIR, f"{filename}.parquet")

    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail=f"{symbol} file not found")

    try:
        df = pd.read_parquet(path)

        # 🔵 Clean column names
        df.columns = [c.strip() for c in df.columns]

        # 🔵 Ensure Date column exists
        if "Date" not in df.columns:
            df.reset_index(inplace=True)

        df["Date"] = pd.to_datetime(df["Date"])
        df = df.sort_values("Date").reset_index(drop=True)

        if "Close" not in df.columns:
            raise HTTPException(status_code=500, detail="Close column missing")

        # 🔵 Keep only required columns
        df = df[["Date", "Close"]]

        # ==============================
        # 🔥 RANGE FILTER (CRITICAL)
        # ==============================
        last_date = df["Date"].max()

        days_map = {
            "1D": 1,
            "5D": 5,
            "1M": 30,
            "6M": 180,
            "1Y": 365,
            "5Y": 1825,
        }

        days = days_map.get(range, None)

        if days:
            cutoff = last_date - pd.Timedelta(days=days)
            df = df[df["Date"] >= cutoff].reset_index(drop=True)

        # ==============================
        # 🔥 DETECT EXTREMA ON FILTERED DATA
        # ==============================
        extrema = detect_extrema(df, threshold=0.10)

        # 🔵 Normalize extrema dates
        for e in extrema:
            e["date"] = pd.to_datetime(e["date"]).strftime("%Y-%m-%d")

        # 🔵 Convert price data dates
        df["Date"] = df["Date"].dt.strftime("%Y-%m-%d")

        # 🔍 Debug logs (optional)
        print(f"{symbol} | Range: {range}")
        print(f"Data points: {len(df)}")
        print(f"Extrema found: {len(extrema)}")

        return {
            "prices": df.to_dict(orient="records"),
            "extrema": extrema
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==============================
# 🔵 GET ALL STOCK SYMBOLS
# ==============================
@app.get("/stocks")
def get_stocks():
    files = os.listdir(DATA_DIR)

    symbols = [
        f.replace(".parquet", "") + ".NS"
        for f in files
        if f.endswith(".parquet")
    ]

    return {"stocks": symbols}