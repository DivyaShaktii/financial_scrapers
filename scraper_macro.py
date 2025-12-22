import requests
from bs4 import BeautifulSoup
import sqlite3
from datetime import datetime

def fetch_macro_data():
    # 1. The Source URL (Moneycontrol FII/DII Page)
    url = "https://www.moneycontrol.com/stocks/marketstats/fii_dii_activity/index.php"
    
    # 2. Add Headers (To look like a real browser)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        print("📡 Connecting to Moneycontrol for FII/DII Data...")
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        # 3. Locate the specific data in the HTML
        # Moneycontrol puts the latest data in the first row of the table
        # We look for the "Net" columns
        
        # Note: This logic assumes the standard Moneycontrol table structure
        # In a real production app, you'd add more checks here.
        table = soup.find('table', {'class': 'mctable1'})
        rows = table.find_all('tr')
        
        # usually row 2 or 3 has the latest data (skipping headers)
        latest_row = rows[2] 
        cols = latest_row.find_all('td')

        # Moneycontrol Format: [Date, FII Buy, FII Sell, FII Net, DII Buy, DII Sell, DII Net]
        # We need FII Net (Index 3) and DII Net (Index 6)
        fii_net = float(cols[3].text.replace(',', ''))
        dii_net = float(cols[6].text.replace(',', ''))
        
        # 4. Calculate the Score (Your Logic)
        score = 0
        sentiment = "Bearish"
        
        if fii_net > 0 and dii_net > 0:
            score = 10
            sentiment = "Strong Bullish"
        elif fii_net < 0 and dii_net > 0:
            score = 6
            sentiment = "Stable/Neutral"
        elif fii_net > 0 and dii_net < 0:
            score = 4
            sentiment = "Mild Bullish"
        else:
            score = 0
            sentiment = "Bearish"

        print(f"   -> FII Net: {fii_net} Cr")
        print(f"   -> DII Net: {dii_net} Cr")
        print(f"   -> Score: {score} ({sentiment})")

        # 5. Save to Database
        conn = sqlite3.connect('sector_scorer.db')
        cursor = conn.cursor()
        today = datetime.now().strftime("%Y-%m-%d")
        
        cursor.execute('''
        INSERT OR REPLACE INTO daily_macro (date, fii_net_crores, dii_net_crores, sentiment_score)
        VALUES (?, ?, ?, ?)
        ''', (today, fii_net, dii_net, score))
        
        conn.commit()
        conn.close()
        print("✅ Macro Data Saved!")

    except Exception as e:
        print(f"❌ Error fetching Macro Data: {e}")

if __name__ == "__main__":
    fetch_macro_data()