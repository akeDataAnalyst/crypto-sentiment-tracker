# Crypto Market Sentiment Analyzer from News Feeds

## **Description**  
A Python tool that collects recent cryptocurrency news from **NewsData.io** (free tier) and public RSS feeds, applies VADER sentiment analysis to score daily market tone, and correlates sentiment with next-day price movements for BTC, ETH, and SOL.

## **Problem**  
Cryptocurrency prices are highly sensitive to news, social hype, and media narratives. Without systematic quantification, it's challenging to distinguish noise from meaningful signals in a 24/7 global market.

## **Solution**  
- Aggregated news articles from NewsData.io (free tier, keyword-targeted crypto news) and RSS feeds (Cointelegraph, CoinDesk, CryptoSlate, etc.)  
- Used VADER NLP to compute compound sentiment scores (-1 very negative → +1 very positive) on titles, summaries, and content  
- Aggregated to daily level (mean sentiment + article count)  
- Merged with daily price data (Binance via CCXT / CoinGecko fallback)  
- Calculated correlations between sentiment and next-day returns

## **Key Results (Feb 2026 Sample)**  
- **Strong correlation** (+0.878) between daily news sentiment and next-day BTC returns  
- Positive sentiment spikes (e.g. +0.281 on Feb 13) preceded meaningful gains (BTC +4.01%, ETH +5.22%, SOL +7.69% next day)  
- Fading/neutral-to-negative sentiment (Feb 14–16) aligned with reduced upside → pullback (BTC -1.50%, ETH -5.83% on Feb 16)  
- Rising article volume (up to 52 articles on Feb 16) acted as a fear/discussion indicator during the correction

## **Technologies**  
- Data collection: feedparser (RSS), requests + NewsData.io API, python-dotenv (key management)  
- Sentiment analysis: vaderSentiment  
- Processing & analysis: pandas, numpy  
- Visualization: Plotly (interactive charts)  
- Price data: ccxt (Binance), pycoingecko (fallback)

## **Files**  
- `01_data_collection.ipynb` – NewsData.io + RSS + price fetching  
- `02_sentiment_scoring.ipynb` – VADER scoring & aggregation  
- `03_correlation_analysis.ipynb` – Merge, correlation, insights  
- `daily_sentiment_vader.csv` – Daily sentiment scores  
- `daily_prices_btc_eth_sol.csv` – Price history  
- `merged_sentiment_prices_final.csv` – Combined dataset  
- `sentiment_vs_btc_next_day_return.html` – Interactive Plotly chart  
- `app.py` – Streamlit dashboard

## **Dashboard**  
Interactive Streamlit app showing:  
- Sentiment vs next-day returns chart  
- Daily sentiment trend  
- Correlation table  
- Recent data table  
- Download buttons for CSVs  
