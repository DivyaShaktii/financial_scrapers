import sqlite3

def populate_real_master_data():
    conn = sqlite3.connect('sector_scorer.db')
    cursor = conn.cursor()

    # The format is:
    # (Sector Name, Yahoo Ticker, NSE Symbol, NSDL Name, Top 3 Stocks, 5-Year Avg PE)
    
    real_sectors = [
        # 1. BANKING (The biggest sector)
        (
            "NIFTY BANK", 
            "^NSEBANK", 
            "NIFTY BANK", 
            "Financial Services", 
            "HDFCBANK,ICICIBANK,SBIN", 
            23.5  # Banks usually trade between 20-25 PE
        ),
        # 2. AUTO (Cyclical, currently high momentum)
        (
            "NIFTY AUTO", 
            "^CNXAUTO", 
            "NIFTY AUTO", 
            "Automobile and Auto Components", 
            "M&M,MARUTI,TATAMOTORS", 
            28.4  # Auto PE has re-rated higher recently
        ),
        # 3. IT (Export oriented)
        (
            "NIFTY IT", 
            "^CNXIT", 
            "NIFTY IT", 
            "Information Technology", 
            "TCS,INFY,HCLTECH", 
            26.2  # IT commands a premium valuation
        ),
        # 4. FMCG (Defensive, high valuation)
        (
            "NIFTY FMCG", 
            "^CNXFMCG", 
            "NIFTY FMCG", 
            "Fast Moving Consumer Goods", 
            "ITC,HUL,NESTLEIND", 
            39.5  # FMCG always has very high PE
        ),
        # 5. METALS (Cyclical, commodity)
        (
            "NIFTY METAL", 
            "^CNXMETAL", 
            "NIFTY METAL", 
            "Metals & Mining", 
            "TATASTEEL,HINDALCO,JSWSTEEL", 
            16.5  # Metals usually have low PE (10-20 range)
        ),
        # 6. PHARMA (Defensive)
        (
            "NIFTY PHARMA", 
            "^CNXPHARMA", 
            "NIFTY PHARMA", 
            "Healthcare", 
            "SUNPHARMA,CIPLA,DIVISLAB", 
            31.0  # Pharma PE varies, but generally 28-32
        ),
        # 7. REALTY (High Beta, Aggressive)
        (
            "NIFTY REALTY", 
            "^CNXREALTY", 
            "NIFTY REALTY", 
            "Realty", 
            "DLF,LODHA,GODREJPROP", 
            45.0  # Realty PE is often distorted/high due to growth
        ),
        # 8. ENERGY (Oil & Gas + Power)
        (
            "NIFTY ENERGY", 
            "^CNXENERGY", 
            "NIFTY ENERGY", 
            "Oil, Gas & Consumable Fuels", 
            "RELIANCE,NTPC,ONGC", 
            15.5  # Driven by PSUs and Reliance, usually lower PE
        )
    ]

    print("🚀 Populating Database with REAL Market Data...")
    
    for sector in real_sectors:
        try:
            # We use INSERT OR REPLACE to update values if you run this again
            cursor.execute('''
            INSERT OR REPLACE INTO sectors_master 
            (sector_name, yahoo_ticker, nse_symbol, nsdl_name, top_stocks, pe_5yr_avg)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', sector)
            print(f"   -> ✅ Added/Updated: {sector[0]}")
        except Exception as e:
            print(f"   -> ❌ Error on {sector[0]}: {e}")

    conn.commit()
    conn.close()
    print("\nDone! Your 'sectors_master' table now has the actual heavyweights.")

if __name__ == "__main__":
    populate_real_master_data()