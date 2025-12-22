import requests
import pandas as pd
import sqlite3
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- CONFIGURATION: BROAD SECTOR MAPPING ---
# Maps Trendlyne Sector names to your Database Names
NAME_MAP = {
    "banking": "NIFTY BANK",
    "automobiles": "NIFTY AUTO",
    "software": "NIFTY IT",
    "technology": "NIFTY IT",
    "it": "NIFTY IT",
    "fmcg": "NIFTY FMCG",
    "metal": "NIFTY METAL",
    "pharma": "NIFTY PHARMA",
    "healthcare": "NIFTY PHARMA",
    "real estate": "NIFTY REALTY",
    "realty": "NIFTY REALTY",
    "oil": "NIFTY ENERGY",
    "power": "NIFTY ENERGY",
    "energy": "NIFTY ENERGY",
    "media": "NIFTY MEDIA",
    "infrastructure": "NIFTY INFRA",
    "construction": "NIFTY INFRA",
    "public sector bank": "NIFTY PSU BANK",
    "financial services": "NIFTY FIN SERVICE"
}

def fetch_momentum_turnaround():
    print("📡 Connecting to Trendlyne API (JSON Mode)...")
    
    url = "https://trendlyne.com/equity/sector-industry-analysis/overall/full-yr-changeP/"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
        "Referer": "https://trendlyne.com/",
        "X-Requested-With": "XMLHttpRequest"
    }

    try:
        response = requests.get(url, headers=headers, verify=False)
        data = response.json()

        # 1. Navigate to Data
        rows = []
        if 'body' in data and 'sector' in data['body']:
            rows = data['body']['sector']['tableData']
        else:
            print("❌ Could not find 'body -> sector -> tableData'")
            return
        
        print(f"   -> Found {len(rows)} sectors in Trendlyne data.")

        # 2. Process Data
        results = []
        
        for item in rows:
            try:
                # Extract Name
                raw_name = item.get('stock_column', {}).get('stockName', '').lower()
                
                # Map to Database Name
                db_name = None
                for key, val in NAME_MAP.items():
                    if key in raw_name:
                        db_name = val
                        break
                
                if not db_name: continue

                # EXTRACT METRICS (Using the keys from your Debug Output: _sec suffix)
                # These keys match your JSON exactly now.
                w = float(item.get('week_changeP_mcapw_sec', 0) or 0)
                m = float(item.get('month_changeP_mcapw_sec', 0) or 0)
                q = float(item.get('qtr_changeP_mcapw_sec', 0) or 0)
                pe = float(item.get('pe_ttm_mcapw_sec', 0) or 0)
                
                results.append({
                    "sector": db_name,
                    "weekly": w,
                    "monthly": m,
                    "quarterly": q,
                    "pe": pe
                })

            except Exception:
                continue

        # 3. Aggregation & Sorting
        if not results:
            print("❌ No matching sectors found. Check if Trendlyne names match NAME_MAP keys.")
            return

        df = pd.DataFrame(results)
        
        # Group by sector (Average duplicates if any)
        df = df.groupby('sector').mean().reset_index()
        
        # Sort by Weekly Return (Highest First) -> For Momentum Scoring
        df = df.sort_values(by='weekly', ascending=False)
        
        # 4. Display & Return
        print("\n🏆 --- MOMENTUM RANKING (Top 5) ---")
        top_5 = df.head(5)
        
        final_data = []

        for index, row in top_5.iterrows():
            sec = row['sector']
            w = row['weekly']
            q = row['quarterly']
            pe = row['pe']
            
            # SCORING LOGIC
            is_turnaround = False
            note = "Momentum"
            
            # Turnaround = High Weekly + Lagging Quarterly (< 5%)
            if q < 5.0:
                is_turnaround = True
                note = "🔥 TURNAROUND (Lagging Qtr + High Weekly)"
            
            print(f"{sec:<20} | W: {w:>6.2f}% | Q: {q:>6.2f}% | PE: {pe:>5.1f} | {note}")
            
            final_data.append({
                "sector": sec,
                "is_turnaround": is_turnaround,
                "weekly": w,
                "monthly": row['monthly'],
                "quarterly": q,
                "pe": pe
            })
            
        return final_data

    except Exception as e:
        print(f"❌ Script Error: {e}")

if __name__ == "__main__":
    fetch_momentum_turnaround()