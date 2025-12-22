# 📈 Sector Scorer (Indian Market)

An automated tool that analyzes and scores Indian Stock Market sectors (0-100) to identify the best investment opportunities. It uses live data to rank sectors based on Institutional Flow, Momentum, Valuation, and Volume.

## 🧠 Scoring Logic (0-100 Points)
The tool aggregates data from 4 sources to generate a final score:
1.  **Smart Money (30 pts):** FII/DII daily flow (Moneycontrol) + FPI Sector Allocation ranks (NSDL).
2.  **Momentum (30 pts):** Weekly/Monthly/Quarterly price trends & Turnaround detection (Trendlyne).
3.  **Valuation (25 pts):** Current PE vs 5-Year Historical Average (Undervalued/Overvalued).
4.  **Volume (15 pts):** Delivery percentage of top 3 stocks in the sector (NSE Bhavcopy).

## 📂 File Structure

| File Name | Description |
| :--- | :--- |
| **`main.py`** | **The Controller.** Runs all scrapers, calculates scores, and prints the Top 3 / Bottom 3 sectors. |
| `scraper_macro.py` | Fetches daily FII/DII net flow data and determines market sentiment. |
| `scraper_nsdl.py` | Scrapes NSDL Fortnightly reports to rank sectors by FPI inflows. |
| `scraper_momentum.py` | Fetches Weekly/Quarterly returns and PE ratios from Trendlyne API. |
| `scraper_volume.py` | Downloads the daily NSE Bhavcopy (CSV) to calculate Delivery % of top stocks. |
| `setup_db.py` | Creates the SQLite database structure (`sector_scorer.db`). |
| `init_sectors.py` | Populates the database with the Sector Universe (Names, Tickers, 5-Yr Avg PE). |
| `sector_scorer.db` | Lightweight SQLite database storing sector config and daily logs. |

## 🚀 How to Run

1.  **Install Dependencies:**
    ```bash
    pip install requests pandas yfinance sqlite3
    ```

2.  **Initialize Database (First time only):**
    ```bash
    python setup_db.py
    python init_sectors.py
    ```

3.  **Run the Scorer:**
    ```bash
    python main.py
    ```

## ⚠️ Note
*   **Time Sensitive:** Run `main.py` **after 6:00 PM IST** to ensure NSE/Bhavcopy data for the day is available.
*   **Data Sources:** Uses publicly available data from NSE, NSDL, Moneycontrol, and Trendlyne.