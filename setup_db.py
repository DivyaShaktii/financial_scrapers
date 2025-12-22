import sqlite3

def create_database():
    # 1. Connect to the database (This creates the file if it doesn't exist)
    conn = sqlite3.connect('sector_scorer.db')
    cursor = conn.cursor()

    # --- TABLE 1: SECTORS MASTER (The "Address Book") ---
    # Stores the static info: Name, Tickers, and the 5-Year Average PE benchmark.
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS sectors_master (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sector_name TEXT UNIQUE,      -- Display Name (e.g., "NIFTY AUTO")
        yahoo_ticker TEXT,            -- For scraping Prices (e.g., "^CNXAUTO")
        nse_symbol TEXT,              -- For scraping PE (e.g., "NIFTY AUTO")
        nsdl_name TEXT,               -- For matching FPI flows (e.g., "Automobile and Auto Components")
        top_stocks TEXT,              -- For scraping Volume (e.g., "MARUTI,TATAMOTORS,M&M")
        pe_5yr_avg REAL               -- The Valuation Baseline (Calculated once)
    )
    ''')

    # --- TABLE 2: DAILY MACRO (FII/DII) ---
    # Stores the daily market sentiment.
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS daily_macro (
        date TEXT PRIMARY KEY,        -- Format: YYYY-MM-DD
        fii_net_crores REAL,
        dii_net_crores REAL,
        sentiment_score INTEGER       -- 0, 4, 6, or 10
    )
    ''')

    # --- TABLE 3: DAILY SECTOR METRICS (The Scorecard) ---
    # Stores the daily scores for every sector.
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS daily_sector_metrics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        sector_name TEXT,
        
        -- Raw Data (What we scraped)
        nsdl_rank INTEGER,
        current_pe REAL,
        weekly_return REAL,
        monthly_return REAL,
        quarterly_return REAL,
        avg_delivery_pct REAL,
        
        -- Final Scores (0-100)
        smart_money_score INTEGER,
        momentum_score INTEGER,
        valuation_score INTEGER,
        volume_score INTEGER,
        total_score INTEGER,
        
        -- The "Why"
        mini_explanation TEXT,
        
        FOREIGN KEY(sector_name) REFERENCES sectors_master(sector_name)
    )
    ''')

    print("✅ Database 'sector_scorer.db' created successfully!")
    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_database()