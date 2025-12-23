📊 NSE & BSE Equity Scrapers (Indian Market)

Automated Python scripts to build clean, fresh equity master datasets for NSE and BSE, using official exchange sources with Yahoo Finance enrichment.

📈 NSE Scraper
🧾 What This Script Does

This script builds a complete NSE equities master file from scratch.

It:

Fetches all tradable NSE symbols

Loads official company name and listing date from NSE

Uses Yahoo Finance as a fallback for missing data

Adds P/E ratio, market cap, and sector

Saves the result as a CSV file

Each run generates fresh data (no cache).

📂 Output
output/nse_equities_master_full.csv

📑 Columns
Column Name	Description
symbol	NSE trading symbol
companyName	Official company name
listingDate	NSE listing date
pe	Price-to-Earnings ratio
market_cap	Market capitalization
sector	Industry / sector
🔗 Data Sources

NSE Pre-open API
→ Complete tradable symbol universe

NSE EQUITY_L.csv
→ Official company name and listing date

Yahoo Finance
→ Fallback for missing name/date
→ Source for P/E, market cap, and sector

⚠️ Why Some Values Are Empty

P/E → Missing for loss-making companies

Sector → May be missing for ETFs or newly listed stocks

Listing Date → May be missing for very recent IPOs

This reflects real data availability, not a script error.

🚀 How to Run
pip install pandas requests yfinance
python nse_full_async3.py

⏱ Runtime

~10–20 minutes
(Depends on symbol count and Yahoo response time)

🧠 Summary

Creates a clean NSE stock master dataset using:

NSE as the primary source

Yahoo Finance only as a fallback

<hr/>
📊 BSE Scraper
🧾 What This Script Does

This script builds a BSE mainboard equity stock master from scratch.

It:

Fetches all BSE-listed equity instruments

Filters only Active Equity stocks

Uses Yahoo Finance to enrich data with:

Sector

Industry

P/E ratio

Saves the final dataset as a single CSV file

Each run generates fresh data.

📂 Output
output/bse_useful_stocks.csv

📑 Columns
Column Name	Description
Security Code	BSE security code
Issue Name	Stock issue name
Security ID	BSE security identifier
Instrument	Instrument type
Face Value	Face value
BSE URL	Official BSE stock page
Issuer Name	Company name
Market Cap	Market capitalization
Sector (Yahoo)	Sector classification
Industry (Yahoo)	Industry classification
PE (Yahoo)	Trailing P/E ratio
🔗 Data Sources Used
🏛 BSE Scrip Master API

Used to obtain:

Security code

Issue name

Security ID

Instrument type

Face value

Issuer name

Market capitalization

Official BSE stock URL

Trading status

🌐 Yahoo Finance

Used to fetch:

Sector

Industry

Trailing P/E

Yahoo is required because BSE does not provide these fields in free APIs.

⚠️ Why Some Values May Be Empty

P/E → Missing for loss-making companies

Sector / Industry → Missing for thinly traded or newly listed stocks

Yahoo coverage → Not complete for all equities

⚙️ How the Script Works

Fetches BSE equity master data

Filters only Active Equity stocks

Selects relevant columns

Fetches Yahoo data in parallel

Merges Yahoo enrichment into BSE data

Renames columns for readability

Saves the final CSV file

📦 Installation
pip install pandas requests yfinance

🚀 How to Run
python bse_full.py

⏱ Runtime

~5–8 minutes
(Depends on stock count and Yahoo response speed)

🧠 Summary

Creates a clean, analyst-ready BSE equity dataset using:

BSE as the primary source

Yahoo Finance for enrichment
