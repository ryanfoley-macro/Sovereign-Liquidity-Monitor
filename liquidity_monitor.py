import pandas as pd
from fredapi import Fred
import matplotlib.pyplot as plt
import ssl

# --- CONFIGURATION ---
# SECURITY WARNING: Never commit your actual API key to GitHub.
# Use an environment variable or a config file in production.
API_KEY = '0c08ca5ae0934d88877f40bbfdd2fb13'  # <--- REPLACE THIS WHEN RUNNING LOCALLY, BUT LEAVE IT BLANK FOR GITHUB

# --- THE MAC FIX ---
ssl._create_default_https_context = ssl._create_unverified_context

def fetch_liquidity_data():
    print("--- SOVEREIGN LIQUIDITY MONITOR (v1.0) ---")
    print("Connecting to Federal Reserve Database...")
    
    try:
        fred = Fred(api_key=API_KEY)
        
        # 1. PULL THE DATA
        # WALCL = Fed Total Assets (The Source)
        # RRPONTSYD = Reverse Repo (The Drain)
        # WTREGEN = Treasury General Account (The Checking Account)
        assets = fred.get_series('WALCL')
        rrp = fred.get_series('RRPONTSYD')
        tga = fred.get_series('WTREGEN')
        
        print("Data retrieved successfully.")

        # 2. CLEAN & NORMALIZE
        df = pd.DataFrame({
            'Fed_Assets': assets,
            'Reverse_Repo': rrp,
            'TGA': tga
        })
        
        # Filter for the "Fiscal Dominance" era (2023-Present)
        df = df['2023-01-01':].ffill().dropna()

        # 3. CONVERT UNITS
        # WALCL (Assets) and TGA are in Millions. We divide by 1000 to get Billions.
        df['Fed_Assets'] = df['Fed_Assets'] / 1000
        df['TGA'] = df['TGA'] / 1000
        
        # RRP is already in Billions, so we leave it alone.
        
        # 4. THE SOVEREIGN FORMULA: Net Liquidity
        # Net Liq = Fed Assets - TGA - RRP
        df['Net_Liquidity'] = df['Fed_Assets'] - df['TGA'] - df['Reverse_Repo']
        
        return df

    except Exception as e:
        print(f"Error: {e}")
        return pd.DataFrame()

def plot_liquidity(df):
    if df.empty:
        return

    print("Generating Dashboard...")
    
    plt.figure(figsize=(14, 8))
    
    # Plot 1: The "Fuel" (Net Liquidity)
    plt.subplot(2, 1, 1)
    plt.plot(df.index, df['Net_Liquidity'], label='Net Liquidity (The Fuel)', color='green', linewidth=2)
    plt.title('Sovereign Net Liquidity (Fed Assets - TGA - RRP)', fontsize=14)
    plt.ylabel('Billions ($B)')
    plt.grid(True, alpha=0.3)
    plt.legend()

    # Plot 2: The Components (TGA vs RRP)
    plt.subplot(2, 1, 2)
    plt.plot(df.index, df['Reverse_Repo'], label='Reverse Repo (Liquidity Drain)', color='red', linewidth=1.5)
    plt.plot(df.index, df['TGA'], label='TGA (Gov Checking Acct)', color='blue', linewidth=1.5)
    plt.title('Liquidity Components: RRP vs. TGA', fontsize=12)
    plt.ylabel('Billions ($B)')
    plt.grid(True, alpha=0.3)
    plt.legend()
    
    plt.tight_layout()
    plt.show()

# --- EXECUTION ---
if __name__ == "__main__":
    data = fetch_liquidity_data()
    if not data.empty:
        print(data.tail())
        plot_liquidity(data)