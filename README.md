# AI Multi-Market Paper Trader — v1

A beginner-friendly Streamlit prototype for virtual prediction-market trading.

## What works
- Manually enter a market, category, YES price, and your estimated YES probability.
- Calculate YES/NO edge in percentage points.
- Apply simple virtual risk limits.
- Open virtual positions.
- Manually settle positions using the official YES/NO outcome.
- Track virtual cash, realized P&L, open positions, and settled history.

## Important limitations
- No live market feed.
- No AI model is connected; probabilities are manually entered.
- No Polymarket connection, wallet, deposits, or real-money execution.
- Session state is temporary and can reset when the app restarts.

## Deploy
1. Upload `app.py` and `requirements.txt` to a GitHub repository.
2. Open https://share.streamlit.io and sign in with GitHub.
3. Create an app, choose the repository, and select `app.py`.
4. Deploy.

This app is an educational simulation, not financial advice.
