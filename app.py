import streamlit as st
import pandas as pd
from datetime import datetime, timezone

st.set_page_config(page_title="AI Market Paper Trader", page_icon="📊", layout="wide")

STARTING_BALANCE = 10_000.0
MAX_TRADE_FRACTION = 0.05
MAX_OPEN_EXPOSURE_FRACTION = 0.20

def init_state():
    if "cash" not in st.session_state:
        st.session_state.cash = STARTING_BALANCE
    if "positions" not in st.session_state:
        st.session_state.positions = []
    if "history" not in st.session_state:
        st.session_state.history = []
    if "market_inputs" not in st.session_state:
        st.session_state.market_inputs = []

init_state()

st.title("📊 AI Multi-Market Paper Trader")
st.caption("Version 1.0 · Virtual funds only · No exchange connection · No real-money orders")

st.warning(
    "Prototype mode: market prices and AI probabilities are entered manually. "
    "This version does not fetch live markets and does not contain an AI model."
)

open_exposure = sum(p["stake"] for p in st.session_state.positions)
equity = st.session_state.cash + open_exposure
realized_pnl = sum(x["pnl"] for x in st.session_state.history)

m1, m2, m3, m4 = st.columns(4)
m1.metric("Available virtual cash", f"${st.session_state.cash:,.2f}")
m2.metric("Open stake", f"${open_exposure:,.2f}")
m3.metric("Realized P&L", f"${realized_pnl:,.2f}")
m4.metric("Open positions", str(len(st.session_state.positions)))

st.divider()
st.header("1. Evaluate a market")

with st.form("market_form"):
    c1, c2 = st.columns(2)
    with c1:
        market_name = st.text_input("Market / event name", placeholder="Example: Will BTC be above $100,000 on Friday?")
        category = st.selectbox("Category", ["Crypto", "Politics", "Sports", "Economics", "Technology", "World events", "Other"])
        yes_price = st.number_input("Current YES price (0.01–0.99)", min_value=0.01, max_value=0.99, value=0.50, step=0.01)
    with c2:
        ai_yes_probability = st.number_input("Your estimated YES probability (%)", min_value=1, max_value=99, value=60, step=1)
        edge_threshold = st.number_input("Minimum edge required (percentage points)", min_value=0.0, max_value=30.0, value=5.0, step=0.5)
        stake = st.number_input("Virtual stake ($)", min_value=1.0, max_value=500.0, value=100.0, step=10.0)
    submitted = st.form_submit_button("Evaluate opportunity", type="primary")

if submitted:
    if not market_name.strip():
        st.error("Enter a market name.")
    else:
        p_yes = ai_yes_probability / 100
        p_no = 1 - p_yes
        no_price = 1 - yes_price
        yes_edge = (p_yes - yes_price) * 100
        no_edge = (p_no - no_price) * 100
        threshold = edge_threshold

        if yes_edge >= threshold and yes_edge >= no_edge:
            suggested = "YES"
            edge = yes_edge
        elif no_edge >= threshold:
            suggested = "NO"
            edge = no_edge
        else:
            suggested = "NO TRADE"
            edge = max(yes_edge, no_edge)

        st.session_state.last_eval = {
            "name": market_name.strip(),
            "category": category,
            "yes_price": yes_price,
            "p_yes": p_yes,
            "yes_edge": yes_edge,
            "no_edge": no_edge,
            "suggested": suggested,
            "edge": edge,
            "stake": float(stake),
            "time": datetime.now(timezone.utc).isoformat()
        }

