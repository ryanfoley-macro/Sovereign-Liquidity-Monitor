import feedparser
import csv
import os
import ssl
from datetime import datetime
from collections import Counter

# --- 1. THE MAC SSL FIX ---
if hasattr(ssl, '_create_unverified_context'):
    ssl._create_default_https_context = ssl._create_unverified_context

# --- 2. CONFIGURATION ---
LOG_FILE = 'macro_intel_log.csv'
MAX_SCORE_PER_ARTICLE = 6

feeds = {
    'ENERGY (OilPrice)': 'https://oilprice.com/rss/main',
    'CRYPTO (CoinDesk)': 'https://www.coindesk.com/arc/outboundfeeds/rss/',
    'MACRO (CNBC)': 'https://www.cnbc.com/id/100003114/device/rss/rss.html',
    'GEOPOLITICS (Defense News)': 'https://www.defensenews.com/arc/outboundfeeds/rss/'
}

# --- 3. THE STRICT GATE ---
system_domain_terms = [
    'Repo', 'Liquidity', 'Credit', 'Yield', 'Treasury', 'Fed', 'Powell', 
    'Rates', 'Bond', 'Debt', 'Deficit', 'Stimulus', 'QE', 'QT', 'Balance Sheet',
    'Insolvent', 'Default', 'Spreads', 'Currency', 'Central Bank', 'Monetary',
    'Oil', 'Gas', 'Energy', 'Pipeline', 'OPEC', 'Mining', 'Minerals', 'Commodity',
    'Nuclear', 'Power', 'Grid', 'Lithium', 'Uranium', 'Copper', 'Strategic Petroleum',
    'War', 'Conflict', 'Tariff', 'Sanction', 'China', 'Russia', 'Defense',
    'Military', 'Security', 'Blockade', 'Seizure', 'Supply Chain', 'Export', 'Import',
    'Missile', 'Drone', 'Strike'
]

# --- 4. WEIGHTING SYSTEM ---
keyword_weights = {
    'Repo': 5, 'Liquidity': 5, 'Insolvent': 5, 'Contagion': 5, 'Collapse': 5,
    'Crisis': 5, 'RRP': 5, 'TGA': 5, 'Stimulus': 5, 'QE': 5, 'Bailout': 5,
    'War': 4, 'Missile': 4, 'Drone': 4, 'Conflict': 4, 'Seizure': 4, 'Blockade': 4,
    'Nuclear': 4, 'Invasion': 4, 'Strike': 4, 'Casualties': 4,
    'Default': 3, 'Bankruptcy': 3, 'Delinquency': 3, 'Spreads': 3, 'Credit': 3,
    'Downgrade': 3, 'Distress': 3, 'Write-down': 3, 'Losses': 3,
    'Inflation': 2, 'Powell': 2, 'Fed': 2, 'Rates': 2, 'Treasury': 2, 'Deficit': 2,
    'Recession': 2, 'Debt': 2, 'Yield': 2, 'Tariff': 2, 'Layoffs': 2, 'Jobless': 2,
    'Stock': 1, 'S&P': 1, 'Market': 1, 'Trade': 1, 'Bank': 1, 'Crypto': 1, 'ETF': 1,
    'Oil': 1, 'Gas': 1, 'Energy': 1, 'China': 1, 'Russia': 1, 'Trump': 1, 
    'Gold': 1, 'Silver': 1, 'Housing': 1, 'Mortgage': 1
}

# --- 5. THE SILENCER ---
ignore_terms = [
    'Musk', 'Zuckerberg', 'Bezos', 'Kardashian', 'Celebrity', 'Influencer', 
    'Viral', 'TikTok', 'Instagram', 'YouTuber', 'Drama', 'Scandal',
    'Review', 'Best of', 'Gift Guide', 'iPhone', 'Android', 'Gadget',
    'NFL', 'NBA', 'MLB', 'FIFA', 'Super Bowl', 'Olympics', 'Quarterback',
    'Movie', 'Cinema', 'Box Office', 'Disney+', 'Netflix', 'Hulu',
    'Diet', 'Workout', 'Weight Loss', 'Fashion', 'Luxury', 'Travel', 
    'Horoscope', 'Astrology', 'Royal Family', 'Prince Harry', 'Food', 'Restaurant',
    'Chipotle', 'Sweetgreen', 'Burger', 'Chef', 'Recipe', 'Retail Trader', 
    'Meme Stock', 'Credit Card', 'Consumer'
]

# --- 6. DATABASE SETUP ---
seen_links = set()

