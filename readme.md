**NSE Scraper**

/*What this script does*/
This script builds a complete NSE equities master file from scratch.
It fetches all tradable NSE symbols, loads official company name and listing date from NSE,
uses Yahoo Finance as a fallback for missing data, adds P/E, market cap, and sector,
and saves the result as a CSV file. Each run generates fresh data (no cache).

**Output**
output/nse_equities_master_full.csv
Columns
symbol
companyName
listingDate
pe
market_cap
sector

**Data sources**
NSE Pre-open API: symbol universe
NSE EQUITY_L.csv: official company name and listing date
Yahoo Finance: fallback for missing name/date and for PE, market cap, sector

**Why some values are empty**
P/E is missing for loss-making companies.
Sector may be missing for ETFs or new stocks.
Listing date may be missing for very recent listings.
This reflects real data availability.

**How to run**
pip install pandas requests yfinance
python nse_full_async3.py

**Runtime**
First run takes approximately 10–20 minutes depending on symbol count and Yahoo response
time.

**Summary**
This script creates a clean NSE stock Data using NSE as the primary source and Yahoo Finance
as a fallback.

**BSE Scraper**

/*What this script does*/
This script builds a BSE mainboard equity stock master from scratch.
It fetches all BSE-listed equity instruments, filters only Active Equity stocks,
uses Yahoo Finance to enrich data with Sector, Industry, and P/E ratio,
and saves the final dataset as a single CSV file. Each run generates fresh data.

**Output**
output/bse_useful_stocks.csv
Columns in output
Security Code
Issue Name
Security ID
Instrument
Face Value
BSE URL
Issuer Name
Market Cap
Sector (Yahoo)
Industry (Yahoo)
PE (Yahoo)

**Data sources used**
BSE Scrip Master API
Used to obtain security code, issue name, security ID, instrument type,
face value, issuer name, market capitalization, official BSE stock URL,
and trading status.

**Yahoo Finance**
Used to fetch sector, industry, and trailing P/E ratio.
Yahoo is required because BSE does not provide these fields in free APIs.

**Why some values may be empty**
P/E is missing for loss-making companies.
Sector or Industry may be missing for thinly traded or newly listed stocks.
Yahoo coverage is not complete for all equities.

**How the script works**
Fetches BSE equity master data.
Filters only Active Equity stocks.
Selects relevant columns.
Fetches Yahoo data in parallel.
Merges Yahoo enrichment into BSE data.
Renames columns for readability.
Saves the final CSV file.

**Installation**
pip install pandas requests yfinance

**How to run**
python bse_full.py

**Runtime**
Typically 5–8 minutes depending on stock count and Yahoo response speed.

**Summary**
This script creates a clean, analyst-ready BSE Stock data using BSE as the primary
source and Yahoo Finance for enrichment.