import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Crypto News Sentiment Tracker",
    page_icon="📰📈",
    layout="wide"
)

# ────────────────────────────────────────────────
# Robust data loading with error handling
# ────────────────────────────────────────────────
@st.cache_data
def load_data():
    def safe_load_csv(file_path, name="file"):
        try:
            # Try loading with index as date (common when saved with index)
            df = pd.read_csv(file_path, index_col=0, parse_dates=True)
            if df.index.name is None or 'Unnamed' in str(df.index.name):
                df.index.name = 'date'
            return df
        except Exception as e1:
            try:
                # Fallback: date as column
                df = pd.read_csv(file_path)
                date_col = next((c for c in df.columns if 'date' in c.lower() or 'Unnamed' in c), None)
                if date_col:
                    df = df.rename(columns={date_col: 'date'})
                    df['date'] = pd.to_datetime(df['date'], errors='coerce')
                    df = df.dropna(subset=['date'])
                    df = df.set_index('date')
                    return df
                else:
                    raise ValueError(f"No date column found in {file_path}")
            except Exception as e2:
                st.error(f"Failed to load {name} ({file_path}): {e2}")
                st.stop()

    sentiment = safe_load_csv('daily_sentiment_vader.csv', "Sentiment data")
    prices   = safe_load_csv('daily_prices_btc_eth_sol.csv', "Prices data")
    merged   = safe_load_csv('merged_sentiment_prices_final.csv', "Merged data")

    return sentiment, prices, merged

# Load data – this is where most errors happen
try:
    sentiment_df, prices_df, merged_df = load_data()
    st.success("All data loaded successfully")
except Exception as e:
    st.error(f"Critical load error: {e}")
    st.stop()

# ────────────────────────────────────────────────
# Header
# ────────────────────────────────────────────────
st.title("Crypto News Sentiment Tracker")
st.markdown("""
Analyze daily sentiment from crypto news and its link to price movements  
**Sample period:** February 2026  
**Sentiment method:** VADER NLP on news feeds  
**Key result:** +0.878 correlation between sentiment and next-day BTC returns
""")

# ────────────────────────────────────────────────
# Sidebar (now safe – variables are defined)
# ────────────────────────────────────────────────
st.sidebar.header("Dashboard Controls")

if not merged_df.empty:
    date_range = st.sidebar.date_input(
        "Select date range",
        value=(merged_df.index.min().date(), merged_df.index.max().date()),
        min_value=merged_df.index.min().date(),
        max_value=merged_df.index.max().date()
    )
    coin = st.sidebar.selectbox("Focus coin for returns", ["BTC", "ETH", "SOL"])
else:
    st.sidebar.warning("No merged data – check CSV files")

# Filter
if not merged_df.empty:
    start_date, end_date = date_range if len(date_range) == 2 else (merged_df.index.min().date(), merged_df.index.max().date())
    filtered = merged_df.loc[start_date:end_date]
else:
    filtered = pd.DataFrame()

# ────────────────────────────────────────────────
# Tabs
# ────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["Sentiment vs Returns", "Trend View", "Data & Insights"])

with tab1:
    if filtered.empty:
        st.warning("No data in selected range or load failed")
    else:
        st.subheader(f"Sentiment vs {coin} Next-Day Return %")

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=filtered.index,
            y=filtered['sentiment_mean'],
            name='Daily Sentiment',
            line=dict(color='royalblue'),
            yaxis='y'
        ))

        if 'sentiment_mean_3d' in filtered.columns:
            fig.add_trace(go.Scatter(
                x=filtered.index,
                y=filtered['sentiment_mean_3d'],
                name='3-Day Smoothed',
                line=dict(color='darkblue', dash='dash', width=3),
                yaxis='y'
            ))

        ret_col = f"{coin.lower()}_next_ret"
        if ret_col in filtered.columns:
            fig.add_trace(go.Bar(
                x=filtered.index,
                y=filtered[ret_col],
                name=f'{coin} Next-Day %',
                marker_color='orange',
                opacity=0.7,
                yaxis='y2'
            ))

        fig.update_layout(
            title=f"News Sentiment vs {coin} Next-Day Return",
            xaxis_title="Date",
            yaxis=dict(title="Sentiment", side='left'),
            yaxis2=dict(title=f"{coin} % Change", overlaying='y', side='right'),
            hovermode='x unified',
            height=600
        )

        fig.add_hline(y=0, line_dash='dash', line_color='gray')

        st.plotly_chart(fig, use_container_width=True)

with tab2:
    if filtered.empty:
        st.warning("No data available")
    else:
        st.subheader("Sentiment Trend")
        fig_trend = px.line(filtered, x=filtered.index, y=['sentiment_mean'],
                            title="Daily Sentiment Score")
        if 'sentiment_mean_3d' in filtered.columns:
            fig_trend.add_scatter(x=filtered.index, y=filtered['sentiment_mean_3d'],
                                  name='3-Day Smoothed', line=dict(dash='dash'))
        fig_trend.add_hline(y=0, line_dash='dash', line_color='gray')
        st.plotly_chart(fig_trend, use_container_width=True)

with tab3:
    st.subheader("Correlation & Data Snapshot")
    if not merged_df.empty:
        corr_cols = ['sentiment_mean']
        if 'sentiment_mean_3d' in merged_df.columns:
            corr_cols.append('sentiment_mean_3d')
        corr_cols += ['btc_next_ret', 'eth_next_ret', 'sol_next_ret']
        corr_table = merged_df[corr_cols].corr().round(3)
        st.dataframe(corr_table.style.background_gradient(cmap='RdYlGn'))

        st.dataframe(filtered.tail(10).round(3))

        st.download_button("Download Merged CSV", merged_df.to_csv(), "merged_sentiment_prices.csv")
    else:
        st.warning("No merged data loaded")

st.caption("Sentiment Tracker | Portfolio Demo")