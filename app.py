import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go
from datetime import datetime

# --- LLAVE API ---
API_KEY = '47e6003535bac841cd890537c4b2674e'

st.set_page_config(page_title="AI QUANTUM BETTING", layout="wide")

# --- ESTADO DE SESIÓN (Persistencia durante la navegación) ---
if 'balance' not in st.session_state: st.session_state.balance = 1000.0
if 'history_chart' not in st.session_state: st.session_state.history_chart = [1000.0]
if 'active_bets' not in st.session_state: st.session_state.active_bets = []

# --- DISEÑO BLACK & GOLD ---
st.markdown("""
    <style>
    .stApp { background-color: #050505; color: white; }
    .stMetric { background-color: #111 !important; border: 1px solid #d4af37 !important; border-radius: 10px; padding: 10px; }
    .card { background: #111; padding: 20px; border-radius: 15px; border: 1px solid #333; margin-bottom: 15px; }
    .stButton>button { background: linear-gradient(90deg, #d4af37, #b8962e); color: black; font-weight: bold; width: 100%; border: none; }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR PROFESIONAL ---
with st.sidebar:
    st.title("🛡️ CONTROL PANEL")
    st.metric("CAPITAL DISPONIBLE", f"{st.session_state.balance:.2f} €")
    liga = st.selectbox("MERCADO LÍDER", ["soccer_spain_la_liga", "soccer_spain_segunda_division", "soccer_epl"])
    riesgo = st.slider("MODO KELLY (RIESGO)", 0.1, 0.5, 0.2)
    if st.button("RESET TOTAL"):
        st.session_state.balance = 1000.0
        st.session_state.history_chart = [1000.0]
        st.session_state.active_bets = []
        st.rerun()

# --- NAVEGACIÓN ---
t1, t2, t3 = st.tabs(["🚀 SEÑALES IA", "📋 APUESTAS ABIERTAS", "📈 RENDIMIENTO PRO"])

# --- LÓGICA DE DATOS ---
def fetch_data():
    url = f'https://api.the-odds-api.com/v4/sports/{liga}/odds/?apiKey={API_KEY}&regions=eu&markets=h2h'
    r = requests.get(url)
    return r.json() if r.status_code == 200 else []

# TAB 1: SEÑALES
with t1:
    st.subheader("Algoritmo Predictivo en Tiempo Real")
    partidos = fetch_data()
    if partidos:
        for p in partidos[:8]:
            try:
                home, away = p['home_team'], p['away_team']
                cuota = p['bookmakers'][0]['markets'][0]['outcomes'][0]['price']
                # IA MODEL (Simulando ventaja del 10%)
                confianza = round((1/cuota) + 0.10, 2)
                edge = (confianza * cuota) - 1
                
                if edge > 0.02:
                    stake = round((edge/(cuota-1)) * riesgo * st.session_state.balance, 2)
                    with st.container():
                        st.markdown(f'<div class="card"><b>{home} vs {away}</b><br>Confianza IA: {int(confianza*100)}%</div>', unsafe_allow_html=True)
                        c1, c2, c3 = st.columns([1,1,1])
                        c1.metric("CUOTA", cuota)
                        c2.metric("INVERSIÓN", f"{stake}€")
                        if c3.button("EJECUTAR", key=p['id']):
                            st.session_state.active_bets.append({'id': p['id'], 'desc': f"{home} (Gana)", 'cuota': cuota, 'stake': stake})
                            st.session_state.balance -= stake
                            st.rerun()
            except: continue

# TAB 2: GESTIÓN DE RIESGO
with t2:
    st.subheader("Órdenes en Ejecución")
    if not st.session_state.active_bets:
        st.write("No hay órdenes activas.")
    else:
        for i, bet in enumerate(st.session_state.active_bets):
            with st.container():
                st.markdown(f'<div class="card"><b>{bet["desc"]}</b> | Inversión: {bet["stake"]}€</div>', unsafe_allow_html=True)
                c1, c2 = st.columns(2)
                if c1.button("✅ ACERTADA", key=f"win_{i}"):
                    st.session_state.balance += (bet['stake'] * bet['cuota'])
                    st.session_state.history_chart.append(st.session_state.balance)
                    st.session_state.active_bets.pop(i)
                    st.rerun()
                if c2.button("❌ FALLADA", key=f"loss_{i}"):
                    st.session_state.history_chart.append(st.session_state.balance)
                    st.session_state.active_bets.pop(i)
                    st.rerun()

# TAB 3: ANALYTICS (LO QUE VENDE)
with t3:
    st.subheader("Curva de Crecimiento de Capital")
    fig = go.Figure(data=go.Scatter(y=st.session_state.history_chart, mode='lines+markers', line=dict(color='#d4af37', width=4)))
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white", margin=dict(l=0,r=0,t=0,b=0), xaxis_title="Nº Operación", yaxis_title="Euros")
    st.plotly_chart(fig, use_container_width=True)
