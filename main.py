import sqlite3
import pandas as pd
from datetime import datetime

# Import your scrapers
# Make sure all files are in the same folder
import scraper_macro
import scraper_nsdl
import scraper_volume
import scraper_momentum

def calculate_scores():
    print("\n🚀 STARTING SECTOR SCORER ENGINE...\n")

    # 1. FETCH ALL DATA
    # -----------------
    
    # A. Macro (FII/DII)
    # We run the scraper, which saves to DB. Then we read the latest entry.
    scraper_macro.fetch_macro_data() 
    
    conn = sqlite3.connect('sector_scorer.db')
    cursor = conn.cursor()
    
    # Get Macro Score
    today = datetime.now().strftime("%Y-%m-%d")
    cursor.execute("SELECT sentiment_score, fii_net_crores, dii_net_crores FROM daily_macro ORDER BY date DESC LIMIT 1")
    macro_row = cursor.fetchone()
    
    if macro_row:
        macro_score = macro_row[0]
        fii_val = macro_row[1]
        print(f"   -> Macro Sentiment Score: {macro_score}/10 (FII: {fii_val} Cr)")
    else:
        macro_score = 0
        print("   -> ⚠️ No Macro Data found. Defaulting to 0.")

    # B. NSDL Ranks
    nsdl_ranks = scraper_nsdl.fetch_nsdl_data()
    
    # C. Volume Data
    volume_data = scraper_volume.fetch_bhavcopy()
    
    # D. Momentum & PE Data (Trendlyne)
    momentum_list = scraper_momentum.fetch_momentum_turnaround()
    # Convert list to dictionary for easier lookup
    momentum_map = {item['sector']: item for item in momentum_list}

    # 2. SCORING ALGORITHM
    # --------------------
    print("\n🧮 CALCULATING SCORES...")
    
    final_results = []
    
    # Get Master Data (including 5Yr Avg PE)
    cursor.execute("SELECT sector_name, pe_5yr_avg FROM sectors_master")
    all_sectors = cursor.fetchall()

    for sec_name, pe_avg in all_sectors:
        
        # --- INIT ---
        score_smart_money = 0
        score_momentum = 0
        score_valuation = 0
        score_volume = 0
        notes = []

        # --- CATEGORY 1: SMART MONEY (30 Pts) ---
        # 1.1 FII/DII (10 pts) -> Already fetched as macro_score
        score_smart_money += macro_score
        
        # 1.2 NSDL Rank (20 pts)
        rank = nsdl_ranks.get(sec_name, 99) # Default 99 if not found
        if rank == 1: score_smart_money += 20
        elif rank == 2: score_smart_money += 16
        elif rank == 3: score_smart_money += 12
        elif 4 <= rank <= 8: score_smart_money += 6
        
        if rank <= 3: notes.append(f"Top FPI Inflow (#{rank})")

        # --- CATEGORY 2: MOMENTUM (30 Pts) ---
        mom_data = momentum_map.get(sec_name, {})
        w_ret = mom_data.get('weekly', 0)
        m_ret = mom_data.get('monthly', 0)
        q_ret = mom_data.get('quarterly', 0)
        
        # 2.1 Quarterly Lag (Turnaround Candidate) (10 pts)
        if q_ret < -5: 
            score_momentum += 10
            notes.append("Oversold Qtr (Turnaround)")
        elif -5 <= q_ret <= 5: 
            score_momentum += 8
        elif 5 < q_ret <= 10: 
            score_momentum += 5
            
        # 2.2 Weekly Rank (Top 3) (10 pts)
        # We need to check rank relative to others in momentum_list
        # momentum_list is already sorted by Weekly Return Descending
        
        # Find rank in the list
        current_w_rank = 99
        for idx, item in enumerate(momentum_list):
            if item['sector'] == sec_name:
                current_w_rank = idx + 1
                break
        
        if current_w_rank <= 3: 
            score_momentum += 10
            notes.append("High Weekly Momentum")
        elif current_w_rank <= 5: score_momentum += 8
        elif current_w_rank <= 10: score_momentum += 5

        # 2.3 Monthly Trend (10 pts)
        if m_ret > 6: score_momentum += 10
        elif 3 <= m_ret <= 6: score_momentum += 6
        elif 0 <= m_ret < 3: score_momentum += 3

        # --- CATEGORY 3: VALUATION (25 Pts) ---
        current_pe = mom_data.get('pe', 0)
        
        if current_pe > 0 and pe_avg > 0:
            pe_diff = ((current_pe - pe_avg) / pe_avg) * 100
            
            # 3.1 PE Diff Scoring
            if pe_diff < -20: 
                score_valuation += 15
                notes.append("Deeply Undervalued")
            elif -20 <= pe_diff < -10: 
                score_valuation += 12
                notes.append("Undervalued")
            elif -10 <= pe_diff <= 10: 
                score_valuation += 8
            elif 10 < pe_diff <= 20: 
                score_valuation += 4
            else:
                notes.append("Overvalued")

            # 3.2 Relative Valuation (10 pts) - Simplified logic
            # If PE is lower than historical avg, give points
            if current_pe < pe_avg: score_valuation += 10
            else: score_valuation += 3
        else:
            # If no PE data, assume neutral
            score_valuation += 8 

        # --- CATEGORY 4: VOLUME (15 Pts) ---
        deliv = volume_data.get(sec_name, 0)
        
        if deliv > 50: 
            score_volume += 15
            notes.append("Strong Delivery Volume")
        elif 40 <= deliv <= 50: score_volume += 10
        elif 30 <= deliv < 40: score_volume += 5
        
        # --- FINAL TOTAL ---
        total_score = score_smart_money + score_momentum + score_valuation + score_volume
        
        # Cap at 100
        if total_score > 100: total_score = 100
        
        final_results.append({
            "Sector": sec_name,
            "Score": total_score,
            "Explanation": " + ".join(notes),
            "Metrics": f"PE: {current_pe} (Avg {pe_avg}) | W: {w_ret:.1f}% | Vol: {deliv:.1f}%"
        })

    conn.close()

    # 3. DISPLAY OUTPUT
    # -----------------
    df_res = pd.DataFrame(final_results)
    df_res = df_res.sort_values(by="Score", ascending=False)
    
    print("\n" + "="*50)
    print("      🏆 SECTOR SCORER - TOP OPPORTUNITIES      ")
    print("="*50)
    
    # Top 3
    print("\n🟢 TOP 3 SECTORS (BUY CANDIDATES):")
    for i in range(min(3, len(df_res))):
        row = df_res.iloc[i]
        print(f"{i+1}. {row['Sector']} — {row['Score']}/100")
        print(f"   📝 {row['Explanation']}")
        print(f"   📊 {row['Metrics']}\n")

    # Bottom 3
    print("🔴 3 WORST SECTORS (AVOID):")
    for i in range(min(3, len(df_res))):
        row = df_res.iloc[-(i+1)]
        print(f"{i+1}. {row['Sector']} — {row['Score']}/100")
        print(f"   Note: {row['Explanation'] if row['Explanation'] else 'Weak Momentum/Overvalued'}\n")

if __name__ == "__main__":
    calculate_scores()