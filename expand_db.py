import sqlite3

def add_new_sectors():
    conn = sqlite3.connect('sector_scorer.db')
    cursor = conn.cursor()
    
    # New Sectors to Add
    # Format: (Sector Name, Yahoo Ticker, NSE Symbol, NSDL Name, Top Stocks, PE_Avg)
    new_sectors = [
        ("NIFTY PSU BANK", "^CNXPSUBANK", "NIFTY PSU BANK", "Financial Services", "SBIN,BANKBARODA,PNB", 12.5),
        ("NIFTY INFRA", "^CNXINFRA", "NIFTY INFRA", "Construction", "L&T,RELIANCE,BHARTIARTL", 22.0),
        ("NIFTY MEDIA", "^CNXMEDIA", "NIFTY MEDIA", "Media Entertainment", "SUNTV,PVRINOX,ZEEL", 21.0),
        ("NIFTY FIN SERVICE", "^CNXFINANCE", "NIFTY FIN SERVICE", "Financial Services", "HDFC,BAJFINANCE,BAJAJFINSV", 24.0)
    ]
    
    print("Expanding Database...")
    for s in new_sectors:
        try:
            cursor.execute('''
            INSERT OR IGNORE INTO sectors_master (sector_name, yahoo_ticker, nse_symbol, nsdl_name, top_stocks, pe_5yr_avg)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', s)
            print(f" -> Added {s[0]}")
        except Exception as e:
            print(f"Error: {e}")
            
    conn.commit()
    conn.close()

if __name__ == "__main__":
    add_new_sectors()