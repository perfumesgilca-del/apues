import streamlit as st
import pandas as pd
import datetime

# --- CONFIGURACIÓN DE MARCA ---
st.set_page_config(page_title="AI BETTING SYSTEM - PREMIUM", layout="wide")

# --- CSS DE ALTO NIVEL (DARK GOLD/PLATINUM) ---
st.markdown("""
    <style>
    .stApp { background-color: #0b0e11; color: #ffffff; }
    .premium-card { 
        background: linear-gradient(135deg, #1e1e1e 0%, #2d2d2d 100%);
        padding: 25px; border-radius: 15px; border: 1px solid #d4af37;
        margin-bottom: 20px; box-shadow: 0 4px 15px rgba(212, 175, 55, 0.1);
    }
    .badge-premium { background-color: #d4af37; color: black; padding: 2px 10px; border-radius: 5px; font-weight: bold; font-size: 12px; }
    .metric-box { background-color: #161b22; padding: 15px; border-radius: 10px; text-align: center; border: 1px solid #30363d; }
    </style>
    """, unsafe_allow_html=True)

# --- INICIALIZACIÓN DE ESTADOS ---
if 'bank' not in st.session_state: st.session_state.bank = 1000.0
if 'profit' not in st.session_state: st.session_state.profit = 125.40 # Simulación de ganancia previa

# --- SIDEBAR (PANEL DE USUARIO PREMIUM) ---
with st.sidebar:
    st.markdown("### 💎 USUARIO PREMIUM")
    st.write("Plan: **Anual Professional**")
    st.divider()
    st.metric("BANKROLL TOTAL", f"{st.session_state.bank:.2f} €", delta=f"{st.session_state.profit} € (Last 30d)")
    st.divider()
    riesgo = st.slider("Ajuste Criterio de Kelly", 0.1, 1.0, 0.25)
    st.info("El riesgo actual está optimizado para un crecimiento del 15% mensual.")

# --- DASHBOARD PRINCIPAL ---
st.title("🛡️ AI Betting Intelligence Unit")

col1, col2, col3 = st.columns(3)
col1.markdown('<div class="metric-box">📅 JORNADA: 34<br><b>LaLiga / Premier</b></div>', unsafe_allow_html=True)
col2.markdown('<div class="metric-box">📈 YIELD HISTÓRICO<br><b style="color:#00ff00">+12.4%</b></div>', unsafe_allow_html=True)
col3.markdown('<div class="metric-box">✅ WIN RATE IA<br><b>68.2%</b></div>', unsafe_allow_html=True)

st.divider()

# --- SECCIÓN DE PICKS ---
st.subheader("🎯 Señales Algorítmicas")

# Datos simulados con Categorías
signals = [
    {"tipo": "PREMIUM 💎", "liga": "🇪🇸 LaLiga", "evento": "Real Madrid vs Barcelona", "pick": "GANA REAL MADRID (ML)", "cuota": 2.10, "confianza": 0.82},
    {"tipo": "VALOR ⭐", "liga": "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League", "evento": "Man. City vs Arsenal", "pick": "MÁS DE 9.5 CÓRNERS", "cuota": 1.95, "confianza": 0.65},
    {"tipo": "PREMIUM 💎", "liga": "🇪🇸 Segunda División", "evento": "Eibar vs Zaragoza", "pick": "MENOS DE 2.5 GOLES", "cuota": 1.80, "confianza": 0.78},
    {"tipo": "ESTADÍSTICA 📊", "liga": "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League", "evento": "Tottenham vs Newcastle", "pick": "AMBOS MARCAN (SÍ)", "cuota": 1.65, "confianza": 0.72}
]

for s in signals:
    # Cálculo Kelly
    edge = (s['confianza'] * s['cuota']) - 1
    stake_pct = (edge / (s['cuota'] - 1)) * riesgo
    stake_final = min(stake_pct, 0.05) * st.session_state.bank

    st.markdown(f"""
    <div class="premium-card">
        <span class="badge-premium">{s['tipo']}</span>
        <div style="display: flex; justify-content: space-between; align-items: center; margin-top:10px;">
            <div>
                <small style="color: #8b949e;">{s['liga']}</small>
                <h3 style="margin:0;">{s['evento']}</h3>
                <h4 style="color: #d4af37; margin:0;">{s['pick']}</h4>
            </div>
            <div style="text-align: right;">
                <small style="color: #8b949e;">STAKE SUGERIDO</small>
                <h2 style="margin:0; color: #ffffff;">{stake_final:.2f} €</h2>
                <small style="color: #00ff00;">CONFIDENCIA IA: {int(s['confianza']*100)}%</small>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button(f"Ejecutar Inversión: {s['evento']}", key=s['evento']):
        st.session_state.bank -= stake_final
        st.toast(f"Orden de {stake_final}€ ejecutada correctamente.")
        st.rerun()