if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Timestamp', 'Source', 'Category', 'Headline', 'Link', 'Score'])
    print(f"[+] Created new log file: {LOG_FILE}")
else:
    with open(LOG_FILE, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        try:
            next(reader, None)
            for row in reader:
                if len(row) > 4:
                    seen_links.add(row[4])
        except csv.Error:
            pass 

print(f"--- FOLEY MACRO INTELLIGENCE REPORT ---")
print(f"--- {datetime.now().strftime('%Y-%m-%d %H:%M')} ---\n")

# --- 7. THE SCORING ENGINE ---
new_hits = 0
ignored_stats = Counter()
gated_out_count = 0

for source_name, url in feeds.items():
    print(f"Scanning {source_name}...")
    try:
        feed = feedparser.parse(url)
        if not feed.entries:
            print("     [!] Error: No entries found.")
            continue

        for entry in feed.entries[:30]:
            title = entry.title
            summary = entry.get('summary', '') 
            link = entry.link
            full_text = f"{title} {summary}"
            
            # NOISE CHECK
            triggered_ignore = False
            for ignore in ignore_terms:
                if ignore.lower() in full_text.lower():
                    ignored_stats[ignore] += 1
                    triggered_ignore = True
                    break
            if triggered_ignore:
                continue

            # MACRO GATE
            is_relevant = False
            for domain_word in system_domain_terms:
                if domain_word.lower() in full_text.lower():
                    is_relevant = True
                    break
            if not is_relevant:
                gated_out_count += 1
                continue

            # SCORING
            entry_score = 0
            for word, weight in keyword_weights.items():
                if word.lower() in full_text.lower():
                    entry_score += weight
            
            final_score = min(entry_score, MAX_SCORE_PER_ARTICLE)
            
            if final_score > 0:
                if link not in seen_links:
                    print(f" [NEW][Score: {final_score}] {title}")
                    
                    with open(LOG_FILE, 'a', newline='', encoding='utf-8') as f:
                        writer = csv.writer(f)
                        category = source_name.split(' ')[0]
                        writer.writerow([
                            datetime.now().strftime('%Y-%m-%d %H:%M'), 
                            source_name, 
                            category, 
                            title, 
                            link, 
                            final_score
                        ])
                    
                    seen_links.add(link)
                    new_hits += 1

    except Exception as e:
        print(f"Error reading {source_name}: {e}")
    print("-" * 40)

# --- 8. THE GHOSTWRITER (INSTITUTIONAL EDITION) ---
today_str = datetime.now().strftime('%Y-%m-%d')
today_display = datetime.now().strftime('%B %d, %Y')

score_buckets = {'PLUMBING': 0, 'CONFLICT': 0, 'MACRO': 0, 'OTHER': 0}
bucket_map = {
    'PLUMBING': ['Repo', 'Liquidity', 'Insolvent', 'Contagion', 'Collapse', 'Crisis', 'RRP', 'TGA', 'Stimulus', 'QE', 'Bailout', 'Credit', 'Default', 'Bank', 'Spreads', 'Yield'],
    'CONFLICT': ['War', 'Missile', 'Drone', 'Conflict', 'Seizure', 'Blockade', 'Nuclear', 'Invasion', 'Strike', 'Casualties', 'Oil', 'Gas', 'Energy', 'Pipeline', 'Defense', 'Military'],
    'MACRO': ['Inflation', 'Powell', 'Fed', 'Rates', 'Treasury', 'Deficit', 'Recession', 'Debt', 'Tariff', 'Jobs', 'Stock', 'S&P', 'Market', 'Housing']
}
source_fallback = {'ENERGY': 'CONFLICT', 'GEOPOLITICS': 'CONFLICT', 'MACRO': 'MACRO', 'CRYPTO': 'MACRO'}

top_stories = []
daily_score = 0
daily_count = 0

if os.path.exists(LOG_FILE):
    with open(LOG_FILE, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader, None) 
        for row in reader:
            if len(row) > 5:
                if row[0].startswith(today_str):
                    score = int(row[5])
                    source_cat = row[2]
                    headline = row[3]
                    link = row[4]
                    daily_score += score
                    daily_count += 1
                    top_stories.append((headline, score, link))
                    
                    assigned = False
                    for key, keywords in bucket_map.items():
                        if any(k.lower() in headline.lower() for k in keywords):
                            score_buckets[key] += score
                            assigned = True
                            break
                    if not assigned:
                        fallback_bucket = source_fallback.get(source_cat, 'OTHER')
                        score_buckets[fallback_bucket] += score

top_stories.sort(key=lambda x: x[1], reverse=True)
top_5 = top_stories[:5]

if daily_score > 0:
    top_driver = max(score_buckets, key=score_buckets.get)
else:
    top_driver = "NONE"

# --- THE NARRATIVE LIBRARY (CLEAN & PUBLIC) ---
analysis_text = ""
action_plan = ""

if top_driver == 'CONFLICT':
    analysis_text = (
        "The Liquidity Monitor has detected a significant regime shift towards GEOPOLITICAL CONFLICT. "
        f"With a Conflict Score of {score_buckets['CONFLICT']}, physical risks (War/Energy/Supply Chains) "
        "are overpowering standard macro inputs. Markets are likely pricing in supply shocks."
    )
    action_plan = (
        "1. ENERGY: Overweight Global Energy Producers and Integrated Oil.\n"
        "2. DEFENSE: Monitor Industrial Defense primes for expanding order books.\n"
        "3. HEDGE: Physical Commodities are the preferred hedge over sovereign bonds."
    )

elif top_driver == 'PLUMBING':
    analysis_text = (
        "CRITICAL WARNING: The system has detected elevated stress in FINANCIAL PLUMBING. "
        f"A Plumbing Score of {score_buckets['PLUMBING']} indicates potential collateral shortages or banking risks. "
        "Systemic risk is elevated beyond normal variance."
    )
    action_plan = (
        "1. CASH: Prioritize Cash Equivalents and Short-Duration Treasuries (T-Bills).\n"
        "2. SOVEREIGN: Monitor Hard Assets as 'System Exit' liquidity proxies.\n"
        "3. RISK OFF: Reduce exposure to high-beta and credit-sensitive equities."
    )

elif top_driver == 'MACRO':
    analysis_text = (
        "The market is operating in a standard MACRO/POLICY regime. "
        "Stress is driven by Central Bank expectations, rates, and inflation data. "
        "Volatility is likely contained within normal ranges absent a policy shock."
    )
    action_plan = (
        "1. NEUTRAL: No emergency actions required. Maintain standard allocation.\n"
        "2. WATCH: 10Y Yields and Dollar Index (DXY) for directional cues.\n"
        "3. IGNORE: Intraday volatility unless accompanied by volume expansion."
    )
else:
    analysis_text = "Market signals are muted. No dominant stressor detected."
    action_plan = "Maintain current positioning."

most_ignored = ignored_stats.most_common(3)
noise_summary = ", ".join([f"{term} ({count})" for term, count in most_ignored]) if most_ignored else "None"

# --- GENERATE THE FILE REPORT ---
report = f"""
CONFIDENTIAL // MARKET INTELLIGENCE BRIEF
DATE: {today_display}
SUBJECT: DAILY MACRO REGIME ANALYSIS
------------------------------------------------------------
1. SITUATION ANALYSIS
---------------------
{analysis_text}

The 'Daily Macro Stress Index' closed at {daily_score}. 
Dominant Driver: >> {top_driver} << ({int((score_buckets[top_driver]/daily_score)*100) if daily_score else 0}% of Signal)

2. STRATEGIC POSTURE
--------------------
{action_plan}

3. CRITICAL INTEL (Top 5 Signals)
---------------------------------
"""
for i, (head, scr, lnk) in enumerate(top_5, 1):
    report += f"{i}. {head} [Severity: {scr}]\n   LINK: {lnk}\n"

report += f"""
4. SYSTEM DIAGNOSTICS
---------------------
Noise Artifacts Filtered: {sum(ignored_stats.values())} ({noise_summary})
Political Fluff Gated: {gated_out_count}

------------------------------------------------------------
END OF REPORT
"""

filename = f"Foley_Macro_Brief_{today_str}.txt"
with open(filename, "w", encoding="utf-8") as f:
    f.write(report)

# --- TERMINAL DASHBOARD ---
print(f"\n========================================")
print(f"   DAILY MACRO STRESS INDEX: {daily_score}")
print(f"   (Dominant Driver: {top_driver})")
print(f"----------------------------------------")
print(f"   STRESS COMPOSITION:")
for category, score in score_buckets.items():
    if score > 0:
        bar = "█" * int(score / 5) 
        print(f"   {category}: {score} {bar}")
print(f"----------------------------------------")
print(f"[+] WRITTEN BRIEF GENERATED: {filename}")
print(f"    (Clean, Ticker-Free Version for Distribution)")
print(f"========================================")
print("\n--- END OF BRIEF ---")