if "last_eval" in st.session_state:
    e = st.session_state.last_eval
    st.subheader("Evaluation result")
    st.write(f"**{e['name']}** · {e['category']}")
    a, b, c = st.columns(3)
    a.metric("Market YES price", f"{e['yes_price']*100:.1f}%")
    b.metric("Estimated YES probability", f"{e['p_yes']*100:.1f}%")
    c.metric("Estimated edge", f"{e['edge']:.1f} pp")
    st.write(f"YES edge: **{e['yes_edge']:.1f} percentage points** · NO edge: **{e['no_edge']:.1f} percentage points**")
    if e["suggested"] == "NO TRADE":
        st.info("Decision: NO TRADE — estimated edge does not meet your threshold.")
    else:
        st.success(f"Decision: potential {e['suggested']} opportunity. This is a paper-trading signal, not a guarantee.")
        max_trade = STARTING_BALANCE * MAX_TRADE_FRACTION
        max_exposure = STARTING_BALANCE * MAX_OPEN_EXPOSURE_FRACTION
        allowed = min(max_trade, max_exposure - open_exposure, st.session_state.cash)
        if allowed <= 0:
            st.error("Risk limit reached. Close or settle an existing position before opening another.")
        else:
            requested = min(e["stake"], allowed)
            if requested < e["stake"]:
                st.caption(f"Risk controls reduced the stake from ${e['stake']:.2f} to ${requested:.2f}.")
            if st.button(f"Open virtual {e['suggested']} position · ${requested:.2f}"):
                price = e["yes_price"] if e["suggested"] == "YES" else 1 - e["yes_price"]
                shares = requested / price
                st.session_state.cash -= requested
                st.session_state.positions.append({
                    "id": len(st.session_state.positions) + len(st.session_state.history) + 1,
                    "name": e["name"],
                    "category": e["category"],
                    "side": e["suggested"],
                    "entry_price": price,
                    "stake": requested,
                    "shares": shares,
                    "opened": datetime.now(timezone.utc).isoformat()
                })
                st.success("Virtual position opened.")
                st.rerun()

st.divider()
st.header("2. Open virtual positions")
if st.session_state.positions:
    pos_df = pd.DataFrame(st.session_state.positions)
    st.dataframe(pos_df[["id", "name", "category", "side", "entry_price", "stake", "shares"]], use_container_width=True, hide_index=True)
    st.caption("To settle a position, select its actual final outcome below. Settlement is manual; verify the event's official resolution first.")
    ids = [p["id"] for p in st.session_state.positions]
    selected_id = st.selectbox("Position to settle", ids, format_func=lambda x: next(p["name"] for p in st.session_state.positions if p["id"] == x))
    outcome = st.selectbox("Official market outcome", ["YES", "NO"])
    if st.button("Settle selected position"):
        p = next(p for p in st.session_state.positions if p["id"] == selected_id)
        won = (p["side"] == outcome)
        payout = p["shares"] if won else 0.0
        pnl = payout - p["stake"]
        st.session_state.cash += payout
        st.session_state.history.append({
            "id": p["id"], "name": p["name"], "category": p["category"],
            "side": p["side"], "outcome": outcome, "stake": p["stake"],
            "payout": payout, "pnl": pnl, "settled": datetime.now(timezone.utc).isoformat()
        })
        st.session_state.positions = [x for x in st.session_state.positions if x["id"] != selected_id]
        st.success(f"Settled. Virtual P&L: ${pnl:,.2f}")
        st.rerun()
else:
    st.info("No open positions yet. Evaluate a market above to begin.")

st.divider()
st.header("3. Settled trade history")
if st.session_state.history:
    hist = pd.DataFrame(st.session_state.history)
    st.dataframe(hist[["id", "name", "category", "side", "outcome", "stake", "payout", "pnl"]], use_container_width=True, hide_index=True)
    total = hist["pnl"].sum()
    wins = (hist["pnl"] > 0).sum()
    st.metric("Closed-trade win rate", f"{wins/len(hist)*100:.1f}%", help="Only based on settled paper trades.")
else:
    st.info("No settled trades yet.")

st.divider()
st.header("4. Risk rules in this prototype")
st.markdown("""
- Maximum single trade: **5% of starting virtual balance**.
- Maximum combined open stake: **20% of starting virtual balance**.
- No leverage, borrowing, deposits, wallet connection or live execution.
- Probability estimates are user-entered; they are not validated AI forecasts.
- A market should only be settled using its official resolution.
""")

with st.expander("Reset the paper-trading account"):
    st.warning("This permanently clears this browser session's virtual positions and trade history.")
    confirm = st.checkbox("I understand that this resets my paper account.")
    if st.button("Reset virtual account", disabled=not confirm):
        for key in ["cash", "positions", "history", "market_inputs", "last_eval"]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

st.caption("Prototype limitation: Streamlit session state is temporary and may reset when the app restarts or the session is lost. Do not use this as a financial decision system.")
