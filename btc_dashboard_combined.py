# (zawartość pliku BTC dashboard.py – już wcześniej wygenerowana)


import streamlit as st
import numpy as np

st.header("📌 Twoja pozycja handlowa")

# Pola wejściowe
entry_price = st.number_input("💰 Cena wejścia (USD)", min_value=0.0, value=100000.0, step=100.0)
stop_loss = st.number_input("🛑 Stop loss (USD)", min_value=0.0, value=98000.0, step=100.0)

# Proste symulowane dane historyczne – będą zastąpione analizą rzeczywistą
historical_simulations = {
    "profits": np.array([0.02, 0.05, -0.01, 0.08, 0.03, -0.02]),
    "losses": np.array([-0.03, -0.04, -0.02, -0.01])
}

# Obliczenia ryzyka i zysku
avg_profit = np.mean(historical_simulations["profits"])
avg_loss = np.mean(historical_simulations["losses"])
estimated_exit = entry_price * (1 + avg_profit)
risk = (entry_price - stop_loss) / entry_price * 100

st.markdown("---")
st.subheader("📊 Prognoza na podstawie danych historycznych")
st.metric("📈 Średni potencjalny zysk", f"{avg_profit*100:.1f}% (≈ ${estimated_exit:,.0f})")
st.metric("📉 Średnia strata historyczna", f"{avg_loss*100:.1f}%")
st.metric("⚠️ Ryzyko (do stop loss)", f"{risk:.1f}%")

# Sygnał logiczny
signal = ""
if avg_profit > 0.03 and risk < 5:
    signal = "🟢 WARTO ROZWAŻYĆ POZYCJĘ"
elif avg_profit < 0.01 or risk > 8:
    signal = "🔴 ZBYT RYZYKOWNIE"
else:
    signal = "🟡 OBSERWUJ RYNEK"

st.markdown("---")
st.subheader("📢 SYGNAŁ NA DZIEŃ DZISIEJSZY")
st.markdown(f"### {signal}")
