import pandas as pd
import requests
import sqlite3
import urllib3
from datetime import datetime, timedelta

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_fortnight_dates():
    dates_to_try = []
    today = datetime.now()
    current_15 = today.replace(day=15)
    if today >= current_15: dates_to_try.append(current_15)
    first_of_month = today.replace(day=1)
    prev_month_end = first_of_month - timedelta(days=1)
    dates_to_try.append(prev_month_end)
    dates_to_try.append(prev_month_end.replace(day=15))
    return [d.strftime("%b%d%Y") for d in dates_to_try]

def fetch_nsdl_data():
    # Returns a dictionary: { "NIFTY BANK": Rank_Integer }
    print("   [NSDL] Fetching Ranks...")
    base_url = "https://www.fpi.nsdl.co.in/web/StaticReports/Fortnightly_Sector_wise_FII_Investment_Data/FIIInvestSector_{}.html"
    target_dates = get_fortnight_dates()
    
    headers = {"User-Agent": "Mozilla/5.0"}
    df = None

    for date_str in target_dates:
        try:
            resp = requests.get(base_url.format(date_str), headers=headers, verify=False)
            if resp.status_code == 200:
                dfs = pd.read_html(resp.text)
                if len(dfs) > 0:
                    df = dfs[0]
                    break
        except: continue

    if df is None: return {}

    # Clean Data
    ranks = {}
    try:
        # Simple extraction logic based on index
        data_list = []
        for index, row in df.iterrows():
            try:
                sec = str(row[1])
                val = str(row[2]).replace(',', '')
                if "Total" in sec or "Sector" in sec: continue
                if val.replace('.','').replace('-','').isdigit():
                    data_list.append((sec, float(val)))
            except: continue
        
        # Rank
        temp_df = pd.DataFrame(data_list, columns=['Sec','Inv'])
        temp_df['rank'] = temp_df['Inv'].rank(ascending=False)
        nsdl_raw_map = dict(zip(temp_df['Sec'], temp_df['rank']))

        # Map to DB
        conn = sqlite3.connect('sector_scorer.db')
        cur = conn.cursor()
        cur.execute("SELECT sector_name, nsdl_name FROM sectors_master")
        
        for db_name, nsdl_name in cur.fetchall():
            # Try exact or partial match
            for key, rank in nsdl_raw_map.items():
                if nsdl_name.lower() in key.lower() or key.lower() in nsdl_name.lower():
                    ranks[db_name] = int(rank)
                    break
        conn.close()
    except: pass
    
    return ranks

if __name__ == "__main__":
    print(fetch_nsdl_data())