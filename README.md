Sovereign Liquidity Monitor (v1.0)
Automated Macro-Liquidity Tracking & Narrative Stress Engine

"In a regime of Fiscal Dominance, liquidity is not just a variable; it is the only variable."

1. The Thesis
The post-2020 economic regime has shifted from Monetary Dominance (Fed controls inflation via rates) to Fiscal Dominance (Fed manages liquidity to support Sovereign Debt).

Traditional analysis focuses on corporate earnings or P/E ratios. This system operates on a different premise: Asset prices are primarily a function of Net Liquidity.

This project is a Python-based Operator's System designed to:

Quantify the Plumbing: Track the real-time flows of the Federal Reserve Balance Sheet (RRP, TGA, SOMA).

Measure Narrative Stress: Scrape and score global financial news to identify disconnects between "Sentiment" (Narrative) and "Reality" (Plumbing).

Log Regime Shifts: Build a proprietary dataset of liquidity conditions to backtest future volatility.

2. System Architecture (v1.0)
The system is built as an automated ETL (Extract, Transform, Load) pipeline using Python.

A. The Hard Plumbing (Liquidity Monitor)

Data Source: Federal Reserve Economic Data (FRED) API.

Key Metrics Tracked:

RRPONTSYD (Reverse Repo): Measures excess cash draining from the system.

WTREGEN (Treasury General Account): The government's checking account (liquidity withdrawal/injection).

WALCL (Total Assets): The raw size of the Fed's Balance Sheet.

Calculation: Computes Net Liquidity (Fed Assets - TGA - RRP) to determine the actual capital available for risk assets.

B. The Narrative Engine (Intel Officer)

Data Source: RSS Feeds from major financial outlets (WSJ, FT, CNBC, Crypto Media).

Methodology:

Scrapes headlines in real-time.

Applies a Keyword Scoring Algorithm to detect specific stress vectors (e.g., "Liquidity," "Crisis," "Yields," "Bailout").

Generates a daily "Narrative Stress Score" (0-100) to quantify market anxiety.

C. The Data Warehouse

Output: Automated .csv logging system that appends daily snapshots.

Goal: To build a historical time-series that allows for Z-score analysis of "Liquidity Stress" vs. "Narrative Panic."

3. Current Capabilities
Automated Data Extraction: Pulls live data from St. Louis Fed servers.

Sentiment Scoring: Filters noise and identifies high-velocity narrative shifts.

Regime Logging: Creates a permanent record of daily liquidity conditions for future backtesting.

Error Handling: Robust logic to handle API timeouts or missing feed data (Production-Ready).

4. Roadmap & Future Improvements (v2.0)
Current version (v1.0) establishes the data pipeline. Version 2.0 will focus on statistical normalization and deeper credit signals.

[Planned] Statistical Normalization: Implementing rolling Z-Scores (30-day/90-day) to establish statistical baselines for "High Stress" days, moving beyond raw index values.

[Planned] Credit Plumbing Integration: Adding SOFR (Secured Overnight Financing Rate) and OIS Spreads to monitor interbank lending stress beyond just raw liquidity levels.

[Planned] Weighted Sentiment Logic: Upgrading the NLP engine to weigh "Plumbing Keywords" (Repo, Collateral) higher than general "Market Noise" keywords.

5. Technology Stack
Language: Python 3.9+

Libraries: pandas, pandas_datareader, requests, beautifulsoup4, feedparser

Data Source: FRED API (St. Louis Fed)

6. Disclaimer
This software is for educational and research purposes only. It is not financial advice. The "Net Liquidity" equation is a theoretical model used for macro analysis and should not be the sole basis for investment decisions.

Author: [Ryan Foley / www.linkedin.com/in/ryan-foley-47aa1227b] Macro Analyst | Developer | Private Credit Researcher
