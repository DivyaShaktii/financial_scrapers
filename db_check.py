import sqlite3
import pandas as pd

# Connect
conn = sqlite3.connect('sector_scorer.db')

# Read Data
df = pd.read_sql("SELECT * FROM sectors_master", conn)

# Print
print(df)
conn.close()