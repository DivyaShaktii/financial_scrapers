import pandas as pd
import requests
import sqlite3
from io import BytesIO
from datetime import datetime

def fetch_bhavcopy():
    # Returns dictionary: { "NIFTY AUTO": 55.2 }
    print("   [Volume] Fetching Delivery %...")
    today = datetime.now()
    date_str = today.strftime("%d%m%Y")
    
    # If running after market hours, use today. If morning, use yesterday? 
    # For safety, let's assume we run this in evening.
    url = f"https://nsearchives.nseindia.com/products/content/sec_bhavdata_full_{date_str}.csv"
    
    headers = {'User-Agent': 'Mozilla/5.0'}
    delivery_map = {}

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 404:
            print("   ⚠️ Bhavcopy not found for today (Market might be open or holiday).")
            return {}

        df = pd.read_csv(BytesIO(response.content), skipinitialspace=True)
        df.columns = [c.strip() for c in df.columns]
        if 'SERIES' in df.columns: df = df[df['SERIES'] == 'EQ']
        
        # Clean numeric
        target_col = 'DELIV_PER'
        if target_col not in df.columns: return {}
        
        df[target_col] = pd.to_numeric(df[target_col].astype(str).str.strip(), errors='coerce')
        
        # Map
        conn = sqlite3.connect('sector_scorer.db')
        cur = conn.cursor()
        cur.execute("SELECT sector_name, top_stocks FROM sectors_master")
        
        for sec_name, stock_str in cur.fetchall():
            stock_list = [s.strip() for s in stock_str.split(',')]
            subset = df[df['SYMBOL'].isin(stock_list)]
            if not subset.empty:
                delivery_map[sec_name] = subset[target_col].mean()
        
        conn.close()
    except: pass
    
    return delivery_map

if __name__ == "__main__":
    print(fetch_bhavcopy())