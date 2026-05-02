print("🚀 Script started")

import pandas as pd
import json
import os

from backend.services.extrema import detect_extrema

# 🔥 BASE PATH
BASE_DIR = os.getcwd()

DATA_DIR = os.path.join(BASE_DIR, "backend", "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "frontend", "public", "data")

os.makedirs(OUTPUT_DIR, exist_ok=True)


def normalize_date(d):
    return str(d).split(" ")[0]


def process_stock(file):
    path = os.path.join(DATA_DIR, file)
    symbol = file.replace(".parquet", "")

    print(f"➡️ Processing: {symbol}")

    df = pd.read_parquet(path)
    df = df.reset_index()

    # 🔥 CLEAN
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values("Date")
    df["Date"] = df["Date"].dt.strftime("%Y-%m-%d")

    # 🔥 EXTREMA DETECTION
    extrema = detect_extrema(df, threshold=0.02)

    # 🔥 BUILD EXTREMA MAP
    extrema_map = {}

    for e in extrema:
        date = normalize_date(e["date"])

        if date not in extrema_map:
            extrema_map[date] = {"min": None, "max": None}

        if e["type"] == "min":
            extrema_map[date]["min"] = round(float(e["price"]), 2)

        if e["type"] == "max":
            extrema_map[date]["max"] = round(float(e["price"]), 2)

    # 🔥 BUILD CHART DATA
    chart_data = []

    for _, row in df.iterrows():
        date = row["Date"]
        price = round(float(row["Close"]), 2)

        ext = extrema_map.get(date, {})

        chart_data.append({
            "date": date,
            "price": price,
            "min": ext.get("min"),
            "max": ext.get("max")
        })

    # 🔥 SAVE
    output_path = os.path.join(OUTPUT_DIR, f"{symbol}.json")

    with open(output_path, "w") as f:
        json.dump(chart_data, f)

    print(f"✅ {symbol} done")


def main():
    print("🔥 MAIN RUNNING")
    print("📂 DATA DIR:", DATA_DIR)

    files = [f for f in os.listdir(DATA_DIR) if f.endswith(".parquet")]

    print(f"📊 TOTAL FILES: {len(files)}")

    if not files:
        print("❌ No parquet files found.")
        return

    for file in files:
        process_stock(file)


if __name__ == "__main__":
    main()